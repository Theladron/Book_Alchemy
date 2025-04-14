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
    if request.method == "POST":
        title = request.form.get("title")
        isbn = request.form.get("isbn")
        publication_year = request.form.get("publication_year")
        author_id = request.form.get("author_id")

        # checking for empty fields
        if not title or title.strip() == "":
            return jsonify({"error": "Title is required"}), 400
        if not isbn or isbn.strip() == "":
            return jsonify({"error": "ISBN is required"}), 400
        if not publication_year or publication_year.strip() == "":
            return jsonify({"error": "Publication year is required"}), 400
        if not author_id or author_id.strip() == "":
            return jsonify({"error": "Author ID is required"}), 400

        # checking for existing book
        existing_book = Book.query.filter_by(isbn=isbn).first()
        if not existing_book:
            book = Book(
                title=title,
                isbn=isbn,
                publication_year=publication_year,
                author_id=author_id
            )
        else:
            return jsonify({"error": "Book with this ISBN already exists"}), 400
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

        # fetching book poster, handling data error
        try:
            response = requests.get(url).json()
        except requests.exceptions.RequestException:
            return jsonify({"error": "Error connecting to Google Books API"}), 400
        if response['totalItems'] == 0:
            return jsonify({"error": "No book found with this ISBN"}), 400

        # checking title
        if title != response['items'][0]['volumeInfo']['title']:
            return jsonify({"error": "Title does not match the book found"}), 400

        # creating fallback in case the book exists, but the poster is not found
        try:
            item = response.get('items', [])[0]
            thumbnail = item['volumeInfo']['imageLinks']['thumbnail']
        except (IndexError, KeyError, TypeError):
            thumbnail = "static/image/fallback_cover.png"

        poster = BookPoster(book_isbn=isbn, poster_url=thumbnail)

        db.session.add(book)
        db.session.add(poster)
        db.session.commit()
        return jsonify({"message": "Book created successfully"}), 201
    query = db.session.query(Author)
    return render_template('add_book.html')


@app.route('/book/<int:book_id>/delete', methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    author_id = book.author_id
    db.session.delete(book)
    db.session.commit()

    remaining_books = Book.query.filter_by(author_id=author_id).count()

    # checking if author has no other books
    if remaining_books == 0:
        author = Author.query.get(author_id)
        db.session.delete(author)
        db.commit()
        return jsonify({
            "message": "Book and its author (no other books) deleted successfully"
        }), 200

    return jsonify({"message": "Book deleted successfully"}), 200

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
