from password_generator.src.database import DatabaseManager


self.db = DatabaseManager("passwords.db")
self.check_expiry_notifications()
self.ui.btn_expiry_check.clicked.connect(self.show_expiring_passwords)

