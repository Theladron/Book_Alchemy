import os
from flask import Flask
from data_models import db

# creating absolute path to the data folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# creating absolute path to the database
DB_PATH = os.path.join(DATA_DIR, 'library.sqlite')

# setting up flask and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# creating the database with tables
with app.app_context():
    db.create_all()
    print("Database and tables created successfully!")