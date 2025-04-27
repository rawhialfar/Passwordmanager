import bcrypt
from cryptography.fernet import Fernet
import sqlite3
import re

# Generate Fernet key for encryption
key = Fernet.generate_key()
fernet = Fernet(key)

# SQLite database connection
conn = sqlite3.connect('passwords.db')
cursor = conn.cursor()

# Create table for storing passwords
cursor.execute('''
CREATE TABLE IF NOT EXISTS stored_passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT,
    username TEXT,
    encrypted_password TEXT,
    category TEXT,
    created_at TIMESTAMP,
    expiry_date TIMESTAMP
)
''')

# Password complexity check
def is_strong_password(password: str) -> bool:
    return (
        len(password) >= 8 and
        any(char.isupper() for char in password) and
        any(char.islower() for char in password) and
        any(char.isdigit() for char in password) and
        any(char in "!@#$%^&*()\-_=+\[\]{};:\'\",.<>/?`~\\|" for char in password)
    )

# Encrypt password using bcrypt and Fernet
def encrypt_password(password: str):
    if is_strong_password(password):
        # Encrypt password with bcrypt
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        encrypted_password = fernet.encrypt(hashed_password)
        return encrypted_password
    else:
        return None  # Return None for weak passwords

# Store password in SQLite database
def store_password(website: str, username: str, password: str, category: str = 'General'):
    encrypted_password = encrypt_password(password)
    if encrypted_password:
        cursor.execute('''
        INSERT INTO stored_passwords (website, username, encrypted_password, category, created_at, expiry_date)
        VALUES (?, ?, ?, ?, datetime('now'), datetime('now', '+90 days'))
        ''', (website, username, encrypted_password, category))
        conn.commit()
        print("Password stored successfully!")
    else:
        print("Weak password. Please use a stronger password.")

# Test the script with a sample password
store_password('1234', 'user123', 'SecurePass123!')
