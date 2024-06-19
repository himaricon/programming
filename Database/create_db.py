import json
import sqlite3
import sys
from config import CONFIG 

class ExampleDB:
    @staticmethod
    def initialize(database_connection: sqlite3.Connection):
        cursor = database_connection.cursor()
        try:
            print("Dropping existing tables (if present)...")
            cursor.execute("DROP TABLE IF EXISTS user")
            cursor.execute("DROP TABLE IF EXISTS friends")
        except sqlite3.OperationalError as db_error:
            print(f"Unable to drop table. Error: {db_error}")

        print("Creating tables...")
        cursor.execute(ExampleDB.CREATE_TABLE_USER)
        cursor.execute(ExampleDB.CREATE_TABLE_FRIENDS)
        database_connection.commit()

        print("Populating database with sample data...")
        # Sample users can be added here if needed
        database_connection.commit()

    CREATE_TABLE_USER = """
    CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        friends_requests TEXT NOT NULL,
        music_data ARRAY NOT NULL
    )
    """

    CREATE_TABLE_FRIENDS = """
    CREATE TABLE IF NOT EXISTS friends (
        friendship_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        friend_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (friend_id) REFERENCES users(user_id)
    )
    """

    INSERT_USER = "INSERT INTO user (user_id, username, password, friends_requests, music_data) VALUES (?, ?, ?, ?, ?)"

    @staticmethod
    def add_user(cursor, user_id, username, password, friends=None, friends_requests=None, music_data=None):
        if friends is None:
            friends = []
        if friends_requests is None:
            friends_requests = []
        if music_data is None:
            music_data = []

        cursor.execute(ExampleDB.INSERT_USER, (
            user_id, username, password,
            json.dumps(friends_requests),
            json.dumps(music_data)
        ))

def main():
    """Execute main function."""
    db_conn = sqlite3.connect(CONFIG["database"]["name"])
    db_conn.row_factory = sqlite3.Row

    ExampleDB.initialize(db_conn)

    # Example of adding a user
    cursor = db_conn.cursor()
    ExampleDB.add_user(cursor, 1, "himar", "himar_password")
    db_conn.commit()
    
    db_conn.close()
    print("Database creation finished!")    

    return 0

# --- Program entry ---
if __name__ == "__main__":
    sys.exit(main())
