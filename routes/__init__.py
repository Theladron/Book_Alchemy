from .books import books_bp
from .authors import authors_bp
from .main import main_bp

def register_blueprints(app):
    app.register_blueprint(books_bp)
    app.register_blueprint(authors_bp)
    app.register_blueprint(main_bp)