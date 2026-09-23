        #db.py-- All database logic for the Banking Management System


import hashlib
import random
from datetime import datetime, timedelta

import mysql.connector
import streamlit as st

MAX_FAILED_ATTEMPTS = 3
LOCKOUT_MINUTES = 15

# Simplified annual interest rates used across the app.
SAVINGS_INTEREST_RATE = 4.0     # % per year, applied to savings accounts
FD_RATES = {
    6: 6.25,
    12: 6.75,
    24: 7.00,
    36: 7.10,
}
LOAN_RATES = {
    6: 8.50,
    12: 9.00,
    24: 9.50,
    36: 10.00,
    60: 10.50,
}      # % per year, flat rate for simplicity


#CONNECTION

def get_connection():
    """
    Reads credentials from .streamlit/secrets.toml, so you never
    hardcode a password in the source file. See secrets.toml.example
    for the format expected.
    """
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=cfg.get("port", 3306),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
    )


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


#ACCOUNT CREATION or LOGIN

def create_account(name, age, mobile, password, account_type):
    conn = get_connection()
    cur = conn.cursor()
    cibil = random.randint(650,900)

    cur.execute(
    """
    INSERT INTO accounts
    (name, age, mobile, password_hash,
    account_type,
    balance,
    cibil_score)

    VALUES
    (%s,%s,%s,%s,%s,0,%s)
    """,(name,age,mobile,hash_password(password),account_type,cibil,))
    conn.commit()
    acc_no = cur.lastrowid
    cur.close()
    conn.close()
    return acc_no


def get_account(acc_no):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM accounts WHERE acc_no = %s", (acc_no,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row




def get_account_name(acc_no):

    account = get_account(acc_no)

    if account:
        return account["name"]

    return None





def verify_login(acc_no, password):
    """
    Returns one of: "not_found", "locked", "wrong_password", "success".
    Tracks failed attempts and locks the account after MAX_FAILED_ATTEMPTS.
    """
    account = get_account(acc_no)
    if account is None:
        return "not_found"

    # Check lockout
    if account["locked_until"] and account["locked_until"] > datetime.now():
        return "locked"

    if account["password_hash"] != hash_password(password):
        _register_failed_attempt(acc_no, account["failed_attempts"])
        return "wrong_password"

    #Successful login clears any previous failed attempts
    _reset_failed_attempts(acc_no)
    return "success"


def _register_failed_attempt(acc_no, current_attempts):
    conn = get_connection()
    cur = conn.cursor()
    new_attempts = current_attempts + 1
    if new_attempts >= MAX_FAILED_ATTEMPTS:
        locked_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
        cur.execute(
            "UPDATE accounts SET failed_attempts = %s, locked_until = %s WHERE acc_no = %s",
            (new_attempts, locked_until, acc_no),
        )
    else:
        cur.execute(
            "UPDATE accounts SET failed_attempts = %s WHERE acc_no = %s",
            (new_attempts, acc_no),
        )
    conn.commit()
    cur.close()
    conn.close()


def _reset_failed_attempts(acc_no):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE accounts SET failed_attempts = 0, locked_until = NULL WHERE acc_no = %s",
        (acc_no,),
    )
    conn.commit()
    cur.close()
    conn.close()


def change_password(acc_no, old_password, new_password):

    account = get_account(acc_no)

    print("=" * 50)
    print("Account Number :", acc_no)
    print("Current Hash   :", account["password_hash"])
    print("Old Hash       :", hash_password(old_password))
    print("New Hash       :", hash_password(new_password))

    if account["password_hash"] != hash_password(old_password):
        print("Old password does not match!")
        return False, "Old Password is incorrect."

    if old_password == new_password:
        print("New password is same as old password!")
        return False, "New Password cannot be the same as the old password."

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE accounts SET password_hash = %s WHERE acc_no = %s",
        (hash_password(new_password), acc_no),
    )

    print("Rows Updated:", cur.rowcount)

    conn.commit()


    cur.execute(
        "SELECT password_hash FROM accounts WHERE acc_no = %s",
        (acc_no,)
    )

    print("Database Hash :", cur.fetchone()[0])

    cur.close()
    conn.close()

    print("=" * 50)

    return True, "Password Changed Successfully."



#TRANSACTIONS

def _log_transaction(cur, acc_no, txn_type, amount, balance_after):
    cur.execute(
        """INSERT INTO transactions (acc_no, txn_type, amount, balance_after)
           VALUES (%s, %s, %s, %s)""",
        (acc_no, txn_type, amount, balance_after),
    )


def deposit(acc_no, amount):
    if amount <= 0:
        return False, "Invalid Amount"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no = %s", (amount, acc_no))
    cur.execute("SELECT balance FROM accounts WHERE acc_no = %s", (acc_no,))
    new_balance = cur.fetchone()[0]
    _log_transaction(cur, acc_no, "Deposit", amount, new_balance)
    conn.commit()
    cur.close()
    conn.close()
    return True, f"Deposit Successful. Current Balance: ₹{new_balance:.2f}"


def withdraw(acc_no, amount):
    account = get_account(acc_no)
    if amount <= 0:
        return False, "Invalid Amount"
    if amount > account["balance"]:
        return False, "Insufficient Balance"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance - %s WHERE acc_no = %s", (amount, acc_no))
    cur.execute("SELECT balance FROM accounts WHERE acc_no = %s", (acc_no,))
    new_balance = cur.fetchone()[0]
    _log_transaction(cur, acc_no, "Withdraw", amount, new_balance)
    conn.commit()
    cur.close()
    conn.close()
    return True, f"Withdrawal Successful. Current Balance: ₹{new_balance:.2f}"


