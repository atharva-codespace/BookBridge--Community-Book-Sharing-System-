"""
models/review.py
Defines the Review entity and all database operations (CRUD) for the
Reviews table (Module 5: User Ratings & Feedback System).
"""

from database.db import Database


class Review:
    """Represents a single row from the Reviews table plus all Review CRUD operations."""

    def __init__(self, review_id=None, rating=None,
                 review=None, review_date=None):
        self.review_id = review_id
        self.rating = rating
        self.review = review
        self.review_date = review_date

    @staticmethod
    def _row_to_review(row):
        if not row:
            return None
        return Review(
            review_id=row.get("review_id"),
            rating=row.get("rating"),
            review=row.get("review"),
            review_date=row.get("review_date"),
        )

    # ==================== CREATE ====================
    @classmethod
    def create(cls, reviewer_id, rating, feedback_comment,user_id):
        db = Database.get_instance()
        query = """
            INSERT INTO reviews (review_ID, Rating, review,user_id)
            VALUES (%s, %s, %s,%s)
        """
        return db.execute_query(query, (reviewer_id, rating, feedback_comment, user_id), commit=True)

    # ==================== READ ====================
    _SELECT_WITH_NAMES = """
        SELECT r.*, u.Full_Name AS Reviewer_Name, b.Title AS Book_Title
        FROM Reviews r
        JOIN Users u ON u.User_ID = r.Reviewer_ID
        LEFT JOIN Books b ON b.Book_ID = r.Book_ID
    """

    @classmethod
    def get_by_book(cls, book_id):
        db = Database.get_instance()
        rows = db.fetch_all(
            cls._SELECT_WITH_NAMES + " WHERE r.Book_ID = %s ORDER BY r.Review_ID DESC",
            (book_id,),
        )
        return [cls._row_to_review(r) for r in rows]

    @classmethod
    def get_by_reviewer(cls, reviewer_id):
        db = Database.get_instance()
        rows = db.fetch_all(
             " SELECT * FROM reviews WHERE user_id = %s ORDER BY Review_ID DESC",
            (reviewer_id,),
        )
        return [cls._row_to_review(r) for r in rows]

    @classmethod
    def get_all(cls):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * FROM reviews  ORDER BY review_id DESC")
        return [cls._row_to_review(r) for r in rows]

    @classmethod
    def get_average_rating(cls, book_id):
        db = Database.get_instance()
        row = db.fetch_one(
            "SELECT AVG(Rating) AS avg_rating, COUNT(*) AS total FROM Reviews WHERE Book_ID = %s",
            (book_id,),
        )
        return (row.get("avg_rating"), row.get("total")) if row else (None, 0)

    # ==================== DELETE ====================
    @classmethod
    def delete(cls, review_id):
        db = Database.get_instance()
        db.execute_query("DELETE FROM Reviews WHERE Review_ID = %s", (review_id,), commit=True)
