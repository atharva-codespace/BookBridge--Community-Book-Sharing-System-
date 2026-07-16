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

from datetime import date, timedelta

from models.admin import Admin
from models.book import Book
from models.book_request import BookRequest
from models.delivery import Delivery
from models.notification import Notification
from models.reservation import Reservation, MAX_RESERVATION_DAYS
from models.user import User
from models.wishlist import Wishlist
from utils.email_sender import send_admin_request_email
from utils.helpers import confirm_action, print_table

DELIVERY_LEAD_DAYS = 2

WISHLIST_FIELDS = ["Wishlist_ID", "Book_Title", "Price"]
REQUEST_FIELDS = ["Request_ID", "Book_Title", "Request_Date", "Status"]
RESERVATION_FIELDS = ["Reservation_ID", "Book_name", "Expiry_date", "Status"]
NOTIFICATION_FIELDS = ["Notification_ID", "Message", "status"]

AVAILABILITY_ON_FULFILL = {
    "Sale": "Sold",
    "Donation": "Donated",
    "Exchange": "Exchanged",
}


def _wishlist_to_row(w, price=None):
    return {"Wishlist_ID": w.wishlist_id, "Book_Title": w.book_title, "Price": price}


def _request_to_row(r):
    return {"Request_ID": r.request_id, "Book_Title": r.book_name,
            "Requester_Name": r.user_id, "Request_Date": r.request_date,
            "Status": r.status}


def _reservation_to_row(r):
    return {"Reservation_ID": r.reservation_id, "Book_name": r.book_name,
            "Expiry_date": r.expiry_date, "Status": r.status}


