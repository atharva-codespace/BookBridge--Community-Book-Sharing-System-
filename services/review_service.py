"""
services/review_service.py
Module 5 (User Ratings & Feedback System) business logic. Replaces the old
models/submit_review.py prototype, which imported `from reviewdb import
get_connection` (wrong path), ran input() at module import time, and
checked reviewer identity against a non-existent Users.user_id column
instead of the logged-in session.
"""

from models.book import Book
from models.book_request import BookRequest
from models.review import Review
from services.validation import Validation
from utils.helpers import confirm_action, get_non_empty_input, print_table

REVIEW_TABLE_FIELDS = ["Review_ID", "Rating", "Feedback_Comment", "Review_Date"]


def _review_to_row(review):
    return {
        "Review_ID": review.review_id,
        "Rating": review.rating,
        "Feedback_Comment": review.review,
        "Review_Date": review.review_date,
    }


def _print_reviews(reviews, title=None):
    print_table([_review_to_row(r) for r in reviews], headers=REVIEW_TABLE_FIELDS, title=title)


class ReviewService:
    """Implements every Ratings & Feedback operation."""

    def __init__(self, session):
        self.session = session

    # ==================== SUBMIT REVIEW ====================
    def submit_review(self):
        print("\n--- SUBMIT A REVIEW ---")
        book_id = None
        book_name = input("Enter Book Name to review (leave blank for general feedback): ").strip()
        requested_book = BookRequest.has_requested(book_name, self.session.user_id)
        if not requested_book:
                print("You can only review books you have requested. Review cancelled.")
                return
            # book_id = int(book_name)
            

        rating = input("Rating (1-5): ").strip()
        if not Validation.validate_rating(rating):
            print("Rating must be a whole number between 1 and 5. Review cancelled.")
            return

        feedback = get_non_empty_input("Feedback: ")

        Review.create(self.session.user_id, int(rating), feedback,self.session.user_id)
        print("Review submitted successfully!")

    # ==================== VIEW REVIEWS ====================
    def view_reviews_for_book(self):
        book_choice = input("Enter Book ID: ").strip()
        if not book_choice.isdigit():
            print("Invalid Book ID.")
            return
        reviews = Review.get_by_book(int(book_choice))
        avg_rating, total = Review.get_average_rating(int(book_choice))
        _print_reviews(reviews, title="REVIEWS FOR THIS BOOK")
        if total:
            print(f"Average Rating: {float(avg_rating):.1f} / 5 ({total} review(s))")

    def view_my_reviews(self):
        reviews = Review.get_by_reviewer(self.session.user_id)
        _print_reviews(reviews, title="MY REVIEWS")

    # ==================== ADMIN MODERATION ====================
    def admin_view_all_reviews(self):
        _print_reviews(Review.get_all(), title="ALL REVIEWS (ADMIN VIEW)")

    def admin_delete_review(self):
        rid = input("Enter Review ID to delete: ").strip()
        if not rid.isdigit():
            print("Invalid Review ID.")
            return
        if confirm_action("Confirm deletion of this review?"):
            Review.delete(int(rid))
            print("Review deleted successfully.")
        else:
            print("Deletion cancelled.")
