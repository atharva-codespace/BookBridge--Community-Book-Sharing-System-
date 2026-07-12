from database import conn

def view_books():
    cursor = conn.cursor()

    query = "SELECT * FROM books"

    try:
        cursor.execute(query)
        books = cursor.fetchall()

        if not books:
            print("\nNo books found.")
            return

        print("\n========== BOOK LIST ==========\n")

        for book in books:
            print(f"Book ID         : {book[0]}")
            print(f"Title           : {book[1]}")
            print(f"Author          : {book[2]}")
            print(f"ISBN            : {book[3]}")
            print(f"Category        : {book[4]}")
            print(f"Price           : {book[5]}")
            print(f"Availability    : {book[6]}")
            print(f"Seller Name     : {book[7]}")
            print(f"Phone           : {book[8]}")
            print(f"Location        : {book[9]}")
            print(f"Book Condition  : {book[10]}")
            print(f"Listing Type    : {book[11]}")
            print(f"Edition         : {book[12]}")
            print(f"Owner ID        : {book[13]}")
            print("-" * 50)

    except Exception as e:
        print("Error :", e)

    finally:
        cursor.close()


if __name__ == "__main__":
    view_books()