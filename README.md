# 🏦 Banking Management System

A full-stack **Banking Management System** built using **Python, Streamlit, MySQL, and Pandas**. The application provides separate customer and admin workflows for account management, banking transactions, loans, fixed deposits, transaction history, and account security.

The project uses **MySQL for persistent data storage** and **Streamlit** for the interactive web interface.

---

## 📌 Project Overview

The Banking Management System simulates core banking operations through a web-based application.

Customers can create and manage their accounts, perform transactions, view their financial information, apply for loans, and manage fixed deposits.

Administrators can manage customer-related banking operations and review loan applications.

### Architecture

```text
┌──────────────────────────┐
│       Streamlit UI       │
│        daulat.py         │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   Database / DB Layer    │
│          db.py           │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│         MySQL            │
│     banking_system       │
└──────────────────────────┘
```

---

## ✨ Features

### 👤 Customer Management

* Customer registration
* Customer login
* Profile management
* Password change
* Account information management
* Customer dashboard
* Account balance viewing

### 🔐 Authentication & Security

* Customer and admin authentication
* Password hashing using **SHA-256**
* Failed-login lockout mechanism
* Password management
* Input validation
* Transaction confirmation
* Receiver verification for fund transfers

### 💰 Banking Transactions

* Deposit money
* Withdraw money
* Transfer funds
* Balance validation
* Insufficient-balance validation
* Receiver verification
* Transaction confirmation
* Persistent transaction records
* Transaction history

### 📄 Transaction Statements

* View transaction history
* Generate/download transaction statements
* CSV statement generation using **Pandas**

### 💳 Loan Management

* Loan application
* CIBIL-score-based logic
* Dynamic interest-rate calculation
* Loan tenure handling
* EMI calculation
* Loan application tracking
* Admin loan approval/rejection workflow

### 🏦 Fixed Deposits

* Fixed Deposit creation
* Interest-rate calculation
* Tenure-based maturity calculation
* FD maturity information

### 👨‍💼 Admin Features

* Admin authentication
* Customer-related management
* Loan application review
* Loan approval/rejection
* Administrative banking workflows

---

## 🛠️ Tech Stack

| Technology          | Purpose                              |
| ------------------- | ------------------------------------ |
| **Python**          | Application and business logic       |
| **Streamlit**       | Web application interface            |
| **MySQL**           | Persistent database                  |
| **Pandas**          | Transaction statement/CSV processing |
| **mysql.connector** | Python–MySQL connectivity            |
| **TOML**            | Secure application configuration     |
| **Git & GitHub**    | Version control                      |

---

## 📁 Project Structure

```text
Banking-Management-System/
│
├── daulat.py                 # Main Streamlit application
├── db.py                     # Database operations and MySQL connectivity
├── schema.sql                # Database schema
├── requirements.txt          # Python dependencies
├── secrets.toml.example      # Example configuration file
├── .gitignore                # Files excluded from Git
│
└── .streamlit/
    └── secrets.toml          # Local database credentials (not committed)
```

---

## 🗄️ Database

The application uses **MySQL** with the following database configuration:

```text
Database: banking_system
Host: localhost
Port: 3306
```

The complete database structure is provided in:

```text
schema.sql
```

Run the SQL schema in MySQL before starting the application.

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Banking-Management-System.git
cd Banking-Management-System
```

Replace `YOUR_USERNAME` with your GitHub username.

---

### 2. Create and activate the environment

The project was developed using a dedicated Python environment.

For Conda:

```bash
conda create -n crashcourse python=3.14
conda activate crashcourse
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure MySQL

Create the database:

```sql
CREATE DATABASE banking_system;
```

Then execute the provided:

```text
schema.sql
```

file to create the required tables and database structure.

---

### 5. Configure Streamlit secrets

Create:

```text
.streamlit/secrets.toml
```

using `secrets.toml.example` as a reference.

Example:

```toml
[mysql]
host = "localhost"
port = 3306
user = "your_mysql_username"
password = "your_mysql_password"
database = "banking_system"
```

