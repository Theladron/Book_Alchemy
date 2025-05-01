import os
import datetime
import requests
from flask import Flask, render_template, redirect, url_for, jsonify, request
from data_models import db, Author, Book, BookPoster, BookDetails
from db_validator import validate_database

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(basedir, 'data')
db_file = os.path.join(data_folder, 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file}"

# Checks if the database, tables and columns exist
validate_database(app)

db.init_app(app)

@app.route('/add_author', methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get("name").strip()
        birth_date = request.form.get("birthdate")
        date_of_death = request.form.get("date_of_death")

        # Check duplicate author
        if Author.query.filter(Author.name.ilike(name)).first():
            return jsonify({"error": f"Author '{name}' already exists."}), 400

        if not birth_date:
            return jsonify({"error": "Birth date is required"}), 400

        if not name:
            return jsonify({"error": "Name is required"}), 400

        try:
            birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid birthdate format. Use YYYY-MM-DD."}), 400

        if date_of_death:
            try:
                date_of_death = datetime.datetime.strptime(date_of_death, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date_of_death format. Use YYYY-MM-DD."}), 400
        else:
            date_of_death = None

        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        return jsonify({"message": "Author created successfully", "author_id": author.id}), 201

    return render_template('add_author.html')

@app.route('/add_book', methods=["GET", "POST"])
def add_book():
    authors = Author.query.order_by(Author.name).all()

    if request.method == "POST":
        mode = request.form.get("mode")  # "manual" or "isbn_lookup"
        isbn = request.form.get("isbn", "").strip()

        if not isbn:
            return jsonify({"error": "ISBN is required"}), 400

        # Check if book already exists
        if Book.query.filter_by(isbn=isbn).first():
            return jsonify({"error": "Book with this ISBN already exists"}), 400

        # Set defaults / fallbacks
        thumbnail = "static/image/fallback_cover.png"
        info_link = "No data available for this book"
        data = {"totalItems": 0, "items": []}

        # Try fetching from the API for both modes
        try:
            resp = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")
            data = resp.json()
            if data.get("totalItems", 0) > 0:
                vol = data["items"][0]["volumeInfo"]
                # override fallback values if present
                thumbnail = vol.get("imageLinks", {}).get("thumbnail", thumbnail)
                info_link = vol.get("infoLink", info_link)
        except requests.exceptions.RequestException:
            # silent fallback since we created default data for this case
            pass

        # ===== MODE 1: ISBN LOOKUP =====
        if mode == "isbn_lookup":
            if data.get("totalItems", 0) == 0:
                return jsonify({"error": "No book found with this ISBN"}), 400

            vol = data["items"][0]["volumeInfo"]
            title = vol.get("title")
            year = vol.get("publishedDate", "")[:4]
            author_name = vol.get("authors", [""])[0]

            if not title or not year or not author_name:
                return jsonify({"error": "Incomplete book data from API"}), 400

            author = Author.query.filter(Author.name.ilike(author_name)).first()
            if not author:
                return jsonify({"error": f"Author '{author_name}' not found in database. Please add them first."}), 400

            book = Book(
                title=title,
                isbn=isbn,
                publication_year=int(year),
                author_id=author.id
            )

        # ===== MODE 2: MANUAL ENTRY =====
        elif mode == "manual":
            title = request.form.get("title", "").strip()
            year = request.form.get("publication_year", "").strip()
            author_id = request.form.get("author_id", "").strip()

            if not title or not year or not author_id:
                return jsonify({"error": "All fields are required in manual mode"}), 400

            book = Book(
                title=title,
                isbn=isbn,
                publication_year=int(year),
                author_id=int(author_id)
            )

        else:
            return jsonify({"error": "Invalid submission mode"}), 400

        # Persist Book and Poster
        poster = BookPoster(book_isbn=isbn, poster_url=thumbnail)
        db.session.add(book)
        db.session.add(poster)
        db.session.commit()

        # Persist BookDetails (infoLink or fallback text)
        details = BookDetails(book_isbn=isbn, details=info_link)
        db.session.add(details)
        db.session.commit()

        return jsonify({"message": "Book added successfully"}), 201

    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/delete', methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    author_id = book.author_id
    isbn = book.isbn

    # 1) Delete any posters for this book
    BookPoster.query.filter_by(book_isbn=isbn).delete(synchronize_session=False)

    # 2) Delete the book itself
    db.session.delete(book)
    db.session.commit()

    # 3) Check remaining books by this author
    remaining_books = Book.query.filter_by(author_id=author_id).count()
    if remaining_books == 0:
        # Inform frontend that this was the author's last book
        return jsonify({
            "message": "Book deleted successfully. This was the author's last book.",
            "author_id": author_id
        }), 200

    return jsonify({"message": "Book deleted successfully"}), 200


@app.route('/author/<int:author_id>/delete', methods=["DELETE"])
def delete_author(author_id):
    author = Author.query.get(author_id)
    if not author:
        return jsonify({"error": "Author not found"}), 404

    # 1) Gather all ISBNs for this author's books
    isbns = [book.isbn for book in Book.query.filter_by(author_id=author_id).all()]

    # 2) Delete all posters for those ISBNs
    if isbns:
        BookPoster.query.filter(BookPoster.book_isbn.in_(isbns)) \
                        .delete(synchronize_session=False)

    # 3) Delete all books by this author
    Book.query.filter_by(author_id=author_id).delete(synchronize_session=False)

    # 4) Finally delete the author
    db.session.delete(author)
    db.session.commit()

    return jsonify({"message": "Author and all their books deleted"}), 200


@app.route('/')
def index():
    sort_by = request.args.get("sort_by", "title")
    order   = request.args.get("order", "asc")
    search  = request.args.get("search", "").strip()

    # Base query: join BookPoster, Book, Author, BookDetails
    query = (
        db.session.query(BookPoster, Book, Author, BookDetails)
        .join(Book, BookPoster.book_isbn == Book.isbn)
        .join(Author, Book.author_id == Author.id)
        .outerjoin(BookDetails, BookDetails.book_isbn == Book.isbn)
    )

    # Apply search filter
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Book.title.ilike(like), Author.name.ilike(like))
        )

    # Sorting
    columns = {
        "title": Book.title,
        "author": Author.name,
        "year": Book.publication_year
    }
    col = columns.get(sort_by, Book.title)
    if order == "desc":
        query = query.order_by(col.desc())
    else:
        query = query.order_by(col.asc())

    books = query.all()
    return render_template(
        'home.html',
        books=books,
        sort_by=sort_by,
        order=order,
        search=search
    )

#with app.app_context():
    #db.create_all()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
