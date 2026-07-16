-- ============================================================
-- database.sql
-- Database schema for the Used Book Exchange, Donation & Resale
-- Platform ("Book Bank Management System").
-- ============================================================

USE sql12832760;

DROP TABLE IF EXISTS Notifications;
DROP TABLE IF EXISTS Reservations;
DROP TABLE IF EXISTS Book_Requests;
DROP TABLE IF EXISTS Wishlist;
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS User_Preferences;
DROP TABLE IF EXISTS Password_Change_History;
DROP TABLE IF EXISTS Profile_Update_History;
DROP TABLE IF EXISTS Login_History;
DROP TABLE IF EXISTS Administrators;
DROP TABLE IF EXISTS Users;


-- ------------------------------------------------------------
-- Users
-- ------------------------------------------------------------

CREATE TABLE Users (
    User_ID               INT AUTO_INCREMENT PRIMARY KEY,
    Full_Name             VARCHAR(100) NOT NULL,
    Email                 VARCHAR(100) NOT NULL UNIQUE,
    Phone_Number          VARCHAR(10) NOT NULL UNIQUE,
    Location              VARCHAR(100),
    Username              VARCHAR(50) NOT NULL UNIQUE,
    Password_Hash         VARCHAR(255) NOT NULL,
    Role                  ENUM('Buyer','Seller','Donor','Exchange User') NOT NULL,
    Account_Status        ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
    Account_Created_Date  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Security_Question     VARCHAR(255),
    Security_Answer_Hash  VARCHAR(255),
    Is_Deleted            TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Administrators
-- ------------------------------------------------------------

CREATE TABLE Administrators (
    Admin_ID        INT AUTO_INCREMENT PRIMARY KEY,
    Full_Name       VARCHAR(100) NOT NULL,
    Email           VARCHAR(100) NOT NULL UNIQUE,
    Phone_Number    VARCHAR(10) NOT NULL,
    Username        VARCHAR(50) NOT NULL UNIQUE,
    Password_Hash   VARCHAR(255) NOT NULL,
    Admin_Level     VARCHAR(50) NOT NULL,
    Created_By      VARCHAR(50),
    Created_Date    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Account_Status  ENUM('Active','Inactive') NOT NULL DEFAULT 'Active'
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Login History
-- ------------------------------------------------------------

CREATE TABLE Login_History (
    Login_ID      INT AUTO_INCREMENT PRIMARY KEY,
    User_ID       INT NOT NULL,
    Login_Date    DATE NOT NULL,
    Login_Time    TIME NOT NULL,
    Logout_Date   DATE,
    Logout_Time   TIME,
    FOREIGN KEY (User_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Profile Update History
-- ------------------------------------------------------------

CREATE TABLE Profile_Update_History (
    Update_ID       INT AUTO_INCREMENT PRIMARY KEY,
    User_ID         INT NOT NULL,
    Field_Changed   VARCHAR(50) NOT NULL,
    Old_Value       VARCHAR(255),
    New_Value       VARCHAR(255),
    Updated_Date    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Password Change History
-- ------------------------------------------------------------

CREATE TABLE Password_Change_History (
    Change_ID      INT AUTO_INCREMENT PRIMARY KEY,
    User_ID        INT NOT NULL,
    Changed_Date   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- User Preferences
-- ------------------------------------------------------------

CREATE TABLE User_Preferences (
    Preference_ID                INT AUTO_INCREMENT PRIMARY KEY,
    User_ID                      INT NOT NULL UNIQUE,
    Preferred_Role               ENUM('Buyer','Seller','Donor','Exchange User'),
    Notification_Enabled         TINYINT(1) NOT NULL DEFAULT 1,
    Email_Alerts_Enabled         TINYINT(1) NOT NULL DEFAULT 1,
    City                         VARCHAR(100),
    State                        VARCHAR(100),
    Preferred_Exchange_Location  VARCHAR(150),
    FOREIGN KEY (User_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Books
-- ------------------------------------------------------------

CREATE TABLE Books (
    Book_ID         INT AUTO_INCREMENT PRIMARY KEY,
    Title           VARCHAR(150) NOT NULL,
    Author          VARCHAR(100) NOT NULL,
    ISBN            VARCHAR(20),
    Category        VARCHAR(50),
    Price           DECIMAL(10,2) NOT NULL DEFAULT 0,
    Availability    ENUM('Available','Reserved','Sold','Donated','Exchanged') NOT NULL DEFAULT 'Available',
    Seller_Name     VARCHAR(100),
    Phone           VARCHAR(10),
    Location        VARCHAR(100),
    Book_Condition  ENUM('New','Like New','Good','Fair','Used') NOT NULL DEFAULT 'Good',
    Listing_Type    ENUM('Sale','Donation','Exchange') NOT NULL DEFAULT 'Sale',
    Edition         VARCHAR(50),
    Owner_ID        INT NOT NULL,
    Listed_Date     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Is_Deleted      TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (Owner_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Reviews
-- ------------------------------------------------------------

CREATE TABLE Reviews (
    Review_ID         INT AUTO_INCREMENT PRIMARY KEY,
    Reviewer_ID       INT NOT NULL,
    Book_ID           INT,
    Rating            INT NOT NULL,
    Feedback_Comment  VARCHAR(500),
    Review_Date       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Reviewer_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE,
    FOREIGN KEY (Book_ID)
        REFERENCES Books(Book_ID)
        ON DELETE CASCADE,
    CONSTRAINT chk_rating_range CHECK (Rating BETWEEN 1 AND 5)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Wishlist
-- ------------------------------------------------------------

CREATE TABLE Wishlist (
    Wishlist_ID   INT AUTO_INCREMENT PRIMARY KEY,
    User_ID       INT NOT NULL,
    Book_ID       INT NOT NULL,
    Added_Date    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_wishlist_user_book (User_ID, Book_ID),
    FOREIGN KEY (User_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE,
    FOREIGN KEY (Book_ID)
        REFERENCES Books(Book_ID)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Book Requests
-- ------------------------------------------------------------

-- A Book_Requests row is a permanent log of "this user requested/received
-- this book" - the action is instant (no owner-approval step), so the row
-- is written already-fulfilled. It also doubles as the review-eligibility
-- record: only a user with a Book_Requests row for a given Book_ID may
-- submit a review for that book (see services/review_service.py).
CREATE TABLE Book_Requests (
    Request_ID      INT AUTO_INCREMENT PRIMARY KEY,
    Book_ID         INT NOT NULL,
    Requester_ID    INT NOT NULL,
    Owner_ID        INT NOT NULL,
    Message         VARCHAR(255),
    Request_Date    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Book_ID)
        REFERENCES Books(Book_ID)
        ON DELETE CASCADE,
    FOREIGN KEY (Requester_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE,
    FOREIGN KEY (Owner_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Reservations
-- ------------------------------------------------------------

-- A Reservation is created directly by the "Reserve Book" action (no prior
-- Book_Requests row involved) and later resolved via Complete (book flips to
-- Sold/Donated/Exchanged per its Listing_Type) or Cancel (book reverts to
-- Available).
CREATE TABLE Reservations (
    Reservation_ID  INT AUTO_INCREMENT PRIMARY KEY,
    Book_ID         INT NOT NULL,
    User_ID         INT NOT NULL,
    Reserved_Date   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Expiry_Date     DATE NOT NULL,
    Status          ENUM('Active','Completed','Cancelled','Expired') NOT NULL DEFAULT 'Active',
    FOREIGN KEY (Book_ID)
        REFERENCES Books(Book_ID)
        ON DELETE CASCADE,
    FOREIGN KEY (User_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Notifications
-- ------------------------------------------------------------

CREATE TABLE Notifications (
    Notification_ID  INT AUTO_INCREMENT PRIMARY KEY,
    User_ID          INT NOT NULL,
    Message          VARCHAR(255) NOT NULL,
    Status           ENUM('Unread','Read') NOT NULL DEFAULT 'Unread',
    Created_Date     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID)
        REFERENCES Users(User_ID)
        ON DELETE CASCADE
) ENGINE=InnoDB;



CREATE TABLE IF NOT EXISTS Delivery_Boys (
    Delivery_Boy_ID  INT AUTO_INCREMENT PRIMARY KEY,
    Full_Name        VARCHAR(100) NOT NULL,
    Email            VARCHAR(100) NOT NULL UNIQUE,
    Phone_Number     VARCHAR(10) NOT NULL,
    Username         VARCHAR(50) NOT NULL UNIQUE,
    Password_Hash    VARCHAR(255) NOT NULL,
    Vehicle_Info     VARCHAR(100),
    Account_Status   ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
    Created_By       VARCHAR(50),
    Created_Date     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS Deliveries (
    Delivery_ID             INT AUTO_INCREMENT PRIMARY KEY,
    Request_ID              INT NOT NULL,
    Delivery_Boy_ID         INT,
    Book_Name                VARCHAR(150) NOT NULL,
    Requester_ID             INT NOT NULL,
    Pickup_Name              VARCHAR(100),
    Pickup_Phone             VARCHAR(10),
    Pickup_Location          VARCHAR(150),
    Drop_Name                VARCHAR(100),
    Drop_Phone               VARCHAR(10),
    Drop_Location            VARCHAR(150),
    Expected_Delivery_Date   DATE,
    Delivered_Date           DATE,
    Status                   ENUM('Pending','Assigned','Picked Up','Delivered','Cancelled')
                             NOT NULL DEFAULT 'Pending',
    Created_Date             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Delivery_Boy_ID)
        REFERENCES Delivery_Boys(Delivery_Boy_ID)
        ON DELETE SET NULL
) ENGINE=InnoDB;
