from database import cursor
from tabulate import tabulate

def search_book():

    print("\n===== BOOK SEARCH =====")

    print("1. Search by Title")
    print("2. Search by Author")
    print("3. Search by ISBN")
    print("4. Search by Category")
    print("5. Search by Price Range")
    print("6. Search by Availability")
    print("7. Search by Location")
    print("8. Search by Condition")
    print("9. Search by Edition")

    choice = input("Enter Choice : ")

    if choice == "1":
        title = input("Enter Book Title : ")
        cursor.execute(
            "SELECT * FROM Books WHERE Title LIKE %s",
            ('%' + title + '%',)
        )

    elif choice == "2":
        author = input("Enter Author Name : ")
        cursor.execute(
            "SELECT * FROM Books WHERE Author LIKE %s",
            ('%' + author + '%',)
        )

    elif choice == "3":
        isbn = input("Enter ISBN : ")
        cursor.execute(
            "SELECT * FROM Books WHERE ISBN=%s",
            (isbn,)
        )

    elif choice == "4":
        category = input("Enter Category : ")
        cursor.execute(
            "SELECT * FROM Books WHERE Category=%s",
            (category,)
        )

    elif choice == "5":
        minimum = input("Minimum Price : ")
        maximum = input("Maximum Price : ")

        cursor.execute(
            "SELECT * FROM Books WHERE Price BETWEEN %s AND %s",
            (minimum, maximum)
        )

    elif choice == "6":
        status = input("Availability (Available/Sold) : ")

        cursor.execute(
            "SELECT * FROM Books WHERE Availability=%s",
            (status,)
        )

    elif choice == "7":
        location = input("Enter Location : ")

        cursor.execute(
            "SELECT * FROM Books WHERE Location LIKE %s",
            ('%' + location + '%',)
        )

    elif choice == "8":

        print("\n===== SEARCH BY CONDITION =====")
        print("1. Like New")
        print("2. New")
        print("3. Good")
        print("4. Fair")
        print("5. Used")

        condition_choice = input("Enter Choice : ")

        if condition_choice == "1":
            condition = "Like New"

        elif condition_choice == "2":
            condition = "New"

        elif condition_choice == "3":
            condition = "Good"

        elif condition_choice == "4":
            condition = "Fair"

        elif condition_choice == "5":
            condition = "Used"

        else:
            print("Invalid Choice")
            return

        cursor.execute(
            "SELECT * FROM Books WHERE Book_Condition=%s",
            (condition,)
        )

    elif choice == "9":

        edition = input("Enter Edition  : ")

        cursor.execute(
            "SELECT * FROM Books WHERE Edition=%s",
            (edition,)
        )

    else:
        print("Invalid Choice")
        return

    books = cursor.fetchall()

    if books:

        print("\n=========== SEARCH RESULT ===========")

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
        print("\nNo Book Found.")