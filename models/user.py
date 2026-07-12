"""
models/user.py
Defines the User entity and all database operations (CRUD) for the
Users table. Every SQL statement below uses parameterized queries
(%s placeholders + a params tuple) so user input can never be
interpreted as SQL code (prevents SQL Injection).
"""

from datetime import datetime
from database.db import Database


class User:
    """Represents a single row from the Users table plus all Users CRUD operations."""

    def __init__(self, user_id=None, full_name=None, email=None, phone_number=None,
                 location=None, username=None, password_hash=None, role=None,
                 account_status=None, account_created_date=None,
                 security_question=None, security_answer_hash=None, is_deleted=0):
        self.user_id = user_id
        self.full_name = full_name
        self.email = email
        self.phone_number = phone_number
        self.location = location
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.account_status = account_status
        self.account_created_date = account_created_date
        self.security_question = security_question
        self.security_answer_hash = security_answer_hash
        self.is_deleted = is_deleted

    @staticmethod
    def _row_to_user(row):
        """Converts a DB row (dict) into a User object. Returns None for an empty row."""
        if not row:
            return None
        return User(
            user_id=row.get("User_ID"),
            full_name=row.get("Full_Name"),
            email=row.get("Email"),
            phone_number=row.get("Phone_Number"),
            location=row.get("Location"),
            username=row.get("Username"),
            password_hash=row.get("Password_Hash"),
            role=row.get("Role"),
            account_status=row.get("Account_Status"),
            account_created_date=row.get("Account_Created_Date"),
            security_question=row.get("Security_Question"),
            security_answer_hash=row.get("Security_Answer_Hash"),
            is_deleted=row.get("Is_Deleted", 0),
        )

    # ==================== CREATE ====================
    @classmethod
    def create(cls, full_name, email, phone_number, location, username,
               password_hash, role=None, security_question=None, security_answer_hash=None):
        """Inserts a new user into the Users table and returns the new User_ID."""
        db = Database.get_instance()
        query = """
            INSERT INTO Users
            (Full_Name, Email, Phone_Number, Location, Username, Password_Hash,
             Role, Account_Status, Account_Created_Date, Security_Question, Security_Answer_Hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (full_name, email, phone_number, location, username, password_hash,
                   role, "Active", datetime.now(), security_question, security_answer_hash)
        return db.execute_query(query, params, commit=True)

    # ==================== READ ====================
    @classmethod
    def get_by_id(cls, user_id):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Users WHERE User_ID = %s AND Is_Deleted = 0", (user_id,))
        return cls._row_to_user(row)

    @classmethod
    def get_by_username(cls, username):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Users WHERE Username = %s AND Is_Deleted = 0", (username,))
        return cls._row_to_user(row)

    @classmethod
    def get_by_email(cls, email):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Users WHERE Email = %s AND Is_Deleted = 0", (email,))
        return cls._row_to_user(row)

    @classmethod
    def get_by_phone(cls, phone_number):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Users WHERE Phone_Number = %s AND Is_Deleted = 0", (phone_number,))
        return cls._row_to_user(row)

    @classmethod
    def get_by_username_or_email(cls, identifier):
        """Used at login time - identifier can be either a Username or an Email."""
        db = Database.get_instance()
        row = db.fetch_one(
            "SELECT * FROM Users WHERE (Username = %s OR Email = %s) AND Is_Deleted = 0",
            (identifier, identifier),
        )
        return cls._row_to_user(row)

    @classmethod
    def get_all(cls):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * FROM Users WHERE Is_Deleted = 0 ORDER BY User_ID")
        return [cls._row_to_user(r) for r in rows]

    @classmethod
    def search(cls, keyword):
        """Searches active users by username, email, or exact user id."""
        db = Database.get_instance()
        like = f"%{keyword}%"
        rows = db.fetch_all(
            """SELECT * FROM Users
               WHERE Is_Deleted = 0
               AND (Username LIKE %s OR Email LIKE %s OR CAST(User_ID AS CHAR) = %s)""",
            (like, like, keyword),
        )
        return [cls._row_to_user(r) for r in rows]

    # ==================== UPDATE ====================
    @classmethod
    def update_profile(cls, user_id, full_name, email, phone_number, location):
        db = Database.get_instance()
        query = """
            UPDATE Users
            SET Full_Name = %s, Email = %s, Phone_Number = %s, Location = %s
            WHERE User_ID = %s
        """
        db.execute_query(query, (full_name, email, phone_number, location, user_id), commit=True)

    @classmethod
    def update_password(cls, user_id, new_password_hash):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Users SET Password_Hash = %s WHERE User_ID = %s",
            (new_password_hash, user_id), commit=True,
        )

    @classmethod
    def update_status(cls, user_id, status):
        """Status must be 'Active' or 'Inactive'."""
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Users SET Account_Status = %s WHERE User_ID = %s",
            (status, user_id), commit=True,
        )

    @classmethod
    def update_security_answer(cls, user_id, security_question, security_answer_hash):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Users SET Security_Question = %s, Security_Answer_Hash = %s WHERE User_ID = %s",
            (security_question, security_answer_hash, user_id), commit=True,
        )

    # ==================== DELETE (soft delete) ====================
    @classmethod
    def soft_delete(cls, user_id):
        """Soft delete is preferred over a hard DELETE so history/audit data is preserved."""
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Users SET Is_Deleted = 1, Account_Status = 'Inactive' WHERE User_ID = %s",
            (user_id,), commit=True,
        )
