"""
services/profile.py
Handles profile viewing/editing (Feature 5), account preferences
(Feature 7), activity history (Feature 9), and account
deactivation/deletion (Feature 8) for the currently logged-in user.

Presentation note: only the printed messages/prompts have been upgraded to
utils/ui.py styling (detail panels for profile/history views, styled
forms). Every validation rule and database call is unchanged.
"""

from datetime import datetime
from database.db import Database
from models.user import User
from services.validation import Validation
from utils import ui
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
            ui.error("Profile not found.")
            return
        ui.detail_panel("YOUR PROFILE", {
            "User ID": user.user_id,
            "Full Name": user.full_name,
            "Email": user.email,
            "Phone Number": user.phone_number,
            "Location": user.location,
            "Username": user.username,
            "Role": user.role,
            "Account Status": user.account_status,
            "Member Since": user.account_created_date,
        })

    # ==================== EDIT PROFILE ====================
    def edit_profile(self):
        user = User.get_by_id(self.session.user_id)
        if not user:
            ui.error("Profile not found.")
            return

        ui.section_header("EDIT PROFILE", icon="✏️")
        ui.info("Press Enter to keep the current value.")

        new_name = ui.prompt("Full Name", default=user.full_name).strip() or user.full_name
        if not Validation.validate_name(new_name):
            ui.error("Invalid name. Update cancelled.")
            return

        new_email = ui.prompt("Email", default=user.email).strip() or user.email
        if new_email != user.email:
            if not Validation.validate_email(new_email):
                ui.error("Invalid email format. Update cancelled.")
                return
            existing = User.get_by_email(new_email)
            if existing and existing.user_id != user.user_id:
                ui.error("This email is already in use by another account. Update cancelled.")
                return

        new_phone = ui.prompt("Phone Number", default=user.phone_number).strip() or user.phone_number
        if new_phone != user.phone_number:
            if not Validation.validate_phone(new_phone):
                ui.error("Invalid phone number. Update cancelled.")
                return
            existing = User.get_by_phone(new_phone)
            if existing and existing.user_id != user.user_id:
                ui.error("This phone number is already in use by another account. Update cancelled.")
                return

        new_location = ui.prompt("Location", default=user.location).strip() or user.location

        try:
            # Log every changed field into Profile_Update_History (Feature 9)
            self._log_change(user.user_id, "Full_Name", user.full_name, new_name)
            self._log_change(user.user_id, "Email", user.email, new_email)
            self._log_change(user.user_id, "Phone_Number", user.phone_number, new_phone)
            self._log_change(user.user_id, "Location", user.location, new_location)

            User.update_profile(user.user_id, new_name, new_email, new_phone, new_location)
            ui.success("Profile updated successfully.")
        except Exception as e:
            ui.error(f"Failed to update profile: {e}")

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
        ui.info(f"Current Preferred Role: {prefs.get('Preferred_Role') or 'Not set'}")
        for idx, r in enumerate(roles, start=1):
            ui.console.print(f"  [bright_magenta]{idx}[/bright_magenta]. {r}")
        choice = ui.prompt("Select new preferred role").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(roles):
            new_role = roles[int(choice) - 1]
            self.db.execute_query(
                "UPDATE User_Preferences SET Preferred_Role = %s WHERE User_ID = %s",
                (new_role, self.session.user_id), commit=True,
            )
            ui.success(f"Preferred role updated to {new_role}.")
        else:
            ui.warning("Invalid choice. No changes made.")

    def manage_notification_preferences(self):
        prefs = self._get_or_create_preferences(self.session.user_id)
        ui.info(f"Notifications currently: {'Enabled' if prefs.get('Notification_Enabled') else 'Disabled'}")
        ui.info(f"Email Alerts currently : {'Enabled' if prefs.get('Email_Alerts_Enabled') else 'Disabled'}")
        notif = confirm_action("Enable Notifications?")
        email_alerts = confirm_action("Enable Email Alerts?")
        self.db.execute_query(
            "UPDATE User_Preferences SET Notification_Enabled = %s, Email_Alerts_Enabled = %s WHERE User_ID = %s",
            (int(notif), int(email_alerts), self.session.user_id), commit=True,
        )
        ui.success("Notification preferences updated.")

    def manage_location_preferences(self):
        prefs = self._get_or_create_preferences(self.session.user_id)
        ui.info(f"Current City: {prefs.get('City') or 'Not set'}")
        ui.info(f"Current State: {prefs.get('State') or 'Not set'}")
        ui.info(f"Current Preferred Exchange Location: {prefs.get('Preferred_Exchange_Location') or 'Not set'}")

        city = ui.prompt("New City").strip()
        state = ui.prompt("New State").strip()
        exchange_location = ui.prompt("New Preferred Exchange Location").strip()

        if not (city and state and exchange_location):
            ui.error("All location fields are required. Update cancelled.")
            return

        self.db.execute_query(
            """UPDATE User_Preferences
               SET City = %s, State = %s, Preferred_Exchange_Location = %s
               WHERE User_ID = %s""",
            (city, state, exchange_location, self.session.user_id), commit=True,
        )
        ui.success("Location preferences updated.")

    # ==================== ACTIVITY HISTORY (Feature 9) ====================
    def view_login_history(self):
        rows = self.db.fetch_all(
            "SELECT * FROM Login_History WHERE User_ID = %s ORDER BY Login_ID DESC",
            (self.session.user_id,),
        )
        if not rows:
            ui.info("No login history found.")
            return
        ui.section_header("LOGIN HISTORY", icon="🕒")
        table_rows = []
        for row in rows:
            logout_info = (f"{row['Logout_Date']} {row['Logout_Time']}"
                            if row["Logout_Date"] else "Still active / not recorded")
            table_rows.append({
                "Login": f"{row['Login_Date']} {row['Login_Time']}",
                "Logout": logout_info,
            })
        ui.table(table_rows, headers=["Login", "Logout"])

    def view_account_activity(self):
        profile_updates = self.db.fetch_all(
            "SELECT * FROM Profile_Update_History WHERE User_ID = %s ORDER BY Update_ID DESC",
            (self.session.user_id,),
        )
        password_changes = self.db.fetch_all(
            "SELECT * FROM Password_Change_History WHERE User_ID = %s ORDER BY Change_ID DESC",
            (self.session.user_id,),
        )

        ui.section_header("PROFILE UPDATE HISTORY", icon="📊")
        if not profile_updates:
            ui.info("No profile updates recorded.")
        else:
            ui.table(
                [{"Date": row["Updated_Date"], "Field": row["Field_Changed"],
                  "Change": f"'{row['Old_Value']}' -> '{row['New_Value']}'"} for row in profile_updates],
                headers=["Date", "Field", "Change"],
            )

        ui.section_header("PASSWORD CHANGE HISTORY", icon="🔑")
        if not password_changes:
            ui.info("No password changes recorded.")
        else:
            ui.table(
                [{"Changed On": row["Changed_Date"]} for row in password_changes],
                headers=["Changed On"],
            )

    # ==================== ACCOUNT STATUS (Feature 8) ====================
    def deactivate_account(self):
        if confirm_action("Are you sure you want to deactivate your account?"):
            User.update_status(self.session.user_id, "Inactive")
            ui.success("Your account has been deactivated. You will be logged out.")
            return True
        ui.warning("Deactivation cancelled.")
        return False

    def delete_account(self):
        """Soft delete: the record is flagged Is_Deleted = 1, never hard-removed."""
        if confirm_action("Are you sure you want to permanently delete your account?"):
            User.soft_delete(self.session.user_id)
            ui.success("Your account has been deleted. You will be logged out.")
            return True
        ui.warning("Account deletion cancelled.")
        return False
