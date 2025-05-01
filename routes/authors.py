from flask import Blueprint, render_template, request, jsonify
from data_models import db, Author, Book, BookPoster
import datetime

authors_bp = Blueprint("authors", __name__)

@authors_bp.route('/add_author', methods=["GET", "POST"])
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




@authors_bp.route('/author/<int:author_id>/delete', methods=["DELETE"])
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