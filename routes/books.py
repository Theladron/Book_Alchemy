from flask import Blueprint, render_template, request, jsonify
from data_models import db, Book, BookPoster, BookDetails, Author
from services.chatgpt import get_book_recommendations
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

        # Set default values
        thumbnail = "static/image/fallback_cover.png"
        info_link = "N/A"
        subtitle = "N/A"
        description = "N/A"
        publisher = "N/A"
        pages = "N/A"
        categories = "N/A"

        data = {"totalItems": 0, "items": []}

        try:
            resp = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")
            data = resp.json()
            if data.get("totalItems", 0) > 0:
                vol = data["items"][0]["volumeInfo"]
                thumbnail = vol.get("imageLinks", {}).get("thumbnail", thumbnail)
                info_link = vol.get("infoLink", info_link)
                subtitle = vol.get("subtitle", subtitle)
                description = vol.get("description", description)
                publisher = vol.get("publisher", publisher)
                pages = vol.get("pageCount", pages)
                categories_list = vol.get("categories", [])
                categories = ", ".join(categories_list) if categories_list else "N/A"
        except requests.exceptions.RequestException:
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
                return jsonify({
                    "error": f"Author '{author_name}' not found in database. Please add them first."
                }), 400

            book = Book(
                title=title,
                isbn=isbn,
                publication_year=int(year),
                author_id=author.id,
                rating=0
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
                author_id=int(author_id),
                rating=0
            )

        else:
            return jsonify({"error": "Invalid submission mode"}), 400

        try:
            book.poster = BookPoster(poster_url=thumbnail)
            book.details = BookDetails(
                subtitle=subtitle,
                description=description,
                publisher=publisher,
                pages=pages,
                categories=categories
            )
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Database error", "details": str(e)}), 500

        return jsonify({"message": "Book added successfully"}), 201

    return render_template('add_book.html', authors=authors)


@books_bp.route('/book/<int:book_id>/delete', methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    author_id = book.author_id

    try:
        # Delete is cascaded for poster and details
        db.session.delete(book)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    # Check if this was the author's last book
    remaining_books = Book.query.filter_by(author_id=author_id).count()
    if remaining_books == 0:
        return jsonify({
            "message": "Book deleted successfully. This was the author's last book.",
            "author_id": author_id
        }), 200

    return jsonify({"message": "Book deleted successfully"}), 200


@books_bp.route("/book_details/<int:book_id>")
def book_details(book_id):
    # Fetch the book details
    details = db.session.query(BookDetails).filter_by(book_id=book_id).first()

    if not details:
        return jsonify({"details": "No book details available."})

    # Fetch book details
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Return relevant book information, fallback to "N/A" if missing
    subtitle = details.subtitle or "N/A"
    description = details.description or "N/A"
    publisher = details.publisher or "N/A"
    pages = details.pages or "N/A"
    categories = details.categories or "N/A"

    details_text = (
        f"Subtitle: {subtitle}\n"
        f"Description: {description}\n"
        f"Publisher: {publisher}\n"
        f"Pages: {pages}\n"
        f"Categories: {categories}"
    )

    return jsonify({"details": details_text})


@books_bp.route("/book/<int:book_id>/recommendations", methods=["GET"])
def get_recommendations(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    details = book.details
    title = book.title

    # Ensure categories are not None or empty, default to "N/A"
    genre = details.categories if details and details.categories and details.categories != "N/A" else "N/A"

    recommendation_text = get_book_recommendations(title, genre)
    recommendations = recommendation_text.split('\n')
    recommendations = [line.strip() for line in recommendations if line.strip()]

    return jsonify({"recommendations": recommendations})


def update_rating(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    # Get the new rating from the request
    new_rating = request.json.get("rating")
    if not new_rating or not (1 <= new_rating <= 10):
        return jsonify({"error": "Rating must be between 1 and 10"}), 400

    # Update the book's rating
    book.rating = new_rating

    try:
        db.session.commit()
        return jsonify({"message": "Rating updated successfully", "rating": new_rating}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
