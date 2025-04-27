import pytest
import bcrypt
import sqlite3
from cryptography.fernet import Fernet
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

class PasswordManager:
    def __init__(self, db_path: str, key: bytes):
        self.db_path = db_path
        self.fernet = Fernet(key)

    def set_master_password(self, password):
        """Hash and store master password securely with bcrypt and encrypt the hash using Fernet"""
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        encrypted_password = self.fernet.encrypt(hashed_password.encode()).decode()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO master_auth (hashed_password) VALUES (?);", (encrypted_password,))
            conn.commit()

    def get_stored_password(self):
        """Retrieve the stored encrypted password from the database (for testing)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hashed_password FROM master_auth;")
            result = cursor.fetchone()
        return result[0] if result else None

@pytest.fixture
def password_manager(tmp_path):
    """Fixture to create a PasswordManager with a temporary database and encryption key."""
    db_path = tmp_path / "test_db.sqlite"
    key = Fernet.generate_key()
    manager = PasswordManager(str(db_path), key)

    # Create table structure
    with sqlite3.connect(manager.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE master_auth (hashed_password TEXT);")
        conn.commit()

    return manager

def test_double_encryption(password_manager):
    """Test that the password is first hashed with bcrypt and then encrypted with Fernet."""
    test_password = "SecurePassword123!"
    password_manager.set_master_password(test_password)
    
    stored_password = password_manager.get_stored_password()
    
    # Ensure the stored password is encrypted
    assert stored_password is not None
    assert isinstance(stored_password, str)
    
    # Decrypt the stored password using Fernet
    decrypted_hash = password_manager.fernet.decrypt(stored_password.encode()).decode()

    # Ensure the decrypted value is a bcrypt hash
    assert decrypted_hash.startswith("$2b$")  # Bcrypt hashes start with "$2b$"
    assert bcrypt.checkpw(test_password.encode(), decrypted_hash.encode())  # Verify the hash is correct
