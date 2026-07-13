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

    def __init__(self, wishlist_id=None, user_id=None, added_date=None,
                 book_title=None, ):
        self.wishlist_id = wishlist_id
        self.user_id = user_id
        self.added_date = added_date
        self.book_title = book_title

    @staticmethod
    def _row_to_wishlist(row):
        if not row:
            return None
        return Wishlist(
            wishlist_id=row.get("wishlist_id"),
            user_id=row.get("user_id"),
            added_date=row.get("date_added"),
            book_title=row.get("book_name"),
        )

    # ==================== CREATE ====================
    @classmethod
    def add(cls, user_id, book_name):
        db = Database.get_instance()
        return db.execute_query(
            "INSERT INTO wishlist (user_id, book_name) VALUES (%s, %s)",
            (user_id, book_name), commit=True,
        )

    # ==================== READ ====================
    @classmethod
    def exists(cls, user_id, book_name):
        db = Database.get_instance()
        row = db.fetch_one(
            "SELECT * FROM wishlist WHERE user_id = %s AND book_name = %s",
            (user_id, book_name),
        )
        return row is not None

    @classmethod
    def get_by_user(cls, user_id):
        db = Database.get_instance()
        rows = db.fetch_all(
            """
            SELECT *
            FROM wishlist 
            WHERE user_id = %s
            ORDER BY date_added DESC
            """,
            (user_id,),
        )
        return [cls._row_to_wishlist(r) for r in rows]

    @classmethod
    def get_by_id(cls, wishlist_name):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM wishlist WHERE book_name = %s", (wishlist_name,))
        return cls._row_to_wishlist(row)

    # ==================== DELETE ====================
    @classmethod
    def remove(cls, wishlist_id):
        db = Database.get_instance()
        db.execute_query("DELETE FROM wishlist WHERE wishlist_id = %s", (wishlist_id,), commit=True)
