"""
services/admin_management.py
Administrator-only operations: creating new admins (Feature 11),
promoting an existing user to admin (Feature 12), and managing user
accounts - view / search / activate / deactivate / delete (Feature 10).
Every method here assumes the caller has already passed the
Authorization.require_admin() check in main.py.
"""

from database.db import Database
from models.user import User
from models.admin import Admin
from services.validation import Validation
from utils.hashing import Hashing
from utils.helpers import confirm_action


class AdminManagement:
    """Implements every Admin Dashboard operation."""

    def __init__(self, session):
        self.session = session
        self.db = Database.get_instance()

    # ==================== REGISTER NEW ADMIN (Feature 11) ====================
    def register_admin(self):
        print("\n--- REGISTER NEW ADMINISTRATOR ---")
        try:
            full_name = input("Full Name: ").strip()
            if not Validation.validate_name(full_name):
                print("Invalid name. Registration cancelled.")
                return

            email = input("Email: ").strip()
            if not Validation.validate_email(email):
                print("Invalid email format. Registration cancelled.")
                return
            if Admin.get_by_email(email):
                print("An administrator with this email already exists.")
                return

            phone = input("Phone Number (10 digits): ").strip()
            if not Validation.validate_phone(phone):
                print("Invalid phone number. Registration cancelled.")
                return

            username = input("Username: ").strip()
            if not Validation.validate_not_empty(username):
                print("Username cannot be empty.")
                return
            if Admin.get_by_username(username):
                print("This username is already taken.")
                return

            password = input("Password: ").strip()
            valid, reason = Validation.validate_password_strength(password)
            if not valid:
                print(reason)
                return
            confirm_password = input("Confirm Password: ").strip()
            if password != confirm_password:
                print("Passwords do not match. Registration cancelled.")
                return

            admin_level = input("Admin Level (e.g. SuperAdmin / Moderator): ").strip()
            if not Validation.validate_not_empty(admin_level):
                print("Admin level cannot be empty.")
                return

            password_hash = Hashing.hash_password(password)
            Admin.create(full_name, email, phone, username, password_hash,
                         admin_level, created_by=self.session.username)
            print(f"Administrator '{username}' created successfully.")

        except Exception as e:
            print(f"Failed to register administrator: {e}")

    # ==================== PROMOTE USER TO ADMIN (Feature 12) ====================
    def promote_user_to_admin(self):
        print("\n--- PROMOTE USER TO ADMIN ---")
        print("Search by: 1. Username  2. Email  3. User ID")
        choice = input("Choice: ").strip()

        user = None
        if choice == "1":
            user = User.get_by_username(input("Enter Username: ").strip())
        elif choice == "2":
            user = User.get_by_email(input("Enter Email: ").strip())
        elif choice == "3":
            uid = input("Enter User ID: ").strip()
            if uid.isdigit():
                user = User.get_by_id(int(uid))
        else:
            print("Invalid choice.")
            return

        if not user:
            print("User not found.")
            return

        print("\n--- USER DETAILS ---")
        print(f"User ID   : {user.user_id}")
        print(f"Full Name : {user.full_name}")
        print(f"Email     : {user.email}")
        print(f"Username  : {user.username}")
        print(f"Role      : {user.role}")
        print(f"Status    : {user.account_status}")

        if Admin.get_by_username(user.username) or Admin.get_by_email(user.email):
            print("This user is already an administrator.")
            return

        if not confirm_action("Promote this user to Administrator?"):
            print("Promotion cancelled.")
            return

        admin_level = input("Assign Admin Level (e.g. Moderator): ").strip()
        if not Validation.validate_not_empty(admin_level):
            print("Admin level cannot be empty. Promotion cancelled.")
            return

        # The user keeps their original User record; a new Administrators row is added.
        Admin.promote_from_user(user, admin_level, created_by=self.session.username)
        print(f"User '{user.username}' has been promoted to Administrator.")

    # ==================== VIEW USERS ====================
    def view_users(self):
        users = User.get_all()
        if not users:
            print("No users found.")
            return
        print("\n--- ALL USERS ---")
        for u in users:
            print(f"[{u.user_id}] {u.username} | {u.full_name} | {u.email} | "
                  f"{u.role} | {u.account_status}")

    # ==================== SEARCH USER ====================
    def search_user(self):
        keyword = input("Search by Username, Email, or User ID: ").strip()
        if not Validation.validate_not_empty(keyword):
            print("Search term cannot be empty.")
            return
        results = User.search(keyword)
        if not results:
            print("No matching users found.")
            return
        print("\n--- SEARCH RESULTS ---")
        for u in results:
            print(f"[{u.user_id}] {u.username} | {u.full_name} | {u.email} | "
                  f"{u.role} | {u.account_status}")

    # ==================== ACTIVATE / DEACTIVATE / DELETE ====================
    def activate_user(self):
        user = self._select_user_by_id("activate")
        if user:
            User.update_status(user.user_id, "Active")
            print(f"User '{user.username}' has been activated.")

    def deactivate_user(self):
        user = self._select_user_by_id("deactivate")
        if user:
            User.update_status(user.user_id, "Inactive")
            print(f"User '{user.username}' has been deactivated.")

    def delete_user(self):
        user = self._select_user_by_id("delete")
        if user and confirm_action(f"Confirm permanent deletion of '{user.username}'?"):
            User.soft_delete(user.user_id)
            print(f"User '{user.username}' has been deleted.")
        elif user:
            print("Deletion cancelled.")

    def _select_user_by_id(self, action_name):
        uid = input(f"Enter User ID to {action_name}: ").strip()
        if not uid.isdigit():
            print("Invalid User ID.")
            return None
        user = User.get_by_id(int(uid))
        if not user:
            print("User not found.")
        return user

    # ==================== VIEW ADMINS ====================
    def view_admins(self):
        admins = Admin.get_all()
        if not admins:
            print("No administrators found.")
            return
        print("\n--- ALL ADMINISTRATORS ---")
        for a in admins:
            print(f"[{a.admin_id}] {a.username} | {a.full_name} | {a.email} | "
                  f"{a.admin_level} | {a.account_status} | Created by: {a.created_by}")
