class TooltipContent:
    """Repository of tooltip content organized by context"""
    
    # Password Generator tooltips
    PASSWORD_GENERATOR = {
        "length_slider": "Adjust the password length.\nLonger passwords are more secure.",
        "lowercase": "Include lowercase letters (a-z).\nRecommended for balanced security.",
        "uppercase": "Include uppercase letters (A-Z).\nImproves password strength significantly.",
        "digits": "Include numbers (0-9).\nAdds complexity to your password.",
        "special": "Include special characters (!@#$%^&*).\nGives maximum security.",
        "refresh": "Generate a new password with current settings.",
        "copy": "Copy the password to your clipboard.",
        "visibility": "Toggle password visibility.\nAutomatically hides after inactivity.",
        "save": "Save this password with a site name and username.",
        "password_field": "Your generated password.\nHover to reveal, mouse away to hide.",
    }
    
    # Password Strength tooltips
    PASSWORD_STRENGTH = {
        "strength_meter": "Password strength indicator:\n"
                         "■□□□ - Weak: Easily cracked\n"
                         "■■□□ - Medium: Moderate protection\n"
                         "■■■□ - Strong: Good protection\n"
                         "■■■■ - Very Strong: Excellent protection",
        "entropy": "Entropy measures password randomness.\n"
                 "Higher values (70+) indicate better security.",
    }
    
    # Category tooltips
    CATEGORIES = {
        "dropdown": "Organize passwords by category for easier management.",
        "work": "For professional accounts and services.",
        "personal": "For personal accounts and services.",
        "banking": "For financial accounts and services.",
    }
    
    # Navigation tooltips
    NAVIGATION = {
        "sidebar_generator": "Password Generator: Create new secure passwords",
        "sidebar_history": "Password History: View previously generated passwords",
        "sidebar_expiry": "Expiring Passwords: Check passwords that need updating",
        "sidebar_export": "Export: Save your passwords to a file",
    }
    