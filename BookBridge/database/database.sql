-- ============================================================
-- database.sql
-- Database schema for the Used Book Exchange, Donation & Resale
-- Platform ("Book Bank Management System").
--
-- Run this once before starting the application:
--   mysql -u root -p < database.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS book_bank;
USE book_bank;

-- Drop tables in reverse dependency order (safe to re-run this script)
DROP TABLE IF EXISTS User_Preferences;
DROP TABLE IF EXISTS Password_Change_History;
DROP TABLE IF EXISTS Profile_Update_History;
DROP TABLE IF EXISTS Login_History;
DROP TABLE IF EXISTS Administrators;
DROP TABLE IF EXISTS Users;

-- ------------------------------------------------------------
-- Users table
-- NOTE: Security_Question / Security_Answer_Hash and Is_Deleted
-- are small additions (beyond the base spec) required to support
-- Forgot Password (Feature 6) and Soft Delete (Feature 8).
-- ------------------------------------------------------------
CREATE TABLE Users (
    User_ID               INT AUTO_INCREMENT PRIMARY KEY,
    Full_Name             VARCHAR(100) NOT NULL,
    Email                 VARCHAR(100) NOT NULL UNIQUE,
    Phone_Number          VARCHAR(10)  NOT NULL UNIQUE,
    Location              VARCHAR(100),
    Username              VARCHAR(50)  NOT NULL UNIQUE,
    Password_Hash         VARCHAR(255) NOT NULL,
    Role                  ENUM('Buyer','Seller','Donor','Exchange User') NOT NULL,
    Account_Status        ENUM('Active','Inactive') NOT NULL DEFAULT 'Active',
    Account_Created_Date  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Security_Question     VARCHAR(255),
    Security_Answer_Hash  VARCHAR(255),
    Is_Deleted             TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Administrators table
-- ------------------------------------------------------------
CREATE TABLE Administrators (
    Admin_ID        INT AUTO_INCREMENT PRIMARY KEY,
    Full_Name       VARCHAR(100) NOT NULL,
    Email           VARCHAR(100) NOT NULL UNIQUE,
    Phone_Number    VARCHAR(10)  NOT NULL,
    Username        VARCHAR(50)  NOT NULL UNIQUE,
    Password_Hash   VARCHAR(255) NOT NULL,
    Admin_Level     VARCHAR(50)  NOT NULL,
    Created_By      VARCHAR(50),
    Created_Date    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Account_Status  ENUM('Active','Inactive') NOT NULL DEFAULT 'Active'
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Login history (Feature 9: Activity History)
-- ------------------------------------------------------------
CREATE TABLE Login_History (
    Login_ID      INT AUTO_INCREMENT PRIMARY KEY,
    User_ID       INT NOT NULL,
    Login_Date    DATE NOT NULL,
    Login_Time    TIME NOT NULL,
    Logout_Date   DATE,
    Logout_Time   TIME,
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Profile update history (Feature 9)
-- ------------------------------------------------------------
CREATE TABLE Profile_Update_History (
    Update_ID       INT AUTO_INCREMENT PRIMARY KEY,
    User_ID         INT NOT NULL,
    Field_Changed   VARCHAR(50) NOT NULL,
    Old_Value       VARCHAR(255),
    New_Value       VARCHAR(255),
    Updated_Date    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Password change history (Feature 9)
-- ------------------------------------------------------------
CREATE TABLE Password_Change_History (
    Change_ID     INT AUTO_INCREMENT PRIMARY KEY,
    User_ID       INT NOT NULL,
    Changed_Date  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Account preferences (Feature 7)
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
    FOREIGN KEY (User_ID) REFERENCES Users(User_ID) ON DELETE CASCADE
) ENGINE=InnoDB;
