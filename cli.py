import argparse
import sqlite3
from Server.user_api_shim import add_user

# Global variable for the database connection
DATABASE_NAME = "users.db"

def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)

def main():
    parser = argparse.ArgumentParser(description="CLI for interacting with user database")
    subparsers = parser.add_subparsers(dest="command")

    add_user_parser = subparsers.add_parser("add_user")
    add_user_parser.add_argument("username")
    add_user_parser.add_argument("password")
    


    
    

    args = parser.parse_args()

    if args.command == "add_user":
        conn = get_db_connection()
        add_user(args.username, args.password)
        conn.close()
   
if __name__ == "__main__":
    main()
