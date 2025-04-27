from enum import IntEnum
from math import log2
import secrets
import re


class StrengthToEntropy(IntEnum):
    Pathetic = 0
    Weak = 30
    Good = 50
    Strong = 70
    Excellent = 120


class PasswordStrength:
    WEAK = 'Weak'
    MEDIUM = 'Medium'
    STRONG = 'Strong'
    VERY_STRONG = 'Very Strong'


# Dictionary of common weak passwords for detection
COMMON_PASSWORDS = [
    "password", "123456", "qwerty", "admin",
    
    "123456789", "12345678", "1234567", "12345", "54321", "111111", "000000",
]


def create_new(length: int, characters: str) -> str:
    return ''.join(secrets.choice(characters) for _ in range(length))


def get_entropy(length: int, character_number: int) -> float:
    try:
        entropy = length * log2(character_number)
    except ValueError:
        return 0.0

    return round(entropy, 2)


def contains_dictionary_word(password: str, ignore_length_threshold: int = 25) -> bool:
    # If password is very long, ignore dictionary check
    if len(password) >= ignore_length_threshold:
        return False
        
    password_lower = password.lower()
    
    # Check exact matches first
    if password_lower in COMMON_PASSWORDS:
        return True
    
    # Check if any dictionary word is contained within the password
    for word in COMMON_PASSWORDS:
        if len(word) >= 4 and word in password_lower:  # Only consider words of length 4+
            return True
            
    # Check for common patterns with numbers substituted for letters (l33t speak)
    leetspeak_patterns = {
        'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7', 'l': '1'
    }
    
    transformed_password = password_lower
    for char, replacement in leetspeak_patterns.items():
        transformed_password = transformed_password.replace(replacement, char)
    
    # Check transformed password against dictionary
    for word in COMMON_PASSWORDS:
        if len(word) >= 4 and word in transformed_password:
            return True
            
    return False


def is_strong_password(password: str) -> bool:
    """Check if a password meets strength requirements."""
    # For very long passwords, we only check character variety, not dictionary words
    if len(password) >= 25:
        return (
            len(password) >= 8 and
            any(char.isupper() for char in password) and
            any(char.islower() for char in password) and
            any(char.isdigit() for char in password) and
            any(char in "!@#$%^&*()\-_=+\[\]{};:\'\",.<>/?`~\\|" for char in password)
        )
    
    # For shorter passwords, also check for dictionary words
    if contains_dictionary_word(password):
        return False
        
    return (
        len(password) >= 8 and
        any(char.isupper() for char in password) and
        any(char.islower() for char in password) and
        any(char.isdigit() for char in password) and
        any(char in "!@#$%^&*()\-_=+\[\]{};:\'\",.<>/?`~\\|" for char in password)
    )


def evaluate_password_strength(password: str) -> str:
    # Check password length first
    if len(password) < 8:
        return PasswordStrength.WEAK
    
    # Very long passwords get special treatment
    if len(password) >= 25:
        # Even for long passwords, we still need character variety
        missing_classes = 0
        if not re.search(r'[A-Z]', password): missing_classes += 1
        if not re.search(r'[a-z]', password): missing_classes += 1
        if not re.search(r'[0-9]', password): missing_classes += 1
        if not re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?`~\\|]', password): missing_classes += 1
        
        # With 0-1 missing character classes, it's very strong
        # With 2 missing classes, it's strong
        # With 3+ missing classes, it's medium
        if missing_classes <= 1:
            return PasswordStrength.VERY_STRONG
        elif missing_classes == 2:
            return PasswordStrength.STRONG
        else:
            return PasswordStrength.MEDIUM
    
    # For shorter passwords, check for dictionary words
    if contains_dictionary_word(password):
        return PasswordStrength.WEAK
    
    # Check for character variety
    if not re.search(r'[A-Z]', password):
        return PasswordStrength.MEDIUM
    if not re.search(r'[a-z]', password):
        return PasswordStrength.MEDIUM
    if not re.search(r'[0-9]', password):
        return PasswordStrength.MEDIUM
    if not re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?`~\\|]', password):
        return PasswordStrength.MEDIUM

    # Check for sequential patterns
    if re.search(r'(1234|abcd|qwerty)', password.lower()):
        return PasswordStrength.WEAK

    # Final strength assessment
    if len(password) >= 12:
        return PasswordStrength.VERY_STRONG
    else:
        return PasswordStrength.STRONG