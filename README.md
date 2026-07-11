# Book Bank Management System

A console-based Used Book Exchange, Donation & Resale Platform built with
pure Python and MySQL (no web or GUI frameworks).

## Setup

1. **Create the database.**

   ```
   mysql -u root -p < database/database.sql
   ```

2. **Install dependencies.**

   ```
   pip install -r requirements.txt
   ```

3. **Set your MySQL credentials.**

   Open `database/db.py` and edit the `DB_CONFIG` dictionary (`host`,
   `user`, `password`) to match your local MySQL setup.

4. **Run the application.**

   ```
   python main.py
   ```

On the very first run, since the `Administrators` table is empty, the
program will walk you through creating the first administrator account
before showing the main menu. After that, you can log in as that admin
to create additional admins or promote existing users.

## Notes

- Passwords are never stored in plain text - every password is hashed
  with bcrypt before it touches the database.
- All SQL queries use parameterized placeholders (`%s`), which prevents
  SQL Injection.
- Account deletion is a soft delete (`Is_Deleted` flag) so history and
  audit data are preserved.
- Two columns not listed in the original spec (`Security_Question`,
  `Security_Answer_Hash`) were added to `Users` to make Forgot Password
  possible, and `Is_Deleted` was added to support soft delete.
