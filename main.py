"""
main.py
Entry point for the Book Bank Management System.

Run this file to start the console application:
    python main.py

This module wires every service together and implements:
  - Feature 1  : System Entry menu
  - Feature 4  : User Dashboard loop
  - Feature 10 : Admin Dashboard loop
  - Feature 14 : Dynamic Menu (only the correct dashboard is ever shown)
  - Feature 15 : Global exception handling / invalid-choice handling
"""

import sys

from database.db import Database
from models.admin import Admin
from services.authentication import Authentication, Session
from services.registration import Registration
from services.profile import ProfileManagement
from services.password import PasswordManagement
from services.admin_management import AdminManagement
from services.authorization import Authorization
from services.validation import Validation
from utils.hashing import Hashing
from utils.menus import show_main_menu, show_user_dashboard, show_admin_dashboard
from utils.helpers import pause, get_non_empty_input


# ======================================================================
# USER DASHBOARD LOOP (Feature 4)
# ======================================================================
def user_dashboard_loop(session, auth):
    """Displays the User Dashboard and routes choices to ProfileManagement /
    PasswordManagement until the user logs out, deactivates, or deletes."""
    profile = ProfileManagement(session)
    password_mgmt = PasswordManagement(session)

    while True:
        # Defensive re-check: only a logged-in User may see this menu (Feature 13/14)
        if not Authorization.require_user(session):
            return

        show_user_dashboard(session.username)
        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                profile.view_profile()
            elif choice == "2":
                profile.edit_profile()
            elif choice == "3":
                password_mgmt.change_password()
            elif choice == "4":
                password_mgmt.forgot_password()
            elif choice == "5":
                profile.manage_notification_preferences()
            elif choice == "6":
                profile.manage_location_preferences()
            elif choice == "7":
                profile.view_login_history()
            elif choice == "8":
                profile.view_account_activity()
            elif choice == "9":
                if profile.deactivate_account():
                    auth.logout()
                    return
            elif choice == "10":
                if profile.delete_account():
                    auth.logout()
                    return
            elif choice == "11":
                auth.logout()
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-11).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        pause()


# ======================================================================
# ADMIN DASHBOARD LOOP (Feature 10)
# ======================================================================
def admin_dashboard_loop(session, auth):
    """Displays the Admin Dashboard and routes choices to AdminManagement
    until the administrator logs out."""
    admin_mgmt = AdminManagement(session)

    while True:
        # Defensive re-check: only a logged-in Admin may see this menu (Feature 13/14)
        if not Authorization.require_admin(session):
            return

        show_admin_dashboard(session.username)
        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                admin_mgmt.register_admin()
            elif choice == "2":
                admin_mgmt.promote_user_to_admin()
            elif choice == "3":
                admin_mgmt.view_users()
            elif choice == "4":
                admin_mgmt.search_user()
            elif choice == "5":
                admin_mgmt.activate_user()
            elif choice == "6":
                admin_mgmt.deactivate_user()
            elif choice == "7":
                admin_mgmt.delete_user()
            elif choice == "8":
                admin_mgmt.view_admins()
            elif choice == "9":
                auth.logout()
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-9).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        pause()


# ======================================================================
# FIRST-TIME ADMIN BOOTSTRAP
# The Administrators table starts empty, but Feature 11 (Register New
# Admin) can only be performed by an admin who is already logged in.
# To break this chicken-and-egg problem, main() checks once at startup
# whether any administrator exists; if not, it walks the operator
# through creating the very first one before showing the main menu.
# ======================================================================
def bootstrap_first_admin():
    try:
        if Admin.get_all():
            return  # At least one administrator already exists - nothing to do
    except Exception as e:
        print(f"Could not check for existing administrators: {e}")
        return

    print("\nNo administrator account exists yet. Let's create the first one.")
    try:
        full_name = get_non_empty_input("Full Name: ")

        while True:
            email = get_non_empty_input("Email: ")
            if not Validation.validate_email(email):
                print("Invalid email format.")
                continue
            if Admin.get_by_email(email):
                print("An administrator with this email already exists.")
                continue
            break

        while True:
            phone = get_non_empty_input("Phone Number (10 digits): ")
            if Validation.validate_phone(phone):
                break
            print("Invalid phone number. It must be exactly 10 digits.")

        while True:
            username = get_non_empty_input("Username: ")
            if not Admin.get_by_username(username):
                break
            print("This username is already taken.")

        while True:
            password = get_non_empty_input("Password: ")
            valid, reason = Validation.validate_password_strength(password)
            if not valid:
                print(reason)
                continue
            confirm = get_non_empty_input("Confirm Password: ")
            if password != confirm:
                print("Passwords do not match.")
                continue
            break

        admin_level = get_non_empty_input("Admin Level (e.g. SuperAdmin): ")

        password_hash = Hashing.hash_password(password)
        Admin.create(full_name, email, phone, username, password_hash,
                     admin_level, created_by="SYSTEM")
        print(f"First administrator '{username}' created successfully. You can now log in.")

    except Exception as e:
        print(f"Failed to create the first administrator: {e}")


# ======================================================================
# MAIN PROGRAM LOOP (Feature 1: System Entry)
# ======================================================================
def main():
    # Establish the database connection once at startup.
    try:
        Database.get_instance()
    except Exception:
        print("Could not connect to the database. Please check your MySQL "
              "configuration in database/db.py and ensure the MySQL server is running.")
        sys.exit(1)

    bootstrap_first_admin()

    session = Session()
    auth = Authentication(session)
    registration = Registration()

    while True:
        show_main_menu()
        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                identifier = get_non_empty_input("Username or Email: ")
                password = input("Password: ").strip()
                if auth.login_user(identifier, password):
                    user_dashboard_loop(session, auth)

            elif choice == "2":
                identifier = get_non_empty_input("Admin Username or Email: ")
                password = input("Password: ").strip()
                if auth.login_admin(identifier, password):
                    admin_dashboard_loop(session, auth)

            elif choice == "3":
                registration.register_user()

            elif choice == "4":
                print("\nThank you for using Book Bank Management System. Goodbye!")
                Database.get_instance().close()
                sys.exit(0)

            else:
                print("Invalid choice. Please select 1-4.")

        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Exiting safely...")
            Database.get_instance().close()
            sys.exit(0)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        pause()


if __name__ == "__main__":
    main()
