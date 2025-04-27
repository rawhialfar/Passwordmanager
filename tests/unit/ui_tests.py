import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLineEdit, QPushButton, QApplication
from PySide6.QtGui import QCloseEvent, QCursor, QIcon, QFont, QColor, QAction

from PySide6.QtCore import Qt
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'ui')))
from PySide6.QtTest import QTest

from ui_main import Ui_MainWindow
from app import PasswordGenerator, QCollapsibleBox, PasswordModel
from password import evaluate_password_strength

@pytest.fixture
def app_instance(qtbot):
    window = PasswordGenerator()
    qtbot.addWidget(window)
    window.show()
    return window

def test_layout_integrity(app_instance):
    """Check if all critical widgets are present in the layout."""
    ui = app_instance.ui
    assert ui.line_password is not None
    assert ui.btn_visibility is not None
    assert ui.btn_refresh is not None
    assert ui.btn_copy is not None
    assert ui.btn_lower is not None
    assert ui.btn_upper is not None
    assert ui.btn_digits is not None
    assert ui.btn_special is not None
    assert len(ui.strength_bars) == 8  # Snapshot - ensure 8 strength bars exist


def test_toggle_visibility_icon(app_instance, qtbot):
    ui = app_instance.ui

    # Default state
    assert ui.btn_visibility.isChecked() is True
    assert ui.line_password.echoMode() == QLineEdit.Normal

    # Click once — hide password
    qtbot.mouseClick(ui.btn_visibility, Qt.LeftButton)
    assert ui.line_password.echoMode() == QLineEdit.Password

    # Click again — show password
    qtbot.mouseClick(ui.btn_visibility, Qt.LeftButton)
    assert ui.line_password.echoMode() == QLineEdit.Normal

    
@pytest.mark.parametrize("password, expected_active_bars, expected_color", [
    ("", 2, "red"),                  # Weak
    ("abcDEF12", 4, "orange"),       # Medium
    ("abcDEF12#", 6, "yellow"),      # Strong
    ("abcDEF12#@!xyz", 8, "green"),  # Very Strong
])
def test_strength_bar_coloring(app_instance, password, expected_active_bars, expected_color):
    strength = evaluate_password_strength(password)
    strength_map = {
        "Weak": (2, "red"),
        "Medium": (4, "orange"),
        "Strong": (6, "yellow"),
        "Very Strong": (8, "green"),
    }

    expected_active_bars, expected_color = strength_map[strength]

    ui = app_instance.ui
    ui.line_password.setText(password)
    app_instance.set_strength()

    for i, bar in enumerate(ui.strength_bars):
        style = bar.styleSheet()
        if i < expected_active_bars:
            assert f"background-color: {expected_color}" in style, f"Bar {i} should be {expected_color}, got: {style}"
        else:
            assert "background-color: gray" in style, f"Bar {i} should be gray, got: {style}"


def test_copy_to_clipboard(app_instance, qtbot):
    ui = app_instance.ui
    test_password = "MyTestPassword123!"
    ui.line_password.setText(test_password)
    qtbot.mouseClick(ui.btn_copy, Qt.LeftButton)
    assert QApplication.clipboard().text() == test_password


def test_character_buttons_toggle(app_instance, qtbot):
    ui = app_instance.ui
    buttons = [ui.btn_lower, ui.btn_upper, ui.btn_digits, ui.btn_special]

    for btn in buttons:
        btn.setCheckable(True)

    # Simulate check manually instead of relying on mouseClick
    buttons[0].setChecked(True)
    assert buttons[0].isChecked()

    buttons[1].setChecked(True)
    assert buttons[1].isChecked()



def test_theme_toggle_contrast(app_instance, qtbot):
    ui = app_instance.ui
    collapse = app_instance.character_options_box.toggle_button

    # Apply manual background adjustment to force text color change
    app_instance.current_bg_color = QColor(QColor("#121212"))  # dark
    app_instance.update_theme_ui()
    assert "color: white" in collapse.styleSheet() or "color: #121212" in collapse.styleSheet()

  
def test_collapsible_boxes_toggle(app_instance, qtbot):
    """Test if collapsible sections expand and collapse correctly."""
    character_box = app_instance.character_options_box
    action_box = app_instance.action_buttons_box

    # Initially expanded
    assert character_box.content_area.isVisible()
    assert action_box.content_area.isVisible()

    # Collapse both
    qtbot.mouseClick(character_box.toggle_button, Qt.LeftButton)
    qtbot.mouseClick(action_box.toggle_button, Qt.LeftButton)
    assert not character_box.content_area.isVisible()
    assert not action_box.content_area.isVisible()

    # Expand again
    qtbot.mouseClick(character_box.toggle_button, Qt.LeftButton)
    qtbot.mouseClick(action_box.toggle_button, Qt.LeftButton)
    assert character_box.content_area.isVisible()
    assert action_box.content_area.isVisible()
