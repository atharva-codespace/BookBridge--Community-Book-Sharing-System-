"""
models/admin.py
Defines the Admin entity and all database operations (CRUD) for the
Administrators table.
"""

from datetime import datetime
from database.db import Database


class Admin:
    """Represents a single row from the Administrators table plus all Admin CRUD operations."""

    def __init__(self, admin_id=None, full_name=None, email=None, phone_number=None,
                 username=None, password_hash=None, admin_level=None,
                 created_by=None, created_date=None, account_status=None):
        self.admin_id = admin_id
        self.full_name = full_name
        self.email = email
        self.phone_number = phone_number
        self.username = username
        self.password_hash = password_hash
        self.admin_level = admin_level
        self.created_by = created_by
        self.created_date = created_date
        self.account_status = account_status

    @staticmethod
    def _row_to_admin(row):
        if not row:
            return None
        return Admin(
            admin_id=row.get("Admin_ID"),
            full_name=row.get("Full_Name"),
            email=row.get("Email"),
            phone_number=row.get("Phone_Number"),
            username=row.get("Username"),
            password_hash=row.get("Password_Hash"),
            admin_level=row.get("Admin_Level"),
            created_by=row.get("Created_By"),
            created_date=row.get("Created_Date"),
            account_status=row.get("Account_Status"),
        )

    # ==================== CREATE ====================
    @classmethod
    def create(cls, full_name, email, phone_number, username, password_hash,
               admin_level, created_by):
        db = Database.get_instance()
        query = """
            INSERT INTO Administrators
            (Full_Name, Email, Phone_Number, Username, Password_Hash,
             Admin_Level, Created_By, Created_Date, Account_Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (full_name, email, phone_number, username, password_hash,
                   admin_level, created_by, datetime.now(), "Active")
        return db.execute_query(query, params, commit=True)

    # ==================== READ ====================
    @classmethod
    def get_by_id(cls, admin_id):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Administrators WHERE Admin_ID = %s", (admin_id,))
        return cls._row_to_admin(row)

    @classmethod
    def get_by_username(cls, username):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Administrators WHERE Username = %s", (username,))
        return cls._row_to_admin(row)

    @classmethod
    def get_by_email(cls, email):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Administrators WHERE Email = %s", (email,))
        return cls._row_to_admin(row)

    @classmethod
    def get_by_username_or_email(cls, identifier):
        """Used at admin login time - identifier can be either a Username or an Email."""
        db = Database.get_instance()
        row = db.fetch_one(
            "SELECT * FROM Administrators WHERE (Username = %s OR Email = %s)",
            (identifier, identifier),
        )
        return cls._row_to_admin(row)

    @classmethod
    def get_all(cls):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * FROM Administrators ORDER BY Admin_ID")
        return [cls._row_to_admin(r) for r in rows]

    # ==================== UPDATE ====================
    @classmethod
    def update_status(cls, admin_id, status):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Administrators SET Account_Status = %s WHERE Admin_ID = %s",
            (status, admin_id), commit=True,
        )

    @classmethod
    def update_password(cls, admin_id, new_password_hash):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Administrators SET Password_Hash = %s WHERE Admin_ID = %s",
            (new_password_hash, admin_id), commit=True,
        )

    # ==================== PROMOTION ====================
    @classmethod
    def promote_from_user(cls, user, admin_level, created_by, password_hash=None):
        """
        Copies a User's data into the Administrators table (Feature 12: Promote
        User To Admin). The original User record in the Users table is left
        completely untouched, so the person keeps their normal user account too.
        """
        db = Database.get_instance()
        query = """
            INSERT INTO Administrators
            (Full_Name, Email, Phone_Number, Username, Password_Hash,
             Admin_Level, Created_By, Created_Date, Account_Status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            user.full_name, user.email, user.phone_number, user.username,
            password_hash or user.password_hash, admin_level, created_by,
            datetime.now(), "Active",
        )
        return db.execute_query(query, params, commit=True)

    # ==================== DELETE ====================
    @classmethod
    def delete(cls, admin_id):
        """Hard delete of an admin account (admins are few and managed carefully)."""
        db = Database.get_instance()
        db.execute_query("DELETE FROM Administrators WHERE Admin_ID = %s", (admin_id,), commit=True)
