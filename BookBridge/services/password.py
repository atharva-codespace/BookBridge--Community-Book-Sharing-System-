"""
services/password.py
Handles password changes and the Forgot Password recovery flow
(Feature 6) for the currently logged-in (or, for recovery, not-yet
logged-in) user.
"""

from datetime import datetime
from database.db import Database
from models.user import User
from services.validation import Validation
from utils.hashing import Hashing


class PasswordManagement:
    """Password change and recovery operations."""

    def __init__(self, session=None):
        self.session = session
        self.db = Database.get_instance()

    # ==================== CHANGE PASSWORD ====================
    def change_password(self):
        """Requires the user to already be logged in. Verifies the current
        password, checks the new password's strength, then hashes and stores it."""
        user = User.get_by_id(self.session.user_id)
        if not user:
            print("User not found.")
            return

        current_password = input("Current Password: ").strip()
        if not Hashing.verify_password(current_password, user.password_hash):
            print("Incorrect current password. Password change cancelled.")
            return

        new_password = input("New Password: ").strip()
        valid, reason = Validation.validate_password_strength(new_password)
        if not valid:
            print(reason)
            return

        confirm_password = input("Confirm New Password: ").strip()
        if new_password != confirm_password:
            print("Passwords do not match. Password change cancelled.")
            return

        new_hash = Hashing.hash_password(new_password)
        User.update_password(user.user_id, new_hash)
        self._log_password_change(user.user_id)
        print("Password changed successfully.")

    def _log_password_change(self, user_id):
        self.db.execute_query(
            "INSERT INTO Password_Change_History (User_ID, Changed_Date) VALUES (%s, %s)",
            (user_id, datetime.now()), commit=True,
        )

    # ==================== FORGOT PASSWORD ====================
    def forgot_password(self):
        """
        Recovers access using the registered email plus a security-question
        answer set at registration time (Feature 6: 'Ask security verification').
        """
        print("\n--- FORGOT PASSWORD ---")
        email = input("Enter your registered Email: ").strip()
        user = User.get_by_email(email)
        if not user:
            print("No account found with that email.")
            return

        if not user.security_question:
            print("No security question is set for this account. Please contact support.")
            return

        print(f"Security Question: {user.security_question}")
        answer = input("Your Answer: ").strip()

        if not Hashing.verify_password(answer.lower(), user.security_answer_hash):
            print("Incorrect answer. Password reset denied.")
            return

        new_password = input("Enter New Password: ").strip()
        valid, reason = Validation.validate_password_strength(new_password)
        if not valid:
            print(reason)
            return

        confirm_password = input("Confirm New Password: ").strip()
        if new_password != confirm_password:
            print("Passwords do not match. Password reset cancelled.")
            return

        new_hash = Hashing.hash_password(new_password)
        User.update_password(user.user_id, new_hash)
        self._log_password_change(user.user_id)
        print("Password reset successfully. You may now log in.")
