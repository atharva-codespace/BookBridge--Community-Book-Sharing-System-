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