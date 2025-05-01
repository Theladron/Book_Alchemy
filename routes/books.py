from flask import Blueprint, render_template, request, jsonify
from data_models import db, Book, BookPoster, BookDetails, Author
import requests

books_bp = Blueprint("books", __name__)

@books_bp.route('/add_book', methods=["GET", "POST"])
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


@books_bp.route('/book/<int:book_id>/delete', methods=["DELETE"])
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