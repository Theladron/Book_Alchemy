import os

from flask import Flask

from data_models import db
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

register_blueprints(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
