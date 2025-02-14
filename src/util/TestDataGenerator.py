import os

from sqlalchemy import text, inspect

from src.extensions import db


class TableNotFoundError(Exception):
    """Custom exception for when a table does not exist."""
    pass


def initialize_test_data(test_data_dir='test_data', force_insert=False):
    if not os.path.exists(test_data_dir):
        print(f"Invalid test data directory: '{test_data_dir}' - skipping generating test data")
        return

    for filename in os.listdir(test_data_dir):
        if filename.endswith('.sql'):
            try:
                filename_table_prefix = filename.split('_')[0]
                existing_tables = inspect(db.engine).get_table_names()

                if filename_table_prefix not in existing_tables:
                    raise TableNotFoundError(f"Table: '{filename_table_prefix}' not found.")

                is_table_empty = db.session.execute(text(f"SELECT COUNT(*) FROM {filename_table_prefix}")).scalar() == 0

                if is_table_empty or force_insert:
                    with open(os.path.join(test_data_dir, filename), 'r') as sql_file:
                        sql_script = sql_file.read()

                    db.session.execute(text(sql_script))
                    db.session.commit()
                    print(f"Successfully executed test data SQL script: '{filename}'")
                else:
                    print(f"Skipping test data generation for script: '{filename}'")
            except Exception as e:
                print(f"Failed to execute test data SQL script: '{filename}'. Error: {e}")
                db.session.rollback()
