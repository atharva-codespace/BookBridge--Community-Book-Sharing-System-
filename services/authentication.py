"""
services/authentication.py
Handles login for both Users and Administrators, and defines the
Session class that tracks who is currently logged in for the
duration of the running console application (Session Management).

Presentation note: only the printed messages have been upgraded to the
Rich-based utils/ui.py styling (success/error banners). Every credential
check, Login_History write, and Session field assignment is unchanged.
"""

from datetime import datetime
from models.user import User
from models.admin import Admin
from models.delivery_boy import DeliveryBoy
from utils.hashing import Hashing
from utils import ui
from database.db import Database


class Session:
    """
    Represents the current logged-in session. This is a console app used
    by one person at a time, so a single Session object (created once in
    main.py and passed to every service) is enough to model "who is logged
    in right now" and drive the Dynamic Menu requirement (Feature 14).
    """

    def __init__(self):
        self.is_authenticated = False
        self.user_type = None          # "user" or "admin"
        self.user_id = None            # User_ID or Admin_ID depending on user_type
        self.username = None
        self.full_name = None
        self.role = None               # Registered default role (Buyer/Seller/Donor/Exchange User)
        self.active_role = None        # This session's chosen mode - may differ from `role`
        self.admin_level = None        # Admins only
        self.login_history_id = None   # Tracks the open Login_History row (to fill logout time)

    def login_as_user(self, user: User, login_history_id=None):
        self.is_authenticated = True
        self.user_type = "user"
        self.user_id = user.user_id
        self.username = user.username
        self.full_name = user.full_name
        self.role = user.role
        self.active_role = None        # chosen right after login via choose_session_mode()
        self.admin_level = None
        self.login_history_id = login_history_id

    def login_as_admin(self, admin: Admin):
        self.is_authenticated = True
        self.user_type = "admin"
        self.user_id = admin.admin_id
        self.username = admin.username
        self.full_name = admin.full_name
        self.role = None
        self.admin_level = admin.admin_level
        self.login_history_id = None

    def login_as_delivery_boy(self, delivery_boy: DeliveryBoy):
        self.is_authenticated = True
        self.user_type = "delivery_boy"
        self.user_id = delivery_boy.delivery_boy_id
        self.username = delivery_boy.username
        self.full_name = delivery_boy.full_name
        self.role = None
        self.admin_level = None
        self.login_history_id = None

    def logout(self):
        """Clears the session completely (used after logout/deactivate/delete)."""
        self.__init__()


class Authentication:
    """Handles credential verification and the login / logout workflow."""

    def __init__(self, session: Session):
        self.session = session
        self.db = Database.get_instance()

    # ==================== USER LOGIN ====================
    def login_user(self, identifier: str, password: str) -> bool:
        """
        Logs a user in using their Username or Email (Feature 3).
        Only Active accounts may log in. Returns True on success.
        """
        try:
            user = User.get_by_username_or_email(identifier)
            if user is None:
                ui.error("Login failed: No account found with that username/email.")
                return False

            if user.account_status != "Active":
                ui.error("Login failed: This account is Inactive. Please contact support.")
                return False

            if not Hashing.verify_password(password, user.password_hash):
                ui.error("Login failed: Incorrect password.")
                return False

            # Record this login in Login_History (Feature 9: Activity History)
            login_history_id = self.db.execute_query(
                "INSERT INTO Login_History (User_ID, Login_Date, Login_Time) VALUES (%s, %s, %s)",
                (user.user_id, datetime.now().date(), datetime.now().time().strftime("%H:%M:%S")),
                commit=True,
            )

            self.session.login_as_user(user, login_history_id)
            ui.success(f"Login successful. Welcome, {user.full_name}!")
            return True

        except Exception as e:
            ui.error(f"An error occurred during login: {e}")
            return False

    # ==================== ADMIN LOGIN ====================
    def login_admin(self, identifier: str, password: str) -> bool:
        """Logs an administrator in using their Username or Email (Feature 10)."""
        try:
            admin = Admin.get_by_username_or_email(identifier)
            if admin is None:
                ui.error("Login failed: No administrator account found with that username/email.")
                return False

            if admin.account_status != "Active":
                ui.error("Login failed: This administrator account is Inactive.")
                return False

            if not Hashing.verify_password(password, admin.password_hash):
                ui.error("Login failed: Incorrect password.")
                return False

            self.session.login_as_admin(admin)
            ui.success(f"Admin login successful. Welcome, {admin.full_name}!")
            return True

        except Exception as e:
            ui.error(f"An error occurred during login: {e}")
            return False

    # ==================== DELIVERY BOY LOGIN ====================
    def login_delivery_boy(self, identifier: str, password: str) -> bool:
        """Logs a delivery boy in using their Username or Email."""
        try:
            delivery_boy = DeliveryBoy.get_by_username_or_email(identifier)
            if delivery_boy is None:
                ui.error("Login failed: No delivery boy account found with that username/email.")
                return False

            if delivery_boy.account_status != "Active":
                ui.error("Login failed: This delivery boy account is Inactive.")
                return False

            if not Hashing.verify_password(password, delivery_boy.password_hash):
                ui.error("Login failed: Incorrect password.")
                return False

            self.session.login_as_delivery_boy(delivery_boy)
            ui.success(f"Delivery boy login successful. Welcome, {delivery_boy.full_name}!")
            return True

        except Exception as e:
            ui.error(f"An error occurred during login: {e}")
            return False

    # ==================== LOGOUT ====================
    def logout(self):
        """Logs the current session out, recording the logout time for users."""
        try:
            if self.session.user_type == "user" and self.session.login_history_id:
                self.db.execute_query(
                    "UPDATE Login_History SET Logout_Date = %s, Logout_Time = %s WHERE Login_ID = %s",
                    (datetime.now().date(), datetime.now().time().strftime("%H:%M:%S"),
                     self.session.login_history_id),
                    commit=True,
                )
            if self.session.username:
                ui.info(f"{self.session.username} logged out successfully.")
        except Exception as e:
            ui.error(f"An error occurred during logout: {e}")
        finally:
            self.session.logout()
