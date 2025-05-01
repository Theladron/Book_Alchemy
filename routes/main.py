from flask import Blueprint, render_template, request
from data_models import db, Book, BookPoster, Author, BookDetails

main_bp = Blueprint("main", __name__)

@main_bp.route('/')
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