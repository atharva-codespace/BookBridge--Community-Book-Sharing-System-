"""
services/request_service.py
Module 4 (Book Request, Reservation & Wishlist Management) business logic,
tied to the logged-in Session instead of the hardcoded requester_id/user_id = 1
used throughout the original prototype at
D:\\Atharva's ITR\\project\\module4\\BookBank. Also fixes that prototype's
Request constructor bug (the message argument silently landed in a
request_type parameter and was lost) and makes Notifications persist to the
database instead of living only in an in-memory list.

Flow: there is no owner-approval step. "Request Book" immediately marks the
book Sold/Donated/Exchanged (per its Listing_Type) and logs a Book_Requests
row - which also doubles as the review-eligibility record. "Reserve Book"
immediately marks the book Reserved and creates a Reservation, which is
later resolved via Complete (book flips to its final status) or Cancel
(book reverts to Available). Either action notifies the book's owner.
"""

from models.book import Book
from models.book_request import BookRequest
from models.notification import Notification
from models.reservation import Reservation
from models.wishlist import Wishlist
from utils.helpers import confirm_action, print_table

WISHLIST_FIELDS = ["Wishlist_ID", "Book_Title"]
REQUEST_FIELDS = ["Request_ID", "Book_Title", "Request_Date"]
RESERVATION_FIELDS = ["Reservation_ID", "Book_name", "Expiry_date", "Status"]
NOTIFICATION_FIELDS = ["Notification_ID", "Message", "Status", "Created_Date"]

AVAILABILITY_ON_FULFILL = {
    "Sale": "Sold",
    "Donation": "Donated",
    "Exchange": "Exchanged",
}


def _wishlist_to_row(w):
    return {"Wishlist_ID": w.wishlist_id, "Book_Title": w.book_title,
            }


def _request_to_row(r):
    return {"Request_ID": r.request_id, "Book_Title": r.book_name,
            "Requester_Name": r.user_id, "Request_Date": r.request_date}


def _reservation_to_row(r):
    return {"Reservation_ID": r.reservation_id, "Book_name": r.book_name,
            "Expiry_date": r.expiry_date, "Status": r.status}


def _notification_to_row(n):
    return {"Notification_ID": n.notification_id, "Message": n.message,
            "Status": n.status, "Created_Date": n.created_date}


def _availability_block_message(availability):
    """Returns a specific reason a book can't be requested/reserved, or None if it's free."""
    if availability == "Available":
        return None
    if availability == "Reserved":
        return "This book is already reserved."
    if availability in ("Sold", "Donated", "Exchanged"):
        return f"This book is already {availability.lower()}."
    return "This book is not available."


