from flask import Blueprint, render_template, request, jsonify

from data_models import db, Book, BookPoster, Author
from services.chatgpt import get_homepage_recommendations

main_bp = Blueprint("main", __name__)


@main_bp.route('/')
def index():
    sort_by = request.args.get("sort_by", "title")
    order = request.args.get("order", "asc")
    search = request.args.get("search", "").strip()

    query = (
        db.session.query(BookPoster, Book, Author)  # only 3 items
        .join(Book, BookPoster.book_id == Book.id)
        .join(Author, Book.author_id == Author.id)
    )

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(Book.title.ilike(like), Author.name.ilike(like))
        )

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


@main_bp.route('/book_recommendations', methods=["GET"])
def book_recommendations():
    books_with_ratings = Book.query.filter(Book.rating > 0).all()

    recommendations_text = get_homepage_recommendations(books_with_ratings)

    recommendations = recommendations_text.split('\n')
    recommendations = [line.strip() for line in recommendations if line.strip()]

    return jsonify({"recommendations": recommendations})
