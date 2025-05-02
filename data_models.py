from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# -----------------------
# Author and AuthorDetails
# -----------------------

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date, nullable=True)

    details = db.relationship("AuthorDetails", backref="author", uselist=False,
                              cascade="all, delete-orphan")

    def __str__(self):
        return f"Name: {self.name}, born: {self.birth_date}, died: {self.date_of_death}"

    def __repr__(self):
        return f"<Author {self.name}>"


class AuthorDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    top_subject = db.Column(db.String(80), nullable=False)
    top_work = db.Column(db.String(80), nullable=False)
    work_count = db.Column(db.Integer, nullable=False)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    isbn = db.Column(db.String(80), unique=True, nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    details = db.relationship("BookDetails", backref="book", uselist=False,
                              cascade="all, delete-orphan")
    poster = db.relationship("BookPoster", backref="book", uselist=False,
                             cascade="all, delete-orphan")

    def __str__(self):
        return (f"Title: {self.title}, author_id: {self.author_id}, "
                f"year: {self.publication_year}, isbn: {self.isbn}")

    def __repr__(self):
        return f"<Book {self.title}>"


class BookDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    subtitle = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(80), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    categories = db.Column(db.String(80), nullable=False)


class BookPoster(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    poster_url = db.Column(db.String(200), nullable=False)