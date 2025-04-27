import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit, QInputDialog, QMessageBox, 
                             QPushButton, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QComboBox, QAbstractItemView, QHeaderView, QWidget, QHBoxLayout, 
                             QScrollArea, QToolButton, QSizePolicy, QFileDialog, QFrame, QToolTip,
                             QLabel, QMenu) 
from PySide6.QtGui import QCloseEvent, QCursor, QIcon, QFont, QColor, QAction
from PySide6.QtCore import (Qt, QTimer, QEvent, Signal, Property, QObject, QParallelAnimationGroup, 
                          QPropertyAnimation, QAbstractAnimation)

import os
import csv
import re
from datetime import datetime, timedelta
from theme_manager import ThemeManager
from tooltip_manager import TooltipManager
from tooltip_content import TooltipContent
import sqlite3

import buttons
import password
from password import evaluate_password_strength
from ui.ui_main import Ui_MainWindow
from password_history import PasswordHistoryDialog
import ui.resources
from database import DatabaseManager
from auth import auth
from sessionDialog import SessionWarningDialog
COLOR_PRESETS = {
    "Green": "#013220",
    "Purple": "#301934",
    "Brown": "#aa5500",
    "Red": "#aa1717",
    "Light Blue": "#00b2b2"
}
# Custom collapsible box widget
class QCollapsibleBox(QWidget):
    def __init__(self, title="", parent=None):
        super(QCollapsibleBox, self).__init__(parent)
        # Get the color based on theme - set explicit color rather than "inherit"
        text_color = "white"  # Default for dark theme
        if parent and hasattr(parent, 'theme_manager'):
            if not parent.theme_manager.is_dark_mode:
                text_color = "#121212"  # Dark text for light theme

        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: white;
            }
            QToolButton:hover {
                background-color: rgba(128, 128, 128, 0.2);
            }
            QToolButton::menu-indicator { 
                color: {text_color};
                image: none; 
            }
        """)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)
        self.toggle_button.clicked.connect(lambda: self.setContentVisible(self.toggle_button.isChecked()))
       

        self.toggle_animation = QParallelAnimationGroup(self)

        self.content_area = QScrollArea()
        # Ensure it's completely hidden initially
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        # Hide scrollbars to prevent them from showing up
        self.content_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_area.setFrameShape(QFrame.NoFrame)
        self.content_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
                border-radius: 5px;
                padding: 0px;
                margin: 0px;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self.content_area, b"maximumHeight"))
        
    def setContentVisible(self, visible: bool):
        if self.content_area:
            self.content_area.setVisible(visible)
            if visible:
                self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            else:
                self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.updateGeometry()  # Triggers layout recalculation
            
    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(Qt.DownArrow if not checked else Qt.RightArrow)
        
        # Important: set direction first, then start animation
        self.toggle_animation.setDirection(
            QAbstractAnimation.Forward if not checked else QAbstractAnimation.Backward
        )
        
        # When closing, immediately set to 0 height to avoid the peek issue
        if checked:  # If collapsing
            self.content_area.setMaximumHeight(0)
            self.content_area.setMinimumHeight(0)
        
        self.toggle_animation.start()

    def update_collapsible_box_theme(self, box, theme):
        # Update collapsible box styling based on theme
        if theme == "dark":
            box.toggle_button.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                    color: white;  /* Explicit white text for dark theme */
                }
                QToolButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QToolButton::menu-indicator { 
                    image: none; 
                }
            """)
        else:
            box.toggle_button.setStyleSheet("""
                QToolButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                    color: #121212;  /* Explicit dark text for light theme */
                }
                QToolButton:hover {
                    background-color: rgba(0, 0, 0, 0.1);
                }
                QToolButton::menu-indicator { 
                    image: none; 
                }
            """)

    def setContentLayout(self, layout):
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        
        # Calculate sizes properly
        collapsed_height = self.sizeHint().height() - self.content_area.maximumHeight()
        content_height = layout.sizeHint().height()
        
        # Ensure collapsed state is correct
        self.content_area.setMinimumHeight(0)
        self.content_area.setMaximumHeight(0)
        
        # Adjust animations
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(300)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)
        
        content_animation = self.toggle_animation.animationAt(self.toggle_animation.animationCount() - 1)
        content_animation.setDuration(300)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)

# Simple data binding class - minimal implementation
class PasswordModel(QObject):
    passwordChanged = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._password = ""
    
    def get_password(self):
        return self._password
    
    def set_password(self, value):
        if self._password != value:
            self._password = value
            self.passwordChanged.emit(value)

