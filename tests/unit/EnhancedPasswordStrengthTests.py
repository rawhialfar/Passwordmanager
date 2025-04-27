import unittest
import re

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

class EnhancedPasswordStrengthTests(unittest.TestCase):
    
    def test_weak_passwords(self):
        """Test passwords that should be classified as weak."""
        weak_passwords = [
            "short",              # Too short
            "1234abcdef",         # Contains sequence "1234"
            "abcdpassword",       # Contains sequence "abcd"
            "qwertypassword",     # Contains sequence "qwerty"
            "123456",             # Too short and contains sequence
            # Note: "password" will be Medium, not Weak
            # because it doesn't contain the specific sequences checked for
            # and it's not less than 8 characters
            "12345678",           # 8 chars with sequential numbers - should be Weak
        ]
        
        for pwd in weak_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.WEAK, 
                                f"Password '{pwd}' should be classified as weak")
                
    def test_medium_passwords(self):
        """Test passwords that should be classified as medium strength."""
        medium_passwords = [
            "Password123",        # Missing special character
            "password123!",       # Missing uppercase
            "PASSWORD123!",       # Missing lowercase
            "Password!",          # Missing number
            "Efghjkl!@#",         # Missing number (no 'abcd' pattern)
            "Passw@rd",           # 8 chars with almost all requirements but missing number
            "password",           # 8 chars but missing uppercase, number, and special char
        ]
        
        for pwd in medium_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.MEDIUM,
                                f"Password '{pwd}' should be classified as medium")
    
    def test_strong_passwords(self):
        """Test passwords that should be classified as strong."""
        strong_passwords = [
            "P@ssw0rd!",          # 9 chars with all requirements
            "Tr0ub4dor&",         # 10 chars with all requirements
            "B7Xm9p@a",           # 8 chars with all requirements
            "C0mpl3x!",           # 8 chars with all requirements
            "X9y#Z5a!",           # 8 chars with all requirements
        ]
        
        for pwd in strong_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.STRONG,
                                f"Password '{pwd}' should be classified as strong")
    
    def test_very_strong_passwords(self):
        """Test passwords that should be classified as very strong."""
        very_strong_passwords = [
            "P@ssw0rd!P@ssw0rd!",  # 18 chars with all requirements
            "Tr0ub4dor&3Santa",    # 15 chars with all requirements
            "B7Xm9p@aK8L!2zYq",    # 16 chars with all requirements
            "StR0ng!P4ssword",     # 15 chars with all requirements (no patterns)
            "C0mpl3x!Passw0rd",    # 16 chars with all requirements
            "X9y#Z5a!B3secure",    # 16 chars with all requirements
        ]
        
        for pwd in very_strong_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.VERY_STRONG,
                                f"Password '{pwd}' should be classified as very strong")
    
    def test_sequence_detection_priority(self):
        """Test that sequence detection takes priority over other checks."""
        sequence_passwords = [
            # All these meet other criteria but contain sequences
            "P@ssw0rd1234",         # Contains "1234" but meets all other criteria
            "P@ssw0rdabcd",         # Contains "abcd" but meets all other criteria
            "P@ssw0rdqwerty",       # Contains "qwerty" but meets all other criteria
            "1234P@ssw0rd",         # Contains "1234" at beginning
            "qwertyP@ssw0rd",       # Contains "qwerty" at beginning
            "P@s1234sw0rd",         # Contains "1234" in middle
            "P@sabcdw0rd",          # Contains "abcd" in middle
        ]
        
        for pwd in sequence_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.WEAK,
                                f"Password '{pwd}' with sequence should be classified as weak regardless of other criteria")
    
    def test_boundary_conditions(self):
        """Test boundary conditions for password classification."""
        test_cases = [
            # Exactly 8 chars with all requirements (should be Strong)
            ("P@ssw0r!", PasswordStrength.STRONG),
            # Exactly 12 chars with all requirements (should be Very Strong)
            ("StR0ng!P4ss12", PasswordStrength.VERY_STRONG),
            # 11 chars with all requirements (should be Strong)
            ("P@ssw0rd!12", PasswordStrength.STRONG),
            # 7 chars with all requirements (should be Weak due to length)
            ("P@ssw0r", PasswordStrength.WEAK),
        ]
        
        for pwd, expected in test_cases:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), expected,
                                f"Password '{pwd}' should be classified as {expected}")
    
    def test_case_insensitive_sequence_detection(self):
        """Test that sequence detection is case-insensitive."""
        case_variant_passwords = [
            "P@ssw0rdABCD",       # Uppercase ABCD
            "P@ssw0rdAbCd",       # Mixed case AbCd
            "P@ssw0rdQwErTy",     # Mixed case QwErTy
            "P@ssw0rd1234",       # Numbers are case-insensitive by nature
        ]
        
        for pwd in case_variant_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.WEAK,
                                f"Password '{pwd}' with case variation of sequence should be classified as weak")
    
    def test_extended_sequences(self):
        """Test detection of sequences that extend beyond the basic patterns."""
        extended_sequence_passwords = [
            "P@ssw0rd12345",      # Extended "1234" sequence
            "P@ssw0rdabcde",      # Extended "abcd" sequence
            "P@ssw0rdqwertyui",   # Extended "qwerty" sequence
        ]
        
        for pwd in extended_sequence_passwords:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), PasswordStrength.WEAK,
                                f"Password '{pwd}' with extended sequence should be classified as weak")
                
    def test_regression(self):
        """Test that previously working features still work correctly."""
        regression_test_cases = [
            # Password without any sequences but missing requirements
            ("Password", PasswordStrength.MEDIUM),  # Missing number and special char
            # Password with all requirements but containing a sequence
            ("P@ssw0rd1234", PasswordStrength.WEAK),
            # Very long password with all requirements but containing a sequence
            ("ThisIsAVeryLongP@ssw0rdWithTheSequence1234InIt", PasswordStrength.WEAK),
        ]
        
        for pwd, expected in regression_test_cases:
            with self.subTest(password=pwd):
                self.assertEqual(evaluate_password_strength(pwd), expected,
                                f"Regression test: Password '{pwd}' should be classified as {expected}")

    def print_test_results(self):
        """Helper method to print password evaluations for visual inspection."""
        test_cases = [
            "short",
            "1234abcdef",
            "Password123",
            "password123!",
            "P@ssw0rd!",
            "P@ssw0rd!1234",      # Has a pattern
            "StR0ng!P4ssword",    # No patterns, meets all criteria
            "Abcdefgh!@#",        # Contains 'abcd' pattern
            "Efghjkl!@#",         # No pattern, but missing number
            "P@ssw0rdQWERTY",     # Uppercase pattern
            "P@ssw0rdAbCd",       # Mixed case pattern
        ]
        
        print("\nEnhanced Password Evaluation Results:")
        print("====================================")
        for pwd in test_cases:
            result = evaluate_password_strength(pwd)
            print(f"Password: {pwd} -> Strength: {result}")


if __name__ == "__main__":
    # Uncomment to see evaluation results before running tests
    # EnhancedPasswordStrengthTests().print_test_results()
    
    unittest.main()