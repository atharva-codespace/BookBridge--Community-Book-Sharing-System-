from database import conn

def delete_book():
    cursor = conn.cursor()

    book_id = int(input("Enter Book ID to Delete : "))

    check_query = "SELECT * FROM books WHERE book_id = %s"
    cursor.execute(check_query, (book_id,))
    book = cursor.fetchone()

    if not book:
        print("Book not found!")
        cursor.close()
        return

    confirm = input("Are you sure you want to delete this book? (Y/N): ")

    if confirm.upper() == "Y":
        delete_query = "DELETE FROM books WHERE book_id = %s"

        try:
            cursor.execute(delete_query, (book_id,))
            conn.commit()

            if cursor.rowcount > 0:
                print("Book Deleted Successfully!")
            else:
                print("Book could not be deleted.")

        except Exception as e:
            print("Error :", e)

    else:
        print("Delete Operation Cancelled.")

    cursor.close()


if __name__ == "__main__":
    delete_book()