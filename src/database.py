import sqlite3
import os
from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime, timedelta
import bcrypt

class DatabaseManager:
    def __init__(self, db_path="passwords.db"):
        self.db_path = db_path
        self.key = self.load_or_generate_key()
        self.fernet = Fernet(self.key)
        self.initialize_database()

    def get_connection(self):
        """Return a database connection"""
        return sqlite3.connect(self.db_path)
    
    def load_or_generate_key(self):
        """Load or generate encryption key for database"""
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as file:
                return file.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as file:
                file.write(key)
            return key

    def initialize_database(self):
        """Ensures all required tables exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS master_auth (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hashed_password TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS master_email (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL
                );
            
                CREATE TABLE IF NOT EXISTS stored_passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website TEXT NOT NULL,
                    username TEXT NOT NULL,
                    encrypted_password TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expiry_date TIMESTAMP NOT NULL
                );

                CREATE TABLE IF NOT EXISTS dismissed_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password_id INTEGER NOT NULL,
                    dismissed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (password_id) REFERENCES stored_passwords(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS password_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    encrypted_password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS password_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name TEXT UNIQUE NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS verification_codes (
                    email TEXT PRIMARY KEY,
                    code TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

            # Ensure default categories exist
            cursor.execute("SELECT COUNT(*) FROM password_categories;")
            if cursor.fetchone()[0] == 0:
                cursor.executemany("INSERT INTO password_categories (category_name) VALUES (?);",
                                [('Work',), ('Personal',), ('Banking',)])
                conn.commit()
                print("Default categories added.")

            # Check if the expiry_date column exists and add it if necessary
            cursor.execute("PRAGMA table_info(stored_passwords);")
            columns = [column[1] for column in cursor.fetchall()]
            if "expiry_date" not in columns:
                cursor.execute("""
                    ALTER TABLE stored_passwords
                    ADD COLUMN expiry_date TIMESTAMP;
                """)
                conn.commit()
                print("expiry_date column added to stored_passwords table.")

            # Clear dismissed alerts
            cursor.execute("DELETE FROM dismissed_alerts;")
            conn.commit()

    def set_master_email(self, email):
        """Store the master email in a separate table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO master_email (email) VALUES (?);", (email,))
            conn.commit()
            
    def get_master_email(self):
        """Retrieve the stored master email"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM master_email LIMIT 1;")
            email = cursor.fetchone()
            return email[0] if email else None

    def master_email_exists(self):
        """Check if a master email exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM master_email;")
            return cursor.fetchone()[0] > 0

    def encrypt_password(self, password):
        """Encrypts password before storing"""
        return self.fernet.encrypt(password.encode()).decode()
        
    def decrypt_password(self, encrypted_password):
        """Decrypts password for retrieval"""
        try:
            return self.fernet.decrypt(encrypted_password.encode()).decode()
        except (InvalidToken, binascii.Error):
            return None

    def check_password_expiry(self, password_id: int) -> bool:
        """Check if a password has expired"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT expiry_date FROM stored_passwords WHERE id = ?", (password_id,))
            result = cursor.fetchone()

            if result:
                expiry_date = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
                if expiry_date < datetime.now():
                    return True  # Password has expired
            return False  # Password is still valid

    def save_password(self, website, username, password, category="Other", expiry_date=None):
        """Insert encrypted password into the database with the selected category and expiry date."""
        
        if expiry_date is None:  # Ensure expiry_date is always set
            expiry_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')

        encrypted_password = self.encrypt_password(password)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stored_passwords (website, username, encrypted_password, category, expiry_date)
                VALUES (?, ?, ?, ?, ?);
            """, (website, username, encrypted_password, category, expiry_date))
            conn.commit()

    def get_all_passwords(self):
        """Fetch and decrypt stored passwords"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, website, username, encrypted_password, category FROM stored_passwords;")
            data = cursor.fetchall()
            return [(row[0], row[1], row[2], self.decrypt_password(row[3]), row[4]) for row in data]

    def save_password_to_history(self, password):
        """Store encrypted password history"""
        encrypted_password = self.encrypt_password(password)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO password_history (encrypted_password) VALUES (?);", (encrypted_password,))
            conn.commit()

    def get_password_history(self, limit=None, search_term=None):
        """Retrieve password history from the database with optional search functionality."""
        query = "SELECT id, encrypted_password, created_at FROM password_history"
        params = []

        # Apply search filter if a search term is provided
        if search_term:
            query += " WHERE encrypted_password LIKE ?"
            params.append(f"%{search_term}%")

        query += " ORDER BY created_at DESC"  # Sort by creation date in descending order

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        # Execute the query and fetch the results
        return self.execute_query(query, params)

    def add_category(self, category_name):
        """Add a new password category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO password_categories (category_name) VALUES (?);", (category_name,))
            conn.commit()

    def get_categories(self):
        """Retrieve all password categories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category_name FROM password_categories;")
            return [row[0] for row in cursor.fetchall()]

    def master_password_exists(self):
        """Check if a master password is already set"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM master_auth;")
            return cursor.fetchone()[0] > 0

    def set_master_password(self, password):
        """Hash and store master password securely with bcrypt and encrypt the hash using Fernet"""
        # Hash password with bcrypt
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # Encrypt the hashed password using Fernet
        encrypted_password = self.fernet.encrypt(hashed_password.encode()).decode()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO master_auth (hashed_password) VALUES (?);", (encrypted_password,))
            conn.commit()

    def verify_master_password(self, password):
        """Verify if the entered master password is correct"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hashed_password FROM master_auth LIMIT 1;")
            stored_password = cursor.fetchone()
            
            if stored_password:
                try:
                    # Decrypt the stored hash first
                    decrypted_hashed_password = self.fernet.decrypt(stored_password[0].encode()).decode()
                    
                    # Verify against bcrypt
                    return bcrypt.checkpw(password.encode(), decrypted_hashed_password.encode())
                except:
                    return False
            return False

    def reset_master_password(self, email, entered_code):
        """Reset the master password only if the verification code is correct"""
        if not self.verify_code(email, entered_code):
            print("Reset failed. Invalid or expired verification code.")
            return False

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM master_auth;")
            conn.commit()
        print("Master password has been reset. Please set a new one.")
        return True

    def verify_code(self, email, entered_code):
        """Verify if the entered code matches the stored code"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code FROM verification_codes WHERE email = ?", (email,))
            stored_code = cursor.fetchone()
            
            if stored_code and stored_code[0] == entered_code:
                return True
            return False

    def export_passwords(self):
        """Fetch password records with only decrypted passwords"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, website, username, encrypted_password, category, created_at 
                FROM stored_passwords
                ORDER BY website;
            """)
            data = cursor.fetchall()
            
            # Create rows with decrypted password instead of encrypted
            result = []
            for row in data:
                decrypted_password = self.decrypt_password(row[3])  # Decrypt the password
                # Create new row without encrypted password
                new_row = (row[0], row[1], row[2], decrypted_password, row[4], row[5])
                result.append(new_row)
                
            return result
    
    def dismiss_expiry_alert(self, password_id):
        """Mark an expiry alert as dismissed in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO dismissed_alerts (password_id) VALUES (?)", (password_id,))
            conn.commit()

    def get_active_expiring_passwords(self):
        """Retrieve passwords expiring soon, excluding dismissed ones, but allow window to open."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT sp.id, sp.website, sp.username, sp.expiry_date
                FROM stored_passwords sp
                LEFT JOIN dismissed_alerts da ON sp.id = da.password_id
                WHERE sp.expiry_date BETWEEN datetime('now') AND datetime('now', '+7 days')
                AND (da.password_id IS NULL OR da.password_id = '')  -- Ensure only dismissed passwords are hidden
            """)
            results = cursor.fetchall()

        return results  # Still return results even if empty

    def reset_dismissed_alerts(self):
        """Reset all dismissed alerts (for debugging or user request)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE stored_passwords SET dismissed = 0")
            conn.commit()
        
    def execute_query(self, query, params=()):
        """Executes a parameterized query and returns the result."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def set_tooltip_preference(self, enabled):
        """Save user preference for tooltips"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """)
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences (key, value)
                VALUES ('tooltips_enabled', ?);
            """, (str(int(enabled)),))  # Store as 1 or 0
            conn.commit()

    def get_tooltip_preference(self):
        """Retrieve user preference for tooltips"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """)
            cursor.execute("SELECT value FROM user_preferences WHERE key = 'tooltips_enabled';")
            result = cursor.fetchone()
            
            if result:
                return result[0] == '1'  # Convert '1' to True, '0' to False
            return True  # Default to enabled if no preference found


# Ensure the database initializes properly
db = DatabaseManager()
