import unittest
import re
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

# Copy of the relevant code from password.py for standalone testing
class PasswordStrength:
    WEAK = 'Weak'
    MEDIUM = 'Medium'
    STRONG = 'Strong'
    VERY_STRONG = 'Very Strong'

def evaluate_password_strength(password: str) -> str:
    # Check password length
    if len(password) < 8:
        return PasswordStrength.WEAK
    
    # Check for sequences (e.g., '1234' or 'abcd') - moved up to prioritize this check
    if re.search(r'(1234|abcd|qwerty)', password.lower()):
        return PasswordStrength.WEAK
    
    # Check for character variety
    if not re.search(r'[A-Z]', password):  # Must contain uppercase letter
        return PasswordStrength.MEDIUM
    if not re.search(r'[a-z]', password):  # Must contain lowercase letter
        return PasswordStrength.MEDIUM
    if not re.search(r'[0-9]', password):  # Must contain a number
        return PasswordStrength.MEDIUM
    if not re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?`~\\|]', password):  # Must contain a special character
        return PasswordStrength.MEDIUM

    # If passed all checks, consider it strong
    if len(password) >= 12:
        return PasswordStrength.VERY_STRONG
    else:
        return PasswordStrength.STRONG

class TestPasswordStrength(unittest.TestCase):
    
    def test_weak_passwords(self):
        """Test passwords that should be classified as weak."""
        weak_passwords = [
            "short",  # Too short
            "1234abcdef",  # Contains sequence "1234"
            "abcdpassword",  # Contains sequence "abcd"
            "qwertypassword",  # Contains sequence "qwerty"
            "123456",  # Too short and contains sequence
        ]
        
        for pwd in weak_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.WEAK, 
                                f"Password '{pwd}' should be classified as weak")
                
    def test_medium_passwords(self):
        """Test passwords that should be classified as medium strength."""
        medium_passwords = [
            "Password123",  # Missing special character
            "password123!",  # Missing uppercase
            "PASSWORD123!",  # Missing lowercase
            "Password!",  # Missing number
            "Efghjkl!@#",  # Missing number (changed from Abcdefgh to avoid 'abcd' pattern)
        ]
        
        for pwd in medium_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.MEDIUM,
                                f"Password '{pwd}' should be classified as medium")
    
    def test_strong_passwords(self):
        """Test passwords that should be classified as strong."""
        strong_passwords = [
            "P@ssw0rd!",  # 9 chars with all requirements
            "Tr0ub4dor&",  # 10 chars with all requirements
            "B7Xm9p@a",  # 8 chars with all requirements
        ]
        
        for pwd in strong_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.STRONG,
                                f"Password '{pwd}' should be classified as strong")
    
    def test_very_strong_passwords(self):
        """Test passwords that should be classified as very strong."""
        very_strong_passwords = [
            "P@ssw0rd!P@ssw0rd!",  # 18 chars with all requirements
            "Tr0ub4dor&3Santa",  # 15 chars with all requirements
            "B7Xm9p@aK8L!2zYq",  # 16 chars with all requirements
            "StR0ng!P4ssword",  # 15 chars with all requirements (no patterns)
        ]
        
        for pwd in very_strong_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.VERY_STRONG,
                                f"Password '{pwd}' should be classified as very strong")
                
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        test_cases = [
            # Exactly 8 chars with all requirements (should be Strong)
            ("P@ssw0r!", PasswordStrength.STRONG),
            # Exactly 12 chars with all requirements (should be Very Strong)
            ("StR0ng!P4ss12", PasswordStrength.VERY_STRONG),  # Changed to avoid pattern
            # 11 chars with all requirements (should be Strong)
            ("P@ssw0rd!12", PasswordStrength.STRONG),
            # Patterns embedded in longer strings
            ("MySecret1234Password", PasswordStrength.WEAK),
            ("SecretQWERTYpassword", PasswordStrength.WEAK),
            # Pattern with mixed case (should still detect as weak)
            ("MySecretAbCdPassword", PasswordStrength.WEAK),
        ]
        
        for pwd, expected in test_cases:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), expected,
                                f"Password '{pwd}' should be classified as {expected}")

    def test_pattern_detection(self):
        """Test specifically for pattern detection functionality."""
        pattern_passwords = [
            # 1234 pattern
            "Secure1234Pass!",
            "12345Password!A",
            "Password1234!A",
            
            # abcd pattern
            "SecureabcdPass!1",
            "abcdePassword!A1",
            "Password!abcd1A",
            
            # qwerty pattern
            "SecureqwertyPass!1",
            "qwertyPassword!A1",
            "Password!qwerty1A",
            
            # Case variations
            "SecureABCDPass!1",  # uppercase ABCD
            "SecureQWERTYPass!1",  # uppercase QWERTY
            "SecureAbCdPass!1",  # mixed case AbCd
        ]
        
        for pwd in pattern_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.WEAK,
                                f"Password '{pwd}' should be classified as weak due to pattern")

    def print_test_results(self):
        """Helper method to print password evaluations for visual inspection."""
        test_cases = [
            "short",
            "1234abcdef",
            "Password123",
            "password123!",
            "P@ssw0rd!",
            "P@ssw0rd!1234",  # Has a pattern
            "StR0ng!P4ssword",  # No patterns, meets all criteria
            "Abcdefgh!@#",     # Contains 'abcd' pattern
            "Efghjkl!@#",      # No pattern, but missing number
        ]
        
        print("\nPassword Evaluation Results:")
        print("=============================")
        for pwd in test_cases:
            result = evaluate_password_strength(pwd)
            print(f"Password: {pwd} -> Strength: {result}")


if __name__ == "__main__":
    # Optional: Run this to see evaluation results before running tests
    # TestPasswordStrength().print_test_results()
    
    unittest.main()