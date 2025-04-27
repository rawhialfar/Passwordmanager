from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QCursor, QIcon, QFont
from PySide6.QtWidgets import (QAbstractSpinBox, QFrame, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QSizePolicy,
                               QSlider, QSpinBox, QVBoxLayout, QWidget, QMessageBox, QTableWidgetItem, QTableWidget, QDialog, QInputDialog, QProgressBar, QToolTip, QApplication, QComboBox)
from PySide6.QtWidgets import QColorDialog, QMenu
from PySide6.QtGui import QCloseEvent, QCursor, QIcon, QFont, QColor, QAction



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(542, 418)
        MainWindow.setCursor(QCursor(Qt.PointingHandCursor))
        QToolTip.setFont(QFont("Verdana", 10))

        icon = QIcon()
        icon.addFile(u":/icons/icons/app-icon.ico", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(u"QWidget {\n"
                                 "    background-color: #121212;\n"
                                 "    color: white;\n"
                                 "    font-family: Verdana;\n"
                                 "    font-size: 16pt;\n"
                                 "    margin: 10px;\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton {\n"
                                 "    border: 2px solid gray;\n"
                                 "    border-radius: 5px;\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton#btn_lower,\n"
                                 "#btn_upper,\n"
                                 "#btn_digits,\n"
                                 "#btn_special {\n"
                                 "    padding: 10px;\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton:hover {\n"
                                 "    border-color: #090;\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton:pressed {\n"
                                 "    border: 4px solid #090;\n"
                                 "    border-radius: 5px;\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton:checked {\n"
                                 "    background-color: #006300;\n"
                                 "    border-color: #090;\n"
                                 "}\n"
                                 "")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        # Layout that holds sidebar and main content
        self.main_layout = QHBoxLayout(self.centralwidget)

        # Sidebar (left side)
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setSpacing(20)

        # Main content (right side, your existing content)
        self.verticalLayout = QVBoxLayout()


        
        # --- Top-right Button Layout: Theme, Background, Accent ---

        # Create layout
        self.top_button_layout = QHBoxLayout()
        self.top_button_layout.setSpacing(10)
        self.top_button_layout.setAlignment(Qt.AlignRight)
        self.verticalLayout.addLayout(self.top_button_layout)

        # Shared style for all 3 buttons
        shared_button_style = """
            QPushButton {
                padding: 8px;
                min-width: 150px;
                background-color: #333;
                color: white;
                border: 2px solid gray;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555;
                border-color: gray;
            }
        """

        # Theme toggle button (same variable name, no icon for now)
        # Theme toggle button (styled identically)
        self.btn_theme_toggle = QPushButton("Dark/Light Mode", self.centralwidget)
        self.btn_theme_toggle.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_theme_toggle.setStyleSheet(shared_button_style)
        self.btn_theme_toggle.setMinimumWidth(150)
        self.top_button_layout.addWidget(self.btn_theme_toggle)

        # Accent color button (same style)
        self.btn_accent_color = QPushButton("Accent Color", self.centralwidget)
        self.btn_accent_color.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_accent_color.setStyleSheet(shared_button_style)
        self.btn_accent_color.setMinimumWidth(150)
        self.top_button_layout.addWidget(self.btn_accent_color)
        
        self.wrapper_frame = QFrame()
        self.wrapper_frame.setStyleSheet("background-color: #1e1e1e; border-radius: 8px;")
        self.wrapper_layout = QVBoxLayout(self.wrapper_frame)
        self.wrapper_layout.setContentsMargins(8, 8, 8, 8)
        self.wrapper_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Sidebar Buttons
        

        # Generator
        self.btn_sidebar_generator = QPushButton()
        self.sidebar_layout.addStretch()
        self.btn_sidebar_generator.setIcon(QIcon("icons/lock.png"))
        self.btn_sidebar_generator.setToolTip("Password Generator")
        self.btn_sidebar_generator.setAccessibleName("Password Generator")
        self.btn_sidebar_generator.setIconSize(QSize(32, 32))
        #self.btn_sidebar_generator.setStyleSheet("QPushButton { border: none; }")
        self.btn_sidebar_generator.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:checked {
                background-color: #333333;
                border-left: 4px solid #00ff00;
            }
        """)
        self.btn_sidebar_generator.setCheckable(True)

        self.sidebar_layout.addWidget(self.btn_sidebar_generator)

        # History
        self.btn_sidebar_history = QPushButton()
        self.btn_sidebar_history.setIcon(QIcon("icons/history.png"))
        self.btn_sidebar_history.setToolTip("Password History")
        self.btn_sidebar_history.setAccessibleName("Password History")
        self.btn_sidebar_history.setIconSize(QSize(32, 32))
        self.btn_sidebar_history.setStyleSheet("QPushButton { border: none; }")
        self.sidebar_layout.addWidget(self.btn_sidebar_history)

        # Expiring Passwords
        self.btn_sidebar_expiry = QPushButton()
        self.btn_sidebar_expiry.setIcon(QIcon("icons/alert.png"))
        self.btn_sidebar_expiry.setToolTip("Expiring Passwords")
        self.btn_sidebar_expiry.setAccessibleName("Expiring Passwords")
        self.btn_sidebar_expiry.setIconSize(QSize(32, 32))
        self.btn_sidebar_expiry.setStyleSheet("QPushButton { border: none; }")
        self.sidebar_layout.addWidget(self.btn_sidebar_expiry)

        # Export
        self.btn_sidebar_export = QPushButton()
        self.btn_sidebar_export.setIcon(QIcon("icons/export.png"))
        self.btn_sidebar_export.setToolTip("Export Passwords")
        self.btn_sidebar_export.setAccessibleName("Export Passwords")
        self.btn_sidebar_export.setIconSize(QSize(32, 32))
        self.btn_sidebar_export.setStyleSheet("QPushButton { border: none; }")
        self.sidebar_layout.addWidget(self.btn_sidebar_export)

        self.sidebar_layout.addStretch()  # Push buttons to top

        self.verticalLayout.setObjectName(u"verticalLayout")
        
        self.icon_lock = QPushButton(self.centralwidget)
        self.icon_lock.setObjectName(u"icon_lock")
        self.icon_lock.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.icon_lock.sizePolicy().hasHeightForWidth())
        self.icon_lock.setSizePolicy(sizePolicy)
        self.icon_lock.setStyleSheet(u"border: none;\n"
                                     "")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons/lock.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.icon_lock.setIcon(icon1)
        self.icon_lock.setIconSize(QSize(100, 100))

        self.verticalLayout.addWidget(self.icon_lock)

        self.layout_password = QHBoxLayout()
        self.layout_password.setObjectName(u"layout_password")
        self.frame_password = QFrame(self.centralwidget)
        self.frame_password.setObjectName(u"frame_password")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_password.sizePolicy().hasHeightForWidth())
        self.frame_password.setSizePolicy(sizePolicy1)
        self.frame_password.setStyleSheet(u"QFrame {\n"
                                          "    border: 2px solid gray;\n"
                                          "    border-radius: 5px;\n"
                                          "    margin-right: 0;\n"
                                          "}\n"
                                          "\n"
                                          "QFrame:hover {\n"
                                          "    border-color: #090;\n"
                                          "}\n"
                                          "")
        self.frame_password.setFrameShape(QFrame.StyledPanel)
        self.frame_password.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_password)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.line_password = QLineEdit(self.frame_password)
        self.line_password.setObjectName(u"line_password")
        self.line_password.setStyleSheet(u"QLineEdit {\n"
                                         "    border: none;\n"
                                         "    margin: 0;\n"
                                         "    font-size: 20pt;\n"
                                         "}\n"
                                         "")
        
        
        
        
        
        self.line_password.setToolTip(
            "🔑 Password Tips:\n"
            "- Use at least 12 characters\n"
            "- Include uppercase and lowercase letters\n"
            "- Use numbers and special characters (!@#$%^&*)\n"
            "- Avoid dictionary words and personal info"
        )

        self.horizontalLayout_10.addWidget(self.line_password)

        self.btn_visibility = QPushButton(self.frame_password)
        self.btn_visibility.setObjectName(u"btn_visibility")
        self.btn_visibility.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_visibility.setStyleSheet(u"QPushButton {\n"
                                          "    border: none;\n"
                                          "    margin: 0;\n"
                                          "    background-color: transparent;\n"
                                          "}\n"
                                          "")
        icon2 = QIcon()
        icon2.addFile(u":/icons/icons/invisible.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon2.addFile(u":/icons/icons/visible.svg", QSize(), QIcon.Normal, QIcon.On)
        self.btn_visibility.setIcon(icon2)
        self.btn_visibility.setIconSize(QSize(30, 30))
        self.btn_visibility.setCheckable(True)
        self.btn_visibility.setChecked(True)

        self.horizontalLayout_10.addWidget(self.btn_visibility)

        self.layout_password.addWidget(self.frame_password)

        self.btn_refresh = QPushButton(self.centralwidget)
        self.btn_refresh.setObjectName(u"btn_refresh")
        self.btn_refresh.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_refresh.setStyleSheet(u"QPushButton {\n"
                                       "    margin-right: 0;\n"
                                       "    margin-left: 0;\n"
                                       "}\n"
                                       "")
        icon3 = QIcon()
        icon3.addFile(u":/icons/icons/refresh.svg", QSize(), QIcon.Normal, QIcon.On)
        self.btn_refresh.setIcon(icon3)
        self.btn_refresh.setIconSize(QSize(52, 52))

        self.layout_password.addWidget(self.btn_refresh)

        self.btn_copy = QPushButton(self.centralwidget)
        self.btn_copy.setObjectName(u"btn_copy")
        self.btn_copy.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_copy.setStyleSheet(u"QPushButton {\n"
                                    "    margin-right: 0px;\n"
                                    "    margin-left: 0;\n"
                                    "}\n"
                                    "")
        icon4 = QIcon()
        icon4.addFile(u":/icons/icons/copy.svg", QSize(), QIcon.Normal, QIcon.On)
        self.btn_copy.setIcon(icon4)
        self.btn_copy.setIconSize(QSize(52, 52))

        self.layout_password.addWidget(self.btn_copy)

        self.verticalLayout.addLayout(self.layout_password)

        # Add sidebar + main content to the main layout
        self.main_layout.addLayout(self.sidebar_layout)     # Sidebar (left)
        self.main_layout.addLayout(self.verticalLayout)     # Main content (right)


        self.layout_info = QHBoxLayout()  # Initialize layout_info

        # Ensure `self.layout_strength_meter` is initialized only ONCE
        if not hasattr(self, "layout_strength_meter"):
            self.layout_strength_meter = QHBoxLayout()
            self.layout_info.addLayout(self.layout_strength_meter)  # Add only once

        # Create 8 bars for the strength meter (instead of 4)
        self.strength_bars = []  # Store bars in a list

        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        for i in range(8):  # Create 8 bars
            bar = QFrame(self.centralwidget)
            bar.setSizePolicy(size_policy)
            bar.setStyleSheet("QFrame { background-color: gray; border: 1px solid black; min-height: 20px; }")
            bar.setToolTip("🛡 Password Strength: Hover to see details")  # Assign tooltip to each bar
            self.layout_strength_meter.addWidget(bar)
            self.strength_bars.append(bar)

        self.layout_strength_meter.setContentsMargins(0, 0, 0, 0)
        self.layout_strength_meter.setSpacing(5)  # Adjust spacing between bars

        self.label_strength = QLabel(self.centralwidget)
        self.label_strength.setObjectName("label_strength")
        self.label_strength.setAlignment(Qt.AlignCenter)
        
        self.label_strength.setToolTip(
            "🛡 Password Strength Guide:\n"
            "- Weak: Needs more characters & variety\n"
            "- Medium: Decent, but could be better\n"
            "- Strong: Well-balanced, consider adding more length\n"
            "- Very Strong: Great! Your password is highly secure"
        )

        self.layout_info.addWidget(self.label_strength)

        self.label_entropy = QLabel(self.centralwidget)
        self.label_entropy.setObjectName(u"label_entropy")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy2.setHeightForWidth(self.label_entropy.sizePolicy().hasHeightForWidth())
        self.label_entropy.setSizePolicy(sizePolicy2)
        self.label_entropy.setAlignment(Qt.AlignCenter)

        self.layout_info.addWidget(self.label_entropy)

        self.verticalLayout.addLayout(self.layout_info)
        
        self.layout_length = QHBoxLayout()
        self.layout_length.setObjectName(u"layout_length")
        self.slider_length = QSlider(self.centralwidget)
        self.slider_length.setObjectName(u"slider_length")
        self.slider_length.setMinimum(8)  # Ensure the minimum length is 8
        self.slider_length.setCursor(QCursor(Qt.PointingHandCursor))
        self.slider_length.setStyleSheet(u"QSlider::groove:horizontal {\n"
                                         "    background-color: transparent;\n"
                                         "    height: 5px;\n"
                                         "}\n"
                                         "\n"
                                         "QSlider::sub-page:horizontal {\n"
                                         "    background-color: #090;\n"
                                         "}\n"
                                         "\n"
                                         "QSlider::add-page:horizontal {\n"
                                         "    background-color: gray;\n"
                                         "}\n"
                                         "\n"
                                         "QSlider::handle:horizontal {\n"
                                         "    background-color: white;\n"
                                         "    width: 22px;\n"
                                         "    border-radius: 10px;\n"
                                         "    margin-top: -8px;\n"
                                         "    margin-bottom: -8px;\n"
                                         "}\n"
                                         "")
        self.slider_length.setMaximum(100)
        self.slider_length.setValue(12)
        self.slider_length.setOrientation(Qt.Horizontal)

        self.layout_length.addWidget(self.slider_length)

        self.spinbox_length = QSpinBox(self.centralwidget)
        self.spinbox_length.setObjectName(u"spinbox_length")
        self.spinbox_length.setStyleSheet(u"QSpinBox {\n"
                                          "    border: 2px solid gray;\n"
                                          "    border-radius: 5px;\n"
                                          "    background: transparent;\n"
                                          "    padding: 2px;\n"
                                          "}\n"
                                          "\n"
                                          "QSpinBox:hover {\n"
                                          "    border-color: #009900;\n"
                                          "}\n"
                                          "")
        self.spinbox_length.setAlignment(Qt.AlignCenter)
        self.spinbox_length.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.spinbox_length.setMaximum(100)
        self.spinbox_length.setValue(12)

        self.layout_length.addWidget(self.spinbox_length)

        self.verticalLayout.addLayout(self.layout_length)

        self.layout_characters = QHBoxLayout()
        self.layout_characters.setObjectName(u"layout_characters")
        self.btn_lower = QPushButton(self.centralwidget)
        self.btn_lower.setObjectName(u"btn_lower")
        self.btn_lower.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_lower.setCheckable(True)
        self.btn_lower.setChecked(True)

        self.layout_characters.addWidget(self.btn_lower)

        self.btn_upper = QPushButton(self.centralwidget)
        self.btn_upper.setObjectName(u"btn_upper")
        self.btn_upper.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_upper.setCheckable(True)
        self.btn_upper.setChecked(True)

        self.layout_characters.addWidget(self.btn_upper)

        self.btn_digits = QPushButton(self.centralwidget)
        self.btn_digits.setObjectName(u"btn_digits")
        self.btn_digits.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_digits.setCheckable(True)
        self.btn_digits.setChecked(True)

        self.layout_characters.addWidget(self.btn_digits)

        self.btn_special = QPushButton(self.centralwidget)
        self.btn_special.setObjectName(u"btn_special")
        self.btn_special.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_special.setCheckable(True)
        self.btn_special.setChecked(True)

        self.layout_characters.addWidget(self.btn_special)

        self.verticalLayout.addLayout(self.layout_characters)

        MainWindow.setCentralWidget(self.centralwidget)
        self.btn_history = QPushButton(self.centralwidget)
        self.btn_history.setObjectName("btn_history")
        self.btn_history.setText("View History")

        self.btn_history.setToolTip("View previously generated passwords")

        self.btn_history = QPushButton(MainWindow)

        # Add the button to the vertical layout
        #self.verticalLayout.addWidget(self.btn_history)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
        # New button to trigger authentication popup
        # Create a horizontal layout for the two buttons
        buttonLayout = QHBoxLayout()

        # Create a horizontal layout for the two buttons
        self.buttons_layout = QHBoxLayout()

        # Add the Reset Password button
        self.forgotPasswordButton = QPushButton("Reset Password", self.centralwidget)
        self.forgotPasswordButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.forgotPasswordButton.setStyleSheet(
            "QPushButton {"
            "   padding: 10px;"
            "   background-color: #444;"
            "   border: 2px solid gray;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   border-color: #900;"
            "   background-color: #666;"
            "}"
        )
        self.buttons_layout.addWidget(self.forgotPasswordButton)

        # Add Save Password Button
        self.btn_save = QPushButton("Save Password", self.centralwidget)
        self.btn_save.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_save.setStyleSheet(
            "QPushButton {"
            "   padding: 10px;"
            "   background-color: #333;"
            "   border: 2px solid gray;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   border-color: #090;"
            "   background-color: #555;"
            "}"
        )
        self.buttons_layout.addWidget(self.btn_save)

        # Add the horizontal button layout to the existing vertical layout
        self.verticalLayout.addLayout(self.buttons_layout)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)


        # Create a container frame for the category section with proper styling
        self.category_frame = QFrame(self.centralwidget)
        self.category_frame.setObjectName("category_frame")
        self.category_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 15px;
                margin-bottom: 15px;
            }
        """)

        # Create a horizontal layout for the category section
        self.category_layout = QHBoxLayout(self.category_frame)
        self.category_layout.setContentsMargins(15, 15, 15, 15)
        self.category_layout.setSpacing(10)

        # Create the category label with improved styling
        self.category_label = QLabel("Category:", self.centralwidget)
        self.category_label.setObjectName("category_label")
        self.category_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                margin: 0;
                padding: 0;
                color: #00cc00;
            }
        """)
        self.category_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Create the category dropdown with improved styling
        self.category_dropdown = QComboBox(self.centralwidget)
        self.category_dropdown.setObjectName("category_dropdown")
        self.category_dropdown.addItems(["Work", "Personal", "Banking"])
        self.category_dropdown.setCurrentIndex(0)  # Default to "Work"
        self.category_dropdown.setStyleSheet("""
            QComboBox {
                border: 2px solid gray;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: #333;
                color: white;
                font-size: 14pt;
                min-width: 150px;
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
            QComboBox::down-arrow {
                width: 16px;
                height: 16px;
                image: url(icons/dropdown.png);  /* You may need to add this icon */
            }
            QComboBox QAbstractItemView {
                background-color: #333;
                color: white;
                selection-background-color: #006300;
                selection-color: white;
                border: 1px solid gray;
                border-radius: 0px;
            }
        """)

        # Add the label and dropdown to the category layout
        self.category_layout.addWidget(self.category_label, 1)  # 1 is the stretch factor
        self.category_layout.addWidget(self.category_dropdown, 2)  # 2 is the stretch factor for more space

        # Add the category frame to the main vertical layout
        self.verticalLayout.addWidget(self.category_frame)

        # Set alignment to center the category frame
        self.verticalLayout.setAlignment(self.category_frame, Qt.AlignCenter)

        # Add Export Password Button
        self.btn_export = QPushButton("Export Passwords", self.centralwidget)
        self.btn_export.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_export.setStyleSheet(
            "QPushButton {"
            "   padding: 10px;"
            "   background-color: #333;"
            "   border: 2px solid gray;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   border-color: #090;"
            "   background-color: #555;"
            "}"
        )
       # self.verticalLayout.addWidget(self.btn_export)

        # Create the "View History" button
        self.btn_history.setObjectName("btn_history")
        self.btn_history.setText("View History")
        self.btn_history.setToolTip("View previously generated passwords")
        self.btn_history.setStyleSheet(
            "QPushButton {"
            "   padding: 10px;"
            "   background-color: #333;"
            "   border: 2px solid gray;"
            "   margin: 0px;"
            "   padding: 0px;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   border-color: #090;"
            "   background-color: #555;"
            "}"
        )
       
       # self.verticalLayout.addWidget(self.btn_history)  # Add to UI
        
        self.btn_expiry_check = QPushButton("View Expiring Passwords", self.centralwidget)
        self.btn_expiry_check.setObjectName("btn_expiry_check")
        self.btn_expiry_check.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)


        self.btn_history.clicked.connect(MainWindow.show_password_history)    # Connect history button
        # self.authButton.clicked.connect(MainWindow.handle_authentication)
        
        self.expiry_alert = QLabel(self.centralwidget)
        self.expiry_alert.setObjectName("expiry_alert")
        self.expiry_alert.setStyleSheet("QLabel { background-color: #ffcc00; color: black; padding: 5px; font-size: 14px; }")
        self.expiry_alert.setAlignment(Qt.AlignCenter)
        self.expiry_alert.setText("")
        self.expiry_alert.hide()  # Hide initially
        

        self.verticalLayout.addWidget(self.expiry_alert)
        
        self.btn_expiry_check = QPushButton(self.centralwidget)
        self.btn_expiry_check.setObjectName(u"btn_expiry_check")
        self.btn_expiry_check.setText("View Expiring Passwords")
        self.btn_expiry_check.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_expiry_check.setStyleSheet(
            "QPushButton {"
            "   padding: 10px;"
            "   background-color: #333;"
            "   border: 2px solid gray;"
            "   border-radius: 5px;"
            "}"
            "QPushButton:hover {"
            "   border-color: #900;"
            "   background-color: #666;"
            "}"
        )
        #self.verticalLayout.addWidget(self.btn_expiry_check)
            
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Password Generator", None))
        self.icon_lock.setText("")
        self.btn_visibility.setText("")
        self.btn_refresh.setText("")
        self.btn_refresh.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+R", None))
        self.btn_copy.setText("")
        self.btn_copy.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
        self.label_strength.setText(QCoreApplication.translate("MainWindow", "", None))
        self.label_entropy.setText("")
        self.btn_lower.setText(QCoreApplication.translate("MainWindow", u"a-z", None))
        self.btn_upper.setText(QCoreApplication.translate("MainWindow", u"A-Z", None))
        self.btn_digits.setText(QCoreApplication.translate("MainWindow", u"0-9", None))
        self.btn_special.setText(QCoreApplication.translate("MainWindow", u"#$%", None))
        self.btn_history.setText(QCoreApplication.translate("MainWindow", u"View History", None))
        
        self.btn_visibility.setChecked(True)
        self.line_password.setEchoMode(QLineEdit.Normal)
    
    def add_theme_toggle_button(self):
        # Create theme toggle button
        self.btn_theme_toggle = QPushButton(self.centralwidget)
        self.btn_theme_toggle.setObjectName("btn_theme_toggle")
        self.btn_theme_toggle.setToolTip("Toggle Dark/Light Theme")
        self.btn_theme_toggle.setAccessibleName("Toggle Theme")
        self.btn_theme_toggle.setCheckable(True)
        self.btn_theme_toggle.setChecked(True)  # Default to dark mode
        
        # Setup icons for dark/light mode
        self.icon_dark = QIcon("src/icons/moon.svg")
        self.icon_light = QIcon("src/icons/sun.svg")
        
        # Set initial icon
        self.btn_theme_toggle.setIcon(self.icon_dark)
        self.btn_theme_toggle.setIconSize(QSize(20, 20))
        
        # Style the button to be circular
        self.btn_theme_toggle.setStyleSheet("""
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
        
        # Create a layout for the toggle button and place it in the top-right corner
        self.theme_toggle_layout = QHBoxLayout()
        self.theme_toggle_layout.addStretch()  # Push the button to the right
        self.theme_toggle_layout.addWidget(self.btn_theme_toggle)
        
        # Insert this layout at the top of the main vertical layout
        self.verticalLayout.insertLayout(0, self.theme_toggle_layout)

def handle_authentication(self):
    if self.authenticate_user():
        QMessageBox.information(self, "Success", "Authentication successful!")
        
def __init__(self, parent=None, db=None):
    super().__init__(parent)
    self.db = db

    # Create UI elements
    self.setWindowTitle("Password History")
    self.setGeometry(100, 100, 800, 400)
    
    # Search bar for filtering history
    self.search_bar = QLineEdit(self)
    self.search_bar.setPlaceholderText("Search passwords...")
    self.search_bar.textChanged.connect(self.on_search_text_changed)

    # Set up table
    self.password_history_table = QTableWidget(self)
    self.password_history_table.setColumnCount(4)
    self.password_history_table.setHorizontalHeaderLabels(['ID', 'Password', 'Created At', 'Description'])
    self.password_history_table.setSortingEnabled(True)

    # Layout
    layout = QVBoxLayout(self)
    layout.addWidget(self.search_bar)
    layout.addWidget(self.password_history_table)

    # Load password history
    self.load_password_history()
    
def on_search_text_changed(self):
    """Filter the password history based on search input."""
    search_term = self.search_bar.text()  # Get the text from the search bar
    self.load_password_history(search_term)  # Reload password history based on the search term

def load_password_history(self, search_term=""):
    """Load and filter the password history based on the search term."""
    
    # Get filtered history based on search term
    history_data = self.db.get_password_history(search_term=search_term)
    
    if not history_data:
        QMessageBox.information(self, "No Data", "No passwords found.")
        return

    # Update the table with the search results
    self.password_history_table.setRowCount(len(history_data))

    for row_idx, (password_id, encrypted_password, created_at, description) in enumerate(history_data):
        self.password_history_table.setItem(row_idx, 0, QTableWidgetItem(str(password_id)))
        self.password_history_table.setItem(row_idx, 1, QTableWidgetItem(encrypted_password))
        self.password_history_table.setItem(row_idx, 2, QTableWidgetItem(str(created_at)))
        self.password_history_table.setItem(row_idx, 3, QTableWidgetItem(description))

    # Adjust column and row sizes for readability
    self.password_history_table.resizeColumnsToContents()
    self.password_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    self.password_history_table.verticalHeader().setDefaultSectionSize(40)  # Adjust vertical size for better view

    # Adding tooltips for each column
    self.password_history_table.setToolTip("Click to sort or filter the history.")

    def update_password_history(self):
        """Update the password history table based on the search term."""
        search_term = self.search_field.text()  # Get the current search term
        self.load_password_history(search_term=search_term)  # Refresh the table with filtered data

    def load_password_history(self, search_term=""):
        """Load password history from the database and display it in the table."""

        # Request the master password
        master_password, ok = QInputDialog.getText(self, "Master Password", "Enter master password:", QLineEdit.Password)
        if not ok or not self.db.verify_master_password(master_password):
            QMessageBox.warning(self, "Access Denied", "Incorrect master password.")
            return

        # Get the password history from the database (with or without search term)
        history_data = self.db.get_password_history(search_term=search_term)

        # Initialize the table for the history
        self.password_history_table.setRowCount(len(history_data))  # Set the number of rows based on the data

        # Fill the table with password history data
        for i, (password_id, encrypted_password, created_at) in enumerate(history_data):
            # Decrypt the password before displaying it
            decrypted_password = self.db.decrypt_password(encrypted_password)

            # Populate the table
            self.password_history_table.setItem(i, 0, QTableWidgetItem(str(password_id)))
            self.password_history_table.setItem(i, 1, QTableWidgetItem(decrypted_password))
            self.password_history_table.setItem(i, 2, QTableWidgetItem(created_at))

        # Adjust column width to fit text and improve header visibility
        self.password_history_table.resizeColumnsToContents()
        self.password_history_table.horizontalHeader().setMinimumSectionSize(50)
        self.password_history_table.verticalHeader().setDefaultSectionSize(40)  # Adjust vertical header size


    def update_table(self):
        """Update the table with filtered data based on search input."""
        search_term = self.search_bar.text()
        self.load_password_history(search_term)