class PasswordGenerator(QMainWindow):
    def __init__(self):
        super(PasswordGenerator, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_theme_toggle.clicked.connect(self.toggle_theme)
        self.setup_theme_manager()
        #self.setup_color_picker()
        self.setup_accent_color_button()

        # Set Roboto font for the entire application
        self.setStyleSheet("""
            * {
                font-family: 'Roboto';
                font-size: 12.5pt;
            }
            QLineEdit {
                font-family: 'Roboto';
                color: white;
                border: none;
                padding: 12.5px;
            }
            QPushButton {
                font-family: 'Roboto';
                padding: 12.5px;
            }
            QLabel {
                font-family: 'Roboto';
                padding: 12.5px;
            }
            QComboBox {
                font-family: 'Roboto';
                padding: 12.5px;
            }
            QSpinBox {
                font-family: 'Roboto';
                padding: 12.5px;
            }
        """)            
        self.setup_theme_manager()
        # Sidebar navigation signals
        self.master_password_verified = False
        self.ui.btn_sidebar_generator.clicked.connect(lambda: [self.highlight_sidebar_button(self.ui.btn_sidebar_generator), self.show_generator_view()])
        self.ui.btn_sidebar_history.clicked.connect(lambda: [self.highlight_sidebar_button(self.ui.btn_sidebar_history), self.show_password_history()])
        self.ui.btn_sidebar_expiry.clicked.connect(lambda: [self.highlight_sidebar_button(self.ui.btn_sidebar_expiry), self.show_expiring_passwords()])
        self.ui.btn_sidebar_export.clicked.connect(lambda: [self.highlight_sidebar_button(self.ui.btn_sidebar_export), self.export_passwords()])
       
        self.ui.btn_sidebar_history.clicked.connect(self.show_password_history)
        self.ui.btn_sidebar_expiry.clicked.connect(self.show_expiring_passwords)
        self.ui.btn_sidebar_export.clicked.connect(self.export_passwords)

        

        # Initialize the data model - minimal binding
        self.model = PasswordModel()
        self.model.passwordChanged.connect(self.update_password_display)
        
        self.ui.btn_export.clicked.connect(self.export_passwords)
        self.ui.btn_expiry_check.clicked.connect(self.show_expiring_passwords)
        
        self.visibility_timer = QTimer(self)  # Create timer
        self.visibility_timer.setInterval(3000)  # Hide password after 3 seconds
        self.visibility_timer.timeout.connect(self.auto_hide_password)  # Connect event

        # Initialize database and authentication manager
        self.db = DatabaseManager()
        self.auth = auth()
        
        # Initialize tooltip system with saved preference
        tooltip_enabled = self.db.get_tooltip_preference()
        self.tooltip_manager = TooltipManager(enabled=tooltip_enabled)
        
        # Connect visibility toggle button
        self.ui.btn_visibility.clicked.connect(self.change_password_visibility)

        # Timer for auto-hiding password after inactivity
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setInterval(10000)  # Hide password after 10 seconds
        self.auto_hide_timer.timeout.connect(self.auto_hide_password)

        # Install event filter for detecting mouse hover events
        self.ui.line_password.installEventFilter(self)
        
        # Install event filter for hover reveal
        self.ui.line_password.installEventFilter(self)

        # Track manual visibility toggle
        self.manual_visibility = False  

        # Session timeout logic
        self.last_activity_time = datetime.now()
        self.session_timeout = timedelta(minutes=5)  
        self.warning_time = timedelta(seconds=30)  
        self.timer = QTimer(self)  
        self.timer.timeout.connect(self.check_session_timeout)
        self.timer.start(1000)  

        self.warning_timer = QTimer(self)  

        # Install event filter to track user activity
        self.installEventFilter(self)

        # Force authentication on app startup (loop until correct)
        while not self.authenticate_user():
            retry = QMessageBox.question(self, "Access Denied", "Incorrect master password! Try again?", 
                                         QMessageBox.Retry | QMessageBox.Close, QMessageBox.Retry)
            if retry == QMessageBox.Close:
                sys.exit(0)  # Exit if the user chooses to close

        self.connect_slider_to_spinbox()
        self.set_password()
        self.do_when_password_edit()

        # Look for these lines:
        for btn in buttons.GENERATE_PASSWORD:
            getattr(self.ui, btn).clicked.connect(self.set_password)

        # Connect UI buttons to methods
        self.ui.btn_visibility.clicked.connect(self.change_password_visibility)
        self.ui.btn_copy.clicked.connect(self.copy_to_clipboard)
        self.ui.forgotPasswordButton.clicked.connect(self.handle_reset_password)
        self.ui.btn_save.clicked.connect(self.save_password)
        self.load_categories()

        # Initialize tooltip manager with enabled state
        self.tooltip_manager = TooltipManager(enabled=True)
        
        # Modify the UI to use collapsible sections
        self.setup_collapsible_sections()
        self.setup_tooltip_toggle()

        # Apply Tooltips
        if self.tooltip_manager.enabled:
            self.apply_tooltips()

        # Set minimum window size
        self.setMinimumSize(860, 759)
        
        # Set size policy for main window
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Enable window to resize automatically
        self.adjustSize()

        # Make the wrapper frame transparent
        self.ui.wrapper_frame.setStyleSheet("background-color: transparent; border: none;")
        
    def toggle_theme(self):
        """Toggle between dark and light mode themes."""
        if self.theme_manager.is_dark_mode:
            self.set_light_mode()
        else:
            self.set_dark_mode()

    def set_dark_mode(self):
        self.theme_manager.is_dark_mode = True
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
            }
        """)
        self.ui.tooltip_toggle.setStyleSheet(self.get_tooltip_toggle_style())

    def set_light_mode(self):
        self.theme_manager.is_dark_mode = False
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                color: #121212;
            }
        """)
        self.ui.tooltip_toggle.setStyleSheet(self.get_tooltip_toggle_style())

    def get_tooltip_toggle_style(self):
        """Update tooltip toggle style based on theme."""
        if self.theme_manager.is_dark_mode:
            return """
                QPushButton {
                    min-width: 80px;
                    min-height: 30px;
                    border: 2px solid #555;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 10pt;
                    background-color: #2ea043;
                    color: white;
                }
                QPushButton:!checked {
                    background-color: #555;
                    color: #cccccc;
                }
            """
        else:
            return """
                QPushButton {
                    min-width: 80px;
                    min-height: 30px;
                    border: 2px solid #999;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 10pt;
                    background-color: #dddddd;
                    color: black;
                }
                QPushButton:!checked {
                    background-color: #eee;
                    color: #222;
                }
            """

    def resizeEvent(self, event):
        """Handle window resize events to ensure proper layout"""
        super().resizeEvent(event)
        width = self.width()
        height = self.height()
        # print(f"Width: {width}, Height: {height}")
        
        self.ui.verticalLayout.invalidate()
        self.ui.verticalLayout.update()
        # Ensure collapsible boxes adjust properly
        if hasattr(self, 'character_options_box'):
            content_layout = self.character_options_box.content_area.layout()
            if content_layout:
                self.character_options_box.content_area.setMinimumHeight(content_layout.sizeHint().height())
        
        if hasattr(self, 'action_buttons_box'):
            content_layout = self.action_buttons_box.content_area.layout()
            if content_layout:
                self.action_buttons_box.content_area.setMinimumHeight(content_layout.sizeHint().height())     

        
    def setup_collapsible_sections(self):
        """Set up collapsible sections for character options and action buttons, with compact and unified styling."""
        
        # --- Character Options Collapsible
        self.character_options_box = QCollapsibleBox(" Character Options")
        self.character_options_box.setStyleSheet("background-color: transparent; ")  # Let wrapper handle visuals

        # Create a NEW layout for the character options content
        character_content_layout = QVBoxLayout()
        character_content_layout.setContentsMargins(0, 10, 0, 15)
        character_content_layout.setSpacing(5)

        char_buttons_layout = QHBoxLayout()
        char_buttons_layout.setSpacing(5)
        char_buttons_layout.setContentsMargins(0, 0, 0, 0)

        for btn in [self.ui.btn_lower, self.ui.btn_upper, self.ui.btn_digits, self.ui.btn_special]:
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 13px 10px;
                    font-size: 12pt;
                    border-radius: 6px;
                    color: white;
                    background-color: #2a2a2a;
                    border: 2px solid #444;
                }
                QPushButton:checked {
                    background-color: #00c853;
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
            """)
            char_buttons_layout.addWidget(btn)

        character_content_layout.addLayout(char_buttons_layout)
        self.character_options_box.setContentLayout(character_content_layout)

        # --- Actions Collapsible
        self.action_buttons_box = QCollapsibleBox(" Actions")
        self.action_buttons_box.setStyleSheet("background-color: transparent;")  # Let wrapper handle visuals

        buttons_content_layout = QVBoxLayout()
        buttons_content_layout.setContentsMargins(0, 10, 0, 10)  # Top: 5, Bottom: 10
        buttons_content_layout.setSpacing(5)

        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(5)
        action_buttons_layout.setContentsMargins(0, 0, 0, 0)

        for btn in [self.ui.btn_save, self.ui.forgotPasswordButton]:
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 12px 15px;
                    font-size: 12pt;
                    border-radius: 6px;
                    color: white;
                    background-color: #2a2a2a;
                    border: 2px solid #444;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
                QPushButton:pressed {
                    background-color: #404040;
                }
            """)
            action_buttons_layout.addWidget(btn, stretch=1)  # Fills the space
            

        buttons_content_layout.addLayout(action_buttons_layout)
        self.action_buttons_box.setContentLayout(buttons_content_layout)

        self.ui.wrapper_layout.addWidget(self.character_options_box)
        self.ui.wrapper_layout.addWidget(self.action_buttons_box)

        index = self.ui.verticalLayout.indexOf(self.ui.layout_length)
        if index >= 0:
            self.ui.verticalLayout.insertWidget(index + 1, self.ui.wrapper_frame)
        else:
            self.ui.verticalLayout.addWidget(self.ui.wrapper_frame)

        # Expand both by default
        self.character_options_box.toggle_button.click()
        self.action_buttons_box.toggle_button.click()
        QTimer.singleShot(0, self.character_options_box.updateGeometry)
        QTimer.singleShot(0, self.action_buttons_box.updateGeometry)
        self.ui.verticalLayout.invalidate()
        self.ui.verticalLayout.update()

        # Make the boxes expand horizontally
        self.character_options_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.action_buttons_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)


    def setup_tooltip_toggle(self):
        """Create toggle button for tooltips in UI"""
        
        # Create tooltip settings frame
        self.tooltip_frame = QFrame(self)
        self.tooltip_frame.setObjectName("tooltip_frame")
        self.tooltip_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 5px;
                margin-bottom: 5px;
            }
        """)
        
        # Create layout for tooltip settings
        tooltip_layout = QHBoxLayout(self.tooltip_frame)
        tooltip_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create label
        self.tooltip_label = QLabel("Beginner Tooltips:", self.tooltip_frame)
        text_color = "white" if self.theme_manager.is_dark_mode else "#121212"
        self.tooltip_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                color: {text_color};
            }
        """)
        self.tooltip_label = self.tooltip_label
        # Create toggle button with improved styling and text indicators
        self.tooltip_toggle = QPushButton("ON", self.tooltip_frame)  # Default text "ON"
        self.tooltip_toggle.setCheckable(True)
        self.tooltip_toggle.setChecked(True)  # Default to enabled
        self.tooltip_toggle.setStyleSheet("""
            QPushButton {
                min-width: 80px;
                min-height: 30px;
                border: 2px solid #555;
                border-radius: 15px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:checked {
                background-color: #2ea043;
                color: white;
                text-align: center;
            }
            QPushButton:!checked {
                background-color: #555;
                color: #cccccc;
                text-align: center;
            }
        """)
        
        # Connect toggle button to tooltip enable/disable
        self.tooltip_toggle.clicked.connect(self.toggle_tooltips)
        
        # Add widgets to layout
        tooltip_layout.addWidget(self.tooltip_label)
        tooltip_layout.addWidget(self.tooltip_toggle)
        self.ui.forgotPasswordButton.setToolTip("Reset your master password if forgotten")
        # Add to main layout at the appropriate position
        category_index = self.ui.verticalLayout.indexOf(self.ui.category_frame)
        if (category_index >= 0):
            self.ui.verticalLayout.insertWidget(category_index + 1, self.tooltip_frame)
        else:
            self.ui.verticalLayout.addWidget(self.tooltip_frame)

        # Set size policy for tooltip frame
        self.tooltip_frame.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )
        
        # Adjust layout constraints
        tooltip_layout.setSpacing(10)
        tooltip_layout.setContentsMargins(10, 5, 10, 5)

    def show_generator_view(self):
        """Switch to the password generator view."""
        QMessageBox.information(self, "View Switched", "Showing Password Generator View")

    def highlight_sidebar_button(self, clicked_button):
        for btn in [
            self.ui.btn_sidebar_generator,
            self.ui.btn_sidebar_history,
            self.ui.btn_sidebar_expiry,
            self.ui.btn_sidebar_export
        ]:
            btn.setChecked(btn == clicked_button)

    # Simple update function for data binding
    def update_password_display(self, password_text):
        self.ui.line_password.setText(password_text)


    def change_password_visibility(self):
        """Toggle password visibility with intuitive icons."""
        if self.ui.btn_visibility.isChecked():
            self.ui.line_password.setEchoMode(QLineEdit.Normal)  # Show password
            self.ui.btn_visibility.setIcon(QIcon(":/icons/icons/visible.svg"))  # Update icon
            self.auto_hide_timer.start()  # Start auto-hide timer
        else:
            self.ui.line_password.setEchoMode(QLineEdit.Password)  # Hide password
            self.ui.btn_visibility.setIcon(QIcon(":/icons/icons/invisible.svg"))  # Update icon
            self.auto_hide_timer.stop()  # Stop timer

    def auto_hide_password(self):
        """Automatically hide the password after inactivity."""
        self.ui.line_password.setEchoMode(QLineEdit.Password)  # Hide password
        self.ui.btn_visibility.setChecked(False)  # Reset button state
        self.ui.btn_visibility.setIcon(QIcon(":/icons/icons/invisible.svg"))  # Update icon
        self.auto_hide_timer.stop()  # Stop the timer

    def eventFilter(self, obj, event):
        """Handles password field hover, auto-hide, and user interactions."""
        # Handle theme-related events
        if event.type() == QEvent.PaletteChange and obj is self:
            # Theme might have changed, ensure all widgets are updated
            QTimer.singleShot(10, self.refresh_all_widgets)

        """Detect when the mouse hovers over the password field to temporarily reveal the password."""
        if obj == self.ui.line_password:
            if event.type() == QEvent.Enter:  # Mouse enters the password field
                if not self.manual_visibility:  # Only reveal if the user hasn't manually toggled visibility
                    self.ui.line_password.setEchoMode(QLineEdit.Normal)
                    # Auto-hide after 3 seconds unless user manually toggles
                    self.visibility_timer.start(3000)  # Hide password after 3 seconds

            elif event.type() == QEvent.Leave:  # Mouse leaves the field
                if not self.manual_visibility:  # Only hide if manually toggled off
                    self.ui.line_password.setEchoMode(QLineEdit.Password)
                    self.ui.btn_visibility.setIcon(QIcon(":/icons/icons/invisible.svg"))
                    self.visibility_timer.stop()  # Stop the timer if mouse leaves early

            elif event.type() in (QEvent.KeyPress, QEvent.MouseButtonPress):  # Any user interaction
                self.visibility_timer.start(5000)  # Restart auto-hide timer (5 sec)


        return super().eventFilter(obj, event)

    def calculate_expiry_date() -> str:
        """Calculate expiry date (90 days from now)"""
        expiry_date = datetime.now() + timedelta(days=90)
        return expiry_date.strftime('%Y-%m-%d %H:%M:%S')
    
    def dismiss_expiry_alert(self, password_id, row):
        """Dismiss an expiring password, remove it from UI, and show a message if all alerts are dismissed."""

        # Mark for dismissal in session and database
        self.dismissed_passwords.add(password_id)

        # Ensure it is recorded in the database
        try:
            self.db.dismiss_expiry_alert(password_id)  # Persist dismissal in DB
        except Exception as e:
            print(f"Error dismissing password in DB: {e}")

        # Ensure expiry_table is initialized before using it
        if self.expiry_table is None:
            print("Warning: expiry_table is not initialized. Skipping UI updates.")
            return

        # Remove the clicked row from UI
        self.expiry_table.removeRow(row)
        QApplication.processEvents()  # Ensure UI updates instantly

        # Ensure all dismissed passwords are removed properly
        if self.expiry_table.rowCount() == 0:
            if self.expiry_dialog is not None:  # Fix: Check if expiry_dialog is set before closing
                self.expiry_dialog.close()
            else:
                print("Warning: expiry_dialog is not initialized. Skipping dialog close.")

    def show_filtered_expiring_passwords(self):
        """Open the expiring passwords window with filters instead of showing all stored passwords."""
        
        expiring_passwords = self.db.get_active_expiring_passwords()
        
        # If nothing remains, notify user & still open filtered passwords window
        if not expiring_passwords:
            QMessageBox.information(self, "No Expiring Passwords", "No passwords are expiring soon.")

        # Open expiring passwords window (with filters)
        self.show_expiring_passwords()
    
    def eventFilter(self, obj, event):
        """Handles password field hover, auto-hide, and user interactions."""
        if obj == self.ui.line_password:
            if event.type() == QEvent.Enter:  # Mouse enters the password field
                if not self.manual_visibility:  # Only reveal if the user hasn't manually toggled visibility
                    self.ui.line_password.setEchoMode(QLineEdit.Normal)

                    # Auto-hide after 3 seconds unless user manually toggles
                    self.visibility_timer.start(3000)  # Hide password after 3 seconds

            elif event.type() == QEvent.Leave:  # Mouse leaves the field
                if not self.manual_visibility:  # Only hide if manually toggled off
                    self.ui.line_password.setEchoMode(QLineEdit.Password)
                    self.ui.btn_visibility.setIcon(QIcon(":/icons/icons/invisible.svg"))
                    self.visibility_timer.stop()  # Stop the timer if mouse leaves early

            elif event.type() in (QEvent.KeyPress, QEvent.MouseButtonPress):  # Any user interaction
                self.visibility_timer.start(5000)  # Restart auto-hide timer (5 sec)

        return super().eventFilter(obj, event)


    def reset_timers(self):
        """Reset the session timeout and warning timers."""
        self.timer.stop()
        self.warning_timer.stop()
        self.timer.start(1000)  

    def check_session_timeout(self):
        """Check if the session has expired or is about to expire."""
        inactive_duration = datetime.now() - self.last_activity_time
        
        if inactive_duration >= self.session_timeout:
            self.auto_logout()
        
        elif inactive_duration >= (self.session_timeout - self.warning_time):
            if not self.warning_timer.isActive():  # Ensure warning popup only triggers once
                self.show_warning_popup()

    def show_warning_popup(self):
        """Show a warning popup before logging out."""
        self.timer.stop()  # Stop the warning timer
        remaining_time = (self.session_timeout - (datetime.now() - self.last_activity_time)).total_seconds()
        # print(f"Remaining time: {remaining_time} seconds")
        # Create and show the custom dialog
        dialog = SessionWarningDialog(remaining_time, self)
        result = dialog.exec()

        if result == QDialog.Accepted:
            # User clicked "Extend Session"
            self.last_activity_time = datetime.now()  
            self.reset_timers()  
        else:
            self.auto_logout()  # Log out immediately

    def auto_logout(self):
        """Log out the user due to inactivity."""
        self.timer.stop()
        self.warning_timer.stop()
        QMessageBox.information(self, "Session Expired", "You have been logged out due to inactivity.")
        self.close()  
        self.authenticate_user()  

    def closeEvent(self, event: QCloseEvent) -> None:
        self.timer.stop()
        self.warning_timer.stop()
        QApplication.clipboard().clear()
        event.accept()
    
    def show_expiring_passwords(self):
        """Prompt for master password, retrieve expiring passwords, and display them in a dialog with a Dismiss All button."""
        # Request master password from the user
        password, ok = QInputDialog.getText(self, "Authentication", "Enter Master Password:", QLineEdit.Password)
        if not ok or not self.db.verify_master_password(password):
            QMessageBox.warning(self, "Access Denied", "Incorrect master password.")
            return

        # Fetch active expiring passwords from the database
        expiring_passwords = self.db.get_active_expiring_passwords()

        # Handle case where no expiring passwords are found
        if not expiring_passwords:
            QMessageBox.information(self, "No Expiring Passwords", "No passwords are expiring soon.")
            self.show_filtered_expiring_passwords_window()
            return

        # Ensure dismissed_passwords is always initialized
        if not hasattr(self, 'dismissed_passwords'):
            self.dismissed_passwords = set()

        # Create a dialog to display expiring passwords
        self.expiry_dialog = QDialog(self)
        self.expiry_dialog.setWindowTitle("Expiring Passwords")
        self.expiry_dialog.setGeometry(250, 150, 700, 310)
        layout = QVBoxLayout()

        # Set up the table widget to display password details
        self.expiry_table = QTableWidget()
        self.expiry_table.setColumnCount(3)
        self.expiry_table.setHorizontalHeaderLabels(["Website", "Username", "Expiry Date"])
        self.expiry_table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                padding: 20px;
                gridline-color: #DDD;
                border: none;
            }
            QHeaderView::section {
                color: white;
                font-weight: bold;
                padding: 5px;
                text-align: center;
            }
        """)
        header = self.expiry_table.horizontalHeader()
        header.setFixedHeight(100)
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.expiry_table.verticalHeader().setDefaultSectionSize(40)
        self.expiry_table.verticalHeader().setVisible(False)

        # Populate the table with expiring password data
        self.expiry_table.setRowCount(len(expiring_passwords))
        for i, (password_id, website, username, expiry_date) in enumerate(expiring_passwords):
            self.expiry_table.setItem(i, 0, QTableWidgetItem(website))
            self.expiry_table.setItem(i, 1, QTableWidgetItem(username))
            self.expiry_table.setItem(i, 2, QTableWidgetItem(expiry_date))

        layout.addWidget(self.expiry_table)

        # Create and configure the Dismiss All button
        dismiss_all_button = QPushButton("Dismiss All")
        dismiss_all_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 7px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        dismiss_all_button.clicked.connect(lambda: self.dismiss_all_expiring_passwords(expiring_passwords))
        layout.addWidget(dismiss_all_button)

        self.expiry_dialog.setLayout(layout)
        self.expiry_dialog.exec()

    def dismiss_all_expiring_passwords(self, expiring_passwords):
        """Dismiss all expiring passwords, clear the table, close the dialog, and open the expiring passwords window."""
        for password_id, _, _, _ in expiring_passwords:
            self.dismissed_passwords.add(password_id)
            self.db.dismiss_expiry_alert(password_id)
        self.expiry_table.setRowCount(0)
        self.expiry_dialog.close()
        self.show_filtered_expiring_passwords_window()

    def show_expiry_alerts_window(self, expiring_passwords):
        """Create the expiry alerts dismissal window, allowing users to dismiss passwords."""

        self.expiry_dialog = QDialog(self)
        self.expiry_dialog.setWindowTitle("Expiring Passwords")
        self.expiry_dialog.setGeometry(250, 150, 700, 310)
        layout = QVBoxLayout()

        # Create Table Widget
        self.expiry_table = QTableWidget()
        self.expiry_table.setColumnCount(4)
        self.expiry_table.setHorizontalHeaderLabels(["Website", "Username", "Expiry Date", "Dismiss"])
        self.expiry_table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                padding: 20px;
                gridline-color: #DDD;
                border: none;
            }
            QHeaderView::section {
                color: white;
                font-weight: bold;
                padding: 5px;
                text-align: center;
            }
        """)

        # Adjust Header & Row Sizes
        header = self.expiry_table.horizontalHeader()
        header.setFixedHeight(100)  # Header height
        header.setSectionResizeMode(QHeaderView.Stretch)  # Expand headers
        self.expiry_table.verticalHeader().setDefaultSectionSize(40)  # Increase row height
        self.expiry_table.verticalHeader().setVisible(False)  # Hide row numbers

        # Store dismissed passwords in session
        self.dismissed_passwords = set()

        # Populate Table
        self.expiry_table.setRowCount(len(expiring_passwords))
        for i, (password_id, website, username, expiry_date) in enumerate(expiring_passwords):
            self.expiry_table.setItem(i, 0, QTableWidgetItem(website))
            self.expiry_table.setItem(i, 1, QTableWidgetItem(username))
            self.expiry_table.setItem(i, 2, QTableWidgetItem(expiry_date))

            # Dismiss Button
            dismiss_button = QPushButton("Dismiss")
            dismiss_button.setStyleSheet("""
                QPushButton {
                    background-color: #d9534f;  /* Red color */
                    color: white;
                    border-radius: 4px;
                    padding: 3px 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c9302c;
                }
            """)
            dismiss_button.clicked.connect(lambda _, pid=password_id, row=i: self.dismiss_expiry_alert(pid, row))
            self.expiry_table.setCellWidget(i, 3, dismiss_button)

        layout.addWidget(self.expiry_table)
        self.expiry_dialog.setLayout(layout)

        # Ensure the window closes before opening the next one
        self.expiry_dialog.exec()

        # If all passwords are dismissed, still open the expiring passwords window
        self.show_filtered_expiring_passwords_window()

    def show_filtered_expiring_passwords_window(self):
        """Open the correct expiring passwords window (with filters) after dismissing alerts."""

        # Retrieve all stored passwords
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT website, username, expiry_date FROM stored_passwords")
            rows = cursor.fetchall()

        # Create a UI Table Window
        self.passwords_window = QDialog(self)
        self.passwords_window.setWindowTitle("Stored Passwords")
        self.passwords_window.setGeometry(300, 200, 650, 400)
        layout = QVBoxLayout()

        # Create Table Widget
        self.password_table = QTableWidget()
        self.password_table.setColumnCount(3)  # Ensure three columns
        self.password_table.setHorizontalHeaderLabels(["Website", "Username", "Expiry Date"])
        self.password_table.setRowCount(len(rows))

        # Fix header text alignment and size
        header = self.password_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Make headers expand with window
        header.setFixedHeight(65)

        # Apply dividers between headers and center text
        header.setStyleSheet("""
            QHeaderView::section {
                color: white;
                font-weight: bold;
                padding: 5px;
                text-align: center;
            }
        """)

        # Adjust column widths for readability
        self.password_table.setColumnWidth(0, 200)  # Website column
        self.password_table.setColumnWidth(1, 180)  # Username column
        self.password_table.setColumnWidth(2, 200)  # Expiry date column

        # Ensure row heights are spaced properly
        self.password_table.verticalHeader().setDefaultSectionSize(30)
        self.password_table.verticalHeader().setVisible(False)  # Hide row numbers

        # Add rows
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.password_table.setItem(i, j, QTableWidgetItem(str(value)))

        layout.addWidget(self.password_table)

        # Add a Filter Dropdown Menu
        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems([
            "Show All",
            "Expired Passwords",
            "Expiring in 7 Days",
            "Expiring in 14 Days",
            "Expiring in 30 Days",
            "Expiring in 60 Days",
            "Expiring in 90 Days"
        ])
        self.filter_dropdown.currentIndexChanged.connect(self.update_password_table)
        layout.addWidget(self.filter_dropdown)

        # Refresh Button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.update_password_table)
        layout.addWidget(self.refresh_button)

        self.passwords_window.setLayout(layout)
        self.passwords_window.show()

        # Store rows globally for filtering
        self.all_passwords = rows
        
    def mark_for_dismissal(self, row, password_id):
        """Mark a password for dismissal and instantly remove it from the table."""
        self.dismissed_passwords.add(password_id)
        self.db.dismiss_expiry_alert(password_id)  # Save in database
        self.expiry_table.removeRow(row)  # Remove row from table immediately

        # If all passwords are dismissed, clear the table & show message
        if self.expiry_table.rowCount() == 0:
            QMessageBox.information(self, "No Remaining Alerts", "No passwords are expiring soon.")

    def finalize_dismissals(self):
        """Finalizes dismissals and ensures the expiring passwords window still opens."""

        # Remove dismissed passwords from the table
        remaining_rows = []
        for row in range(self.expiry_table.rowCount()):
            password_id = self.expiry_table.item(row, 0).data(Qt.UserRole)  # Get stored password ID
            if password_id not in self.dismissed_passwords:
                remaining_rows.append([
                    self.expiry_table.self.expiry_table.item(row, 0).text(),
                    self.expiry_table.item(row, 1).text(),
                    self.expiry_table.item(row, 2).text(),
                ])

        # Update the table to only show remaining passwords
        self.expiry_table.setRowCount(len(remaining_rows))
        for i, row_data in enumerate(remaining_rows):
            for j, value in enumerate(row_data):
                self.expiry_table.setItem(i, j, QTableWidgetItem(value))

        # If no passwords remain, show "No passwords expiring soon."
        if len(remaining_rows) == 0:
            QMessageBox.information(self, "No Expiring Passwords", "No passwords are expiring soon.")

        # Close dismissal window
        self.expiry_dialog.close()

        # **Ensure expiring passwords window still opens**
        self.show_expiring_passwords()

    def update_password_table(self):
        """Filters passwords based on selected expiry timeframe."""
        filter_option = self.filter_dropdown.currentText()

        # Build SQL query based on the selected filter
        query = "SELECT website, username, expiry_date FROM stored_passwords"
        params = ()

        if filter_option == "Expired Passwords":
            query += " WHERE expiry_date < datetime('now')"
        elif filter_option == "Expiring in 7 Days":
            query += " WHERE expiry_date BETWEEN datetime('now') AND datetime('now', '+7 days')"
        elif filter_option == "Expiring in 14 Days":
            query += " WHERE expiry_date BETWEEN datetime('now') AND datetime('now', '+14 days')"
        elif filter_option == "Expiring in 30 Days":
            query += " WHERE expiry_date BETWEEN datetime('now') AND datetime('now', '+30 days')"
        elif filter_option == "Expiring in 60 Days":
            query += " WHERE expiry_date BETWEEN datetime('now') AND datetime('now', '+60 days')"
        elif filter_option == "Expiring in 90 Days":
            query += " WHERE expiry_date BETWEEN datetime('now') AND datetime('now', '+90 days')"

        # Fetch filtered data
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params if params else ())
            filtered_rows = cursor.fetchall()

        # Update table content
        self.password_table.setRowCount(len(filtered_rows))
        for i, row in enumerate(filtered_rows):
            for j, value in enumerate(row):
                self.password_table.setItem(i, j, QTableWidgetItem(str(value)))

        
    # Handle authentication on button press
    def handle_authentication(self):
        if self.authenticate_user():
            QMessageBox.information(self, "Success", "Authentication successful!")

    def connect_slider_to_spinbox(self) -> None:
        self.ui.slider_length.valueChanged.connect(self.ui.spinbox_length.setValue)
        self.ui.spinbox_length.valueChanged.connect(self.ui.slider_length.setValue)
        self.ui.spinbox_length.valueChanged.connect(self.set_password)

    def do_when_password_edit(self) -> None:
        self.ui.line_password.textEdited.connect(self.set_entropy)
        self.ui.line_password.textEdited.connect(self.set_strength)
        self.ui.line_password.textEdited.connect(lambda text: self.model.set_password(text))

    # Retrieve selected character types
    def get_characters(self) -> str:
        chars = ''
        for btn in buttons.Characters:
            if getattr(self.ui, btn.name).isChecked():  # Only include characters for checked buttons
                chars += btn.value
        return chars

    def get_character_number(self) -> int:
        chars = set()
        for btn in buttons.Characters:
            if getattr(self.ui, btn.name).isChecked():
                chars.update(btn.value)
        return len(chars) if chars else 1

    def set_password(self) -> None:
        try:
            password_text = password.create_new(
                length=self.ui.slider_length.value(),
                characters=self.get_characters()
            )
            
            # Use the model instead of directly setting the text
            self.model.set_password(password_text)

            # Save generated password to history
            self.db.save_password_to_history(password_text)

        except IndexError:
            self.ui.line_password.clear()
        self.set_entropy()
        self.set_strength()
        
    def is_strong_password(self, password: str) -> bool:
        """Enforce stricter password complexity"""
        
        # Check for uppercase, lowercase, digits, and special characters
        if not re.search(r'[A-Z]', password):  # Must contain at least one uppercase letter
            return False
        if not re.search(r'[a-z]', password):  # Must contain at least one lowercase letter
            return False
        if not re.search(r'[0-9]', password):  # Must contain at least one number
            return False
        if not re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?`~\\|]', password):
            return False
        
        # Check for common passwords (example list)
        common_passwords = ['password123', '123456', 'qwerty', 'letmein']
        if password.lower() in common_passwords:
            return False
        
        return True
        
    def set_entropy(self) -> None:
        length = len(self.ui.line_password.text())
        char_num = self.get_character_number()
        self.ui.label_entropy.setText(f'Entropy: {password.get_entropy(length, char_num)} bit')

    def set_strength(self) -> None:
        password_text = self.ui.line_password.text()
        strength = evaluate_password_strength(password_text)

        strength_map = {
            "Weak": (2, "red"),         
            "Medium": (4, "orange"),    
            "Strong": (6, "yellow"),    
            "Very Strong": (8, "green") 
        }

        bars_to_activate, color = strength_map.get(strength, (0, "gray"))

        # Tooltip update for strength bars
        tooltip_text = {
            "Weak": "Weak: Increase length & add variety.",
            "Medium": "Medium: Add more characters & mix letters/numbers.",
            "Strong": "Strong: Good, but consider adding more length.",
            "Very Strong": "Very Strong: Secure password!"
        }

        for bar in self.ui.strength_bars:
            bar.setToolTip(tooltip_text.get(strength, "🔄 Analyzing password strength..."))

        # Default gray style
        default_style = "QFrame { background-color: gray; border: 1px solid black; min-width: 50px; min-height: 20px; }"
        active_style = f"QFrame {{ background-color: {color}; border: 1px solid black; min-width: 50px; min-height: 20px; }}"

        # Reset all bars
        for bar in self.ui.strength_bars:
            bar.setStyleSheet(default_style)

        # Activate bars based on strength
        for i in range(bars_to_activate):
            self.ui.strength_bars[i].setStyleSheet(active_style)


    def change_password_visibility(self) -> None:
        if self.ui.btn_visibility.isChecked():
            self.ui.line_password.setEchoMode(QLineEdit.Normal)
        else:
            self.ui.line_password.setEchoMode(QLineEdit.Password)

    def copy_to_clipboard(self) -> None:
        QApplication.clipboard().setText(self.ui.line_password.text())

    def authenticate_user(self):
        """Authenticate the user and show the main window on success."""
        if not self.db.master_password_exists():
            new_password, ok = QInputDialog.getText(self, "Set Master Password", "Create a master password:", QLineEdit.Password)
            if ok and new_password:
                self.db.set_master_password(new_password)
                QMessageBox.information(self, "Success", "Master password set successfully.")
                self.last_activity_time = datetime.now()  # Reset activity time
                self.reset_timers()  # Reset both timers
                self.show()  # Show the main window
                return True
            else:
                QMessageBox.warning(self, "Error", "Master password required!")
                return False

        while True:
            password, ok = QInputDialog.getText(self, "Authentication", "Enter Master Password:", QLineEdit.Password)
            if not ok:
                return False
            if self.db.verify_master_password(password):
                self.last_activity_time = datetime.now()  # Reset activity time
                self.reset_timers()  # Reset both timers
                self.show()  # Show the main window
                return True
            QMessageBox.warning(self, "Access Denied", "Incorrect master password! Try again.")
    
    # Save password to database with the selected category
    def save_password(self):
        if not self.authenticate_user():
            QMessageBox.warning(self, "Access Denied", "Authentication required to save passwords.")
            return

        site, ok1 = QInputDialog.getText(self, "Save Password", "Enter Site Name:")
        username, ok2 = QInputDialog.getText(self, "Save Password", "Enter Username:")
        password_text = self.ui.line_password.text()
        category = self.get_selected_category()  # Retrieve the selected category

        if ok1 and ok2 and password_text:
            # Set expiry date to 90 days from now
            expiry_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')

            # Save the password with the expiry date
            self.db.save_password(site, username, password_text, category, expiry_date)  # Save with expiry date
            QMessageBox.information(self, "Success", f"Password saved successfully under '{category}' category!")
        else:
            QMessageBox.warning(self, "Error", "Invalid input. Password not saved.")


    def get_selected_category(self):
      """Return the selected category from dropdown"""
      if hasattr(self.ui, 'category_dropdown'):
          return self.ui.category_dropdown.currentText()
      return "Other"  # Default if dropdown doesn't exist yet

    def handle_reset_password(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Reset Password")
        msg_box.setText("Would you like to reset the master password?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if msg_box.exec() == QMessageBox.Yes:
            email, ok = QInputDialog.getText(self, "Set Email", "Enter your email address:")
            if ok and email:
                exists = self.db.master_email_exists()
                if exists > 0:                 
                    self.auth.generate_verification_code(email)
                    
                    entered_code, ok = QInputDialog.getText(self, "Reset Password", "Enter verification code:")  
                     
                    self.db.reset_master_password(email, entered_code)    
                    self.authenticate_user()
                    return True
                else:
                    self.db.set_master_email(email)
                    
                    return False
    def show_tooltip(self):
            QMessageBox.information(self, "Password History", "No passwords saved yet!")
     # Load categories from database
    def load_categories(self):
        """Load categories from database into the dropdown menu"""
        categories = self.db.get_categories()
        if not hasattr(self.ui, 'category_dropdown'):
            return  # Skip if UI isn't fully initialized yet with dropdown
        
        # Clear existing items
        self.ui.category_dropdown.clear()
        
        # Add categories to dropdown
        for category in categories:
            self.ui.category_dropdown.addItem(category)
        
        # Default select first item
        if self.ui.category_dropdown.count() > 0:
            self.ui.category_dropdown.setCurrentIndex(0)
    
    def select_category(self, button):
        if self.current_category_button and self.current_category_button != button:
            self.current_category_button.setChecked(False)
        button.setChecked(True)
        self.current_category_button = button
        print(f"Selected category: {button.text()}")

    def show_password_history(self):
        if not self.master_password_verified:
            master_password, ok = QInputDialog.getText(self, "Master Password", "Enter master password:", QLineEdit.Password)
            if not ok or not self.db.verify_master_password(master_password):
                QMessageBox.warning(self, "Access Denied", "Incorrect master password.")
                return
            self.master_password_verified = True  # ✅ Set it only once

        # Proceed to show history
        history_viewer = PasswordHistoryDialog(self, db=self.db)
        # Apply current theme to the history table
        theme = "dark" if self.theme_manager.is_dark_mode else "light"
        
        # Styling for search bar and table
        search_bar_style = f"""
            QLineEdit {{
                background-color: {'#1e1e1e' if theme == 'dark' else '#ffffff'};
                color: {'white' if theme == 'dark' else 'black'} !important;
                border: 1px solid {'#444' if theme == 'dark' else '#cccccc'};
                border-radius: 4px;
                padding: 5px;
            }}
        """
        
        password_history_style = f"""
            QTableWidget {{
                background-color: {'#1e1e1e' if theme == 'dark' else '#ffffff'};
                alternate-background-color: {'#2a2a2a' if theme == 'dark' else '#f0f0f0'};
            }}
            QTableWidget::item {{
                background-color: {'#1e1e1e' if theme == 'dark' else '#ffffff'};
                color: {'white' if theme == 'dark' else 'black'} !important;
            }}
            QHeaderView {{
                background-color: {'#2a2a2a' if theme == 'dark' else '#f0f0f0'};
            }}
            QHeaderView::section {{
                background-color: {'#333' if theme == 'dark' else '#e0e0e0'};
                color: {'white' if theme == 'dark' else 'black'} !important;
                padding: 4px;
                border: 1px solid {'#444' if theme == 'dark' else '#cccccc'};
                font-weight: bold;
            }}
        """
        
        if hasattr(history_viewer, 'search_bar'):
            history_viewer.search_bar.setStyleSheet(search_bar_style)
        
        if hasattr(history_viewer, 'history_table'):
            history_viewer.history_table.setStyleSheet(password_history_style)
            history_viewer.history_table.setAlternatingRowColors(True)
            
            # Manually set text color for each item
            for row in range(history_viewer.history_table.rowCount()):
                for col in range(history_viewer.history_table.columnCount()):
                    item = history_viewer.history_table.item(row, col)
                    if item:
                        # Set text color directly
                        text_color = Qt.white if theme == 'dark' else Qt.black
                        item.setForeground(text_color)

        history_viewer.exec()

    def export_passwords(self):
      #Export password records with only decrypted passwords
      if not self.authenticate_user():
          QMessageBox.warning(self, "Access Denied", "Authentication required to export passwords.")
          return

      try:
          file_path, _ = QFileDialog.getSaveFileName(
              self,
              "Export Passwords",
              "passwords.csv",
              "CSV Files (*.csv)"
          )
          
          if not file_path:  # User cancelled
              return
              
          # Get data from database
          data = self.db.export_passwords()
          
          if not data:
              QMessageBox.information(self, "Export", "No passwords to export.")
              return
              
          # Write to CSV
          with open(file_path, 'w', newline='', encoding='utf-8') as f:
              writer = csv.writer(f)
              # Write headers
              writer.writerow(['ID', 'Website', 'Username', 'Password', 'Category', 'Created At'])
              # Write data
              writer.writerows(data)
              
          QMessageBox.information(self, "Success", f"Data exported successfully to {file_path}")
          
      except Exception as e:
          print(f"Export error: {str(e)}")
          QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
          
    def show_password_history(self):
        """Display the password history after verifying the master password."""

        # Request the master password
        master_password, ok = QInputDialog.getText(self, "Master Password", "Enter master password:", QLineEdit.Password)
        if not ok or not self.db.verify_master_password(master_password):
            QMessageBox.warning(self, "Access Denied", "Incorrect master password.")
            return

        # Show the password history viewer
        history_viewer = PasswordHistoryDialog(self, db=self.db)
        history_viewer.exec()
          
    def toggle_tooltips(self):
        """Toggle tooltips on/off based on button state and save preference"""
        enabled = self.tooltip_toggle.isChecked()
        
        if enabled:
            self.tooltip_manager.enable_tooltips()
            self.apply_tooltips()  # Reapply tooltips
            self.tooltip_toggle.setText("ON")
        else:
            self.tooltip_manager.disable_tooltips()
            self.clear_all_tooltips()  # Clear all tooltips
            self.tooltip_toggle.setText("OFF")
        
        # Save preference to database
        self.db.set_tooltip_preference(enabled)

    def clear_all_tooltips(self):
        """Clear tooltips from all UI elements when disabled"""
        # Clear tooltips from major UI elements
        ui_elements = [
            self.ui.slider_length, self.ui.spinbox_length, self.ui.btn_lower, 
            self.ui.btn_upper, self.ui.btn_digits, self.ui.btn_special,
            self.ui.btn_refresh, self.ui.btn_copy, self.ui.btn_visibility, 
            self.ui.btn_save, self.ui.line_password, self.ui.label_entropy
        ]
        
        for element in ui_elements:
            element.setToolTip("")
        
        # Clear tooltips from strength bars
        for bar in self.ui.strength_bars:
            bar.setToolTip("")
        
        # Clear tooltips from navigation elements
        nav_elements = [
            self.ui.btn_sidebar_generator, self.ui.btn_sidebar_history,
            self.ui.btn_sidebar_expiry, self.ui.btn_sidebar_export
        ]
        
        for element in nav_elements:
            element.setToolTip("")
        
        # Clear tooltips from dropdown and collapsible sections
        if hasattr(self.ui, 'category_dropdown'):
            self.ui.category_dropdown.setToolTip("")
        
        if hasattr(self, 'character_options_box'):
            self.character_options_box.toggle_button.setToolTip("")
        
        if hasattr(self, 'action_buttons_box'):
            self.action_buttons_box.toggle_button.setToolTip("")

    def apply_tooltips(self):
        """Apply tooltips to all relevant UI elements"""
        if not hasattr(self, 'tooltip_manager'):
            return  # Skip if tooltip manager isn't initialized

        tc = TooltipContent
        tm = self.tooltip_manager
        
        # Apply tooltips to password generator elements
        tm.set_tooltip(self.ui.slider_length, tc.PASSWORD_GENERATOR["length_slider"])
        tm.set_tooltip(self.ui.spinbox_length, tc.PASSWORD_GENERATOR["length_slider"])
        tm.set_tooltip(self.ui.btn_lower, tc.PASSWORD_GENERATOR["lowercase"])
        tm.set_tooltip(self.ui.btn_upper, tc.PASSWORD_GENERATOR["uppercase"])
        tm.set_tooltip(self.ui.btn_digits, tc.PASSWORD_GENERATOR["digits"])
        tm.set_tooltip(self.ui.btn_special, tc.PASSWORD_GENERATOR["special"])
        tm.set_tooltip(self.ui.btn_refresh, tc.PASSWORD_GENERATOR["refresh"])
        tm.set_tooltip(self.ui.btn_copy, tc.PASSWORD_GENERATOR["copy"])
        tm.set_tooltip(self.ui.btn_visibility, tc.PASSWORD_GENERATOR["visibility"])
        tm.set_tooltip(self.ui.btn_save, tc.PASSWORD_GENERATOR["save"])
        tm.set_tooltip(self.ui.line_password, tc.PASSWORD_GENERATOR["password_field"])
        
        # Apply tooltips to password strength elements
        for bar in self.ui.strength_bars:
            tm.set_tooltip(bar, tc.PASSWORD_STRENGTH["strength_meter"])
        tm.set_tooltip(self.ui.label_entropy, tc.PASSWORD_STRENGTH["entropy"])
        
        # Apply tooltips to category elements
        if hasattr(self.ui, 'category_dropdown'):
            tm.set_tooltip(self.ui.category_dropdown, tc.CATEGORIES["dropdown"])
        
        # Apply tooltips to navigation elements
        tm.set_tooltip(self.ui.btn_sidebar_generator, tc.NAVIGATION["sidebar_generator"])
        tm.set_tooltip(self.ui.btn_sidebar_history, tc.NAVIGATION["sidebar_history"])
        tm.set_tooltip(self.ui.btn_sidebar_expiry, tc.NAVIGATION["sidebar_expiry"])
        tm.set_tooltip(self.ui.btn_sidebar_export, tc.NAVIGATION["sidebar_export"])
        
        # Apply tooltips to collapsible sections
        if hasattr(self, 'character_options_box'):
            tm.set_tooltip(self.character_options_box.toggle_button, "Click to expand/collapse character options")
        if hasattr(self, 'action_buttons_box'):
            tm.set_tooltip(self.action_buttons_box.toggle_button, "Click to expand/collapse actions")
    
    def setup_theme_manager(self):
        # Initialize theme manager with self as parent
        self.theme_manager = ThemeManager(self)
        
        # Connect theme toggle button to theme manager
        self.ui.btn_theme_toggle.clicked.connect(self.toggle_theme)
        
        # Apply initial theme
        self.apply_current_theme()
        
        # Connect theme changed signal to update UI elements
        self.theme_manager.themeChanged.connect(self.update_theme_ui)

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        current_theme = self.theme_manager.toggle_theme()
        # Reset any custom background color when changing themes
        if hasattr(self, 'current_bg_color'):
            self.current_bg_color = QColor("#121212") if self.theme_manager.is_dark_mode else QColor("#f5f5f5")
            self.centralWidget().setStyleSheet("")  # Clear any custom background

        # Apply the new theme stylesheet
        self.apply_current_theme()
        
        return current_theme

    def apply_current_theme(self):
        """Apply the current theme stylesheet to the application"""
        # Get current theme
        theme = "dark" if self.theme_manager.is_dark_mode else "light"
        
        # Get and apply stylesheet
        stylesheet = self.theme_manager.get_stylesheet_for_theme()
        self.setStyleSheet(stylesheet)
        
        # Update all special widgets that need custom handling
        self.theme_manager.update_all_widgets(theme)
        
        # Force update of all widgets
        for widget in self.findChildren(QWidget):
            # Only apply style operations to widgets that are not QAbstractItemView
            # QAbstractItemView and its subclasses have special update requirements
            if isinstance(widget, QWidget) and hasattr(widget, 'style') and widget.style():
                try:
                    widget.style().unpolish(widget)
                    widget.style().polish(widget)
                    widget.update()
                except Exception as e:
                    print(f"[WARN] Could not polish widget {widget}: {e}")
            else:
                # For QAbstractItemView widgets, just request a visual update
                # without trying to update specific items
                widget.viewport().update()
                    
    def update_theme_ui(self, theme=None):
        # Update UI elements that need custom handling when theme changes
        # Get current theme if not provided
        if theme is None:
            theme = "dark" if self.theme_manager.is_dark_mode else "light"
        
        # Update all widget styles using the theme manager
        self.theme_manager.update_all_widgets(theme)
        
        # Explicitly update collapsible box button text colors
        if hasattr(self, 'character_options_box'):
            text_color = "white" if theme == "dark" else "#121212"
            self.character_options_box.toggle_button.setStyleSheet(f"""
                QToolButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                    color: {text_color};
                }}
                QToolButton:hover {{
                    background-color: rgba(128, 128, 128, 0.2);
                }}
                QToolButton::menu-indicator {{ 
                    image: none; 
                }}
            """)
        
        if hasattr(self, 'action_buttons_box'):
            text_color = "white" if theme == "dark" else "#121212"
            self.action_buttons_box.toggle_button.setStyleSheet(f"""
                QToolButton {{
                    background-color: transparent;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                    color: {text_color};
                }}
                QToolButton:hover {{
                    background-color: rgba(128, 128, 128, 0.2);
                }}
                QToolButton::menu-indicator {{ 
                    image: none; 
                }}
            """)
        
        # Refresh strength indicators
        self.set_strength()

    def refresh_all_widgets(self):
        """Force refresh all widgets to properly apply theme changes"""
        widgets = [w for w in self.findChildren(QWidget) if isinstance(w, QWidget)]
        for widget in widgets:
            style = widget.style()
            if style:
                style.unpolish(widget)
                style.polish(widget)
                widget.update()

        
    def setup_accent_color_button(self):
        # Resize to match background color button
        self.ui.btn_accent_color.setMinimumWidth(150)
        self.ui.btn_accent_color.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background-color: #333;
                color: white;
                border: 2px solid gray;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)

        # Define accent color options
        self.accent_colors = {
            "Green": "#00c853",
            "Red": "#d32f2f",
            "Purple": "#7e57c2",
            "Blue": "#039be5",
            "Orange": "#f57c00"
        }

        # Create menu on demand
        self.accent_menu = QMenu()

        for name, hexcode in self.accent_colors.items():
            action = QAction(name, self)
            action.triggered.connect(lambda _, c=hexcode: self.apply_accent_color(c))
            self.accent_menu.addAction(action)

        # Show menu when button is clicked (not setMenu!)
        self.ui.btn_accent_color.clicked.connect(self.show_accent_menu)

    def show_accent_menu(self):
        pos = self.ui.btn_accent_color.mapToGlobal(self.ui.btn_accent_color.rect().bottomLeft())
        self.accent_menu.exec(pos)

    def apply_accent_color(self, color):
        # Example: update character toggle buttons
        for btn in [self.ui.btn_lower, self.ui.btn_upper, self.ui.btn_digits, self.ui.btn_special]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    padding: 13px 10px;
                    font-size: 12pt;
                    border-radius: 6px;
                    color: white;
                    background-color: #2a2a2a;
                    border: 2px solid #444;
                }}
                QPushButton:checked {{
                    background-color: {color};
                    color: white;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: #3a3a3a;
                }}
            """)

        # Tooltip toggle
        self.tooltip_toggle.setStyleSheet(f"""
            QPushButton {{
                min-width: 80px;
                min-height: 30px;
                border: 2px solid #555;
                border-radius: 15px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:checked {{
                background-color: {color};
                color: white;
            }}
            QPushButton:!checked {{
                background-color: #555;
                color: #ccc;
            }}
        """)

        # Slider bar
        self.ui.slider_length.setStyleSheet(f"""
            QSlider::sub-page:horizontal {{
                background-color: {color};
            }}
            QSlider::add-page:horizontal {{
                background-color: gray;
            }}
            QSlider::handle:horizontal {{
                background-color: white;
                width: 22px;
                border-radius: 10px;
            }}
        """)

        # Border hover (frame_password)
        self.ui.frame_password.setStyleSheet(f"""
            QFrame {{
                border: 2px solid gray;
                border-radius: 5px;
            }}
            QFrame:hover {{
                border-color: {color};
            }}
        """)

        # Category label and dropdown
        self.ui.category_label.setStyleSheet(f"color: {color}; font-size: 16pt; font-weight: bold;")
        self.ui.category_dropdown.setStyleSheet(f"""
            QComboBox {{
                border: 2px solid gray;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: #333;
                color: white;
                font-size: 14pt;
            }}
            QComboBox:hover {{
                border-color: {color};
            }}
            QComboBox QAbstractItemView {{
                selection-background-color: {color};
                selection-color: white;
            }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordGenerator()
    window.show()
    sys.exit(app.exec())
