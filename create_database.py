import sqlite3
from config import Config

if __name__ == '__main__':
    try:
        db = None
        config = Config()
        db = sqlite3.connect(config.get_storage_path())
        with config.get_sql_scripts_path().joinpath('create_storage.sql').open() as f:
            db.executescript(f.read())
            db.commit()
    finally:
        if db:
            db.close()
