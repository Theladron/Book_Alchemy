from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
    Represents an author of one or more books.

    Attributes:
        id (int): Primary key, auto-incrementing unique identifier.
        name (str): Full name of the author (must be unique).
        birth_date (date): The author's birth date.
        date_of_death (date, optional): The author's date of death, if applicable.
        details (AuthorDetails): One-to-one relationship containing additional author details.
    """
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
    """
    Stores additional metadata for an author.

    Attributes:
        id (int): Primary key.
        author_id (int): Foreign key referencing the associated Author.
        top_subject (str): Most common subject or genre associated with the author.
        top_work (str): The author's most popular or notable work.
        work_count (int): Total number of published works by the author.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    top_subject = db.Column(db.String(80), nullable=False)
    top_work = db.Column(db.String(80), nullable=False)
    work_count = db.Column(db.Integer, nullable=False)


class Book(db.Model):
    """
    Represents a book entry in the system.

    Attributes:
        id (int): Primary key.
        title (str): Title of the book.
        isbn (str): Unique ISBN identifier for the book.
        publication_year (int): Year the book was published.
        rating (int): Optional user or critic rating for the book.
        author_id (int): Foreign key linking the book to its author.
        details (BookDetails): One-to-one relationship containing additional metadata.
        poster (BookPoster): One-to-one relationship containing the book's poster image.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80), nullable=False)
    isbn = db.Column(db.String(80), unique=True, nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=True, default=0)

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
    """
    Contains extended details about a specific book.

    Attributes:
        id (int): Primary key.
        book_id (int): Foreign key referencing the Book.
        subtitle (str): Subtitle of the book.
        description (str): A short description or summary of the book.
        publisher (str): Name of the publishing company.
        pages (int): Number of pages in the book.
        categories (str): Comma-separated genres or categories.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    subtitle = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(80), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    categories = db.Column(db.String(80), nullable=False)


class BookPoster(db.Model):
    """
    Contains poster or cover image information for a book.

    Attributes:
        id (int): Primary key.
        book_id (int): Foreign key referencing the Book.
        poster_url (str): URL to the book's cover or promotional image.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    poster_url = db.Column(db.String(200), nullable=False)
