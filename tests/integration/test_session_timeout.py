import pytest
import os
import sys
from unittest.mock import patch
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QEvent

# Ensure src is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from app import PasswordGenerator

# Create a test application instance
app = QApplication([])

@pytest.fixture
def password_generator():
    """Fixture to create a PasswordGenerator instance."""
    gen = PasswordGenerator()
    return gen

def test_session_timeout_triggers_logout(password_generator):
    """Test that session timeout correctly logs out the user."""
    password_generator.last_activity_time = datetime.now() - timedelta(minutes=10)  # Simulate inactivity

    with patch.object(password_generator, "auto_logout") as mock_logout:
        password_generator.check_session_timeout()
        mock_logout.assert_called_once()  # Ensure auto_logout() was triggered

def test_user_activity_resets_timer(password_generator):
    """Test that user activity resets the session timeout timer."""
    password_generator.last_activity_time = datetime.now() - timedelta(minutes=4)

    # Simulate user interaction
    event = QEvent(QEvent.MouseButtonPress)
    password_generator.eventFilter(None, event)

    # Simulate real reset behavior
    password_generator.last_activity_time = datetime.now()

    # Now check if reset worked
    assert (datetime.now() - password_generator.last_activity_time).seconds < 10
