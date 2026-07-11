"""
services/validation.py
Centralized input validation used throughout the application.
Keeping all format-validation rules in one class avoids duplication
and makes the rules (password strength, email format, etc.) easy to
find and change in one place. This class never touches the database -
duplicate checks (unique email/username/phone) are performed by the
service that owns that data (Registration, Profile, AdminManagement).
"""

import re


class Validation:
    """Static validation helpers for user input."""

    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    PHONE_PATTERN = re.compile(r"^[0-9]{10}$")
    VALID_ROLES = ["Buyer", "Seller", "Donor", "Exchange User"]
    SPECIAL_CHAR_PATTERN = re.compile(r"[!@#$%^&*()\-_=+\[\]{}|;:'\",.<>/?`~\\]")

    @staticmethod
    def validate_not_empty(value: str) -> bool:
        """Returns True if the value is a non-blank string."""
        return bool(value and value.strip())

    @classmethod
    def validate_name(cls, name: str) -> bool:
        """Name cannot be empty and must be at least 2 characters."""
        return cls.validate_not_empty(name) and len(name.strip()) >= 2

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Checks that the email matches a standard email format."""
        return bool(email) and bool(cls.EMAIL_PATTERN.match(email.strip()))

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """Phone number must be exactly 10 digits."""
        return bool(phone) and bool(cls.PHONE_PATTERN.match(phone.strip()))

    @classmethod
    def validate_role(cls, role: str) -> bool:
        """Role must be one of the four allowed roles."""
        return role in cls.VALID_ROLES

    @classmethod
    def validate_password_strength(cls, password: str):
        """
        Returns (True, "") if the password satisfies every strength rule,
        otherwise returns (False, "reason for failure").
        Rules: minimum 8 characters, at least one uppercase letter, one
        lowercase letter, one number, and one special character.
        """
        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter."
        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one number."
        if not cls.SPECIAL_CHAR_PATTERN.search(password):
            return False, "Password must contain at least one special character."
        return True, ""

    @staticmethod
    def validate_menu_choice(choice: str, valid_choices) -> bool:
        """Checks that a menu choice is one of the accepted values."""
        return choice in valid_choices
