from reviewdb import get_connection
from datetime import date

# Connect to database
conn = get_connection()
cursor = conn.cursor()


def user_exists(user_id):
    """Check whether a given user_id exists in the Users table (and is not deleted)."""
    check_query = "SELECT user_id FROM Users WHERE user_id = %s AND is_deleted = 0"
    cursor.execute(check_query, (user_id,))
    result = cursor.fetchone()
    return result is not None


# Get input from user
reviewer_name = input("Enter Reviewer Name: ")
rating = int(input("Enter Rating (1-5): "))
feedback = input("Enter Feedback: ")

# Validate that both users exist in the Users table
if not user_exists(reviewer_name):
    print(f"Error: Reviewer with Name {reviewer_name} does not exist. Review not submitted.")
elif rating < 1 or rating > 5:
    print("Rating must be between 1 and 5")
else:
    query = """
    INSERT INTO Reviews
    (Reviewer_Name, Rating, Feedback_Comment, Review_Date)
    VALUES (%s, %s, %s, %s)
    """

    values = (
        reviewer_name,
        rating,
        feedback,
        date.today()
    )

    cursor.execute(query, values)
    conn.commit()

    print("Review submitted successfully!")

# Close connection
cursor.close()
conn.close()