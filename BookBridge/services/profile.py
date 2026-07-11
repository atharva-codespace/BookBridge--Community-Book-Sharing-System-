"""
services/profile.py
Handles profile viewing/editing (Feature 5), account preferences
(Feature 7), activity history (Feature 9), and account
deactivation/deletion (Feature 8) for the currently logged-in user.
"""

from datetime import datetime
from database.db import Database
from models.user import User
from services.validation import Validation
from utils.helpers import confirm_action


class ProfileManagement:
    """All profile-related operations for the currently logged-in user."""

    def __init__(self, session):
        self.session = session
        self.db = Database.get_instance()

    # ==================== VIEW PROFILE ====================
    def view_profile(self):
        user = User.get_by_id(self.session.user_id)
        if not user:
            print("Profile not found.")
            return
        print("\n--- YOUR PROFILE ---")
        print(f"User ID       : {user.user_id}")
        print(f"Full Name     : {user.full_name}")
        print(f"Email         : {user.email}")
        print(f"Phone Number  : {user.phone_number}")
        print(f"Location      : {user.location}")
        print(f"Username      : {user.username}")
        print(f"Role          : {user.role}")
        print(f"Account Status: {user.account_status}")
        print(f"Member Since  : {user.account_created_date}")

    # ==================== EDIT PROFILE ====================
    def edit_profile(self):
        user = User.get_by_id(self.session.user_id)
        if not user:
            print("Profile not found.")
            return

        print("\n--- EDIT PROFILE (press Enter to keep the current value) ---")

        new_name = input(f"Full Name [{user.full_name}]: ").strip() or user.full_name
        if not Validation.validate_name(new_name):
            print("Invalid name. Update cancelled.")
            return

        new_email = input(f"Email [{user.email}]: ").strip() or user.email
        if new_email != user.email:
            if not Validation.validate_email(new_email):
                print("Invalid email format. Update cancelled.")
                return
            existing = User.get_by_email(new_email)
            if existing and existing.user_id != user.user_id:
                print("This email is already in use by another account. Update cancelled.")
                return

        new_phone = input(f"Phone Number [{user.phone_number}]: ").strip() or user.phone_number
        if new_phone != user.phone_number:
            if not Validation.validate_phone(new_phone):
                print("Invalid phone number. Update cancelled.")
                return
            existing = User.get_by_phone(new_phone)
            if existing and existing.user_id != user.user_id:
                print("This phone number is already in use by another account. Update cancelled.")
                return

        new_location = input(f"Location [{user.location}]: ").strip() or user.location

        try:
            # Log every changed field into Profile_Update_History (Feature 9)
            self._log_change(user.user_id, "Full_Name", user.full_name, new_name)
            self._log_change(user.user_id, "Email", user.email, new_email)
            self._log_change(user.user_id, "Phone_Number", user.phone_number, new_phone)
            self._log_change(user.user_id, "Location", user.location, new_location)

            User.update_profile(user.user_id, new_name, new_email, new_phone, new_location)
            print("Profile updated successfully.")
        except Exception as e:
            print(f"Failed to update profile: {e}")

    def _log_change(self, user_id, field, old_value, new_value):
        if old_value == new_value:
            return
        self.db.execute_query(
            """INSERT INTO Profile_Update_History
               (User_ID, Field_Changed, Old_Value, New_Value, Updated_Date)
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, field, str(old_value), str(new_value), datetime.now()),
            commit=True,
        )

    # ==================== PREFERENCES (Feature 7) ====================
    def _get_or_create_preferences(self, user_id):
        row = self.db.fetch_one("SELECT * FROM User_Preferences WHERE User_ID = %s", (user_id,))
        if row is None:
            self.db.execute_query(
                "INSERT INTO User_Preferences (User_ID) VALUES (%s)", (user_id,), commit=True
            )
            row = self.db.fetch_one("SELECT * FROM User_Preferences WHERE User_ID = %s", (user_id,))
        return row

    def manage_preferred_role(self):
        prefs = self._get_or_create_preferences(self.session.user_id)
        roles = Validation.VALID_ROLES
        print(f"\nCurrent Preferred Role: {prefs.get('Preferred_Role') or 'Not set'}")
        for idx, r in enumerate(roles, start=1):
            print(f"{idx}. {r}")
        choice = input("Select new preferred role: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(roles):
            new_role = roles[int(choice) - 1]
            self.db.execute_query(
                "UPDATE User_Preferences SET Preferred_Role = %s WHERE User_ID = %s",
                (new_role, self.session.user_id), commit=True,
            )
            print(f"Preferred role updated to {new_role}.")
        else:
            print("Invalid choice. No changes made.")

    def manage_notification_preferences(self):
        prefs = self._get_or_create_preferences(self.session.user_id)
        print(f"\nNotifications currently: {'Enabled' if prefs.get('Notification_Enabled') else 'Disabled'}")
        print(f"Email Alerts currently : {'Enabled' if prefs.get('Email_Alerts_Enabled') else 'Disabled'}")
        notif = confirm_action("Enable Notifications?")
        email_alerts = confirm_action("Enable Email Alerts?")
        self.db.execute_query(
            "UPDATE User_Preferences SET Notification_Enabled = %s, Email_Alerts_Enabled = %s WHERE User_ID = %s",
            (int(notif), int(email_alerts), self.session.user_id), commit=True,
        )
        print("Notification preferences updated.")

    def manage_location_preferences(self):
        prefs = self._get_or_create_preferences(self.session.user_id)
        print(f"\nCurrent City: {prefs.get('City') or 'Not set'}")
        print(f"Current State: {prefs.get('State') or 'Not set'}")
        print(f"Current Preferred Exchange Location: {prefs.get('Preferred_Exchange_Location') or 'Not set'}")

        city = input("New City: ").strip()
        state = input("New State: ").strip()
        exchange_location = input("New Preferred Exchange Location: ").strip()

        if not (city and state and exchange_location):
            print("All location fields are required. Update cancelled.")
            return

        self.db.execute_query(
            """UPDATE User_Preferences
               SET City = %s, State = %s, Preferred_Exchange_Location = %s
               WHERE User_ID = %s""",
            (city, state, exchange_location, self.session.user_id), commit=True,
        )
        print("Location preferences updated.")

    # ==================== ACTIVITY HISTORY (Feature 9) ====================
    def view_login_history(self):
        rows = self.db.fetch_all(
            "SELECT * FROM Login_History WHERE User_ID = %s ORDER BY Login_ID DESC",
            (self.session.user_id,),
        )
        if not rows:
            print("\nNo login history found.")
            return
        print("\n--- LOGIN HISTORY ---")
        for row in rows:
            logout_info = (f"{row['Logout_Date']} {row['Logout_Time']}"
                            if row["Logout_Date"] else "Still active / not recorded")
            print(f"Login: {row['Login_Date']} {row['Login_Time']}  |  Logout: {logout_info}")

    def view_account_activity(self):
        profile_updates = self.db.fetch_all(
            "SELECT * FROM Profile_Update_History WHERE User_ID = %s ORDER BY Update_ID DESC",
            (self.session.user_id,),
        )
        password_changes = self.db.fetch_all(
            "SELECT * FROM Password_Change_History WHERE User_ID = %s ORDER BY Change_ID DESC",
            (self.session.user_id,),
        )

        print("\n--- PROFILE UPDATE HISTORY ---")
        if not profile_updates:
            print("No profile updates recorded.")
        for row in profile_updates:
            print(f"[{row['Updated_Date']}] {row['Field_Changed']}: "
                  f"'{row['Old_Value']}' -> '{row['New_Value']}'")

        print("\n--- PASSWORD CHANGE HISTORY ---")
        if not password_changes:
            print("No password changes recorded.")
        for row in password_changes:
            print(f"Password changed on {row['Changed_Date']}")

    # ==================== ACCOUNT STATUS (Feature 8) ====================
    def deactivate_account(self):
        if confirm_action("Are you sure you want to deactivate your account?"):
            User.update_status(self.session.user_id, "Inactive")
            print("Your account has been deactivated. You will be logged out.")
            return True
        print("Deactivation cancelled.")
        return False

    def delete_account(self):
        """Soft delete: the record is flagged Is_Deleted = 1, never hard-removed."""
        if confirm_action("Are you sure you want to permanently delete your account?"):
            User.soft_delete(self.session.user_id)
            print("Your account has been deleted. You will be logged out.")
            return True
        print("Account deletion cancelled.")
        return False
