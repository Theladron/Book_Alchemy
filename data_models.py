from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date, nullable=True)

    def __str__(self):
        return f"Name: {self.name}, born: {self.birth_date}, died: {self.date_of_death}"
    def __repr__(self):
        return f"<Author {self.name}>"

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    isbn = db.Column(db.String(80), unique=True, nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def __str__(self):
        return (f"Title: {self.title}, author: {self.author.name}, "
                f"publication year: {self.publication_year}, isbn: {self.isbn}")
    def __repr__(self):
        return f"<Book {self.title}>"

class BookPoster(db.Model):
    id  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_isbn = db.Column(db.String(80), db.ForeignKey('book.isbn'), nullable=False)
    poster_url = db.Column(db.String(80), nullable=False)
