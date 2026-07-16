"""
main.py
Entry point for the Book Bank Management System.

Run this file to start the console application:
    python main.py


This module wires every module together (Account & Profile, Book Inventory,
Book Search, Requests/Reservations/Wishlist, Ratings & Feedback, and Admin
Analytics) through a session-mode-aware menu hierarchy:
  - System Entry menu
  - Right after a User logs in, they choose this session's mode (Buy / Sell
    / Donate / Exchange), defaulting to their registered Role - the same
    account can act as a Buyer today and a Seller tomorrow without a second
    registration, and can switch mid-session via "Switch Mode"
  - Buyer Dashboard (top-level) -> feature submenus -> leaf action menus
  - Owner Dashboard (Seller / Donor / Exchange mode) -> feature submenus
  - Admin Dashboard (top-level) -> feature submenus -> leaf action menus
  - Dynamic Menu: only the dashboard matching the active session mode is
    ever shown
  - Global exception handling / invalid-choice handling at every level
"""

import sys

from database.db import Database
from models.admin import Admin
from services.authentication import Authentication, Session
from services.registration import Registration
from services.profile import ProfileManagement
from services.password import PasswordManagement
from services.admin_management import AdminManagement
from services.book_management import BookManagement
from services.review_service import ReviewService
from services.request_service import RequestService
from services.report_service import ReportService
from services.delivery_management import DeliveryManagement
from services.delivery_service import DeliveryService
from services.authorization import Authorization
from services.validation import Validation
from utils.hashing import Hashing
from utils.menus import (
    MODE_CHOICES,
    show_main_menu,
    show_mode_menu,
    show_buyer_dashboard,
    show_owner_dashboard,
    show_admin_dashboard,
    show_account_menu,
    show_marketplace_menu,
    show_buyer_actions_menu,
    show_wishlist_menu,
    show_my_requests_reservations_menu,
    show_my_listings_menu,
    show_owner_activity_menu,
    show_reviews_menu,
    show_reviews_menu_for_sell,
    show_notifications_menu,
    show_user_mgmt_menu,
    show_book_mgmt_menu,
    show_reviews_mod_menu,
    show_requests_overview_menu,
    show_reports_menu,
    show_delivery_mgmt_menu,
    show_delivery_boy_dashboard,
)
from utils.helpers import pause, get_non_empty_input

ROLE_TO_LISTING_TYPE = {
    "Seller": "Sale",
    "Donor": "Donation",
    "Exchange User": "Exchange",
}


# ======================================================================
# SHARED SUBMENU: MY ACCOUNT (every role)
# ======================================================================
def account_menu_loop(session, auth, profile, password_mgmt):
    """My Account: profile, password, preferences, activity history, account status."""
    while True:
        show_account_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                profile.view_profile()
            elif choice == "2":
                profile.edit_profile()
            elif choice == "3":
                password_mgmt.change_password()
            elif choice == "4":
                password_mgmt.forgot_password()
            elif choice == "5":
                profile.manage_notification_preferences()
            elif choice == "6":
                profile.manage_location_preferences()
            elif choice == "7":
                profile.view_login_history()
            elif choice == "8":
                profile.view_account_activity()
            elif choice == "9":
                if profile.deactivate_account():
                    auth.logout()
                    return
            elif choice == "10":
                if profile.delete_account():
                    auth.logout()
                    return
            elif choice == "11":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-11).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


        if not session.is_authenticated:
            return
        pause()


def reviews_menu_loop(review_service):
    """Ratings & feedback (Module 5) - shared by every role."""
    while True:
        show_reviews_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                review_service.submit_review()
            # elif choice == "2":
            #     review_service.view_reviews_for_book()
            elif choice == "2":
                review_service.view_my_reviews()
            elif choice == "3":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-4).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def notifications_menu_loop(request_service):
    """Shared by every role."""
    while True:
        show_notifications_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                request_service.view_notifications()
            elif choice == "2":
                request_service.mark_notification_read()
            elif choice == "3":
                # Lets someone act on a "buy this book now" notification right
                # here instead of having to separately go to My Requests &
                # Reservations - same underlying action as Complete Reservation.
                request_service.complete_reservation()
            elif choice == "4":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-4).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        pause()


