"""
services/password.py
Handles password changes and the Forgot Password recovery flow
(Feature 6) for the currently logged-in (or, for recovery, not-yet
logged-in) user.

Presentation note: only the printed messages/prompts have been upgraded to
utils/ui.py styling. Verification order and password-strength rules are
unchanged.
"""

from datetime import datetime
from database.db import Database
from models.user import User
from services.validation import Validation
from utils.hashing import Hashing
from utils import ui


class PasswordManagement:
    """Password change and recovery operations."""

    def __init__(self, session=None):
        self.session = session
        self.db = Database.get_instance()

    # ==================== CHANGE PASSWORD ====================
    def change_password(self):
        """Requires the user to already be logged in. Verifies the current
        password, checks the new password's strength, then hashes and stores it."""
        ui.section_header("CHANGE PASSWORD", icon="🔑")
        user = User.get_by_id(self.session.user_id)
        if not user:
            ui.error("User not found.")
            return

        current_password = ui.prompt("Current Password", password=True).strip()
        if not Hashing.verify_password(current_password, user.password_hash):
            ui.error("Incorrect current password. Password change cancelled.")
            return

        new_password = ui.prompt("New Password", password=True).strip()
        valid, reason = Validation.validate_password_strength(new_password)
        if not valid:
            ui.error(reason)
            return

        confirm_password = ui.prompt("Confirm New Password", password=True).strip()
        if new_password != confirm_password:
            ui.error("Passwords do not match. Password change cancelled.")
            return

        new_hash = Hashing.hash_password(new_password)
        User.update_password(user.user_id, new_hash)
        self._log_password_change(user.user_id)
        ui.success("Password changed successfully.")

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
        ui.section_header("FORGOT PASSWORD", icon="❓")
        email = ui.prompt("Enter your registered Email").strip()
        user = User.get_by_email(email)
        if not user:
            ui.error("No account found with that email.")
            return

        if not user.security_question:
            ui.error("No security question is set for this account. Please contact support.")
            return

        ui.info(f"Security Question: {user.security_question}")
        answer = ui.prompt("Your Answer").strip()

        if not Hashing.verify_password(answer.lower(), user.security_answer_hash):
            ui.error("Incorrect answer. Password reset denied.")
            return

        new_password = ui.prompt("Enter New Password", password=True).strip()
        valid, reason = Validation.validate_password_strength(new_password)
        if not valid:
            ui.error(reason)
            return

        confirm_password = ui.prompt("Confirm New Password", password=True).strip()
        if new_password != confirm_password:
            ui.error("Passwords do not match. Password reset cancelled.")
            return

        new_hash = Hashing.hash_password(new_password)
        User.update_password(user.user_id, new_hash)
        self._log_password_change(user.user_id)
        ui.success("Password reset successfully. You may now log in.")
