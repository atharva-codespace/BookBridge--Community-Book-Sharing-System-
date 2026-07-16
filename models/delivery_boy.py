"""
models/delivery_boy.py
Defines the DeliveryBoy entity and all database operations (CRUD) for the
Delivery_Boys table. Delivery boy accounts can only be created by an admin
(Admin Dashboard -> Delivery Management -> Register Delivery Boy) - there is
no self-registration, mirroring how Administrators are created.
"""

from datetime import datetime
from database.db import Database


class DeliveryBoy:
    """Represents a single row from the Delivery_Boys table plus all CRUD operations."""

    def __init__(self, delivery_boy_id=None, full_name=None, email=None, phone_number=None,
                 username=None, password_hash=None, vehicle_info=None, account_status=None,
                 created_by=None, created_date=None):
        self.delivery_boy_id = delivery_boy_id
        self.full_name = full_name
        self.email = email
        self.phone_number = phone_number
        self.username = username
        self.password_hash = password_hash
        self.vehicle_info = vehicle_info
        self.account_status = account_status
        self.created_by = created_by
        self.created_date = created_date

    @staticmethod
    def _row_to_delivery_boy(row):
        if not row:
            return None
        return DeliveryBoy(
            delivery_boy_id=row.get("Delivery_Boy_ID"),
            full_name=row.get("Full_Name"),
            email=row.get("Email"),
            phone_number=row.get("Phone_Number"),
            username=row.get("Username"),
            password_hash=row.get("Password_Hash"),
            vehicle_info=row.get("Vehicle_Info"),
            account_status=row.get("Account_Status"),
            created_by=row.get("Created_By"),
            created_date=row.get("Created_Date"),
        )

    # ==================== CREATE ====================
    @classmethod
    def create(cls, full_name, email, phone_number, username, password_hash,
               vehicle_info, created_by):
        db = Database.get_instance()
        query = """
            INSERT INTO Delivery_Boys
            (Full_Name, Email, Phone_Number, Username, Password_Hash,
             Vehicle_Info, Account_Status, Created_By, Created_Date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (full_name, email, phone_number, username, password_hash,
                  vehicle_info, "Active", created_by, datetime.now())
        return db.execute_query(query, params, commit=True)

    # ==================== READ ====================
    @classmethod
    def get_by_id(cls, delivery_boy_id):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Delivery_Boys WHERE Delivery_Boy_ID = %s", (delivery_boy_id,))
        return cls._row_to_delivery_boy(row)

    @classmethod
    def get_by_username(cls, username):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Delivery_Boys WHERE Username = %s", (username,))
        return cls._row_to_delivery_boy(row)

    @classmethod
    def get_by_email(cls, email):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Delivery_Boys WHERE Email = %s", (email,))
        return cls._row_to_delivery_boy(row)

    @classmethod
    def get_by_username_or_email(cls, identifier):
        """Used at delivery boy login time - identifier can be a Username or an Email."""
        db = Database.get_instance()
        row = db.fetch_one(
            "SELECT * FROM Delivery_Boys WHERE (Username = %s OR Email = %s)",
            (identifier, identifier),
        )
        return cls._row_to_delivery_boy(row)

    @classmethod
    def get_all(cls):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * FROM Delivery_Boys ORDER BY Delivery_Boy_ID")
        return [cls._row_to_delivery_boy(r) for r in rows]

    @classmethod
    def get_all_active(cls):
        db = Database.get_instance()
        rows = db.fetch_all(
            "SELECT * FROM Delivery_Boys WHERE Account_Status = 'Active' ORDER BY Delivery_Boy_ID"
        )
        return [cls._row_to_delivery_boy(r) for r in rows]

    # ==================== UPDATE ====================
    @classmethod
    def update_status(cls, delivery_boy_id, status):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Delivery_Boys SET Account_Status = %s WHERE Delivery_Boy_ID = %s",
            (status, delivery_boy_id), commit=True,
        )

    @classmethod
    def update_password(cls, delivery_boy_id, new_password_hash):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Delivery_Boys SET Password_Hash = %s WHERE Delivery_Boy_ID = %s",
            (new_password_hash, delivery_boy_id), commit=True,
        )

    # ==================== DELETE ====================
    @classmethod
    def delete(cls, delivery_boy_id):
        db = Database.get_instance()
        db.execute_query(
            "DELETE FROM Delivery_Boys WHERE Delivery_Boy_ID = %s",
            (delivery_boy_id,), commit=True,
        )
