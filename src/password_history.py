from database import DatabaseManager
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QDialog, QHeaderView, QMessageBox, QApplication

# Initialize the database manager
db = DatabaseManager()

def save_password_history(password: str):
    """Save a newly generated password to history in the database."""
    db.save_password_to_history(password)

def get_recent_passwords():
    """Retrieve the last few stored passwords from the database."""
    return db.get_password_history()

class PasswordHistoryDialog(QDialog):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db  # Save the db parameter
        self.setWindowTitle("Password History")

        # Initialize the UI
        self.setup_ui()
        self.load_password_history()

        # Call filter_history after UI setup and data loading
        self.filter_history()  # This will call populate_table() with all data on init

    def setup_ui(self):
        """Initialize the UI elements of the dialog."""
        self.setGeometry(200, 100, 600, 400)
        
        # Create table widget for password history
        self.history_table = QTableWidget(self)
        self.history_table.setColumnCount(2)  # Only keep Password and Timestamp columns
        self.history_table.setHorizontalHeaderLabels(["Password", "Timestamp"])

        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # Adjust header and row sizing
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.horizontalHeader().setFixedHeight(40)
        self.history_table.setRowHeight(0, 35)

        # Set up search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search History...")
        self.search_bar.textChanged.connect(self.filter_history)
        self.search_bar.textChanged.connect(self.clear_search)

        # Set up layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.history_table)
        
    def clear_search(self):
        """Clear the search and repopulate the table with all data."""
        if not self.search_bar.text():
            self.filter_history()  # Call filter_history to repopulate with all data

    def load_password_history(self):
        """Load password history from the database."""
        try:
            # Fetch password history with additional details from stored_passwords
            query = """
                SELECT ph.id, sp.website, sp.username, sp.expiry_date, ph.encrypted_password
                FROM password_history ph
                LEFT JOIN stored_passwords sp ON ph.id = sp.id
                ORDER BY ph.created_at DESC
            """
            history_data = self.db.execute_query(query)
            self.populate_table(history_data)  # Populate table immediately after loading data
        except Exception as e:
            print(f"Error loading password history: {e}")
            QMessageBox.warning(self, "Error", "An error occurred while loading the password history.")

    def filter_history(self):
        """Filter password history based on the search query."""
        search_term = self.search_bar.text().lower()
        # Fetch all passwords from the database
        all_history = self.db.get_password_history()

        # Decrypt passwords and filter based on search term
        filtered_data = []
        for item in all_history:
            password_id, encrypted_password, timestamp = item
            decrypted_password = self.db.decrypt_password(encrypted_password)  # Decrypt password
            if decrypted_password and search_term in decrypted_password.lower():  # Case insensitive search
                filtered_data.append((password_id, decrypted_password, timestamp))

        # Clear the table and populate with filtered data
        self.history_table.setRowCount(0)  # Clear the table first
        self.populate_table(filtered_data)
    
    def populate_table(self, history_data):
        """Populate the history table with the provided password history data."""
        self.history_table.setRowCount(0)  # Clear the table first

        # Check what the data structure of `history_data` is
        for row_idx, data in enumerate(history_data):
            if len(data) == 3:  # password_id, decrypted_password, timestamp
                password_id, decrypted_password, timestamp = data
            elif len(data) == 4:  # Adding an extra value (like actions)
                password_id, decrypted_password, timestamp, action = data
            else:
                continue  # Skip rows that don't match the expected format

            self.history_table.insertRow(row_idx)
            self.history_table.setItem(row_idx, 0, QTableWidgetItem(decrypted_password))  # Password column
            self.history_table.setItem(row_idx, 1, QTableWidgetItem(timestamp))  # Timestamp column

            # Set action button (if any)
            if len(data) == 4:  # Action column
                action_button = QPushButton("Action", self)
                self.history_table.setCellWidget(row_idx, 2, action_button)

        QApplication.processEvents()  # Ensure the UI refreshes
