"""
services/admin_management.py
Administrator-only operations: creating new admins (Feature 11),
promoting an existing user to admin (Feature 12), and managing user
accounts - view / search / activate / deactivate / delete (Feature 10).
Every method here assumes the caller has already passed the
Authorization.require_admin() check in main.py.

Presentation note: only the printed messages/prompts have been upgraded to
utils/ui.py styling (styled forms, success/error banners, detail panels).
Every validation rule, duplicate check, and database call is unchanged.
"""

from database.db import Database
from models.user import User
from models.admin import Admin
from services.validation import Validation
from utils.hashing import Hashing
from utils import ui
from utils.helpers import confirm_action, print_table

USER_TABLE_FIELDS = ["User_ID", "Username", "Full_Name", "Email", "Role", "Account_Status"]
ADMIN_TABLE_FIELDS = ["Admin_ID", "Username", "Full_Name", "Email", "Admin_Level", "Account_Status", "Created_By"]


def _user_to_row(u):
    return {"User_ID": u.user_id, "Username": u.username, "Full_Name": u.full_name,
            "Email": u.email, "Role": u.role, "Account_Status": u.account_status}


def _admin_to_row(a):
    return {"Admin_ID": a.admin_id, "Username": a.username, "Full_Name": a.full_name,
            "Email": a.email, "Admin_Level": a.admin_level, "Account_Status": a.account_status,
            "Created_By": a.created_by}


class AdminManagement:
    """Implements every Admin Dashboard operation."""

    def __init__(self, session):
        self.session = session
        self.db = Database.get_instance()

    # ==================== REGISTER NEW ADMIN (Feature 11) ====================
    def register_admin(self):
        ui.section_header("REGISTER NEW ADMINISTRATOR", icon="🛡️")
        try:
            full_name = ui.prompt("Full Name").strip()
            if not Validation.validate_name(full_name):
                ui.error("Invalid name. Registration cancelled.")
                return

            email = ui.prompt("Email").strip()
            if not Validation.validate_email(email):
                ui.error("Invalid email format. Registration cancelled.")
                return
            if Admin.get_by_email(email):
                ui.error("An administrator with this email already exists.")
                return

            phone = ui.prompt("Phone Number (10 digits)").strip()
            if not Validation.validate_phone(phone):
                ui.error("Invalid phone number. Registration cancelled.")
                return

            username = ui.prompt("Username").strip()
            if not Validation.validate_not_empty(username):
                ui.error("Username cannot be empty.")
                return
            if Admin.get_by_username(username):
                ui.error("This username is already taken.")
                return

            password = ui.prompt("Password", password=True).strip()
            valid, reason = Validation.validate_password_strength(password)
            if not valid:
                ui.error(reason)
                return
            confirm_password = ui.prompt("Confirm Password", password=True).strip()
            if password != confirm_password:
                ui.error("Passwords do not match. Registration cancelled.")
                return

            admin_level = ui.prompt("Admin Level (e.g. SuperAdmin / Moderator)").strip()
            if not Validation.validate_not_empty(admin_level):
                ui.error("Admin level cannot be empty.")
                return

            password_hash = Hashing.hash_password(password)
            Admin.create(full_name, email, phone, username, password_hash,
                         admin_level, created_by=self.session.username)
            ui.success(f"Administrator '{username}' created successfully.")

        except Exception as e:
            ui.error(f"Failed to register administrator: {e}")

    # ==================== PROMOTE USER TO ADMIN (Feature 12) ====================
    def promote_user_to_admin(self):
        ui.section_header("PROMOTE USER TO ADMIN", icon="⬆️")
        ui.menu("SEARCH BY", [("1", "Username", "🔤"), ("2", "Email", "📧"), ("3", "User ID", "🆔")])
        choice = ui.prompt("Choice").strip()

        user = None
        if choice == "1":
            user = User.get_by_username(ui.prompt("Enter Username").strip())
        elif choice == "2":
            user = User.get_by_email(ui.prompt("Enter Email").strip())
        elif choice == "3":
            uid = ui.prompt("Enter User ID").strip()
            if uid.isdigit():
                user = User.get_by_id(int(uid))
        else:
            ui.warning("Invalid choice.")
            return

        if not user:
            ui.error("User not found.")
            return

        ui.detail_panel("USER DETAILS", {
            "User ID": user.user_id,
            "Full Name": user.full_name,
            "Email": user.email,
            "Username": user.username,
            "Role": user.role,
            "Status": user.account_status,
        })

        if Admin.get_by_username(user.username) or Admin.get_by_email(user.email):
            ui.warning("This user is already an administrator.")
            return

        if not confirm_action("Promote this user to Administrator?"):
            ui.warning("Promotion cancelled.")
            return

        admin_level = ui.prompt("Assign Admin Level (e.g. Moderator)").strip()
        if not Validation.validate_not_empty(admin_level):
            ui.error("Admin level cannot be empty. Promotion cancelled.")
            return

        # The user keeps their original User record; a new Administrators row is added.
        Admin.promote_from_user(user, admin_level, created_by=self.session.username)
        ui.success(f"User '{user.username}' has been promoted to Administrator.")

    # ==================== VIEW USERS ====================
    def view_users(self):
        users = User.get_all()
        print_table([_user_to_row(u) for u in users], headers=USER_TABLE_FIELDS, title="ALL USERS")

    # ==================== SEARCH USER ====================
    def search_user(self):
        keyword = ui.prompt("Search by Username, Email, or User ID").strip()
        if not Validation.validate_not_empty(keyword):
            ui.error("Search term cannot be empty.")
            return
        results = User.search(keyword)
        print_table([_user_to_row(u) for u in results], headers=USER_TABLE_FIELDS, title="SEARCH RESULTS")

    # ==================== ACTIVATE / DEACTIVATE / DELETE ====================
    def activate_user(self):
        user = self._select_user_by_id("activate")
        if user:
            User.update_status(user.user_id, "Active")
            ui.success(f"User '{user.username}' has been activated.")

    def deactivate_user(self):
        user = self._select_user_by_id("deactivate")
        if user:
            User.update_status(user.user_id, "Inactive")
            ui.success(f"User '{user.username}' has been deactivated.")

    def delete_user(self):
        user = self._select_user_by_id("delete")
        if user and confirm_action(f"Confirm permanent deletion of '{user.username}'?"):
            User.soft_delete(user.user_id)
            ui.success(f"User '{user.username}' has been deleted.")
        elif user:
            ui.warning("Deletion cancelled.")

    def _select_user_by_id(self, action_name):
        uid = ui.prompt(f"Enter User ID to {action_name}").strip()
        if not uid.isdigit():
            ui.error("Invalid User ID.")
            return None
        user = User.get_by_id(int(uid))
        if not user:
            ui.error("User not found.")
        return user

    # ==================== VIEW ADMINS ====================
    def view_admins(self):
        admins = Admin.get_all()
        print_table([_admin_to_row(a) for a in admins], headers=ADMIN_TABLE_FIELDS, title="ALL ADMINISTRATORS")
