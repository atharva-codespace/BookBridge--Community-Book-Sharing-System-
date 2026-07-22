# BookBridge

A console-based Used Book Exchange, Donation & Resale Platform built with
pure Python and SQLite (no web or GUI frameworks). Covers all six modules:
Account & Profile Management, Book Inventory & Listing Management, Book
Search & Discovery, Book Request/Reservation/Wishlist Management, User
Ratings & Feedback, and an Administrative Dashboard with Analytics/Reports.

## Setup

1. **Create the database.**

   ```
   sqlite3 book_bank.db < database/database.sql
   ```

   This creates every table used by the app: `Users`, `Administrators`,
   `Login_History`, `Profile_Update_History`, `Password_Change_History`,
   `User_Preferences`, `Books`, `Reviews`, `Wishlist`, `Book_Requests`,
   `Reservations`, and `Notifications`, in a local `book_bank.db` file at
   the project root.

   Optionally, load some sample data (8 users, 2 admins, 10 books, reviews,
   wishlist entries, requests, reservations, notifications and deliveries)
   to explore the app without entering everything by hand:

   ```
   sqlite3 book_bank.db < database/seed_data.sql
   ```

   Every sample account (users, admins, delivery boys) uses the password
   `Password123!`.

2. **Install dependencies.**

   ```
   pip install -r requirements.txt
   ```

   This installs `bcrypt`, `tabulate` (table formatting), `matplotlib`
   (analytics graphs), and `reportlab` (PDF reports). SQLite support comes
   built into Python, so no separate database driver is needed.

3. **(Optional) Point the app at a different database file.**

   By default the app uses `book_bank.db` in the project root, anchored to
   the file's location so it works no matter which directory you launch
   `main.py` from. To use a different file/path, edit `Database.DB_PATH` in
   `database/db.py`.

4. **(Optional) Enable email features.**

   Two features send email and need credentials:
   - OTP email verification during registration reads `SENDER_EMAIL`/
     `APP_PASSWORD` in `utils/email_sender.py`.
   - Emailing a PDF analytics report reads the `GMAIL_USER`/
     `GMAIL_APP_PASSWORD` environment variables (`services/report_service.py`
     -> `models/mail.py`). Both features work without a real inbox - just
     skip "Email Alerts"/OTP verification or "Email this report?" prompts.

5. **Run the application.**

   ```
   python main.py
   ```

On the very first run, since the `Administrators` table is empty, the
program will walk you through creating the first administrator account
before showing the main menu. After that, you can log in as that admin
to create additional admins or promote existing users.

## Menu structure

- **User Dashboard**: My Account / Marketplace (browse & search books) /
  My Listings (add, edit, delete your books) / Wishlist, Requests &
  Reservations / Reviews & Ratings / Logout.
- **Admin Dashboard**: User Management / Book Management / Reviews
  Moderation / Requests & Reservations Overview / Analytics & Reports /
  Logout.

Each top-level option opens a focused submenu, so no single screen shows
more than a handful of choices.

## Notes

- Passwords are never stored in plain text - every password is hashed
  with bcrypt before it touches the database.
- All SQL queries use parameterized placeholders (`%s`), which prevents
  SQL Injection.
- Account and book deletion are soft deletes (`Is_Deleted` flag) so
  history and audit data are preserved.
- Two columns not listed in the original spec (`Security_Question`,
  `Security_Answer_Hash`) were added to `Users` to make Forgot Password
  possible, and `Is_Deleted` was added to support soft delete.
- All table-shaped output (users, admins, books, search results, reviews,
  requests, reservations, analytics) is rendered with `tabulate` for a
  consistent look across every module.
