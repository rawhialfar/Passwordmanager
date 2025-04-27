from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QWidget, QAbstractItemView, QLabel, QTableWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class ThemeManager(QObject):
    """
    A class to manage theme switching between light and dark modes.
    Emits signals when theme is changed, and stores theme state.
    """
    themeChanged = Signal(str)  # Signal emitted when theme changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark_mode = True  # Default to dark mode
        self.parent = parent
    
    @property
    def is_dark_mode(self):
        """Get current theme mode"""
        return self._dark_mode
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self._dark_mode = not self._dark_mode
        theme_name = "dark" if self._dark_mode else "light"
        self.themeChanged.emit(theme_name)
        return theme_name
    
    def set_theme(self, dark_mode=True):
        """Explicitly set theme mode"""
        if self._dark_mode != dark_mode:
            self._dark_mode = dark_mode
            theme_name = "dark" if self._dark_mode else "light"
            self.themeChanged.emit(theme_name)
            return theme_name
        return "dark" if self._dark_mode else "light"
        
    def get_stylesheet_for_theme(self, theme=None):
        """Return the appropriate stylesheet based on current theme or specified theme"""
        if theme is None:
            theme = "dark" if self._dark_mode else "light"
            
        if theme == "dark":
            return self.get_dark_theme()
        else:
            return self.get_light_theme()
    
    def update_collapsible_box_theme(self, box, theme):
        """Update collapsible box styling based on theme"""
        if theme == "dark":
            box.toggle_button.setStyleSheet("""
                QToolButton {
                    background-color: #1e1e1e;
                    border: 1px solid #444;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                    color: white;
                }
                QToolButton:hover {
                    background-color: #2a2a2a;
                }
                QToolButton::menu-indicator { 
                    image: none; 
                }
            """)
            box.content_area.setStyleSheet("""
                QScrollArea {
                    background-color: #1e1e1e;
                    border: none;
                    border-radius: 5px;
                    padding: 0px;
                    margin: 0px;
                }
                QScrollArea > QWidget > QWidget {
                    background-color: #1e1e1e;
                }
            """)
        else:
            box.toggle_button.setStyleSheet("""
                QToolButton {
                    background-color: #e0e0e0;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 5px;
                    font-weight: bold;
                    color: #121212;
                }
                QToolButton:hover {
                    background-color: #d0d0d0;
                }
                QToolButton::menu-indicator { 
                    image: none; 
                }
            """)
            box.content_area.setStyleSheet("""
                QScrollArea {
                    background-color: #e0e0e0;
                    border: none;
                    border-radius: 5px;
                    padding: 0px;
                    margin: 0px;
                }
                QScrollArea > QWidget > QWidget {
                    background-color: #e0e0e0;
                }
            """)
    
    def update_sidebar_buttons(self, theme):
        """Update sidebar buttons based on theme"""
        if not hasattr(self.parent, 'ui'):
            return
            
        sidebar_buttons = [
            self.parent.ui.btn_sidebar_generator,
            self.parent.ui.btn_sidebar_history,
            self.parent.ui.btn_sidebar_expiry, 
            self.parent.ui.btn_sidebar_export
        ]
        
        if theme == "dark":
            sidebar_style = """
                QPushButton {
                    border: none;
                    background-color: transparent;
                    color: white;
                }
                QPushButton:checked {
                    background-color: #333333;
                    border-left: 4px solid #00ff00;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                }
            """
        else:
            sidebar_style = """
                QPushButton {
                    border: none;
                    background-color: transparent;
                    color: #121212;
                }
                QPushButton:checked {
                    background-color: #d0d0d0;
                    border-left: 4px solid #009900;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
            """
        
        for button in sidebar_buttons:
            button.setStyleSheet(sidebar_style)
    
    def update_theme_toggle_button(self, theme):
        """Update theme toggle button based on theme"""
        if not hasattr(self.parent, 'ui') or not hasattr(self.parent.ui, 'btn_theme_toggle'):
            return
        try:
            if theme == "dark":
                self.parent.ui.btn_theme_toggle.setIcon(QIcon("src/ui/icons/moon.svg"))
                self.parent.ui.btn_theme_toggle.setToolTip("Switch to Light Theme")
                self.parent.ui.btn_theme_toggle.setStyleSheet("""
                    QPushButton#btn_theme_toggle {
                        background-color: #1e1e1e;
                        border: 2px solid #444;
                        border-radius: 15px;
                        padding: 5px;
                        min-width: 30px;
                        max-width: 30px;
                        min-height: 30px;
                        max-height: 30px;
                    }
                    QPushButton#btn_theme_toggle:hover {
                        background-color: #2a2a2a;
                        border-color: #666;
                    }
                """)
            else:
                self.parent.ui.btn_theme_toggle.setIcon(QIcon("src/icons/sun.svg"))
                self.parent.ui.btn_theme_toggle.setToolTip("Switch to Dark Theme")
                self.parent.ui.btn_theme_toggle.setStyleSheet("""
                    QPushButton#btn_theme_toggle {
                        background-color: #e0e0e0;
                        border: 2px solid #cccccc;
                        border-radius: 15px;
                        padding: 5px;
                        min-width: 30px;
                        max-width: 30px;
                        min-height: 30px;
                        max-height: 30px;
                    }
                    QPushButton#btn_theme_toggle:hover {
                        background-color: #d0d0d0;
                        border-color: #aaaaaa;
                    }
                """)
        except Exception as e:
            print(f"Error updating theme toggle button: {e}")
            # Fallback with simple text
            if theme == "dark":
                self.parent.ui.btn_theme_toggle.setText("🌙")
            else:
                self.parent.ui.btn_theme_toggle.setText("☀️")
    
    def update_special_widgets(self, theme):
        """Update special widgets that need custom styling"""
        if not hasattr(self.parent, 'ui'):
            return
            
        # Update history button if it exists
        if hasattr(self.parent.ui, 'btn_history'):
            if theme == "dark":
                self.parent.ui.btn_history.setStyleSheet("""
                    QPushButton {
                        background-color: #333;
                        color: white;
                        padding: 10px;
                        border: 2px solid gray;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        border-color: #090;
                        background-color: #555;
                    }
                """)
            else:
                self.parent.ui.btn_history.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0;
                        color: #121212;
                        padding: 10px;
                        border: 2px solid #aaaaaa;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        border-color: #090;
                        background-color: #d0d0d0;
                    }
                """)
        
        # Update category frame if it exists
        if hasattr(self.parent.ui, 'category_frame'):
            if theme == "dark":
                self.parent.ui.category_frame.setStyleSheet("""
                    QFrame {
                        background-color: #1e1e1e;
                        border: 1px solid #444;
                        border-radius: 8px;
                        margin-top: 15px;
                        margin-bottom: 15px;
                    }
                """)
                # Update category label if it exists
                if hasattr(self.parent.ui, 'category_label'):
                    self.parent.ui.category_label.setStyleSheet("""
                        QLabel {
                            font-size: 16pt;
                            font-weight: bold;
                            color: #00cc00;
                        }
                    """)
            else:
                self.parent.ui.category_frame.setStyleSheet("""
                    QFrame {
                        background-color: #e0e0e0;
                        border: 1px solid #cccccc;
                        border-radius: 8px;
                        margin-top: 15px;
                        margin-bottom: 15px;
                    }
                """)
                # Update category label if it exists
                if hasattr(self.parent.ui, 'category_label'):
                    self.parent.ui.category_label.setStyleSheet("""
                        QLabel {
                            font-size: 16pt;
                            font-weight: bold;
                            color: #009900;
                        }
                    """)
        
        # Update tooltip frame if it exists
        if hasattr(self.parent, 'tooltip_frame'):
            if theme == "dark":
                self.parent.tooltip_frame.setStyleSheet("""
                    QFrame {
                        background-color: #1e1e1e;
                        border: 1px solid #444;
                        border-radius: 5px;
                        margin-top: 5px;
                        margin-bottom: 5px;
                    }
                """)
            else:
                self.parent.tooltip_frame.setStyleSheet("""
                    QFrame {
                        background-color: #e0e0e0;
                        border: 1px solid #cccccc;
                        border-radius: 5px;
                        margin-top: 5px;
                        margin-bottom: 5px;
                    }
                """)
        
        # Update Save/Reset Password buttons, Beginner Tooltips text, and Category Dropdown
        if theme == "dark":
            # Dark theme styles
            save_reset_style = """
                QPushButton {
                    background-color: #1e1e1e;
                    color: white;
                    padding: 10px;
                    border: 2px solid #444;
                    border-radius: 5px;
                    font-size: 12.5pt;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    border-color: #090;
                }
            """
            
            dropdown_style = """
                QComboBox {
                    background-color: #1e1e1e;
                    color: white;
                    border: 2px solid #444;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 12.5pt;
                }
                QComboBox:hover {
                    border-color: #090;
                }
                QComboBox QAbstractItemView {
                    background-color: #1e1e1e;
                    color: white;
                    selection-background-color: #2a2a2a;
                }
            """
            
            tooltip_label_style = """
                QLabel {
                    font-size: 14pt;
                    color: white;
                }
            """
        else:
            # Light theme styles
            save_reset_style = """
                QPushButton {
                    background-color: #e0e0e0;
                    color: #121212;
                    padding: 10px;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    font-size: 12.5pt;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                    border-color: #090;
                }
            """
            
            dropdown_style = """
                QComboBox {
                    background-color: #f0f0f0;
                    color: #121212;
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 12.5pt;
                }
                QComboBox:hover {
                    border-color: #090;
                }
                QComboBox QAbstractItemView {
                    background-color: #f0f0f0;
                    color: #121212;
                    selection-background-color: #d0d0d0;
                }
            """
            
            tooltip_label_style = """
                QLabel {
                    font-size: 14pt;
                    color: #121212;
                }
            """

        # Apply styles
        if hasattr(self.parent.ui, 'btn_save'):
            self.parent.ui.btn_save.setStyleSheet(save_reset_style)
        
        if hasattr(self.parent.ui, 'forgotPasswordButton'):
            self.parent.ui.forgotPasswordButton.setStyleSheet(save_reset_style)
            
        if hasattr(self.parent.ui, 'category_dropdown'):
            self.parent.ui.category_dropdown.setStyleSheet(dropdown_style)
        
        if hasattr(self.parent.ui, 'tooltip_label'):
            self.parent.ui.tooltip_label.setStyleSheet(tooltip_label_style)

        # Update slider handle color
        slider_style = """
            QSlider::handle:horizontal {
                background-color: %s;
                width: 22px;
                border-radius: 10px;
                margin-top: -8px;
                margin-bottom: -8px;
            }
        """ % ("white" if theme == "dark" else "#333333")
        
        if hasattr(self.parent.ui, 'slider_length'):
            current_style = self.parent.ui.slider_length.styleSheet()
            # Preserve existing slider styles while updating handle color
            if "QSlider::handle:horizontal" in current_style:
                current_style = current_style.split("QSlider::handle:horizontal")[0]
            new_style = current_style + slider_style
            self.parent.ui.slider_length.setStyleSheet(new_style)

        # Update tooltip label color
        tooltip_label_style = """
            QLabel {
                font-size: 14pt;
                color: %s;
            }
        """ % ("white" if theme == "dark" else "#121212")
        
        # Find tooltip label in tooltip frame
        if hasattr(self.parent, 'tooltip_frame'):
            for child in self.parent.tooltip_frame.findChildren(QLabel):
                child.setStyleSheet(tooltip_label_style)
    
    def update_collapsible_sections(self, theme):
        # Update collapsible sections based on theme"""
        if hasattr(self.parent, 'character_options_box'):
            if theme == "dark":
                self.parent.character_options_box.toggle_button.setStyleSheet("""
                    QToolButton {
                        background-color: transparent;
                        border: none;
                        border-radius: 5px;
                        padding: 5px;
                        font-weight: bold;
                        color: white;  /* Ensure white text for dark theme */
                    }
                    QToolButton:hover {
                        background-color: rgba(255, 255, 255, 0.1);
                    }
                    QToolButton::menu-indicator { 
                        image: none; 
                    }
                """)
            else:
                self.parent.character_options_box.toggle_button.setStyleSheet("""
                    QToolButton {
                        background-color: transparent;
                        border: none;
                        border-radius: 5px;
                        padding: 5px;
                        font-weight: bold;
                        color: #121212;  /* Ensure dark text for light theme */
                    }
                    QToolButton:hover {
                        background-color: rgba(0, 0, 0, 0.1);
                    }
                    QToolButton::menu-indicator { 
                        image: none; 
                    }
                """)
        
        if hasattr(self.parent, 'action_buttons_box'):
            if theme == "dark":
                self.parent.action_buttons_box.toggle_button.setStyleSheet("""
                    QToolButton {
                        background-color: transparent;
                        border: none;
                        border-radius: 5px;
                        padding: 5px;
                        font-weight: bold;
                        color: white;  /* Ensure white text for dark theme */
                    }
                    QToolButton:hover {
                        background-color: rgba(255, 255, 255, 0.1);
                    }
                    QToolButton::menu-indicator { 
                        image: none; 
                    }
                """)
            else:
                self.parent.action_buttons_box.toggle_button.setStyleSheet("""
                    QToolButton {
                        background-color: transparent;
                        border: none;
                        border-radius: 5px;
                        padding: 5px;
                        font-weight: bold;
                        color: #121212;  /* Ensure dark text for light theme */
                    }
                    QToolButton:hover {
                        background-color: rgba(0, 0, 0, 0.1);
                    }
                    QToolButton::menu-indicator { 
                        image: none; 
                    }
                """)
    
    def update_all_widgets(self, theme=None):
        # Update all widgets with the current theme
        if theme is None:
            theme = "dark" if self._dark_mode else "light"
            
        # Update special widgets
        self.update_sidebar_buttons(theme)
        self.update_theme_toggle_button(theme)
        self.update_special_widgets(theme)
        self.update_collapsible_sections(theme)
        
        # Update any password history table that might be open
        password_history_style = """
            QTableWidget {
                font-size: 14px;
                padding: 20px;
                gridline-color: %s;
                border: none;
                background-color: %s;
                color: %s;
            }
            QHeaderView::section {
                color: %s;
                font-weight: bold;
                padding: 5px;
                text-align: center;
                background-color: %s;
            }
        """ % (
            "#DDD" if theme == "dark" else "#aaaaaa",           # gridline color
            "#1e1e1e" if theme == "dark" else "#ffffff",        # background color
            "white" if theme == "dark" else "#121212",          # text color
            "white" if theme == "dark" else "#121212",          # header text color
            "#333" if theme == "dark" else "#e0e0e0"            # header background color
        )
        
        # Apply this style to any open history tables
        for widget in self.parent.findChildren(QTableWidget):
            widget.setStyleSheet(password_history_style)
    
    def get_dark_theme(self):
        """Return dark theme stylesheet"""
        return """
            QWidget {
                background-color: #121212;
                color: white;
                font-family: Roboto;
                font-size: 12.5pt;
            }
            
            QPushButton {
                border: 2px solid gray;
                border-radius: 5px;
                padding: 12.5px;
            }
            
            QPushButton:hover {
                border-color: #090;
            }
            
            QPushButton:pressed {
                border: 4px solid #090;
                border-radius: 5px;
            }
            
            QPushButton:checked {
                background-color: #006300;
                border-color: #090;
            }
            
            QPushButton#btn_lower,
            #btn_upper,
            #btn_digits,
            #btn_special {
                padding: 7px;
                min-height: 25px;
                font-size: 10pt;
                border: 2px solid #444;
                border-radius: 4px;
                color: white;
                background-color: #1e1e1e;
            }
            
            QPushButton#btn_lower:checked,
            #btn_upper:checked,
            #btn_digits:checked,
            #btn_special:checked {
                background-color: #2ea043;
                border-color: #2ea043;
            }
            
            QPushButton#btn_lower:hover,
            #btn_upper:hover,
            #btn_digits:hover,
            #btn_special:hover {
                background-color: #2a2a2a;
            }
            
            QSlider::groove:horizontal {
                background-color: transparent;
                height: 5px;
            }
            
            QSlider::sub-page:horizontal {
                background-color: #090;
            }
            
            QSlider::add-page:horizontal {
                background-color: gray;
            }
            
            QSlider::handle:horizontal {
                background-color: white;
                width: 22px;
                border-radius: 10px;
                margin-top: -8px;
                margin-bottom: -8px;
            }
            
            QSpinBox {
                border: 2px solid gray;
                border-radius: 5px;
                background: transparent;
                padding: 2px;
            }
            
            QSpinBox:hover {
                border-color: #009900;
            }
            
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: none;
                padding: 12.5px;
            }
            
            QFrame {
                border: 2px solid gray;
                border-radius: 5px;
            }
            
            QComboBox {
                border: 2px solid gray;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: #333;
                color: white;
                font-size: 14pt;
            }
            
            QComboBox:hover {
                border-color: #00cc00;
            }
            
            QComboBox:focus {
                border-color: #00cc00;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: gray;
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #333;
                color: white;
                selection-background-color: #006300;
                selection-color: white;
                border: 1px solid gray;
                border-radius: 0px;
            }
            
            QFrame#category_frame {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 8px;
            }
            
            QLabel#category_label {
                font-size: 16pt;
                font-weight: bold;
                color: #00cc00;
            }
            
            #tooltip_frame {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 5px;
            }
            
            QToolButton {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: white;
            }
            
            QToolButton:hover {
                background-color: #2a2a2a;
            }
            
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
                border-radius: 5px;
                padding: 0px;
                margin: 0px;
            }
            
            QScrollArea > QWidget > QWidget {
                background-color: #1e1e1e;
            }
            
            QTableWidget {
                font-size: 14px;
                padding: 20px;
                gridline-color: #DDD;
                border: none;
                background-color: #1e1e1e;
                color: white;
            }
            
            QHeaderView::section {
                color: white;
                font-weight: bold;
                padding: 5px;
                text-align: center;
                background-color: #333;
            }
            
            QPushButton#btn_theme_toggle {
                background-color: #1e1e1e;
                border: 2px solid #444;
                border-radius: 15px;
                padding: 5px;
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
            }
            
            QPushButton#btn_theme_toggle:hover {
                background-color: #2a2a2a;
                border-color: #666;
            }
            
            QPushButton#btn_history {
                background-color: #333;
                color: white;
                padding: 10px;
                border: 2px solid gray;
                border-radius: 5px;
            }
            
            QPushButton#btn_history:hover {
                border-color: #090;
                background-color: #555;
            }
        """
    
    def get_light_theme(self):
        """Return light theme stylesheet"""
        return """
            QWidget {
                background-color: #f5f5f5;
                color: #121212;
                font-family: Roboto;
                font-size: 12.5pt;
            }
            
            QPushButton {
                border: 2px solid #aaaaaa;
                border-radius: 5px;
                padding: 12.5px;
            }
            
            QPushButton:hover {
                border-color: #090;
            }
            
            QPushButton:pressed {
                border: 4px solid #090;
                border-radius: 5px;
            }
            
            QPushButton:checked {
                background-color: #90EE90;
                border-color: #090;
            }
            
            QPushButton#btn_lower,
            #btn_upper,
            #btn_digits,
            #btn_special {
                padding: 7px;
                min-height: 25px;
                font-size: 10pt;
                border: 2px solid #cccccc;
                border-radius: 4px;
                color: #121212;
                background-color: #e0e0e0;
            }
            
            QPushButton#btn_lower:checked,
            #btn_upper:checked,
            #btn_digits:checked,
            #btn_special:checked {
                background-color: #90EE90;
                border-color: #2ea043;
            }
            
            QPushButton#btn_lower:hover,
            #btn_upper:hover,
            #btn_digits:hover,
            #btn_special:hover {
                background-color: #d0d0d0;
            }
            
            QSlider::groove:horizontal {
                background-color: transparent;
                height: 5px;
            }
            
            QSlider::sub-page:horizontal {
                background-color: #090;
            }
            
            QSlider::add-page:horizontal {
                background-color: #cccccc;
            }
            
            QSlider::handle:horizontal {
                background-color: #333333;
                width: 22px;
                border-radius: 10px;
                margin-top: -8px;
                margin-bottom: -8px;
            }
            
            QSpinBox {
                border: 2px solid #aaaaaa;
                border-radius: 5px;
                background: #ffffff;
                padding: 2px;
            }
            
            QSpinBox:hover {
                border-color: #009900;
            }
            
            QLineEdit {
                background-color: #ffffff;
                color: #121212;
                border: none;
                padding: 12.5px;
            }
            
            QFrame {
                border: 2px solid #aaaaaa;
                border-radius: 5px;
            }
            
            QComboBox {
                border: 2px solid #aaaaaa;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: #e0e0e0;
                color: #121212;
                font-size: 14pt;
            }
            
            QComboBox:hover {
                border-color: #00cc00;
            }
            
            QComboBox:focus {
                border-color: #00cc00;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: #aaaaaa;
                border-left-style: solid;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #121212;
                selection-background-color: #90EE90;
                selection-color: #121212;
                border: 1px solid #aaaaaa;
                border-radius: 0px;
            }
            
            QFrame#category_frame {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-radius: 8px;
            }
            
            QLabel#category_label {
                font-size: 16pt;
                font-weight: bold;
                color: #009900;
            }
            
            #tooltip_frame {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            
            QToolButton {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
                color: #121212;
            }
            
            QToolButton:hover {
                background-color: #d0d0d0;
            }
            
            QScrollArea {
                background-color: #e0e0e0;
                border: none;
                border-radius: 5px;
                padding: 0px;
                margin: 0px;
            }
            
            QScrollArea > QWidget > QWidget {
                background-color: #e0e0e0;
            }
            
            QTableWidget {
                font-size: 14px;
                padding: 20px;
                gridline-color: #aaaaaa;
                border: none;
                background-color: #ffffff;
                color: #121212;
            }
            
            QHeaderView::section {
                color: #121212;
                font-weight: bold;
                padding: 5px;
                text-align: center;
                background-color: #e0e0e0;
            }
            
            QPushButton#btn_theme_toggle {
                background-color: #e0e0e0;
                border: 2px solid #cccccc;
                border-radius: 15px;
                padding: 5px;
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
            }
            
            QPushButton#btn_theme_toggle:hover {
                background-color: #d0d0d0;
                border-color: #aaaaaa;
            }
            
            QPushButton#btn_history {
                background-color: #e0e0e0;
                color: #121212;
                padding: 10px;
                border: 2px solid #aaaaaa;
                border-radius: 5px;
            }
            
            QPushButton#btn_history:hover {
                border-color: #090;
                background-color: #d0d0d0;
            }
        """
    