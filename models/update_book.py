from database import conn

def update_book():
    cursor = conn.cursor()

    book_id = int(input("Enter Book ID to Update : "))

    query = """
    SELECT * FROM books
    WHERE book_id = %s
    """

    cursor.execute(query, (book_id,))
    book = cursor.fetchone()

    if not book:
        print("Book not found!")
        cursor.close()
        return

    print("\nEnter New Details\n")

    title = input("Enter Book Title : ")
    author = input("Enter Author Name : ")
    isbn = input("Enter ISBN : ")
    category = input("Enter Category : ")
    price = float(input("Enter Price : "))
    availability = input("Enter Availability (Available/Sold) : ")
    seller_name = input("Enter Seller Name : ")
    phone = input("Enter Phone Number : ")
    location = input("Enter Location : ")

    print("\nBook Condition")
    print("1. New")
    print("2. Like New")
    print("3. Good")
    print("4. Fair")
    print("5. Used")

    condition_choice = input("Choose (1-5) : ")

    conditions = {
        "1": "New",
        "2": "Like New",
        "3": "Good",
        "4": "Fair",
        "5": "Used"
    }

    book_condition = conditions.get(condition_choice, "Good")

    print("\nListing Type")
    print("1. Sale")
    print("2. Donation")
    print("3. Exchange")

    listing_choice = input("Choose (1-3) : ")

    listings = {
        "1": "Sale",
        "2": "Donation",
        "3": "Exchange"
    }

    listing_type = listings.get(listing_choice, "Sale")

    edition = input("Enter Edition : ")
    owner_id = int(input("Enter Owner ID : "))

    update_query = """
    UPDATE books
    SET
        title=%s,
        author=%s,
        isbn=%s,
        category=%s,
        price=%s,
        availability=%s,
        seller_name=%s,
        phone=%s,
        location=%s,
        book_condition=%s,
        listing_type=%s,
        edition=%s,
        owner_id=%s
    WHERE book_id=%s
    """

    values = (
        title,
        author,
        isbn,
        category,
        price,
        availability,
        seller_name,
        phone,
        location,
        book_condition,
        listing_type,
        edition,
        owner_id,
        book_id
    )

    try:
        cursor.execute(update_query, values)
        conn.commit()

        if cursor.rowcount > 0:
            print("Book Updated Successfully!")
        else:
            print("No changes made.")

    except Exception as e:
        print("Error :", e)

    finally:
        cursor.close()


if __name__ == "__main__":
    update_book()