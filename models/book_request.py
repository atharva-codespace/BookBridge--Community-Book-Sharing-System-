"""
models/book_request.py
Defines the BookRequest entity and all database operations for the
Book_Requests table (Module 4: Book Request, Reservation & Wishlist Management).

A "request" is an instant transaction (Request Book -> the book's
availability changes immediately, no owner-approval step), so a row here
represents an already-completed request. It also doubles as the
review-eligibility record: only a user with a Book_Requests row for a given
Book_ID may submit a review for that book (see services/review_service.py).

Ported from a standalone prototype (models/request.py, services/request_management.py
in D:\\Atharva's ITR\\project\\module4\\BookBank) which hardcoded requester_id=1,
referenced books by name instead of ID, and had a constructor bug that silently
dropped the request message. This version fixes all three and integrates with
the project's Database singleton and Session.
"""

from database.db import Database
from datetime import date

class BookRequest:
    """Represents a single row from the Book_Requests table plus all CRUD operations."""

    def __init__(self, request_id=None, book_name=None, user_id=None,
                request_date=None, status=None):
        self.request_id = request_id
        self.book_name = book_name
        self.user_id = user_id
        self.request_date = request_date
        self.status = status

    @staticmethod
    def _row_to_request(row):
        if not row:
            return None
        return BookRequest(
            request_id=row.get("request_id"),
            book_name=row.get("book_name"),
            user_id=row.get("user_id"),
            request_date=row.get("request_date"),
            status=row.get("status"),
        )

    _SELECT_WITH_NAMES = """
        SELECT br.*, b.Title,
               ru.Full_Name AS Requester_Name, ou.Full_Name AS Owner_Name
        FROM Book_Requests br
        JOIN Books b ON b.Book_ID = br.Book_ID
        JOIN Users ru ON ru.User_ID = br.Requester_ID
        JOIN Users ou ON ou.User_ID = br.Owner_ID
    """

    # ==================== CREATE ====================
    @classmethod
    def  create(cls, book_name, user_id, status="Pending"):
        db = Database.get_instance()
        date_today = date.today()
        query = """
            INSERT INTO requests (book_name, user_ID, request_date, status)
            VALUES (%s, %s, %s, %s)
        """
        return db.execute_query(query, (book_name, user_id, date_today, status), commit=True)

    # ==================== READ ====================
    @classmethod
    def get_by_id(cls, request_id):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * from requests WHERE Request_ID = %s", (request_id,))
        return cls._row_to_request(row)

    @classmethod
    def get_sent_by_user(cls, requester_id):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * from requests WHERE user_id = %s",
            (requester_id,),
        )
        return [cls._row_to_request(r) for r in rows]

    @classmethod
    def get_received_by_owner(cls, owner_id):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * from requests WHERE user_id = %s ORDER BY Request_ID DESC",
            (owner_id,),
        )
        return [cls._row_to_request(r) for r in rows]

    @classmethod
    def get_all(cls):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * from requests ORDER BY Request_ID DESC")
        return [cls._row_to_request(r) for r in rows]

    @classmethod
    def has_requested(cls, book_id, requester_id):
        """Review-eligibility check: has this user ever requested this book?"""
        db = Database.get_instance()
        row = db.fetch_one(
            "SELECT * FROM requests WHERE book_name = %s AND user_ID = %s",
            (book_id, requester_id),
        )
        return cls._row_to_request(row)

    @classmethod
    def get_pending(cls):
        """All requests awaiting an admin decision (admin approval queue)."""
        db = Database.get_instance()
        rows = db.fetch_all(
            "SELECT * from requests WHERE status = %s ORDER BY Request_ID DESC",
            ("Pending",),
        )
        return [cls._row_to_request(r) for r in rows]

    @classmethod
    def has_pending_request(cls, book_name):
        """Blocks a second request for the same book while one is awaiting admin decision."""
        db = Database.get_instance()
        row = db.fetch_one(
            "SELECT * FROM requests WHERE book_name = %s AND status = %s",
            (book_name, "Pending"),
        )
        return cls._row_to_request(row)

    # ==================== UPDATE ====================
    @classmethod
    def update_status(cls, request_id, status):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE requests SET status = %s WHERE Request_ID = %s",
            (status, request_id), commit=True,
        )
