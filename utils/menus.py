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
"""

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
    print("\n--- WHAT WOULD YOU LIKE TO DO TODAY? ---")
    print("1. Buy Books")
    print("2. Sell Books")
    # print("3. Donate Books")
    # print("4. Exchange Books")
    print(f"(Press Enter to use your registered default: {default_role})")


def show_main_menu():
    """System entry menu."""
    print("\n==============================")
    print(" BOOK BANK MANAGEMENT SYSTEM")
    print("==============================")
    print("1. Login as User")
    print("2. Login as Administrator")
    print("3. Register New User")
    print("4. Exit")


# ======================================================================
# COMMON SUBMENUS (shared by every role)
# ======================================================================
def show_account_menu():
    print("\n--- MY ACCOUNT ---")
    print("1  View Profile")
    print("2  Edit Profile")
    print("3  Change Password")
    print("4  Forgot Password")
    print("5  Notification Preferences")
    print("6  Location Preferences")
    print("7  View Login History")
    print("8  View Account Activity")
    print("9  Deactivate Account")
    print("10 Delete Account")
    print("11 Back")


def show_reviews_menu():
    print("\n--- REVIEWS & RATINGS ---")
    print("1. Submit Review")
    # print("2. View Reviews For A Book")
    print("2. View My Reviews")
    print("3. Back")

def show_reviews_menu_for_sell():
    print("\n--- REVIEWS & RATINGS ---")
    # print("1. Submit Review")
    # print("2. View Reviews For A Book")
    print("1. View My Reviews")
    print("2. Back")


def show_notifications_menu():
    print("\n--- NOTIFICATIONS ---")
    print("1. View Notifications")
    print("2. Mark Notification As Read")
    print("3. Back")


# ======================================================================
# BUYER DASHBOARD
# ======================================================================
def show_buyer_dashboard(username):
    print(f"\n========================")
    print(f" BUYER DASHBOARD ({username})")
    print(f"========================")
    print("1. My Account")
    print("2. Browse & Search Books")
    print("3. Request / Reserve a Book")
    print("4. Wishlist")
    print("5. My Requests & Reservations")
    print("6. Reviews & Ratings")
    print("7. Notifications")
    print("8. Switch Mode (Buy / Sell)")
    print("9. Logout")


def show_marketplace_menu():
    print("\n--- BROWSE & SEARCH BOOKS ---")
    print("1. Browse Books")
    print("2. Search Books")
    print("3. Back")


def show_buyer_actions_menu():
    print("\n--- REQUEST / RESERVE A BOOK ---")
    print("1. Request Book")
    print("2. Reserve Book")
    print("3. Back")


def show_wishlist_menu():
    print("\n--- WISHLIST ---")
    print("1. Add Book To Wishlist")
    print("2. Remove Book From Wishlist")
    print("3. View Wishlist")
    print("4. Back")


def show_my_requests_reservations_menu():
    print("\n--- MY REQUESTS & RESERVATIONS ---")
    print("1. View My Requests")
    print("2. View My Reservations")
    print("3. Complete Reservation")
    print("4. Cancel Reservation")
    print("5. Back")


# ======================================================================
# OWNER DASHBOARD (Seller / Donor / Exchange User)
# ======================================================================
def show_owner_dashboard(username, role):
    print(f"\n========================")
    print(f" {role.upper()} DASHBOARD ({username})")
    print(f"========================")
    print("1. My Account")
    print("2. My Listings")
    print("3. Requests & Reservations On My Books")
    print("4. Reviews & Ratings")
    # print("5. Notifications")
    print("5. Switch Mode (Buy / Sell )")
    print("6. Logout")


def show_my_listings_menu(role):
    add_label = ROLE_ADD_LABELS.get(role, "Add Book")
    print("\n--- MY LISTINGS ---")
    print(f"1. {add_label}")
    print("2. View My Listings")
    print("3. Edit Book")
    print("4. Delete Book")
    print("5. Back")


def show_owner_activity_menu():
    print("\n--- REQUESTS & RESERVATIONS ON MY BOOKS ---")
    print("1. View Requests On My Books")
    print("2. View Reservations On My Books")
    print("3. Back")


# ======================================================================
# ADMIN DASHBOARD
# ======================================================================
def show_admin_dashboard(username):
    print(f"\n=====================")
    print(f" ADMIN DASHBOARD ({username})")
    print(f"=====================")
    print("1. User Management")
    print("2. Book Management")
    print("3. Reviews Moderation")
    print("4. Requests & Reservations Overview")
    print("5. See All Reports")
    print("6. Logout")


def show_user_mgmt_menu():
    print("\n--- USER MANAGEMENT ---")
    print("1 Register New Admin")
    print("2 Promote User To Admin")
    print("3 View Users")
    print("4 Search User")
    print("5 Activate User")
    print("6 Deactivate User")
    print("7 Delete User")
    print("8 View Admins")
    print("9 Back")


def show_book_mgmt_menu():
    print("\n--- BOOK MANAGEMENT ---")
    print("1. View All Books")
    print("2. Search Books")
    print("3. Delete Book (Moderation)")
    print("4. Back")


def show_reviews_mod_menu():
    print("\n--- REVIEWS MODERATION ---")
    print("1. View All Reviews")
    print("2. Delete Review")
    print("3. Back")


def show_requests_overview_menu():
    print("\n--- REQUESTS & RESERVATIONS OVERVIEW ---")
    print("1. View All Requests")
    print("2. View All Reservations")
    print("3. Review Pending Book Requests (Approve / Reject)")
    print("4. Force-Expire Reservation")
    print("5. Back")


def show_reports_menu():
    print("\n--- SEE ALL REPORTS ---")
    print("1. Users Report (view graph + email PDF to me)")
    print("2. Books Report (view graph + email PDF to me)")
    print("3. Back")
