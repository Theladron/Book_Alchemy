import os
import sys

from sqlalchemy import inspect

from data_models import db

basedir = os.path.abspath(os.path.dirname(__file__))


def validate_database(app):
    db_path = os.path.join(basedir, 'data', 'library.sqlite')

    if not os.path.isfile(db_path):
        print("❌ Database not found. Please run db_setup.py to create the database.")
        sys.exit(1)

    with app.app_context():
        inspector = inspect(db.engine)

        expected_tables = {
            'author': {'id', 'name', 'birth_date', 'date_of_death'},
            'book': {'id', 'title', 'isbn', 'publication_year', 'author_id', 'rating'},
            'book_poster': {'id', 'book_id', 'poster_url'},
            'book_details': {'id', 'book_id', 'subtitle', 'description',
                             'publisher', 'pages', 'categories'},
            'author_details': {'id', 'author_id', 'top_subject', 'top_work', 'work_count'}
        }

        actual_tables = set(inspector.get_table_names())
        missing_tables = set(expected_tables.keys()) - actual_tables
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}.")
            print("Please delete the database and rerun db_setup.py.")
            sys.exit(1)

        for table, expected_cols in expected_tables.items():
            actual_cols = {col["name"] for col in inspector.get_columns(table)}
            if expected_cols != actual_cols:
                print(f"❌ Table '{table}' has incorrect columns.")
                print(f"Expected: {expected_cols}")
                print(f"Found:    {actual_cols}")
                print("Please delete the database and rerun db_setup.py.")
                sys.exit(1)

    print("✅ Database validated successfully.")
