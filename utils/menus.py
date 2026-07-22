"""
utils/menus.py
Contains every menu display function for the console application. A logged
in User's dashboard shape depends on the *session mode* they choose right
after login (Feature: Dynamic Menu) - Buy, Sell, Donate, or Exchange -
rather than a role fixed forever at registration. Buy mode gets a
browse/request/reserve/wishlist-centric menu, while Sell/Donate/Exchange
mode gets a listing-management-centric menu whose "Add Book" wording
matches the chosen mode. A "Switch Mode" option lets the same account move
between them without logging out. Each top-level dashboard fans out into
small feature submenus so no single screen has more than a handful of
options.

Presentation note: every screen below is rendered through utils/ui.py
(Rich panels/tables, no icons/emojis). The option KEYS and LABELS are
unchanged from the original plain-text menus - only the look has been
upgraded - so main.py's `if choice == "1": ...` dispatch logic keeps
working exactly as before.
"""

from utils import ui

ROLE_ADD_LABELS = {
    "Seller": "Add Book To Sell",
    "Donor": "Add Book To Donate",
    "Exchange User": "Add Book To Exchange",
}

MODE_CHOICES = {
    "1": "Buyer",
    "2": "Seller",
    "3": "Donor",
    "4": "Exchange User",
}


def show_mode_menu(default_role):
    ui.menu(
        "WHAT WOULD YOU LIKE TO DO TODAY?",
        [
            ("1", "Buy Books"),
            ("2", "Sell Books"),
            # ("3", "Donate Books"),
            # ("4", "Exchange Books"),
        ],
        #footer=f"Press Enter to use your registered default: {default_role}",
    )


def show_main_menu():
    """System entry menu."""
    ui.banner("BookBridge", subtitle="Buy - Sell Your Old Books", figlet=True)
    ui.menu(
        "MAIN MENU",
        [
            ("1", "Login as User"),
            ("2", "Login as Administrator"),
            ("3", "Login as Delivery Boy"),
            ("4", "Register as New User"),
            ("5", "AI Project Assistant"),
            ("6", "Exit"),
        ],
    )


# ======================================================================
# COMMON SUBMENUS (shared by every role)
# ======================================================================
def show_account_menu():
    ui.menu(
        "MY ACCOUNT",
        [
            ("1", "View Profile"),
            ("2", "Edit Profile"),
            ("3", "Change Password"),
            ("4", "Forgot Password"),
            ("5", "Notification Preferences"),
            ("6", "Location Preferences"),
            ("7", "View Login History"),
            ("8", "View Account Activity"),
            ("9", "Deactivate Account"),
            ("10", "Delete Account"),
            ("11", "Back"),
        ],
    )


def show_reviews_menu():
    ui.menu(
        "REVIEWS & RATINGS",
        [
            ("1", "Submit Review"),
            # ("2", "View Reviews For A Book"),
            ("2", "View My Reviews"),
            ("3", "Back"),
        ],
    )


def show_reviews_menu_for_sell():
    ui.menu(
        "REVIEWS & RATINGS",
        [
            # ("1", "Submit Review"),
            # ("2", "View Reviews For A Book"),
            ("1", "View My Reviews"),
            ("2", "Back"),
        ],
    )


def show_notifications_menu():
    ui.menu(
        "NOTIFICATIONS",
        [
            ("1", "View Notifications"),
            ("2", "Mark Notification As Read"),
            ("3", "Buy This Book Now (Complete Reservation)"),
            ("4", "Back"),
        ],
    )


# ======================================================================
# BUYER DASHBOARD
# ======================================================================
def show_buyer_dashboard(username):
    ui.menu(
        "BUYER DASHBOARD",
        [
            ("1", "My Account"),
            ("2", "Browse & Search Books"),
            ("3", "Request / Reserve a Book"),
            ("4", "Wishlist"),
            ("5", "My Requests & Reservations"),
            ("6", "Reviews & Ratings"),
            ("7", "Notifications"),
            ("8", "Switch Mode (Buy / Sell)"),
            ("9", "Logout"),
        ],
        footer=f"Signed in as {username}",
    )


def show_marketplace_menu():
    ui.menu(
        "BROWSE & SEARCH BOOKS",
        [
            ("1", "Browse Books"),
            ("2", "Search Books"),
            ("3", "Back"),
        ],
    )


def show_buyer_actions_menu():
    ui.menu(
        "REQUEST / RESERVE A BOOK",
        [
            ("1", "Request Book"),
            ("2", "Reserve Book"),
            ("3", "Back"),
        ],
    )


def show_wishlist_menu():
    ui.menu(
        "WISHLIST",
        [
            ("1", "Add Book To Wishlist"),
            ("2", "Remove Book From Wishlist"),
            ("3", "View Wishlist"),
            ("4", "Buy Book From Wishlist"),
            ("5", "Back"),
        ],
    )