def transfer(acc_no, receiver_no, amount):
    sender = get_account(acc_no)
    receiver = get_account(receiver_no)

    if receiver is None:
        return False, "Receiver Account Not Found"
    if receiver_no == acc_no:
        return False, "Cannot Transfer To Same Account"
    if amount <= 0:
        return False, "Invalid Amount"
    if amount > sender["balance"]:
        return False, "Insufficient Balance"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance - %s WHERE acc_no = %s", (amount, acc_no))
    cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no = %s", (amount, receiver_no))

    cur.execute("SELECT balance FROM accounts WHERE acc_no = %s", (acc_no,))
    sender_balance = cur.fetchone()[0]
    cur.execute("SELECT balance FROM accounts WHERE acc_no = %s", (receiver_no,))
    receiver_balance = cur.fetchone()[0]

    _log_transaction(cur, acc_no, f"Transfer to {receiver_no}", amount, sender_balance)
    _log_transaction(cur, receiver_no, f"Transfer from {acc_no}", amount, receiver_balance)

    conn.commit()
    cur.close()
    conn.close()
    return True, f"Transfer Successful. Current Balance: ₹{sender_balance:.2f}"


def get_transactions(acc_no):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT txn_date AS Date, txn_type AS Type, amount AS Amount, balance_after AS `Balance After` "
        "FROM transactions WHERE acc_no = %s ORDER BY txn_date DESC",
        (acc_no,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


#LOANS

def calculate_emi(principal, annual_rate, tenure_months):

    total_interest = principal * (annual_rate / 100) * (tenure_months / 12)

    total_repayable = principal + total_interest

    return round(total_repayable / tenure_months, 2)


def apply_for_loan(acc_no, loan_amount, tenure_months):
    account = get_account(acc_no)

    if account["cibil_score"] < 700:
        return None
    rate = LOAN_RATES[tenure_months]

    emi = calculate_emi(
        loan_amount,
        rate,
        tenure_months
    )
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO loans
        (acc_no, loan_amount, interest_rate,
        tenure_months, emi, status)

        VALUES
        (%s,%s,%s,%s,%s,'Pending')
        """,
        (
            acc_no,
            loan_amount,
            rate,
            tenure_months,
            emi
        ),
    )
    conn.commit()
    cur.close()
    conn.close()
    return emi


def get_loans(acc_no):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM loans WHERE acc_no = %s ORDER BY applied_on DESC", (acc_no,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_all_loans():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT loans.*, accounts.name FROM loans
           JOIN accounts ON accounts.acc_no = loans.acc_no
           ORDER BY applied_on DESC"""
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def update_loan_status(loan_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE loans SET status = %s WHERE id = %s", (status, loan_id))
    conn.commit()
    cur.close()
    conn.close()


# -----------------------------------------------------
# FIXED DEPOSITS
# -----------------------------------------------------
def calculate_fd_maturity(principal, annual_rate, tenure_months):
    interest = principal * (annual_rate / 100) * (tenure_months / 12)
    return round(principal + interest, 2)


def create_fd(acc_no, principal, tenure_months):
    if tenure_months not in FD_RATES:
        raise ValueError("Unsupported tenure")
    rate = FD_RATES[tenure_months]
    maturity = calculate_fd_maturity(principal, rate, tenure_months)

    account = get_account(acc_no)
    if principal > account["balance"]:
        return None, "Insufficient Balance to open this FD"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance - %s WHERE acc_no = %s", (principal, acc_no))
    cur.execute("SELECT balance FROM accounts WHERE acc_no = %s", (acc_no,))
    new_balance = cur.fetchone()[0]
    _log_transaction(cur, acc_no, "Fixed Deposit", principal, new_balance)
    cur.execute(
        """INSERT INTO fixed_deposits (acc_no, principal, interest_rate, tenure_months, maturity_amount)
           VALUES (%s, %s, %s, %s, %s)""",
        (acc_no, principal, rate, tenure_months, maturity),
    )
    conn.commit()
    cur.close()
    conn.close()
    return maturity, None


def get_fds(acc_no):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM fixed_deposits WHERE acc_no = %s ORDER BY start_date DESC", (acc_no,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# -----------------------------------------------------
# ADMIN
# -----------------------------------------------------
def verify_admin(username, password):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM admins WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        return False
    return row["password_hash"] == hash_password(password)


def get_bank_summary():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT
             COUNT(*) AS total_accounts,
             COALESCE(SUM(balance), 0) AS total_balance
           FROM accounts"""
    )
    summary = cur.fetchone()

    cur.execute("SELECT COUNT(*) AS pending_loans FROM loans WHERE status = 'Pending'")
    summary["pending_loans"] = cur.fetchone()["pending_loans"]

    cur.execute("SELECT COALESCE(SUM(loan_amount),0) AS total_loans_issued FROM loans WHERE status = 'Approved'")
    summary["total_loans_issued"] = cur.fetchone()["total_loans_issued"]

    cur.close()
    conn.close()
    return summary


def get_all_accounts():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT acc_no, name, account_type, mobile, balance, created_at FROM accounts ORDER BY acc_no"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
