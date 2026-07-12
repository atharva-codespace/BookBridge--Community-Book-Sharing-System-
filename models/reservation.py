"""
models/reservation.py
Defines the Reservation entity and all database operations for the
Reservations table (Module 4: Book Request, Reservation & Wishlist Management).

A Reservation is created directly by the "Reserve Book" action - there is no
owner-approval step. It is later resolved via Complete (book flips to
Sold/Donated/Exchanged per its Listing_Type) or Cancel (book reverts to
Available). Ported from a standalone prototype whose model class defaulted
to a 1-day expiry while its service layer actually inserted 7 days - this
version keeps the 7-day expiry the prototype's runtime behavior actually used.
"""

from datetime import date, timedelta

from database.db import Database

RESERVATION_VALIDITY_DAYS = 7


class Reservation:
    """Represents a single row from the Reservations table plus all CRUD operations."""

    def __init__(self, reservation_id=None, book_id=None, user_id=None,
                 reserved_date=None, expiry_date=None, status=None, book_title=None):
        self.reservation_id = reservation_id
        self.book_id = book_id
        self.user_id = user_id
        self.reserved_date = reserved_date
        self.expiry_date = expiry_date
        self.status = status
        self.book_title = book_title

    @staticmethod
    def _row_to_reservation(row):
        if not row:
            return None
        return Reservation(
            reservation_id=row.get("Reservation_ID"),
            book_id=row.get("Book_ID"),
            user_id=row.get("User_ID"),
            reserved_date=row.get("Reserved_Date"),
            expiry_date=row.get("Expiry_Date"),
            status=row.get("Status"),
            book_title=row.get("Title"),
        )

    _SELECT_WITH_TITLE = """
        SELECT rv.*, b.Title
        FROM Reservations rv
        JOIN Books b ON b.Book_ID = rv.Book_ID
    """

    # ==================== CREATE ====================
    @classmethod
    def create(cls, book_id, user_id):
        db = Database.get_instance()
        expiry_date = date.today() + timedelta(days=RESERVATION_VALIDITY_DAYS)
        query = """
            INSERT INTO Reservations (Book_ID, User_ID, Expiry_Date, Status)
            VALUES (%s, %s, %s, 'Active')
        """
        return db.execute_query(query, (book_id, user_id, expiry_date), commit=True)

    # ==================== READ ====================
    @classmethod
    def get_by_id(cls, reservation_id):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM reservations WHERE Reservation_ID = %s", (reservation_id,))
        return cls._row_to_reservation(row)

    @classmethod
    def get_by_user(cls, user_id):
        db = Database.get_instance()
        rows = db.fetch_all(
            "SELECT * FROM reservations WHERE User_ID = %s ORDER BY Reservation_ID DESC",
            (user_id,),
        )
        return [cls._row_to_reservation(r) for r in rows]

    @classmethod
    def get_all(cls):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * FROM reservations ORDER BY Reservation_ID DESC")
        return [cls._row_to_reservation(r) for r in rows]

    @classmethod
    def get_by_owner(cls, owner_id):
        """Reservations held against books owned by owner_id (read-only activity view)."""
        db = Database.get_instance()
        rows = db.fetch_all(
            " SELECT * FROM reservations WHERE user_id = %s ORDER BY Reservation_ID DESC",
            (owner_id,),
        )
        return [cls._row_to_reservation(r) for r in rows]

    # ==================== UPDATE ====================
    @classmethod
    def update_status(cls, reservation_id, status):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Reservations SET Status = %s WHERE Reservation_ID = %s",
            (status, reservation_id), commit=True,
        )
