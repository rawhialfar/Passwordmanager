import pytest
from PySide6.QtWidgets import QApplication
from datetime import datetime, timedelta
import sys
import os

# Add src path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from app import PasswordGenerator

@pytest.fixture(scope="module")
def app_instance():
    return QApplication.instance() or QApplication([])

@pytest.fixture
def password_generator(app_instance, mocker):
    """Create and return PasswordGenerator instance with mocked auth"""
    mocker.patch.object(PasswordGenerator, "authenticate_user", return_value=True)
    mocker.patch.object(PasswordGenerator, "auto_logout", return_value=None)
    generator = PasswordGenerator()
    return generator

@pytest.mark.parametrize(
    "password, expected_strength_label, expected_color, expected_active_bars",
    [
        ("1234", "Weak", "red", 2),
        ("Password123", "Weak", "red", 2),  # Changed from Medium to Weak
        ("Tr0ub4dor&", "Strong", "yellow", 6),
        ("P@ssw0rd!StrongOne", "Very Strong", "green", 8),
    ],
)

def test_password_strength_integration(password_generator, password, expected_strength_label, expected_color, expected_active_bars):
    """Test password strength logic and UI updates."""
    password_generator.ui.line_password.setText(password)
    password_generator.set_strength()

    # Check label or tooltip
    tooltip = password_generator.ui.strength_bars[0].toolTip()
    assert expected_strength_label in tooltip

    # Check active bars count with color
    active_bars = sum(expected_color in bar.styleSheet() for bar in password_generator.ui.strength_bars)
    assert active_bars == expected_active_bars
