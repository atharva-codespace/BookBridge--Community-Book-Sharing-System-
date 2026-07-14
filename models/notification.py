"""
models/notification.py
Defines the Notification entity and all database operations for the
Notifications table (Module 4: Book Request, Reservation & Wishlist Management).

The original prototype (models/notification.py, services/notification_management.py
in D:\\Atharva's ITR\\project\\module4\\BookBank) only appended Notification objects
to an in-memory Python list, so every notification was lost when the program
exited even though an unused SQL table existed for them. This version actually
persists notifications to the database.
"""

from database.db import Database


class Notification:
    """Represents a single row from the Notifications table plus all CRUD operations."""

    def __init__(self, notification_id=None, user_id=None, message=None, status=None,
                 created_date=None):
        self.notification_id = notification_id
        self.user_id = user_id
        self.message = message
        self.status = status
        self.created_date = created_date

    @staticmethod
    def _row_to_notification(row):
        if not row:
            return None
        return Notification(
            notification_id=row.get("notification_id"),
            user_id=row.get("user_id"),
            message=row.get("message"),
            status=row.get("status"),
            created_date=row.get("notification_date"),
        )

    # ==================== CREATE ====================
    @classmethod
    def create(cls, user_id, message):
        db = Database.get_instance()
        return db.execute_query(
            "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
            (user_id, message), commit=True,
        )

    # ==================== READ ====================
    @classmethod
    def get_by_user(cls, user_id):
        db = Database.get_instance()
        rows = db.fetch_all(
            "SELECT * FROM notifications WHERE user_id = %s ORDER BY notification_id DESC",
            (user_id,),
        )
        return [cls._row_to_notification(r) for r in rows]

    @classmethod
    def count_unread(cls, user_id):
        db = Database.get_instance()
        row = db.fetch_one(
            "SELECT COUNT(*) AS total FROM notifications WHERE user_id = %s AND status IS NULL",
            (user_id,),
        )
        return row["total"] if row else 0

    # ==================== UPDATE ====================
    @classmethod
    def mark_read(cls, notification_id):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE notifications SET status = 'Read' WHERE notification_id = %s",
            (notification_id,), commit=True,
        )
