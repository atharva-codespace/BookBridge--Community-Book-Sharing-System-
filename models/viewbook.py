from database import conn
from tabulate import tabulate





# ---------------- VIEW BOOKS ----------------

def view_books():

    cursor = conn.cursor()

    print("\n========== VIEW BOOKS ==========")
    print("1. View All Books")
    print("2. View Available for Sale")
    print("3. View Available for Donation")
    print("4. View Available for Exchange")
    print("5. View Books by Condition")
    print("6. Back")

    choice = input("\nEnter Choice : ")

    if choice == "1":
        cursor.execute("SELECT * FROM Books")

    elif choice == "2":
        cursor.execute("SELECT * FROM Books WHERE Listing_Type='Sale'")

    elif choice == "3":
        cursor.execute("SELECT * FROM Books WHERE Listing_Type='Donation'")

    elif choice == "4":
        cursor.execute("SELECT * FROM Books WHERE Listing_Type='Exchange'")

    elif choice == "5":

        print("\n===== BOOK CONDITION =====")
        print("1. Like New")
        print("2. New")
        print("3. Good")
        print("4. Fair")
        print("5. Used")

        condition = input("Enter Choice : ")

        if condition == "1":
            cursor.execute("SELECT * FROM Books WHERE Book_Condition='Like New'")

        elif condition == "2":
            cursor.execute("SELECT * FROM Books WHERE Book_Condition='New'")

        elif condition == "3":
            cursor.execute("SELECT * FROM Books WHERE Book_Condition='Good'")

        elif condition == "4":
             cursor.execute("SELECT * FROM Books WHERE Book_Condition='Fair'")

        elif condition == "5":
            cursor.execute("SELECT * FROM Books WHERE Book_Condition='Used'")

        else:
            print("Invalid Choice!")
            cursor.close()
            return

    elif choice == "6":
        cursor.close()
        return

    else:
        print("Invalid Choice!")
        cursor.close()
        return

    books = cursor.fetchall()

    if books:

        print("\n=========== BOOKS ===========")

        headers = [
            "Book ID",
            "Title",
            "Author",
            "ISBN",
            "Category",
            "Price",
            "Availability",
            "Seller Name",
            "Phone",
            "Location",
            "Book Condition",
            "Listing Type",
            "Edition",
            "Owner ID"
        ]

        print(tabulate(books, headers=headers, tablefmt="rounded_grid"))

        print("\nTotal Books Found :", len(books))

    else:
        print("\nNo Books Found.")

    cursor.close()