> ⚠️ **Never commit `.streamlit/secrets.toml` to GitHub.**
>
> It contains database credentials and is intentionally excluded through `.gitignore`.

---

### 6. Run the application

```bash
streamlit run daulat.py
```

If the `streamlit` command is not available in the activated environment, use:

```bash
python -m streamlit run daulat.py
```

The application will open in your browser at the local Streamlit address.

---

## 🔒 Security Considerations

The project includes several security-oriented implementations:

* Password hashing using SHA-256
* Failed-login lockout
* Credential validation
* Protected database credentials through Streamlit secrets
* `.gitignore` configuration to prevent secrets from being committed
* Input validation for banking operations
* Receiver verification before fund transfers

### Git Security

The following files/directories are excluded from version control:

```gitignore
.streamlit/secrets.toml
__pycache__/
*.pyc
```

The repository contains:

```text
secrets.toml.example
```

instead of the actual credentials file.

---

## 🧪 Validation & Error Handling

The application validates important banking operations before modifying the database.

Examples include:

* Invalid transaction amounts
* Insufficient account balance
* Invalid receiver account
* Transfer to the same account
* Incorrect login credentials
* Incorrect password during password changes
* Invalid customer inputs
* Loan-related validation
* Transaction confirmation

These validations help prevent invalid operations from reaching the database.

---

## 🐛 Development & Debugging Experience

One of the main goals of this project was not only to implement banking features but also to understand how to debug a real application.

During development, several issues were identified and fixed, including:

### Deposit Workflow Issue

A deposit operation was accidentally connected to transfer-related logic. This caused incorrect session-state handling and unexpected behavior after depositing money.

The issue was traced through the transaction workflow and corrected so that deposit and transfer operations use their respective database functions and session-state logic.

### Database Integration Issues

The project required debugging the interaction between:

```text
Streamlit → Python → MySQL
```

Database connection and query-related issues were investigated while implementing persistent banking operations.

### Transaction Validation

Additional validation was required for:

* Receiver verification
* Invalid transfer amounts
* Insufficient balance
* Same-account transfers
* Transaction confirmation

### Environment & Streamlit Issues

The project also involved resolving Python environment problems, including situations where the `streamlit` command was unavailable because the wrong Python environment was active.

The final setup uses the dedicated `crashcourse` environment.

---

## 📊 Core Application Flow

### Customer Login

```text
Customer
   │
   ▼
Login
   │
   ├── Invalid credentials → Error
   │
   └── Valid credentials
            │
            ▼
       Customer Dashboard
```

### Fund Transfer

```text
Customer
   │
   ▼
Enter Receiver
   │
   ▼
Verify Receiver
   │
   ▼
Enter Amount
   │
   ▼
Validate Balance
   │
   ▼
Confirm Transaction
   │
   ▼
Update MySQL
   │
   ▼
Transaction Recorded
```

### Loan Workflow

```text
Customer
   │
   ▼
Loan Application
   │
   ▼
CIBIL / Eligibility Logic
   │
   ▼
Interest + EMI Calculation
   │
   ▼
Admin Review
   │
   ├── Rejected
   │
   └── Approved
```

---

## 📚 What I Learned

Through this project, I worked with:

* Python application development
* Streamlit application development
* MySQL database integration
* SQL schema design
* CRUD-style database operations
* Authentication workflows
* Password hashing
* Session-state management
* Input validation
* Transaction processing
* Financial calculations
* CSV generation with Pandas
* Debugging and error handling
* Git and GitHub
* Environment management
* Application deployment

---

## 🚀 Future Improvements

Potential improvements for future versions include:

* Role-based access control improvements
* More advanced authentication mechanisms
* Improved transaction reporting
* Automated testing
* Better database transaction handling
* Enhanced UI/UX
* More detailed admin analytics
* Improved audit logging
* Containerized deployment

---

## 👨‍💻 Author

**Daulat Singh**

BCA — Artificial Intelligence & Machine Learning

Interested in **AI/ML, Python development, backend development, and software engineering**.

---

## ⭐ Project

If you find this project useful or interesting, consider giving the repository a ⭐ on GitHub.
