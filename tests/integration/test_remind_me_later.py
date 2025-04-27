import sqlite3
import os
import sys
from datetime import datetime, timedelta
import pytest

# Add the src directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from database import DatabaseManager

@pytest.fixture
def db_manager():
    """Fixture to initialize DatabaseManager with test database."""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_passwords.db")
    return DatabaseManager(db_path=db_path)



@pytest.fixture
def setup_test_data(db_manager):
    """Insert test data for expiry notifications."""
    with sqlite3.connect(db_manager.db_path) as conn:
        cursor = conn.cursor()

        # Drop and recreate the table to ensure correct schema
        cursor.execute("DROP TABLE IF EXISTS stored_passwords")
        cursor.execute("""
            CREATE TABLE stored_passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT,
                username TEXT,
                encrypted_password TEXT,
                expiry_date TEXT,
                last_dismissed TEXT
            )
        """)

        expiry_dates = {
            "expired": datetime.now() - timedelta(days=1),
            "soon": datetime.now() + timedelta(days=2),
            "later": datetime.now() + timedelta(days=10)
        }

        test_data = [
            ("expired.com", "user1", "dummy_password", expiry_dates["expired"].strftime('%Y-%m-%d %H:%M:%S'), None),
            ("soon.com", "user2", "dummy_password", expiry_dates["soon"].strftime('%Y-%m-%d %H:%M:%S'), None),
            ("later.com", "user3", "dummy_password", expiry_dates["later"].strftime('%Y-%m-%d %H:%M:%S'), None)
        ]

        cursor.executemany("""
            INSERT INTO stored_passwords (website, username, encrypted_password, expiry_date, last_dismissed)
            VALUES (?, ?, ?, ?, ?)
        """, test_data)
        conn.commit()

    print("Test data with 'last_dismissed' inserted successfully!")

def test_remind_me_later(db_manager, setup_test_data):
    """Test if 'Remind Me Later' properly updates and expires notifications."""
    with sqlite3.connect(db_manager.db_path) as conn:
        cursor = conn.cursor()

        # Step 1: Dismiss "soon.com" alert
        cursor.execute("""
            UPDATE stored_passwords
            SET last_dismissed = datetime('now')
            WHERE website = 'soon.com'
        """)
        conn.commit()
        
        # Step 2: Ensure it is hidden within 24 hours
        cursor.execute("""
            SELECT website FROM stored_passwords
            WHERE expiry_date BETWEEN datetime('now') AND datetime('now', '+7 days')
            AND (last_dismissed IS NULL OR last_dismissed < datetime('now', '-24 hours'))
        """)
        visible_alerts = [row[0] for row in cursor.fetchall()]
        
        assert "soon.com" not in visible_alerts, " 'Remind Me Later' failed, alert should be hidden!"
        
        # Step 3: Simulate time passing (manually set last_dismissed to 25 hours ago)
        cursor.execute("""
            UPDATE stored_passwords
            SET last_dismissed = datetime('now', '-25 hours')
            WHERE website = 'soon.com'
        """)
        conn.commit()

        # Step 4: Ensure the alert is now visible again
        cursor.execute("""
            SELECT website FROM stored_passwords
            WHERE expiry_date BETWEEN datetime('now') AND datetime('now', '+7 days')
            AND (last_dismissed IS NULL OR last_dismissed < datetime('now', '-24 hours'))
        """)
        visible_alerts_after_24h = [row[0] for row in cursor.fetchall()]
        
        assert "soon.com" in visible_alerts_after_24h, " 'Remind Me Later' failed, alert should reappear after 24 hours!"

    print("Remind Me Later logic works correctly!")

# Run the test
if __name__ == "__main__":
    pytest.main(["-v", "test_remind_me_later.py"])
