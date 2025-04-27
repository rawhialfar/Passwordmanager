import os
import sys
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

# Add src directory to path
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from app import PasswordGenerator


@pytest.fixture(scope="module")
def app_instance():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def password_generator(app_instance):
    return PasswordGenerator()


def test_visibility_toggle_then_timeout(password_generator):
    """
    Full integration test:
    1. Toggle password visibility using UI interaction.
    2. Simulate inactivity.
    3. Trigger session timeout.
    """

    # Step 1: Toggle visibility
    line_edit = password_generator.findChild(QLineEdit, "line_password")
    toggle_button = password_generator.findChild(QPushButton, "btn_visibility")

    assert line_edit is not None, "Password input field not found"
    assert toggle_button is not None, "Visibility toggle button not found"

    # Initial state: password shown (Normal mode)
    assert line_edit.echoMode() == QLineEdit.Normal

    # Click toggle to hide it
    QTest.mouseClick(toggle_button, Qt.LeftButton)
    assert line_edit.echoMode() == QLineEdit.Password

    # Step 2: Simulate inactivity by advancing last activity time
    password_generator.last_activity_time = datetime.now() - timedelta(minutes=10)

    # Step 3: Check that session timeout triggers auto_logout
    with patch.object(password_generator, "auto_logout") as mock_logout:
        password_generator.check_session_timeout()
        mock_logout.assert_called_once()
