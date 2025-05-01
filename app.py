import os
import datetime
import requests
from flask import Flask, render_template, redirect, url_for, jsonify, request
from data_models import db, Author, Book, BookPoster, BookDetails
from db_validator import validate_database
from routes import register_blueprints

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(basedir, 'data')
db_file = os.path.join(data_folder, 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_file}"

db.init_app(app)
# Checks if the database, tables and columns exist
validate_database(app)

# Loads all routes
register_blueprints(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
