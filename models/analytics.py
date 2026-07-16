"""
Modules/analytics.py
Fetches data from Users and Books tables, prints terminal tables,
and generates graphs.
"""

import matplotlib.pyplot as plt
import os
from database.db import Database

db = Database.get_instance()


# ---------------- USER MANAGEMENT ----------------

def fetch_users_data():
    rows = db.fetch_all(
        """
        SELECT User_ID, Full_Name, Email, Phone_Number, Location,
               Username, Role, Account_Status, Account_Created_Date
        FROM Users
        WHERE Is_Deleted = 0
        """
    )
    return rows


def fetch_users_summary():
    summary = {}
    summary["Total Users"] = db.fetch_one("SELECT COUNT(*) AS total FROM Users")["total"]
    summary["Active Users"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM Users WHERE Account_Status='Active'")["total"]
    summary["Inactive Users"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM Users WHERE Account_Status='Inactive'")["total"]
    return summary


# ---------------- BOOK LISTING ----------------

def fetch_books_data():
    rows = db.fetch_all(
        """
        SELECT Book_ID, Title, Author, ISBN, Category, Price,
               Availability, Seller_Name, Location, Book_Condition,
               Listing_Type, Edition
        FROM Books
        """
    )
    return rows


def fetch_books_summary():
    summary = {}
    summary["Total Books"] = db.fetch_one("SELECT COUNT(*) AS total FROM Books")["total"]
    summary["Sale Books"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM Books WHERE Listing_Type='Sale'")["total"]
    summary["Donation Books"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM Books WHERE Listing_Type='Donation'")["total"]
    summary["Exchange Books"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM Books WHERE Listing_Type='Exchange'")["total"]
    return summary


# ---------------- GRAPH GENERATION ----------------
# Note: terminal table printing for this data lives in services/report_service.py,
# which uses the shared utils.helpers.print_table (tabulate-based) so every
# module's output is formatted consistently.

def generate_users_graph(summary):
    os.makedirs("Reports", exist_ok=True)
    path = "Reports/users_chart.png"

    plt.figure(figsize=(6, 4))
    plt.bar(summary.keys(), summary.values(), color="teal")
    plt.title("User Management Overview")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    print(f"Graph saved at: {path}")
    return path


def generate_books_graph(summary):
    os.makedirs("Reports", exist_ok=True)
    path = "Reports/books_chart.png"

    plt.figure(figsize=(6, 4))
    plt.bar(summary.keys(), summary.values(), color="darkorange")
    plt.title("Book Listing Overview")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    print(f"Graph saved at: {path}")
    return path


# ---------------- BOOK REQUESTS ----------------

def fetch_requests_data():
    rows = db.fetch_all(
        "SELECT request_id, book_name, user_id, request_date, status FROM requests "
        "ORDER BY request_id DESC"
    )
    return rows


def fetch_requests_summary():
    summary = {}
    summary["Total Requests"] = db.fetch_one("SELECT COUNT(*) AS total FROM requests")["total"]
    summary["Pending"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM requests WHERE status='Pending'")["total"]
    summary["Approved"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM requests WHERE status='Approved'")["total"]
    summary["Rejected"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM requests WHERE status='Rejected'")["total"]
    return summary


def generate_requests_graph(summary):
    os.makedirs("Reports", exist_ok=True)
    path = "Reports/requests_chart.png"

    plt.figure(figsize=(6, 4))
    plt.bar(summary.keys(), summary.values(), color="mediumpurple")
    plt.title("Book Requests Overview")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    print(f"Graph saved at: {path}")
    return path


# ---------------- RESERVATIONS ----------------

def fetch_reservations_data():
    rows = db.fetch_all(
        "SELECT reservation_id, book_name, user_id, expiry_date, status "
        "FROM reservations ORDER BY reservation_id DESC"
    )
    return rows


def fetch_reservations_summary():
    summary = {}
    summary["Total Reservations"] = db.fetch_one("SELECT COUNT(*) AS total FROM reservations")["total"]
    summary["Active"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM reservations WHERE status='Active'")["total"]
    summary["Completed"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM reservations WHERE status='Completed'")["total"]
    summary["Cancelled"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM reservations WHERE status='Cancelled'")["total"]
    summary["Expired"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM reservations WHERE status='Expired'")["total"]
    return summary


def generate_reservations_graph(summary):
    os.makedirs("Reports", exist_ok=True)
    path = "Reports/reservations_chart.png"

    plt.figure(figsize=(6, 4))
    plt.bar(summary.keys(), summary.values(), color="steelblue")
    plt.title("Reservations Overview")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    print(f"Graph saved at: {path}")
    return path


# ---------------- REVIEWS ----------------

def fetch_reviews_data():
    rows = db.fetch_all(
        "SELECT review_id, user_id, rating, review, review_date FROM reviews "
        "ORDER BY review_id DESC"
    )
    return rows


def fetch_reviews_summary():
    summary = {}
    summary["Total Reviews"] = db.fetch_one("SELECT COUNT(*) AS total FROM reviews")["total"]
    avg_row = db.fetch_one("SELECT AVG(rating) AS avg_rating FROM reviews")
    avg_rating = avg_row["avg_rating"] if avg_row and avg_row["avg_rating"] is not None else 0
    summary["Average Rating"] = round(float(avg_rating), 2)
    for star in range(1, 6):
        summary[f"{star} Star"] = db.fetch_one(
            "SELECT COUNT(*) AS total FROM reviews WHERE rating=%s", (star,))["total"]
    return summary


def generate_reviews_graph(summary):
    os.makedirs("Reports", exist_ok=True)
    path = "Reports/reviews_chart.png"

    star_counts = {k: v for k, v in summary.items() if k.endswith("Star")}

    plt.figure(figsize=(6, 4))
    plt.bar(star_counts.keys(), star_counts.values(), color="goldenrod")
    plt.title("Review Rating Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Number of Reviews")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    print(f"Graph saved at: {path}")
    return path


# ---------------- WISHLIST ----------------

def fetch_wishlist_data():
    rows = db.fetch_all(
        "SELECT wishlist_id, user_id, book_name FROM wishlist "
        "ORDER BY wishlist_id DESC"
    )
    return rows


def fetch_wishlist_summary():
    summary = {}
    summary["Total Wishlist Entries"] = db.fetch_one(
        "SELECT COUNT(*) AS total FROM wishlist")["total"]
    summary["Unique Users"] = db.fetch_one(
        "SELECT COUNT(DISTINCT user_id) AS total FROM wishlist")["total"]
    summary["Unique Books"] = db.fetch_one(
        "SELECT COUNT(DISTINCT book_name) AS total FROM wishlist")["total"]
    return summary


def generate_wishlist_graph(summary):
    os.makedirs("Reports", exist_ok=True)
    path = "Reports/wishlist_chart.png"

    plt.figure(figsize=(6, 4))
    plt.bar(summary.keys(), summary.values(), color="mediumseagreen")
    plt.title("Wishlist Overview")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    print(f"Graph saved at: {path}")
    return path