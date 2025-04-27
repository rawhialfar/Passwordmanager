import pytest
from PySide6.QtWidgets import QApplication
import sys
import os


# Add the src directory to sys.path so Python can find app.py
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from app import PasswordGenerator
from password import evaluate_password_strength


@pytest.fixture(scope="session", autouse=True)
def qapp():
   """Ensure QApplication exists before tests."""
   app = QApplication.instance()
   if app is None:
       app = QApplication([])
   return app


@pytest.fixture
def password_generator(mocker):
   """Fixture to initialize PasswordGenerator without authentication prompt."""
   mocker.patch.object(PasswordGenerator, "authenticate_user", return_value=True)  # Mock authentication
   mocker.patch.object(PasswordGenerator, "auto_logout", return_value=None)  # Mock auto logout


   if hasattr(PasswordGenerator, "check_session_timeout"):
       mocker.patch.object(PasswordGenerator, "check_session_timeout", return_value=None)  # Mock if exists


   generator = PasswordGenerator()
   return generator


@pytest.mark.parametrize(
   "password, expected_active_bars, expected_color",
   [
       ("gpufgyb", 2, "red"),  # Weak password (2 bars)
       ("UtdCMqD2", 4, "orange"),  # Medium password (4 bars)
       ("1Is>B_z~Ar", 6, "yellow"),  # Strong password (6 bars)
       ("<YuHB-155LCwlRVL", 8, "green"),  # Very Strong password (8 bars)
   ],
)
def test_strength_meter(password_generator, password, expected_active_bars, expected_color):
   """Tests if the strength meter updates correctly using QFrame bars."""
   password_generator.ui.line_password.setText(password)
   password_generator.set_strength()


   # Check active bars count
   active_bars = sum(
       expected_color in bar.styleSheet() for bar in password_generator.ui.strength_bars
   )
   assert active_bars == expected_active_bars, f"Expected {expected_active_bars} bars, but got {active_bars}"


   # Ensure only active bars have the expected color
   for i, bar in enumerate(password_generator.ui.strength_bars):
       style = bar.styleSheet()
       if i < expected_active_bars:
           assert f"background-color: {expected_color}" in style, f"Bar {i+1} should be {expected_color} but got {style}"
       else:
           assert "background-color: gray" in style, f"Inactive Bar {i+1} should be gray but got {style}"



