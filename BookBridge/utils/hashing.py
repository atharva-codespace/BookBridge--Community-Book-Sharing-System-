"""
utils/hashing.py
Provides secure password hashing and verification using bcrypt.
Plain-text passwords are NEVER stored anywhere in this application -
only the bcrypt hash is written to the database.
"""

import bcrypt


class Hashing:
    """Utility class for hashing and verifying passwords with bcrypt."""

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hashes a plain-text password and returns it as a UTF-8 string."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Checks a plain-text password against a stored bcrypt hash."""
        if not plain_password or not hashed_password:
            return False
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except (ValueError, TypeError):
            # Raised if the stored hash is malformed / not a valid bcrypt hash
            return False