def show_my_requests_reservations_menu():
    ui.menu(
        "MY REQUESTS & RESERVATIONS",
        [
            ("1", "View My Requests"),
            ("2", "View My Reservations"),
            ("3", "Complete Reservation"),
            ("4", "Cancel Reservation"),
            ("5", "Back"),
        ],
    )


# ======================================================================
# OWNER DASHBOARD (Seller / Donor / Exchange User)
# ======================================================================
def show_owner_dashboard(username, role):
    ui.menu(
        f"{role.upper()} DASHBOARD",
        [
            ("1", "My Account"),
            ("2", "My Listings"),
            ("3", "Requests & Reservations On My Books"),
            ("4", "Reviews & Ratings"),
            # ("5", "Notifications"),
            ("5", "Switch Mode (Buy / Sell)"),
            ("6", "Logout"),
        ],
        footer=f"Signed in as {username}",
    )


def show_my_listings_menu(role):
    add_label = ROLE_ADD_LABELS.get(role, "Add Book")
    ui.menu(
        "MY LISTINGS",
        [
            ("1", add_label),
            ("2", "View My Listings"),
            ("3", "Edit Book"),
            ("4", "Delete Book"),
            ("5", "Back"),
        ],
    )


def show_owner_activity_menu():
    ui.menu(
        "REQUESTS & RESERVATIONS ON MY BOOKS",
        [
            ("1", "View Requests On My Books"),
            ("2", "View Reservations On My Books"),
            ("3", "Back"),
        ],
    )


# ======================================================================
# ADMIN DASHBOARD
# ======================================================================
def show_admin_dashboard(username):
    ui.menu(
        "ADMIN DASHBOARD",
        [
            ("1", "User Management"),
            ("2", "Book Management"),
            ("3", "Reviews Moderation"),
            ("4", "Requests & Reservations Overview"),
            ("5", "See All Reports"),
            ("6", "Delivery Management"),
            ("7", "Logout"),
        ],
        footer=f"Signed in as {username}",
    )


def show_user_mgmt_menu():
    ui.menu(
        "USER MANAGEMENT",
        [
            ("1", "Register New Admin"),
            ("2", "Promote User To Admin"),
            ("3", "View Users"),
            ("4", "Search User"),
            ("5", "Activate User"),
            ("6", "Deactivate User"),
            ("7", "Delete User"),
            ("8", "View Admins"),
            ("9", "Back"),
        ],
    )


def show_book_mgmt_menu():
    ui.menu(
        "BOOK MANAGEMENT",
        [
            ("1", "View All Books"),
            ("2", "Search Books"),
            ("3", "Delete Book"),
            ("4", "Back"),
        ],
    )


def show_reviews_mod_menu():
    ui.menu(
        "REVIEWS MODERATION",
        [
            ("1", "View All Reviews"),
            ("2", "Delete Review"),
            ("3", "Back"),
        ],
    )


def show_requests_overview_menu():
    ui.menu(
        "REQUESTS & RESERVATIONS OVERVIEW",
        [
            ("1", "View All Requests"),
            ("2", "View All Reservations"),
            ("3", "Review Pending Book Requests (Approve / Reject)"),
            ("4", "Force-Expire Reservation"),
            ("5", "Back"),
        ],
    )


def show_reports_menu():
    ui.menu(
        "SEE ALL REPORTS",
        [
            ("1", "Users Report (view graph + email PDF to me)"),
            ("2", "Books Report (view graph + email PDF to me)"),
            ("3", "Requests Report (view graph + email PDF to me)"),
            ("4", "Reservations Report (view graph + email PDF to me)"),
            ("5", "Reviews Report (view graph + email PDF to me)"),
            ("6", "Wishlist Report (view graph + email PDF to me)"),
            ("7", "Back"),
        ],
    )


# ======================================================================
# DELIVERY MANAGEMENT (admin submenu)
# ======================================================================
def show_delivery_mgmt_menu():
    ui.menu(
        "DELIVERY MANAGEMENT",
        [
            ("1", "Register Delivery Boy"),
            ("2", "View Delivery Boys"),
            ("3", "Activate Delivery Boy"),
            ("4", "Deactivate Delivery Boy"),
            ("5", "Delete Delivery Boy"),
            ("6", "View Unassigned Deliveries"),
            ("7", "Assign Delivery Boy To A Delivery"),
            ("8", "View All Deliveries"),
            ("9", "Back"),
        ],
    )


# ======================================================================
# DELIVERY BOY DASHBOARD
# ======================================================================
def show_delivery_boy_dashboard(username):
    ui.menu(
        "DELIVERY BOY DASHBOARD",
        [
            ("1", "View My Deliveries"),
            ("2", "Mark Delivery As Picked Up"),
            ("3", "Mark Delivery As Delivered"),
            ("4", "Logout"),
        ],
        footer=f"Signed in as {username}",
    )
