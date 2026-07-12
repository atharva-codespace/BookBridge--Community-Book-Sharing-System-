"""
models/wishlist.py
Defines the Wishlist entity and all database operations for the
Wishlist table (Module 4: Book Request, Reservation & Wishlist Management).
Books are referenced by Book_ID (not by name) so a listing can be renamed
or duplicated without breaking a user's wishlist.
"""

from database.db import Database


class Wishlist:
    """Represents a single row from the Wishlist table plus all Wishlist operations."""

    def __init__(self, wishlist_id=None, user_id=None, book_id=None, added_date=None,
                 book_title=None, availability=None):
        self.wishlist_id = wishlist_id
        self.user_id = user_id
        self.book_id = book_id
        self.added_date = added_date
        self.book_title = book_title
        self.availability = availability

    @staticmethod
    def _row_to_wishlist(row):
        if not row:
            return None
        return Wishlist(
            wishlist_id=row.get("Wishlist_ID"),
            user_id=row.get("User_ID"),
            book_id=row.get("Book_ID"),
            added_date=row.get("Added_Date"),
            book_title=row.get("Title"),
            availability=row.get("Availability"),
        )

    # ==================== CREATE ====================
    @classmethod
    def add(cls, user_id, book_id):
        db = Database.get_instance()
        return db.execute_query(
            "INSERT INTO Wishlist (user_id, book_name) VALUES (%s, %s)",
            (user_id, book_id), commit=True,
        )

    # ==================== READ ====================
    @classmethod
    def exists(cls, user_id, book_id):
        db = Database.get_instance()
        row = db.fetch_one(
            "SELECT * FROM Wishlist WHERE User_ID = %s AND Book_ID = %s",
            (user_id, book_id),
        )
        return row is not None

    @classmethod
    def get_by_user(cls, user_id):
        db = Database.get_instance()
        rows = db.fetch_all(
            """
            SELECT w.*, b.Title, b.Availability
            FROM Wishlist w
            JOIN Books b ON b.Book_ID = w.Book_ID
            WHERE w.User_ID = %s
            ORDER BY w.Added_Date DESC
            """,
            (user_id,),
        )
        return [cls._row_to_wishlist(r) for r in rows]

    @classmethod
    def get_by_id(cls, wishlist_id):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Wishlist WHERE Wishlist_ID = %s", (wishlist_id,))
        return cls._row_to_wishlist(row)

    # ==================== DELETE ====================
    @classmethod
    def remove(cls, wishlist_id):
        db = Database.get_instance()
        db.execute_query("DELETE FROM Wishlist WHERE Wishlist_ID = %s", (wishlist_id,), commit=True)
