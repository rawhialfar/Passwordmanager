import json
import os
import hashlib
import random
import smtplib
from email.message import EmailMessage
import datetime
import sqlite3
from database import DatabaseManager
class auth:
    def __init__(self, db_path="passwords.db"):
        self.db_path = db_path
    def generate_verification_code(self, email):
        """Generate a 6-digit code, store it in the database, and send it via email"""
        code = str(random.randint(100000, 999999))  # 6-digit code
        expiration_time = (datetime.datetime.utcnow() + datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO verification_codes (email, code, created_at) VALUES (?, ?, ?);",
                        (email, code, expiration_time))
            conn.commit()

        self.send_email(email, code)
        print(f"Verification code sent to {email}. It expires in 5 minutes.")
        return True

    def send_email(self, recipient_email, code):
        print("Sending email...")
        # print("Code:", code)
        """Send the verification code via email"""
        sender_email = "passgen4250@gmail.com"  # Use your email
        sender_password = "groj spdt nppp fypx"  # Use an App Password

        msg = EmailMessage()
        msg["Subject"] = "Your Password Reset Code"
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg.set_content(f"Your password reset verification code is: {code}\nThis code expires in 5 minutes.")

        try:
            smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtpserver.ehlo()
            smtpserver.login(sender_email, sender_password)

            sent_from = sender_email
            sent_to = recipient_email  
            smtpserver.sendmail(sent_from, sent_to, msg.as_string())

            smtpserver.close()
        except Exception as e:
            print("Error sending email:", e)

    def verify_code(self, email, entered_code):
        """Verify the entered reset code"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code, expires_at FROM verification_codes WHERE email = ?;", (email,))
            data = cursor.fetchone()

            if not data:
                print("No verification code found. Please request a new one.")
                return False

            stored_code, expires_at = data
            current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            if entered_code == stored_code and current_time < expires_at:
                print("Code verified successfully!")
                cursor.execute("DELETE FROM verification_codes WHERE email = ?;", (email,))  # Remove used code
                conn.commit()
                return True
            else:
                print("Invalid or expired code.")
                return False
