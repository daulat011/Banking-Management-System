            -- BANKING MANAGEMENT SYSTEM — MySQL SCHEMA

-- Run this once against your MySQL server before starting the app:-
--   mysql -u your_user -p your_database < schema.sql

-- If you already created the database yourself, you can drop the
-- CREATE DATABASE / USE lines and just run the CREATE TABLE statements
-- inside your existing database.

CREATE DATABASE IF NOT EXISTS banking_system;
USE banking_system;

-- ---------------------------------------------------
-- ACCOUNTS
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS accounts (
    acc_no          INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)  NOT NULL,
    age             INT           NOT NULL,
    mobile          VARCHAR(15)   NOT NULL,
    password_hash   VARCHAR(64)   NOT NULL,          -- SHA-256 hex digest
    account_type    ENUM('Savings','Current') NOT NULL DEFAULT 'Savings',
    balance         DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    failed_attempts INT           NOT NULL DEFAULT 0,
    locked_until    DATETIME      NULL,               -- NULL = not locked
    created_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);


-- TRANSACTIONS  (deposits / withdrawals / transfers)

CREATE TABLE IF NOT EXISTS transactions (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    acc_no        INT NOT NULL,
    txn_type      VARCHAR(40)   NOT NULL,
    amount        DECIMAL(12,2) NOT NULL,
    balance_after DECIMAL(12,2) NOT NULL,
    txn_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no) ON DELETE CASCADE
);


-- LOANS

CREATE TABLE IF NOT EXISTS loans (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    acc_no         INT NOT NULL,
    loan_amount    DECIMAL(12,2) NOT NULL,
    interest_rate  DECIMAL(5,2)  NOT NULL,    -- annual %, e.g. 9.50
    tenure_months  INT           NOT NULL,
    emi            DECIMAL(12,2) NOT NULL,
    status         ENUM('Pending','Approved','Rejected','Closed') NOT NULL DEFAULT 'Pending',
    applied_on     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no) ON DELETE CASCADE
);


-- FIXED DEPOSITS

CREATE TABLE IF NOT EXISTS fixed_deposits (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    acc_no           INT NOT NULL,
    principal        DECIMAL(12,2) NOT NULL,
    interest_rate    DECIMAL(5,2)  NOT NULL,
    tenure_months    INT           NOT NULL,
    maturity_amount  DECIMAL(12,2) NOT NULL,
    start_date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status           ENUM('Active','Matured') NOT NULL DEFAULT 'Active',
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no) ON DELETE CASCADE
);


-- ADMIN LOGIN

CREATE TABLE IF NOT EXISTS admins (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL
);

-- default admin login:--  username = admin, password = admin123
-- (CHANGE THIS before deploying anywhere public)
INSERT INTO admins (username, password_hash)
SELECT 'admin', SHA2('admin123', 256)
WHERE NOT EXISTS (SELECT 1 FROM admins WHERE username = 'admin');
