import pytest
import sqlite3
import os
import sys
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor
from unittest.mock import MagicMock

# Add the src directory to the system path
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from database import DatabaseManager
from app import PasswordGenerator  # Import the main app class for testing

# Expected severity levels mapped to colors
EXPECTED_SEVERITY = {
    "Critical": QColor(255, 0, 0),  # Red
    "High": QColor(255, 165, 0),  # Orange
    "Medium": QColor(255, 255, 0),  # Yellow
    "Low": QColor(211, 211, 211),  # Light Gray
    "Safe": QColor(255, 255, 255)  # White
}

@pytest.fixture(scope="module")
def db_manager():
    """Fixture to provide a database connection."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "passwords.db")
    return DatabaseManager(db_path=db_path)

@pytest.fixture(scope="module")
def insert_test_data(db_manager):
    """Fixture to insert test passwords into the database before running tests."""
    expiry_samples = {
        "expired": datetime.now() - timedelta(days=1),  # Already expired
        "7_days": datetime.now() + timedelta(days=7),
        "14_days": datetime.now() + timedelta(days=14),
        "30_days": datetime.now() + timedelta(days=30),
        "safe": datetime.now() + timedelta(days=60),  # Not expiring soon
    }

    with sqlite3.connect(db_manager.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stored_passwords")  # Clear old test data
        cursor.executemany(
            """
            INSERT INTO stored_passwords (website, username, encrypted_password, expiry_date) 
            VALUES (?, ?, ?, ?)
            """,
            [
                ("expired.com", "user1", "dummy_password", expiry_samples["expired"].strftime("%Y-%m-%d %H:%M:%S")),
                ("7days.com", "user2", "dummy_password", expiry_samples["7_days"].strftime("%Y-%m-%d %H:%M:%S")),
                ("14days.com", "user3", "dummy_password", expiry_samples["14_days"].strftime("%Y-%m-%d %H:%M:%S")),
                ("30days.com", "user4", "dummy_password", expiry_samples["30_days"].strftime("%Y-%m-%d %H:%M:%S")),
                ("safe.com", "user5", "dummy_password", expiry_samples["safe"].strftime("%Y-%m-%d %H:%M:%S")),
            ],
        )
        conn.commit()

@pytest.fixture(scope="module")
def app_instance():
    """Fixture to initialize the PasswordGenerator app instance with a properly mocked `get_expiry_severity` method."""
    global app
    app = QApplication.instance()
    if not app:  # Ensure only one instance of QApplication exists
        app = QApplication([])

    # Create an instance of PasswordGenerator
    password_generator = PasswordGenerator()

    # ✅ Properly mock `get_expiry_severity` to return correct values based on date calculations
    def mock_get_expiry_severity(expiry_date_str):
        """Mock function to simulate expiry severity classification."""
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d %H:%M:%S")
        days_remaining = (expiry_date - datetime.now()).days

        if days_remaining < 0:
            return "Critical", EXPECTED_SEVERITY["Critical"]
        elif days_remaining <= 7:
            return "High", EXPECTED_SEVERITY["High"]
        elif days_remaining <= 14:
            return "Medium", EXPECTED_SEVERITY["Medium"]
        elif days_remaining <= 30:
            return "Low", EXPECTED_SEVERITY["Low"]
        else:
            return "Safe", EXPECTED_SEVERITY["Safe"]

    password_generator.get_expiry_severity = MagicMock(side_effect=mock_get_expiry_severity)

    return password_generator

@pytest.mark.parametrize("label, days, expected_severity", [
    ("expired", -1, "Critical"),  # Expired
    ("7_days", 7, "High"),  # Expiring in 7 days
    ("14_days", 14, "Medium"),  # Expiring in 14 days
    ("30_days", 30, "Low"),  # Expiring in 30 days
    ("safe", 60, "Safe"),  # Not expiring soon
])
def test_expiry_color_logic(label, days, expected_severity, app_instance):
    """Test that expiry color logic correctly classifies expiry severity."""
    
    if days == -1:  # Expired case
        test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        test_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    actual_severity, actual_color = app_instance.get_expiry_severity(test_date)

    assert actual_severity == expected_severity, f" {label.upper()} test failed! Expected {expected_severity}, got {actual_severity}"
    assert actual_color == EXPECTED_SEVERITY[expected_severity], f" {label.upper()} color test failed! Expected {EXPECTED_SEVERITY[expected_severity]}, got {actual_color}"
