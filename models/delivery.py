"""
models/delivery.py
Defines the Delivery entity and all database operations for the Deliveries
table. A Delivery row is created automatically the moment an admin approves
a book request (see services/request_service.py ->
admin_review_pending_requests), starting out unassigned ('Pending'). An
admin then assigns it to a Delivery Boy (Admin Dashboard -> Delivery
Management -> Assign Delivery Boy), who sees it on their own dashboard and
moves it through Picked Up -> Delivered.
"""

from datetime import datetime
from database.db import Database


class Delivery:
    """Represents a single row from the Deliveries table plus all CRUD operations."""

    def __init__(self, delivery_id=None, request_id=None, delivery_boy_id=None,
                 book_name=None, requester_id=None, pickup_name=None, pickup_phone=None,
                 pickup_location=None, drop_name=None, drop_phone=None, drop_location=None,
                 expected_delivery_date=None, delivered_date=None, status=None,
                 created_date=None):
        self.delivery_id = delivery_id
        self.request_id = request_id
        self.delivery_boy_id = delivery_boy_id
        self.book_name = book_name
        self.requester_id = requester_id
        self.pickup_name = pickup_name
        self.pickup_phone = pickup_phone
        self.pickup_location = pickup_location
        self.drop_name = drop_name
        self.drop_phone = drop_phone
        self.drop_location = drop_location
        self.expected_delivery_date = expected_delivery_date
        self.delivered_date = delivered_date
        self.status = status
        self.created_date = created_date

    @staticmethod
    def _row_to_delivery(row):
        if not row:
            return None
        return Delivery(
            delivery_id=row.get("Delivery_ID"),
            request_id=row.get("Request_ID"),
            delivery_boy_id=row.get("Delivery_Boy_ID"),
            book_name=row.get("Book_Name"),
            requester_id=row.get("Requester_ID"),
            pickup_name=row.get("Pickup_Name"),
            pickup_phone=row.get("Pickup_Phone"),
            pickup_location=row.get("Pickup_Location"),
            drop_name=row.get("Drop_Name"),
            drop_phone=row.get("Drop_Phone"),
            drop_location=row.get("Drop_Location"),
            expected_delivery_date=row.get("Expected_Delivery_Date"),
            delivered_date=row.get("Delivered_Date"),
            status=row.get("Status"),
            created_date=row.get("Created_Date"),
        )

    # ==================== CREATE ====================
    @classmethod
    def create(cls, request_id, book_name, requester_id, pickup_name, pickup_phone,
               pickup_location, drop_name, drop_phone, drop_location, expected_delivery_date):
        db = Database.get_instance()
        query = """
            INSERT INTO Deliveries
            (Request_ID, Book_Name, Requester_ID, Pickup_Name, Pickup_Phone,
             Pickup_Location, Drop_Name, Drop_Phone, Drop_Location,
             Expected_Delivery_Date, Status, Created_Date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (request_id, book_name, requester_id, pickup_name, pickup_phone,
                  pickup_location, drop_name, drop_phone, drop_location,
                  expected_delivery_date, "Pending", datetime.now())
        return db.execute_query(query, params, commit=True)

    # ==================== READ ====================
    @classmethod
    def get_by_id(cls, delivery_id):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Deliveries WHERE Delivery_ID = %s", (delivery_id,))
        return cls._row_to_delivery(row)

    @classmethod
    def get_all(cls):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * FROM Deliveries ORDER BY Delivery_ID DESC")
        return [cls._row_to_delivery(r) for r in rows]

    @classmethod
    def get_unassigned(cls):
        db = Database.get_instance()
        rows = db.fetch_all(
            "SELECT * FROM Deliveries WHERE Status = 'Pending' ORDER BY Delivery_ID",
        )
        return [cls._row_to_delivery(r) for r in rows]

    @classmethod
    def get_by_delivery_boy(cls, delivery_boy_id):
        db = Database.get_instance()
        rows = db.fetch_all(
            "SELECT * FROM Deliveries WHERE Delivery_Boy_ID = %s ORDER BY Delivery_ID DESC",
            (delivery_boy_id,),
        )
        return [cls._row_to_delivery(r) for r in rows]

    # ==================== UPDATE ====================
    @classmethod
    def assign(cls, delivery_id, delivery_boy_id):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Deliveries SET Delivery_Boy_ID = %s, Status = 'Assigned' WHERE Delivery_ID = %s",
            (delivery_boy_id, delivery_id), commit=True,
        )

    @classmethod
    def update_status(cls, delivery_id, status, delivered_date=None):
        db = Database.get_instance()
        if delivered_date is not None:
            db.execute_query(
                "UPDATE Deliveries SET Status = %s, Delivered_Date = %s WHERE Delivery_ID = %s",
                (status, delivered_date, delivery_id), commit=True,
            )
        else:
            db.execute_query(
                "UPDATE Deliveries SET Status = %s WHERE Delivery_ID = %s",
                (status, delivery_id), commit=True,
            )
