import datetime
from urllib.parse import quote_plus

import requests
from flask import Blueprint, render_template, request, jsonify

from data_models import db, Author, Book, BookPoster, AuthorDetails
from services.chatgpt import get_author_recommendations

authors_bp = Blueprint("authors", __name__)


@authors_bp.route('/add_author', methods=["GET", "POST"])
def add_author():
    """Provides a Html page to add an author on get request, handles and validates
    post requests, calls for additional author information and adds it to the
    database if valid, handles errors"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        birth_date = request.form.get("birthdate")
        date_of_death = request.form.get("date_of_death")

        if not name:
            return jsonify({"error": "Name is required"}), 400
        if not birth_date:
            return jsonify({"error": "Birth date is required"}), 400

        if Author.query.filter(Author.name.ilike(name)).first():
            return jsonify({"error": f"Author '{name}' already exists."}), 400

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

        top_subject = "N/A"
        top_work = "N/A"
        work_count = "N/A"

        try:
            url = f"https://openlibrary.org/search/authors.json?q={quote_plus(name)}"
            resp = requests.get(url)
            data = resp.json()
            if data.get("numFound", 0) > 0:
                doc = data["docs"][0]
                top_subject = doc.get("top_subjects", ["N/A"])[0]
                top_work = doc.get("top_work", "N/A")
                work_count = doc.get("work_count", "N/A")
        except requests.RequestException:
            pass

        author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )
        author.details = AuthorDetails(
            top_subject=top_subject,
            top_work=top_work,
            work_count=work_count
        )

        try:
            db.session.add(author)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Database error", "details": str(e)}), 500

        return jsonify({"message": "Author created successfully"}), 201

    return render_template('add_author.html')


@authors_bp.route('/author/<int:author_id>/delete', methods=["DELETE"])
def delete_author(author_id):
    """Handles author deletion, deletes all books from the author if author is deleted,
        handles exceptions"""
    author = Author.query.get(author_id)
    if not author:
        return jsonify({"error": "Author not found"}), 404

    book_ids = [book.id for book in Book.query.filter_by(author_id=author_id).all()]

    if book_ids:
        BookPoster.query.filter(BookPoster.book_id.in_(book_ids)).delete(synchronize_session=False)

    Book.query.filter(Book.id.in_(book_ids)).delete(synchronize_session=False)

    db.session.delete(author)
    db.session.commit()

    return jsonify({"message": "Author and all their books deleted"}), 200


@authors_bp.route("/author_details/<int:author_id>")
def author_details(author_id):
    """Returns author information if available, else N/A for missing entries, handles exceptions"""
    details = db.session.query(AuthorDetails).filter_by(author_id=author_id).first()

    if not details:
        return jsonify({"error": "No author details available."})

    return jsonify({
        "top_subject": details.top_subject or "N/A",
        "top_work": details.top_work or "N/A",
        "work_count": details.work_count or "N/A"
    })


@authors_bp.route("/author/<int:author_id>/recommendations", methods=["GET"])
def get_author_recommendations_route(author_id):
    """Calls for author recommendations based on the current author the author's top genre, returns
        the recommendations"""
    author = Author.query.get(author_id)
    if not author:
        return jsonify({"error": "Author not found"}), 404

    author_details = author.details
    if not author_details:
        return jsonify({"error": "Author details not found"}), 404

    recommendation_text = get_author_recommendations(author.name, author_details.top_subject)

    recommendations = recommendation_text.split('\n')
    recommendations = [line.strip() for line in recommendations if line.strip()]

    return jsonify({"recommendations": recommendations})
