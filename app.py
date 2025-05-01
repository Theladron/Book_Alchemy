import os
import datetime
import requests
from flask import Flask, render_template, redirect, url_for, jsonify, request
from data_models import db, Author, Book, BookPoster

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data', 'library.sqlite')}"

db.init_app(app)

@app.route('/add_author', methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form.get("name")
        birth_date = request.form.get("birthdate")
        date_of_death = request.form.get("date_of_death")

        if not birth_date:
            return jsonify({"error": "Birth date is required"}), 400

        if not name or name.strip() == "":
            return jsonify({"error": "Name is required"}), 400

        try:

            birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid birthdate format. Use YYYY-MM-DD."}), 400

        if date_of_death.strip() == "":
            date_of_death = None
        elif date_of_death:
            try:
                date_of_death = datetime.datetime.strptime(date_of_death, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date_of_death format. Use YYYY-MM-DD."}), 400
        author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(author)
        db.session.commit()
        return jsonify({"message": "Author created successfully"}), 201
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

        # ===== MODE 1: ISBN LOOKUP =====
        if mode == "isbn_lookup":
            url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            try:
                response = requests.get(url).json()
            except requests.exceptions.RequestException:
                return jsonify({"error": "Error connecting to Google Books API"}), 400

            if response.get("totalItems", 0) == 0:
                return jsonify({"error": "No book found with this ISBN"}), 400

            item = response['items'][0]['volumeInfo']

            title = item.get("title")
            published_year = item.get("publishedDate", "")[:4]
            author_name = item.get("authors", [""])[0]

            if not title or not published_year or not author_name:
                return jsonify({"error": "Incomplete book data from API"}), 400

            # Match author by name
            author = Author.query.filter(Author.name.ilike(author_name)).first()
            if not author:
                return jsonify({"error": f"Author '{author_name}' not found in database. Please add them first."}), 400

            # Get poster
            thumbnail = item.get('imageLinks', {}).get('thumbnail', "static/image/fallback_cover.png")

            # Create entries
            book = Book(title=title, isbn=isbn, publication_year=int(published_year), author_id=author.id)
            poster = BookPoster(book_isbn=isbn, poster_url=thumbnail)

            db.session.add(book)
            db.session.add(poster)
            db.session.commit()

            return jsonify({"message": "Book added using ISBN lookup"}), 201

        # ===== MODE 2: MANUAL ENTRY =====
        elif mode == "manual":
            title = request.form.get("title", "").strip()
            publication_year = request.form.get("publication_year", "").strip()
            author_id = request.form.get("author_id", "").strip()

            if not title or not publication_year or not author_id:
                return jsonify({"error": "All fields are required in manual mode"}), 400

            # Get poster from API, fallback if not found
            try:
                api_response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}").json()
                item = api_response.get("items", [])[0]
                thumbnail = item.get("volumeInfo", {}).get("imageLinks", {}).get("thumbnail", "static/image/fallback_cover.png")
            except Exception:
                thumbnail = "static/image/fallback_cover.png"

            book = Book(
                title=title,
                isbn=isbn,
                publication_year=int(publication_year),
                author_id=int(author_id)
            )
            poster = BookPoster(book_isbn=isbn, poster_url=thumbnail)

            db.session.add(book)
            db.session.add(poster)
            db.session.commit()

            return jsonify({"message": "Book manually added"}), 201

        return jsonify({"error": "Invalid submission mode"}), 400

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
    order = request.args.get("order", "asc")
    search = request.args.get("search", "").strip()

    query = db.session.query(BookPoster,
                             Book,
                             Author).join(Book,
                                          BookPoster.book_isbn == Book.isbn).join(Author)

    if search:
        search_like = f"%{search}%"
        query = query.filter(db.or_(
            Book.title.ilike(search_like),
            Author.name.ilike(search_like)
        ))

    sort_columns = {
        "title": Book.title,
        "author": Author.name,
        "year": Book.publication_year
    }

    sort_column = sort_columns.get(sort_by, Book.title)

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    books = query.all()
    return render_template('home.html', books=books, sort_by=sort_by, order=order, search=search)

#with app.app_context():
    #db.create_all()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