# ======================================================================
# BUYER DASHBOARD - LEAF SUBMENUS
# ======================================================================
def marketplace_menu_loop(book_mgmt):
    """Browse & search the book marketplace (Module 3)."""
    while True:
        show_marketplace_menu()

        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                book_mgmt.browse_books()
            elif choice == "2":
                book_mgmt.search_books()
            elif choice == "3":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-3).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def buyer_actions_menu_loop(request_service):
    """Request Book (instant -> Sold/Donated/Exchanged) / Reserve Book (instant -> Reserved)."""


    while True:
        show_buyer_actions_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                request_service.request_book()
            elif choice == "2":
                request_service.reserve_book()
            elif choice == "3":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-3).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def wishlist_menu_loop(request_service):
    while True:
        show_wishlist_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                request_service.add_to_wishlist()
            elif choice == "2":
                request_service.remove_from_wishlist()
            elif choice == "3":
                request_service.view_wishlist()
            elif choice == "4":
                request_service.buy_from_wishlist()
            elif choice == "5":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-5).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def my_requests_reservations_menu_loop(request_service):
    while True:
        show_my_requests_reservations_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                request_service.view_my_sent_requests()
            elif choice == "2":
                request_service.view_my_reservations()
            elif choice == "3":
                request_service.complete_reservation()
            elif choice == "4":
                request_service.cancel_reservation()
            elif choice == "5":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-5).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def buyer_dashboard_loop(session, auth):
    """Buyer Role: browse/search, request/reserve books, wishlist, reviews, notifications."""
    profile = ProfileManagement(session)
    password_mgmt = PasswordManagement(session)
    book_mgmt = BookManagement(session)
    review_service = ReviewService(session)
    request_service = RequestService(session)

    while True:
        if not Authorization.require_user(session):
            return

        show_buyer_dashboard(session.username)
        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                account_menu_loop(session, auth, profile, password_mgmt)
            elif choice == "2":
                marketplace_menu_loop(book_mgmt)
            elif choice == "3":
                buyer_actions_menu_loop(request_service)
            elif choice == "4":
                wishlist_menu_loop(request_service)
            elif choice == "5":
                my_requests_reservations_menu_loop(request_service)
            elif choice == "6":
                reviews_menu_loop(review_service)
            elif choice == "7":
                notifications_menu_loop(request_service)
            elif choice == "8":
                return  # Switch Mode: back to mode selection, still logged in
            elif choice == "9":
                auth.logout()
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-9).")
                pause()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            pause()

        if not session.is_authenticated:
            return


# ======================================================================
# OWNER DASHBOARD (Seller / Donor / Exchange mode) - LEAF SUBMENUS
# ======================================================================
def my_listings_menu_loop(book_mgmt, role):
    """Add/view/edit/delete my own listings. Add uses the role's fixed Listing_Type."""
    while True:
        show_my_listings_menu(role)
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                book_mgmt.add_book(listing_type=ROLE_TO_LISTING_TYPE.get(role))
            elif choice == "2":
                book_mgmt.view_my_listings()
            elif choice == "3":
                book_mgmt.edit_book()
            elif choice == "4":
                book_mgmt.delete_book()
            elif choice == "5":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-5).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def owner_activity_menu_loop(request_service):
    """Read-only history: who has requested/reserved my listings."""
    while True:
        show_owner_activity_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                request_service.view_requests_on_my_books()
            elif choice == "2":
                request_service.view_reservations_on_my_books()
            elif choice == "3":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-3).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def owner_dashboard_loop(session, auth, role):
    """Seller / Donor / Exchange User Role: manage listings, see activity on them."""
    profile = ProfileManagement(session)
    password_mgmt = PasswordManagement(session)
    book_mgmt = BookManagement(session)
    review_service = ReviewService(session)
    request_service = RequestService(session)

    while True:
        if not Authorization.require_user(session):
            return

        show_owner_dashboard(session.username, role)
        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                account_menu_loop(session, auth, profile, password_mgmt)
            elif choice == "2":
                my_listings_menu_loop(book_mgmt, role)
            elif choice == "3":
                owner_activity_menu_loop(request_service)
            elif choice == "4":
                reviews_menu_loop(review_service)
            # elif choice == "5":
                # notifications_menu_loop(request_service)
            elif choice == "5":
                return  # Switch Mode: back to mode selection, still logged in
            elif choice == "6":
                auth.logout()
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-7).")
                pause()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            pause()

        if not session.is_authenticated:
            return


def choose_session_mode(session):
    """
    Prompts 'What would you like to do today?' and sets session.active_role
    for this session. Blank input accepts the account's registered default
    Role. Called right after login and again whenever the user picks
    'Switch Mode' from inside a dashboard - the same account can act as a
    Buyer in one session (or even mid-session) and a Seller in the next
    without a second registration.
    """
    while True:
        show_mode_menu(session.role)
        choice = input("Enter choice: ").strip()
        if choice == "":
            session.active_role = session.role
            return
        if choice in MODE_CHOICES:
            session.active_role = MODE_CHOICES[choice]
            return
        print("Invalid choice. Please select 1-4, or press Enter for your default.")


