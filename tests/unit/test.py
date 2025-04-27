import sqlite3
import sys
import os
# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database import DatabaseManager

def test_database_connection():
    # Adjust path to point to the correct location of passwords.db
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'passwords.db')

    db_manager = DatabaseManager(db_path=db_path)  # Use the correct DB path
    try:
        # Establish connection
        conn = db_manager.get_connection()
        print("Connection successful!")
        conn.close()  # Close the connection after testing
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_database_connection()
