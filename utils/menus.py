"""
utils/menus.py
Contains all menu display functions for the console application.
Keeping every menu in a single module makes the "Dynamic Menu" requirement
(Feature 14) easy to satisfy: main.py decides WHICH function to call based
on the active session, and each function only prints the options that
role is allowed to see.
"""


def show_main_menu():
    """System entry menu (Feature 1)."""
    print("\n==============================")
    print(" BOOK BANK MANAGEMENT SYSTEM")
    print("==============================")
    print("1. Login as User")
    print("2. Login as Administrator")
    print("3. Register New User")
    print("4. Exit")


def show_user_dashboard(username):
    """User dashboard menu (Feature 4) - only shown to logged-in Users."""
    print(f"\n========================")
    print(f" USER DASHBOARD ({username})")
    print(f"========================")
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
    print("11 Logout")


def show_admin_dashboard(username):
    """Admin dashboard menu (Feature 10) - only shown to logged-in Admins."""
    print(f"\n=====================")
    print(f" ADMIN DASHBOARD ({username})")
    print(f"=====================")
    print("1 Register New Admin")
    print("2 Promote User To Admin")
    print("3 View Users")
    print("4 Search User")
    print("5 Activate User")
    print("6 Deactivate User")
    print("7 Delete User")
    print("8 View Admins")
    print("9 Logout")