def user_dashboard_loop(session, auth):
    """Dynamic Menu dispatcher: routes to the dashboard matching this
    session's chosen mode, and loops back to mode selection on Switch Mode."""
    while True:
        if not Authorization.require_user(session):
            return

        choose_session_mode(session)

        if session.active_role == "Buyer":
            buyer_dashboard_loop(session, auth)
        else:
            owner_dashboard_loop(session, auth, session.active_role)

        if not session.is_authenticated:
            return


# ======================================================================
# ADMIN DASHBOARD - LEAF SUBMENUS
# ======================================================================
def user_mgmt_menu_loop(admin_mgmt):
    while True:
        show_user_mgmt_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                admin_mgmt.register_admin()
            elif choice == "2":
                admin_mgmt.promote_user_to_admin()
            elif choice == "3":
                admin_mgmt.view_users()
            elif choice == "4":
                admin_mgmt.search_user()
            elif choice == "5":
                admin_mgmt.activate_user()
            elif choice == "6":
                admin_mgmt.deactivate_user()
            elif choice == "7":
                admin_mgmt.delete_user()
            elif choice == "8":
                admin_mgmt.view_admins()
            elif choice == "9":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-9).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def book_mgmt_menu_loop(book_mgmt):
    while True:
        show_book_mgmt_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                book_mgmt.admin_view_all_books()
            elif choice == "2":
                book_mgmt.search_books()
            elif choice == "3":
                book_mgmt.admin_delete_book()
            elif choice == "4":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-4).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def reviews_mod_menu_loop(review_service):
    while True:
        show_reviews_mod_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                review_service.admin_view_all_reviews()
            elif choice == "2":
                review_service.admin_delete_review()
            elif choice == "3":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-3).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def requests_overview_menu_loop(request_service):
    while True:
        show_requests_overview_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                request_service.admin_view_all_requests()
            elif choice == "2":
                request_service.admin_view_all_reservations()
            elif choice == "3":
                request_service.admin_review_pending_requests()
            elif choice == "4":
                request_service.admin_expire_reservation()
            elif choice == "5":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-5).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


def reports_menu_loop(report_service):
    """See All Reports: shows analytics + graph on screen and auto-emails the PDF to the admin."""
    while True:
        show_reports_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                report_service.show_user_report()
            elif choice == "2":
                report_service.show_book_report()
            elif choice == "3":
                report_service.show_requests_report()
            elif choice == "4":
                report_service.show_reservations_report()
            elif choice == "5":
                report_service.show_reviews_report()
            elif choice == "6":
                report_service.show_wishlist_report()
            elif choice == "7":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-7).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        pause()


# ======================================================================
# DELIVERY MANAGEMENT (admin submenu)
# ======================================================================
def delivery_mgmt_menu_loop(delivery_mgmt):
    while True:
        show_delivery_mgmt_menu()
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                delivery_mgmt.register_delivery_boy()
            elif choice == "2":
                delivery_mgmt.view_delivery_boys()
            elif choice == "3":
                delivery_mgmt.activate_delivery_boy()
            elif choice == "4":
                delivery_mgmt.deactivate_delivery_boy()
            elif choice == "5":
                delivery_mgmt.delete_delivery_boy()
            elif choice == "6":
                delivery_mgmt.view_unassigned_deliveries()
            elif choice == "7":
                delivery_mgmt.assign_delivery_boy()
            elif choice == "8":
                delivery_mgmt.view_all_deliveries()
            elif choice == "9":
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-9).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        pause()


# ======================================================================
# ADMIN DASHBOARD (top-level)
# ======================================================================
def admin_dashboard_loop(session, auth):
    """Displays the Admin Dashboard and routes choices into each feature area
    until the administrator logs out."""
    admin_mgmt = AdminManagement(session)
    book_mgmt = BookManagement(session)
    review_service = ReviewService(session)
    request_service = RequestService(session)
    report_service = ReportService(session)
    delivery_mgmt = DeliveryManagement(session)

    while True:
        if not Authorization.require_admin(session):
            return

        show_admin_dashboard(session.username)
        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                user_mgmt_menu_loop(admin_mgmt)
            elif choice == "2":
                book_mgmt_menu_loop(book_mgmt)
            elif choice == "3":
                reviews_mod_menu_loop(review_service)
            elif choice == "4":
                requests_overview_menu_loop(request_service)
            elif choice == "5":
                reports_menu_loop(report_service)
            elif choice == "6":
                delivery_mgmt_menu_loop(delivery_mgmt)
            elif choice == "7":
                auth.logout()
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-7).")
                pause()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            pause()


