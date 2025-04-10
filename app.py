import os
import datetime
from flask import Flask, render_template, redirect, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book

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
        if not title or title.strip() == "":
            return jsonify({"error": "Title is required"}), 400
        if not isbn or isbn.strip() == "":
            return jsonify({"error": "ISBN is required"}), 400
        if not publication_year or publication_year.strip() == "":
            return jsonify({"error": "Publication year is required"}), 400
        if not author_id or author_id.strip() == "":
            return jsonify({"error": "Author ID is required"}), 400

        book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)
        db.session.add(book)
        db.session.commit()
        return jsonify({"message": "Book created successfully"}), 201
    return render_template('add_book.html')

@app.route('/')
def index():
    books = db.session.query(Book, Author).join(Author).all()

    return render_template('home.html', books=books)


# with app.app_context():
#     db.create_all()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
