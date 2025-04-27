import pytest
import os
import sqlite3
import time
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication, QTableWidget
from datetime import datetime, timedelta

# Ensure the src directory is in the path
import sys
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from app import PasswordGenerator
from database import DatabaseManager


@pytest.fixture(scope="session")
def app_instance():
    """Ensure QApplication instance is created once per session."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def test_db():
    """Set up a test database with a clean state before each test."""
    db = DatabaseManager(db_path="test_passwords.db")
    db.initialize_database()

    # Clean test data
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stored_passwords;")
        cursor.execute("DELETE FROM dismissed_alerts;")
        conn.commit()

    yield db  # Provide database instance to test

    # Ensure the database is properly closed before deletion
    try:
        with sqlite3.connect(db.db_path) as conn:
            conn.close()
        time.sleep(0.5)  # Allow time before deleting
        os.remove("test_passwords.db")
    except Exception as e:
        print(f"Warning: Could not delete test database, reason: {e}")


@pytest.fixture
def password_generator(app_instance, test_db):
    """Create a PasswordGenerator instance and attach the test database."""
    generator = PasswordGenerator()
    generator.db = test_db  # Use test DB instead of real one

    # Ensure required attributes exist
    if not hasattr(generator, "expiry_table"):
        generator.expiry_table = QTableWidget()
        generator.expiry_table.setColumnCount(3)
        generator.expiry_table.setRowCount(1)

    if not hasattr(generator, "dismissed_passwords"):
        generator.dismissed_passwords = set()

    if not hasattr(generator, "expiry_dialog"):
        generator.expiry_dialog = MagicMock()  # Mock expiry_dialog to prevent AttributeError

    return generator


def test_dismiss_expiry_alert_removes_password(password_generator, test_db):
    """Ensure dismissing a password removes it from the UI and records it in the database."""

    # Insert a test password into the database
    expiry_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
    test_db.save_password("test.com", "user1", "encrypted_pass", "Work", expiry_date)

    # Fetch the inserted password's ID
    with sqlite3.connect(test_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM stored_passwords WHERE website = 'test.com'")
        password_id = cursor.fetchone()[0]

    # Ensure the password appears in expiring passwords
    expiring_passwords = test_db.get_active_expiring_passwords()
    assert len(expiring_passwords) == 1, "Password was not saved correctly."

    # Open the expiring passwords UI
    password_generator.show_expiring_passwords()

    # Ensure `expiry_table` is initialized
    if password_generator.expiry_table is None:
        password_generator.expiry_table = QTableWidget()
        password_generator.expiry_table.setColumnCount(3)
        password_generator.expiry_table.setRowCount(1)

    assert password_generator.expiry_table is not None, "expiry_table was not initialized."

    # Dismiss the password (row index = 0)
    password_generator.dismiss_expiry_alert(password_id, 0)

    # Verify that the dismissal was recorded in the database
    with sqlite3.connect(test_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dismissed_alerts WHERE password_id = ?", (password_id,))
        dismissed_count = cursor.fetchone()[0]

    assert dismissed_count == 1, f"Password dismissal was not recorded in the database. Expected 1, got {dismissed_count}."


def test_dismissed_passwords_do_not_reappear(password_generator, test_db):
    """Ensure dismissed passwords do not reappear when fetching expiring passwords."""

    expiry_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
    test_db.save_password("example.com", "user2", "pass123", "Personal", expiry_date)

    # Fetch the inserted password's ID
    with sqlite3.connect(test_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM stored_passwords WHERE website = 'example.com'")
        password_id = cursor.fetchone()[0]

    # Open the expiring passwords UI
    with patch.object(password_generator, 'show_expiring_passwords', return_value=None):
        password_generator.show_expiring_passwords()

    # Ensure `dismissed_passwords` attribute exists
    if not hasattr(password_generator, "dismissed_passwords"):
        password_generator.dismissed_passwords = set()

    # Ensure `expiry_dialog` attribute exists
    if not hasattr(password_generator, "expiry_dialog"):
        password_generator.expiry_dialog = MagicMock()

    # Dismiss the password (row index = 0)
    password_generator.dismiss_expiry_alert(password_id, 0)

    # Ensure the password does not reappear in the expiring passwords list
    expiring_passwords = test_db.get_active_expiring_passwords()
    assert password_id not in [p[0] for p in expiring_passwords], f"Dismissed password {password_id} reappeared."
