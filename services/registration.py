"""
services/registration.py
Handles new user registration (Feature 2): collects and validates every
field, checks for duplicates, hashes the password with bcrypt, and
stores the new account with Account_Status = Active.

Presentation note: the form now opens with a bordered section header and
every prompt/message goes through utils/ui.py for a consistent look. Field
order, validation rules, OTP verification, and the security-question flow
are all unchanged.
"""

from utils.helpers import get_non_empty_input
from utils.hashing import Hashing
from utils import ui
from services.validation import Validation
from models.user import User
from services.otp_service import OTPService
import traceback

class Registration:
    """Drives the interactive user-registration workflow."""

    def register_user(self):
        ui.section_header("NEW USER REGISTRATION", icon="📝")
        try:
            full_name = self._ask_valid_name()
            email = self._ask_valid_email()
            phone_number = self._ask_valid_phone()
            location = get_non_empty_input("Location: ")
            username = self._ask_valid_username()
            password = self._ask_valid_password()


            otp_service = OTPService()

            if not otp_service.verify_email(email):
                ui.warning("Registration cancelled.")
                return
            # A security question/answer is required to support the
            # Forgot Password recovery flow (Feature 6).

            security_question = get_non_empty_input(
                "Set a security question (used later for password recovery): ")
            security_answer = get_non_empty_input("Answer to your security question: ")
            security_answer_hash = Hashing.hash_password(security_answer.strip().lower())

            # role = self._ask_role()


            password_hash = Hashing.hash_password(password)

            User.create(
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                location=location,
                username=username,
                password_hash=password_hash,
                security_question=security_question,
                security_answer_hash=security_answer_hash,
            )

            ui.success(f"Registration successful! You may now log in as '{username}'.")
            return True

        except Exception:
            traceback.print_exc()
            return False

    # ---------------- individual field prompts with validation ----------------

    def _ask_valid_name(self):
        while True:
            name = ui.prompt("Full Name").strip()
            if Validation.validate_name(name):
                return name
            ui.error("Invalid name. Name cannot be empty and must be at least 2 characters.")

    def _ask_valid_email(self):
        while True:
            email = ui.prompt("Email").strip()
            if not Validation.validate_email(email):
                ui.error("Invalid email format. Please try again.")
                continue
            if User.get_by_email(email):
                ui.error("This email is already registered. Please use another one.")
                continue
            return email

    def _ask_valid_phone(self):
        while True:
            phone = ui.prompt("Phone Number (10 digits)").strip()
            if not Validation.validate_phone(phone):
                ui.error("Invalid phone number. It must be exactly 10 digits.")
                continue
            if User.get_by_phone(phone):
                ui.error("This phone number is already registered. Please use another one.")
                continue
            return phone

    def _ask_valid_username(self):
        while True:
            username = ui.prompt("Username").strip()
            if not Validation.validate_not_empty(username):
                ui.error("Username cannot be empty.")
                continue
            if User.get_by_username(username):
                ui.error("This username is already taken. Please choose another.")
                continue
            return username

    def _ask_valid_password(self):
        while True:
            password = ui.prompt("Password", password=True).strip()
            valid, reason = Validation.validate_password_strength(password)
            if not valid:
                ui.error(reason)
                continue
            confirm = ui.prompt("Confirm Password", password=True).strip()
            if password != confirm:
                ui.error("Passwords do not match. Please try again.")
                continue
            return password

    def _ask_role(self):
        roles = Validation.VALID_ROLES
        while True:
            ui.console.print("[bold]Select Role:[/bold]")
            for idx, r in enumerate(roles, start=1):
                ui.console.print(f"  [bright_magenta]{idx}[/bright_magenta]. {r}")
            choice = ui.prompt("Enter choice number").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(roles):
                return roles[int(choice) - 1]
            ui.error("Invalid choice. Please select a valid role number.")