# ======================================================================
# DELIVERY BOY DASHBOARD (top-level)
# ======================================================================
def delivery_boy_dashboard_loop(session, auth):
    """Displays the Delivery Boy Dashboard: view assigned deliveries and move
    each one through Picked Up -> Delivered."""
    delivery_service = DeliveryService(session)

    while True:
        if not Authorization.require_delivery_boy(session):
            return

        show_delivery_boy_dashboard(session.username)
        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                delivery_service.view_my_deliveries()
            elif choice == "2":
                delivery_service.mark_picked_up()
            elif choice == "3":
                delivery_service.mark_delivered()
            elif choice == "4":
                auth.logout()
                return
            else:
                print("Invalid choice. Please select a valid menu option (1-4).")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        if not session.is_authenticated:
            return
        pause()


# ======================================================================
# FIRST-TIME ADMIN BOOTSTRAP
# The Administrators table starts empty, but Register New Admin can only be
# performed by an admin who is already logged in. To break this
# chicken-and-egg problem, main() checks once at startup whether any
# administrator exists; if not, it walks the operator through creating the
# very first one before showing the main menu.
# ======================================================================
def bootstrap_first_admin():
    try:
        if Admin.get_all():
            return  # At least one administrator already exists - nothing to do
    except Exception as e:
        print(f"Could not check for existing administrators: {e}")
        return

    print("\nNo administrator account exists yet. Let's create the first one.")
    try:
        full_name = get_non_empty_input("Full Name: ")

        while True:
            email = get_non_empty_input("Email: ")
            if not Validation.validate_email(email):
                print("Invalid email format.")
                continue
            if Admin.get_by_email(email):
                print("An administrator with this email already exists.")
                continue
            break

        while True:
            phone = get_non_empty_input("Phone Number (10 digits): ")
            if Validation.validate_phone(phone):
                break
            print("Invalid phone number. It must be exactly 10 digits.")

        while True:
            username = get_non_empty_input("Username: ")
            if not Admin.get_by_username(username):
                break
            print("This username is already taken.")

        while True:
            password = get_non_empty_input("Password: ")
            valid, reason = Validation.validate_password_strength(password)
            if not valid:
                print(reason)
                continue
            confirm = get_non_empty_input("Confirm Password: ")
            if password != confirm:
                print("Passwords do not match.")
                continue
            break

        admin_level = get_non_empty_input("Admin Level (e.g. SuperAdmin): ")

        password_hash = Hashing.hash_password(password)
        Admin.create(full_name, email, phone, username, password_hash,
                     admin_level, created_by="SYSTEM")
        print(f"First administrator '{username}' created successfully. You can now log in.")

    except Exception as e:
        print(f"Failed to create the first administrator: {e}")


# ======================================================================
# MAIN PROGRAM LOOP (System Entry)
# ======================================================================
def main():
    # Establish the database connection once at startup.
    try:
        Database.get_instance()
    except Exception:
        print("Could not connect to the database. Please check your MySQL "
              "configuration in database/db.py and ensure the MySQL server is running.")
        sys.exit(1)

    bootstrap_first_admin()

    session = Session()
    auth = Authentication(session)
    registration = Registration()

    while True:
        show_main_menu()
        choice = input("Enter choice: ").strip()

        try:
            if choice == "1":
                identifier = get_non_empty_input("Username or Email: ")

                password = input("Password: ").strip()

                if auth.login_user(identifier, password):
                    user_dashboard_loop(session, auth)

            elif choice == "2":
                identifier = get_non_empty_input("Admin Username or Email: ")
                password = input("Password: ").strip()
                if auth.login_admin(identifier, password):
                    admin_dashboard_loop(session, auth)

            elif choice == "3":
                identifier = get_non_empty_input("Delivery Boy Username or Email: ")
                password = input("Password: ").strip()
                if auth.login_delivery_boy(identifier, password):
                    delivery_boy_dashboard_loop(session, auth)

            elif choice == "4":
                registration.register_user()

            elif choice == "5":
                print("\nThank you for using Book Bank Management System. Goodbye!")
                Database.get_instance().close()
                sys.exit(0)

            else:
                print("Invalid choice. Please select 1-5.")

        except KeyboardInterrupt:
            print("\n\nProgram interrupted. Exiting safely...")
            Database.get_instance().close()
            sys.exit(0)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


        pause()



if __name__ == "__main__":
    main()
