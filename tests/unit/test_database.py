import pytest
import os
import sqlite3

import sys
from datetime import datetime, timedelta

from unittest.mock import patch


#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))


from database import DatabaseManager



#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))



TEST_DB_PATH = "test_passwords.db"
TEST_KEY_PATH = "test_encryption.key"

@pytest.fixture
def db():
    """Fixture to create a test database instance with a consistent encryption key."""
    
    # Ensure a consistent encryption key for testing
    if not os.path.exists(TEST_KEY_PATH):
        key = DatabaseManager().load_or_generate_key()  # Generate key if not exists
        with open(TEST_KEY_PATH, "wb") as file:
            file.write(key)
    else:
        with open(TEST_KEY_PATH, "rb") as file:
            key = file.read()

    # Use the same key across tests
    db_manager = DatabaseManager(db_path=TEST_DB_PATH)
    db_manager.key = key  # Override the key
    db_manager.fernet = db_manager.fernet.__class__(db_manager.key)  

    # Reset the database before each test
    with sqlite3.connect(TEST_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS stored_passwords;")
        cursor.execute("DROP TABLE IF EXISTS password_history;")
        cursor.execute("DROP TABLE IF EXISTS password_categories;")
        cursor.execute("DROP TABLE IF EXISTS master_auth;")
        cursor.execute("DROP TABLE IF EXISTS master_email;")
        cursor.execute("DROP TABLE IF EXISTS verification_codes;")
        conn.commit()
    
    # Initialize the database with tables
    db_manager.initialize_database()

    yield db_manager  

    
    del db_manager
    try:
        # Close all database connections before removing the file

        with sqlite3.connect(TEST_DB_PATH) as conn:
            pass  
        os.remove(TEST_DB_PATH)
        os.remove(TEST_KEY_PATH)
    except PermissionError:
        print(f"Failed to remove {TEST_DB_PATH}, retrying.")
        try:
            with sqlite3.connect(TEST_DB_PATH) as conn:
                pass  
            os.remove(TEST_DB_PATH)
            os.remove(TEST_KEY_PATH)
        except Exception as e:
            print(f"Final removal failed: {e}")




def test_tables_exist(db):
    """Test if all required tables exist and have correct columns."""
    expected_tables = {
        "master_auth": ["id", "hashed_password"],
        "master_email": ["id", "email"],
        "stored_passwords": ["id", "website", "username", "encrypted_password", "category", "created_at", "expiry_date"],
        "password_history": ["id", "encrypted_password", "created_at"],
        "password_categories": ["id", "category_name"],
        "verification_codes": ["email", "code", "created_at"]
    }

    with sqlite3.connect(TEST_DB_PATH) as conn:
        cursor = conn.cursor()

        for table, expected_columns in expected_tables.items():
            cursor.execute(f"PRAGMA table_info({table});")
            actual_columns = {row[1] for row in cursor.fetchall()}
            assert set(expected_columns) == actual_columns, f"Table {table} is missing columns: {set(expected_columns) - actual_columns}"




def test_password_expiry_date(db):
    """Test if passwords expire correctly after 90 days."""
    expired_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')  # Should be expired
    valid_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')  # Should be valid

    # Save test passwords
    db.save_password("expired.com", "old_user", "password1", "Work", expired_date)
    db.save_password("valid.com", "new_user", "password2", "Personal", valid_date)

    # Check expiration
    assert db.check_password_expiry(1) == True, "Expired password not detected!"
    assert db.check_password_expiry(2) == False, "Valid password marked as expired!"


def test_check_expiry_notifications(db):
    """Test if expiry notification logic correctly identifies multiple expiring passwords."""
    # Insert passwords with different expiry dates
    current_date = datetime.now()
    expiring_soon_1 = (current_date + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')  # Should be flagged
    expiring_soon_2 = (current_date + timedelta(days=6)).strftime('%Y-%m-%d %H:%M:%S')  # Should be flagged
    not_expiring = (current_date + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')  # Should not be flagged

    # Save test passwords
    db.save_password("expiring1.com", "user1", "password1", "Work", expiring_soon_1)
    db.save_password("expiring2.com", "user2", "password2", "Work", expiring_soon_2)
    db.save_password("safe.com", "user3", "password3", "Personal", not_expiring)

    # Query database for passwords expiring in the next 7 days
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM stored_passwords WHERE expiry_date < datetime('now', '+7 days')")
        expiring_count = cursor.fetchone()[0]

    # Expecting 2 passwords to be flagged
    assert expiring_count == 2, f"Expected 2 expiring passwords, but found {expiring_count}"

# This will verify database connection

def test_database_connection(db):
    """Test if the database initializes and connects properly."""
    try:
        with sqlite3.connect(TEST_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            assert tables, "No tables found in the database"
    except Exception as e:
        pytest.fail(f"Database connection test failed: {e}")




# This will verify password encryption & decryption

def test_password_encryption_decryption(db):
    """Test password encryption and decryption for edge cases."""
    
    # Case 1: Empty password
    original_password = ""
    encrypted_password = db.encrypt_password(original_password)
    decrypted_password = db.decrypt_password(encrypted_password)
    assert original_password == decrypted_password, "Encryption/Decryption failed for empty password!"
    
    # Case 2: Very long password
    original_password = "A" * 1000  # Very long password
    encrypted_password = db.encrypt_password(original_password)
    decrypted_password = db.decrypt_password(encrypted_password)
    assert original_password == decrypted_password, "Encryption/Decryption failed for long password!"
    
    # Case 3: Special characters
    original_password = "!@#$%^&*()_+-=<>?"
    encrypted_password = db.encrypt_password(original_password)
    decrypted_password = db.decrypt_password(encrypted_password)
    assert original_password == decrypted_password, "Encryption/Decryption failed for special characters!"

# This will store & retrieve password

def test_store_and_retrieve_password(db):
    """Test if a password can be stored and retrieved correctly."""
    db.save_password("example.com", "user123", "MySecretPass", "Work")
    passwords = db.get_all_passwords()

    assert len(passwords) == 1, "Password not stored correctly"
    assert passwords[0][1] == "example.com", "Website mismatch"
    assert passwords[0][2] == "user123", "Username mismatch"
    assert passwords[0][3] == "MySecretPass", "Password mismatch"
    assert passwords[0][4] == "Work", "Category mismatch"

# This will verify master password hashing

def test_master_password_hashing(db):
    """Test if the master password is correctly hashed and verified."""
    test_password = "MasterPass123"
    db.set_master_password(test_password)

    assert db.master_password_exists(), "Master password not set"
    assert db.verify_master_password(test_password), "Master password verification failed"
    assert not db.verify_master_password("WrongPass"), "Master password verification should fail for incorrect password"

