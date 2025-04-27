import pytest
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication
import sys
import os

# Add app path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from app import PasswordGenerator

# ---------------- Fixtures ------------------

@pytest.fixture(scope="module")
def app_instance():
    return QApplication.instance() or QApplication([])

@pytest.fixture
def generator_with_auth(app_instance, mocker):
    mocker.patch.object(PasswordGenerator, "authenticate_user", return_value=True)
    mocker.patch.object(PasswordGenerator, "auto_logout", return_value=None)
    return PasswordGenerator()

# ---------------- Test Case ------------------

def test_autolock_after_inactivity(generator_with_auth, mocker):
    """Auto-lock triggers after 5+ mins of inactivity."""
    generator_with_auth.last_activity_time = datetime.now() - timedelta(minutes=6)

    mock_logout = mocker.patch.object(generator_with_auth, "auto_logout")
    generator_with_auth.check_session_timeout()

    assert mock_logout.called