class RequestService:
    """Implements every Wishlist, Request, Reservation, and Notification operation."""

    def __init__(self, session):
        self.session = session

    # ==================== WISHLIST ====================
    def add_to_wishlist(self):
        bname= input("Enter Book Name to add to your wishlist: ").strip()
        if not Book.search("title",bname):
            print("Book not found.")
            return
        book_name = bname
        if Wishlist.exists(self.session.user_id, book_name):
            print("This book is already in your wishlist.")
            return
        Wishlist.add(self.session.user_id, bname)
        print("Book added to your wishlist.")

    def remove_from_wishlist(self):
        bwname = input("Enter Book Name to remove from Wishlist: ").strip()
        if not Book.searchinwishlist("title",bwname):
            print("Invalid Book Name in Wishlist.")
            return
        entry = Wishlist.get_by_id(bwname)
        if not entry or entry.user_id != self.session.user_id:
            print("Wishlist entry not found.")
            return
        Wishlist.remove(entry.wishlist_id)
        print("Book removed from your wishlist.")

    def view_wishlist(self):
        entries = Wishlist.get_by_user(self.session.user_id)
        print_table([_wishlist_to_row(w) for w in entries], headers=WISHLIST_FIELDS, title="MY WISHLIST")

    # ==================== REQUEST BOOK (instant, no approval) ====================
    def request_book(self):
        book = self._select_available_book()
        if not book:
            return

        message = input("Message to the owner (optional): ").strip() or None
        BookRequest.create(book.title, self.session.user_id)

        final_status = AVAILABILITY_ON_FULFILL.get(book.listing_type, "Sold")
        Book.update_availability(book.book_id, final_status)
        # Notification.create(
        #     book.owner_id,
        #     f"'{book.title}' was requested by {self.session.full_name} and marked as {final_status}.",
        # )
        print(f"Request successful. '{book.title}' is now {final_status}.")

    def view_my_sent_requests(self):
        requests = BookRequest.get_sent_by_user(self.session.user_id)
        print_table([_request_to_row(r) for r in requests], headers=REQUEST_FIELDS, title="MY REQUESTS")

    def view_requests_on_my_books(self):
        """Read-only history for an owner: who requested their listings."""
        requests = BookRequest.get_received_by_owner(self.session.user_id)
        print_table([_request_to_row(r) for r in requests], headers=REQUEST_FIELDS,
                    title="REQUESTS ON MY BOOKS")

    # ==================== RESERVE BOOK (instant, no approval) ====================
    def reserve_book(self):
        book = self._select_available_book()
        if not book:
            return

        Reservation.create(book.title, self.session.user_id)
        Book.update_availability(book.book_id, "Reserved")
        # Notification.create(
        #     book.owner_id,
        #     f"'{book.title}' was reserved by {self.session.full_name}.",
        # )
        print(f"'{book.title}' has been reserved for you.")

    def _select_available_book(self):
        bname = input("Enter Book Name: ").strip()
        
        book = Book.search_by_availability(bname)
        if not book:
            print("Book not found.")
            return None
        
        if book.owner_id == self.session.user_id:
            print("You cannot request or reserve your own book listing.")
            return None
        block_reason = _availability_block_message(book.availability)
        if block_reason:
            print(block_reason)
            return None
        return book

    # ==================== RESERVATIONS ====================
    def view_my_reservations(self):
        reservations = Reservation.get_by_user(self.session.user_id)
        print_table([_reservation_to_row(r) for r in reservations], headers=RESERVATION_FIELDS,
                    title="MY RESERVATIONS")

    def view_reservations_on_my_books(self):
        """Read-only history for an owner: who reserved their listings."""
        reservations = Reservation.get_by_owner(self.session.user_id)
        print_table([_reservation_to_row(r) for r in reservations], headers=RESERVATION_FIELDS,
                    title="RESERVATIONS ON MY BOOKS")

    def complete_reservation(self):
        reservation = self._select_own_active_reservation()
        if not reservation:
            return
        book = Book.get_by_id(reservation.book_name)
        Reservation.update_status(reservation.reservation_id, "Completed")
        new_status = AVAILABILITY_ON_FULFILL.get(book.availability, "Sold")
        Book.update_availability(reservation.book_id, new_status)
        print(f"Reservation completed. Book marked as '{new_status}'.")

    def cancel_reservation(self):
        reservation = self._select_own_active_reservation()
        if not reservation:
            return
        Reservation.update_status(reservation.reservation_id, "Cancelled")
        Book.update_availability(reservation.book_name, "Available")
        print("Reservation cancelled. The book is available again.")

    def _select_own_active_reservation(self):
        rbook = input("Enter Reserved Book Name: ").strip()
        if not Book.searchinreservations("title",rbook):
            print("Invalid Reservation ID.")
            return None
        reservation = Reservation.get_by_id(rbook)
        if not reservation or reservation.user_id != self.session.user_id:
            print("Reservation not found.")
            return None
        if reservation.status != "Active":
            print(f"This reservation is already {reservation.status}.")
            return None
        return reservation

    # ==================== NOTIFICATIONS ====================
    def view_notifications(self):
        notifications = Notification.get_by_user(self.session.user_id)
        unread = Notification.count_unread(self.session.user_id)
        print_table([_notification_to_row(n) for n in notifications], headers=NOTIFICATION_FIELDS,
                    title="MY NOTIFICATIONS")
        print(f"Unread: {unread}")

    def mark_notification_read(self):
        nid = input("Enter Notification ID to mark as read: ").strip()
        if not nid.isdigit():
            print("Invalid Notification ID.")
            return
        Notification.mark_read(int(nid))
        print("Notification marked as read.")

    # ==================== ADMIN OVERVIEW ====================
    def admin_view_all_requests(self):
        requests = BookRequest.get_all()
        print_table([_request_to_row(r) for r in requests], headers=REQUEST_FIELDS,
                    title="ALL REQUESTS (ADMIN VIEW)")

    def admin_view_all_reservations(self):
        reservations = Reservation.get_all()
        print_table([_reservation_to_row(r) for r in reservations], headers=RESERVATION_FIELDS,
                    title="ALL RESERVATIONS (ADMIN VIEW)")

    def admin_expire_reservation(self):
        rid = input("Enter Reservation ID to force-expire: ").strip()
        if not rid.isdigit():
            print("Invalid Reservation ID.")
            return
        reservation = Reservation.get_by_id(int(rid))
        if not reservation or reservation.status != "Active":
            print("No active reservation with that ID.")
            return
        if not confirm_action(f"Expire reservation for '{reservation.book_title}'?"):
            print("Cancelled.")
            return
        Reservation.update_status(reservation.reservation_id, "Expired")
        Book.update_availability(reservation.book_id, "Available")
        print("Reservation expired. The book is available again.")