def _notification_to_row(n):
    return {"Notification_ID": n.notification_id, "Message": n.message, "status":n.status}


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
        rows = []
        for w in entries:
            book = Book.search_book(w.book_title)
            rows.append(_wishlist_to_row(w, price=book.price if book else "N/A"))
        print_table(rows, headers=WISHLIST_FIELDS, title="MY WISHLIST")

    def buy_from_wishlist(self):
        """Lets the user submit a purchase request straight from a wishlist entry,
        instead of having to re-type the book name under Request Book."""
        entries = Wishlist.get_by_user(self.session.user_id)
        if not entries:
            print("Your wishlist is empty.")
            return
        rows = []
        for w in entries:
            book = Book.search_book(w.book_title)
            rows.append(_wishlist_to_row(w, price=book.price if book else "N/A"))
        print_table(rows, headers=WISHLIST_FIELDS, title="MY WISHLIST")

        bname = input("Enter the Book Title (from above) to buy: ").strip()
        entry = next((w for w in entries if w.book_title.lower() == bname.lower()), None)
        if not entry:
            print("That title isn't in your wishlist.")
            return

        book = Book.search_book(entry.book_title)
        if not book:
            print("This book is no longer available.")
            return
        if book.owner_id == self.session.user_id:
            print("You cannot buy your own book listing.")
            return

        if book.availability == "Available":
            self._submit_request_for_book(book)
            return
        if book.availability == "Reserved":
            self._handle_unavailable_book(book, _availability_block_message(book.availability))
            self._submit_request_for_book(book, is_competing_claim=True)
            return
        print(_availability_block_message(book.availability))

    # ==================== REQUEST BOOK (needs admin approval) ====================
    def request_book(self):
        book, is_competing_claim = self._select_book_for_request()
        if not book:
            return
        self._submit_request_for_book(book, is_competing_claim=is_competing_claim)

    def _submit_request_for_book(self, book, is_competing_claim=False):
        """Shared by 'Request Book' and 'Buy From Wishlist' - creates the Pending
        request and emails admins for approval. `is_competing_claim` is True when
        the book is currently Reserved by someone else and this requester wants
        to buy it immediately - see _select_book_for_request()."""
        if BookRequest.has_pending_request(book.title):
            print("This book already has a pending request awaiting admin approval.")
            return

        input("Message to the owner (optional): ").strip()
        BookRequest.create(book.title, self.session.user_id)

        self._notify_admins_of_pending_request(book.title)
        if is_competing_claim:
            print(f"Your request for '{book.title}' has been queued. It's currently reserved by "
                  f"another user - we've told them you want to buy it right now. If they buy it "
                  f"first, your request will be automatically rejected. If they release it (or "
                  f"don't act in time), an admin will review and can approve your request instead.")
        else:
            print(f"Request submitted for '{book.title}'. An admin will review it and you'll be "
                  f"notified once it's approved or rejected.")

    def _notify_admins_of_pending_request(self, book_title):
        """Emails every active admin so they can approve/reject the request from
        Admin Dashboard -> Requests & Reservations Overview -> Review Pending Book Requests."""
        admins = Admin.get_all()
        for admin in admins:
            if admin.account_status != "Active" or not admin.email:
                continue
            try:
                send_admin_request_email(admin.email, self.session.full_name, book_title)
            except Exception as e:
                print(f"(Could not email admin {admin.email}: {e})")

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

        days_input = input(
            f"Reserve for how many days (1-{MAX_RESERVATION_DAYS}, max {MAX_RESERVATION_DAYS}): "
        ).strip()
        if not days_input.isdigit() or not (1 <= int(days_input) <= MAX_RESERVATION_DAYS):
            print(f"Invalid duration. Please enter a whole number between 1 and {MAX_RESERVATION_DAYS}.")
            return
        days = int(days_input)

        Reservation.create(book.title, self.session.user_id, days=days)
        Book.update_availability(book.title, "Reserved")
        # Notification.create(
        #     book.owner_id,
        #     f"'{book.title}' was reserved by {self.session.full_name}.",
        # )
        print(f"'{book.title}' has been reserved for you for {days} day(s).")

    def _select_available_book(self):
        """Used by 'Reserve Book': strictly requires the book to currently be
        Available. You can't reserve a book someone else already has reserved -
        see _select_book_for_request() for the Request-side competing-claim flow."""
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
            self._handle_unavailable_book(book, block_reason)
            return None
        return book

    def _select_book_for_request(self):
        """Used by 'Request Book' / 'Buy From Wishlist'. Unlike
        _select_available_book(), a book that is currently Reserved by someone
        else is NOT a dead end here: the requester's claim is allowed through
        as a 'competing claim' (returned as (book, True)) so User 2 can buy it
        via Request if the reservation holder doesn't buy it first. A book
        that's already Sold/Donated/Exchanged is still a hard block."""
        bname = input("Enter Book Name: ").strip()

        book = Book.search_book(bname)
        if not book:
            print("Book not found.")
            return None, False

        if book.owner_id == self.session.user_id:
            print("You cannot request your own book listing.")
            return None, False

        if book.availability == "Available":
            return book, False

        if book.availability == "Reserved":
            self._handle_unavailable_book(book, _availability_block_message(book.availability))
            return book, True

        print(_availability_block_message(book.availability))
        return None, False

    def _handle_unavailable_book(self, book, block_reason):
        """When a book can't be reserved (or is being requested while reserved)
        because someone else already has it Reserved, let that person know a
        second buyer is interested and ready to buy right now, so they can
        decide to buy now (Complete Reservation) or release it (Cancel
        Reservation) instead of just letting the 2nd user hit a dead end."""
        print(block_reason)
        if book.availability != "Reserved":
            return

        reservation = Reservation.get_by_id(book.title)
        if not reservation or reservation.status != "Active":
            return

        Notification.create(
            reservation.user_id,
            f"Another user wants to buy '{book.title}' right now. BUY THIS BOOK NOW: go to "
            f"My Requests & Reservations > Complete Reservation to claim it before they do. "
            f"Otherwise, do nothing (or use Cancel Reservation to release it early) and the "
            f"other user will be able to get it - your reservation otherwise holds until "
            f"{reservation.expiry_date}.",
        )
        print(f"'{book.title}' is currently reserved by another user until {reservation.expiry_date}. "
              f"We've notified them that you want to buy it immediately.")

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
        Book.update_availability(reservation.book_name, new_status)
        # Anyone who filed a competing request while this book was Reserved
        # (i.e. wanted to "buy it now" via Request) has lost the race - reject
        # their pending request instead of leaving it to an admin to notice.
        self._reject_competing_requests(book.title, reason="another user (the reservation holder) bought it first")
        print(f"Reservation completed. Book marked as '{new_status}'.")

    def cancel_reservation(self):
        reservation = self._select_own_active_reservation()
        if not reservation:
            return
        Reservation.update_status(reservation.reservation_id, "Cancelled")
        Book.update_availability(reservation.book_name, "Available")
        # If someone filed a competing request while this book was Reserved,
        # let them know it's now free and an admin will review their request.
        self._notify_pending_requesters_book_available(reservation.book_name)
        print("Reservation cancelled. The book is available again.")

    def _reject_competing_requests(self, book_title, reason):
        """Auto-rejects any Pending request(s) for a book once it's no longer
        obtainable (the reservation holder bought it), and notifies those
        requesters instead of leaving their request stuck as Pending forever."""
        for req in BookRequest.get_pending():
            if req.book_name == book_title:
                BookRequest.update_status(req.request_id, "Rejected")
                Notification.create(
                    req.user_id,
                    f"Your request for '{book_title}' was rejected because {reason}.",
                )

    def _notify_pending_requesters_book_available(self, book_title):
        """Lets anyone with a Pending request on a book know its reservation
        was released, so they know an admin can now approve their request."""
        for req in BookRequest.get_pending():
            if req.book_name == book_title:
                Notification.create(
                    req.user_id,
                    f"'{book_title}' is available again - its reservation was released. "
                    f"An admin will review your pending request.",
                )

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
        Book.update_availability(reservation.book_name, "Available")
        print("Reservation expired. The book is available again.")

    def admin_review_pending_requests(self):
        """Lets an admin approve or reject a book request. Only on approval does
        the book's availability actually change and the requester get notified."""
        pending = BookRequest.get_pending()
        print_table([_request_to_row(r) for r in pending], headers=REQUEST_FIELDS,
                    title="PENDING BOOK REQUESTS")
        if not pending:
            return

        rid = input("Enter Request ID to review (or press Enter to go back): ").strip()
        if not rid:
            return
        if not rid.isdigit():
            print("Invalid Request ID.")
            return

        request = BookRequest.get_by_id(int(rid))
        if not request or request.status != "Pending":
            print("No pending request with that ID.")
            return

        book = Book.get_by_id(request.book_name)
        if not book:
            print("The book for this request could not be found. Rejecting the request.")
            BookRequest.update_status(request.request_id, "Rejected")
            Notification.create(request.user_id, f"Your request for '{request.book_name}' was rejected.")
            return

        if book.availability in ("Sold", "Donated", "Exchanged"):
            print(f"'{book.title}' is already {book.availability.lower()} - this request can "
                  f"no longer be fulfilled. Rejecting it.")
            BookRequest.update_status(request.request_id, "Rejected")
            Notification.create(
                request.user_id,
                f"Your request for '{book.title}' was rejected because it is no longer available.",
            )
            return

        if book.availability == "Reserved":
            reservation = Reservation.get_by_id(book.title)
            if reservation and reservation.status == "Active" and reservation.user_id != request.user_id:
                print(f"Note: '{book.title}' is still actively reserved by another user until "
                      f"{reservation.expiry_date} (this requester wants to buy it now - a "
                      f"competing claim).")
                if not confirm_action("Approve this request anyway and override that reservation?"):
                    print("Left pending - review again once the reservation is completed, "
                          "cancelled, or force-expired.")
                    return
                Reservation.update_status(reservation.reservation_id, "Cancelled")
                Notification.create(
                    reservation.user_id,
                    f"Your reservation for '{book.title}' was overridden by an admin because "
                    f"another user's request was approved instead.",
                )

        if not confirm_action(f"Approve request for '{book.title}' from user #{request.user_id}?"):
            BookRequest.update_status(request.request_id, "Rejected")
            Notification.create(request.user_id, f"Your request for '{book.title}' was rejected by the admin.")
            print("Request rejected. The requester has been notified.")
            return

        final_status = AVAILABILITY_ON_FULFILL.get(book.listing_type, "Sold")
        Book.update_availability(book.title, final_status)
        BookRequest.update_status(request.request_id, "Approved")

        delivery_date = date.today() + timedelta(days=DELIVERY_LEAD_DAYS)
        Notification.create(
            request.user_id,
            f"Your request for '{book.title}' was approved. It is now marked as {final_status}. "
            f"Expected delivery date: {delivery_date}.",
        )
        self._create_delivery_record(request, book, delivery_date)
        print(f"Request approved. '{book.title}' is now {final_status}, delivery is expected "
              f"{delivery_date}, and the requester has been notified.")

    def _create_delivery_record(self, request, book, delivery_date):
        """Creates the unassigned Delivery row an admin will later hand to a
        delivery boy (Admin Dashboard -> Delivery Management -> Assign Delivery Boy)."""
        requester = User.get_by_id(request.user_id)
        try:
            Delivery.create(
                request_id=request.request_id,
                book_name=book.title,
                requester_id=request.user_id,
                pickup_name=book.seller_name,
                pickup_phone=book.phone,
                pickup_location=book.location,
                drop_name=requester.full_name if requester else None,
                drop_phone=requester.phone_number if requester else None,
                drop_location=requester.location if requester else None,
                expected_delivery_date=delivery_date,
            )
        except Exception as e:
            print(f"(Could not create a delivery record: {e})")
