import sqlite3
from cryptography.fernet import Fernet
import os
from datetime import datetime, timedelta

# Load encryption key
key_file = "encryption.key"
if not os.path.exists(key_file):
    print("Encryption key not found!")
    exit(1)

with open(key_file, "rb") as file:
    key = file.read()

fernet = Fernet(key)

# Connect to database
db_path = "passwords.db"
if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch passwords
cursor.execute("""
    SELECT id, website, username, encrypted_password, expiry_date
    FROM stored_passwords
    WHERE id NOT IN (SELECT password_id FROM dismissed_alerts)
""")
rows = cursor.fetchall()

if not rows:
    print("No passwords found in the database.")
    exit(0)

self.passwordTable.setColumnCount(5)  # Adjust columns
self.passwordTable.setHorizontalHeaderLabels(["Website", "Username", "Expiry Date", "Status", "Dismiss"])

# Make headers bold and readable
header = self.passwordTable.horizontalHeader()
header.setSectionResizeMode(QHeaderView.Stretch)
header.setStyleSheet("""
    QHeaderView::section {
        font-weight: bold;
        background-color: #f0f0f0;
        padding: 6px;
        border-bottom: 2px solid #ccc;
    }
""")

# Adjust row height
self.passwordTable.verticalHeader().setDefaultSectionSize(35)
self.passwordTable.verticalHeader().setVisible(False)  # Hide row numbers


print("\nStored Passwords:\n" + "=" * 50)
for password_id, website, username, encrypted_password, expiry_date in rows:
    decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
    expiry_status = get_expiry_status(expiry_date)
    
    print(f"Website: {website}\nUsername: {username}\nExpiry: {expiry_date} - {expiry_status}\nDecrypted: {decrypted_password}\n" + "-" * 50)

    # Determine expiry status
    expiry_date_obj = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')
    if expiry_date_obj < datetime.now():
        status = " Expired"
    elif expiry_date_obj < datetime.now() + timedelta(days=7):
        status = " Expiring Soon"
    else:
        status = " Active"

    # Populate UI Table
    rowPosition = self.passwordTable.rowCount()
    self.passwordTable.insertRow(rowPosition)
    self.passwordTable.setItem(rowPosition, 0, QTableWidgetItem(website))
    self.passwordTable.setItem(rowPosition, 1, QTableWidgetItem(username))
    self.passwordTable.setItem(rowPosition, 2, QTableWidgetItem(expiry_date))
    self.passwordTable.setItem(rowPosition, 3, QTableWidgetItem(expiry_status))
    
    # Add Dismiss Button
    dismiss_button = QPushButton("Dismiss")
    dismiss_button.clicked.connect(lambda _, pid=password_id: self.dismiss_expiry_alert(pid))
    self.passwordTable.setCellWidget(rowPosition, 4, dismiss_button)


def dismiss_expiry_alert(self, password_id):
    """Hide an expiry alert and store dismissal in the database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO dismissed_alerts (password_id) VALUES (?)", (password_id,))
        conn.commit()
    
    # Refresh table after dismissal
    self.load_passwords()


if not data:
    print("No passwords found in the database.")
    exit(0)

# Print encrypted and decrypted passwords
print("\nStored Passwords:\n" + "=" * 50)
for website, username, encrypted_password in data:
    decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
    print(f"Website: {website}\nUsername: {username}\nEncrypted: {encrypted_password}\nDecrypted: {decrypted_password}\n" + "-" * 50)

# Close DB connection
conn.close()
