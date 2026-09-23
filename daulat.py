            #BANKING MANAGEMENT SYSTEM

# All database work in db.py, This file is only UI:
# screens, forms, buttons, and which db.py function to call.


import streamlit as st
import pandas as pd
import time

import db

st.set_page_config(page_title="Banking Management System", page_icon="🏦", layout="centered")

st.markdown("""
<style>

/* Hide 'Press Enter to submit form' */
div[data-testid="InputInstructions"]{
    display:none;
}

</style>
""", unsafe_allow_html=True)


#SESSION STATE
#(only UI state now — the data itself lives in MySQL)

if "logged_in_acc" not in st.session_state:
    st.session_state.logged_in_acc = None

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False



# SCREEN: not logged in,  then:  Customer Login / Create Account / Admin Login

def show_auth_screen():
    st.title("Banking Management System")

    tab_login, tab_create, tab_admin = st.tabs(["Login", "Create Account", "Admin Login"])

    with tab_login:
        st.subheader("Customer Login")
        with st.form("login_form"):
            acc_input = st.text_input("Account Number")
            pw_input = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

        if submitted:
            if not acc_input.strip().isdigit():
                st.error("Please enter a valid numeric account number.")
            else:
                result = db.verify_login(int(acc_input), pw_input)
                if result == "not_found":
                    st.error("Account Not Found")
                elif result == "locked":
                    st.error(
                        f"Account locked due to {db.MAX_FAILED_ATTEMPTS} failed attempts. "
                        f"Try again in {db.LOCKOUT_MINUTES} minutes."
                    )
                elif result == "wrong_password":
                    st.error("Wrong Password")
                else:
                    st.session_state.logged_in_acc = int(acc_input)
                    st.success("Login Successful")
                    st.rerun()

    with tab_create:
        st.subheader("Create Account")
        with st.form("create_account_form", clear_on_submit=True):
            name = st.text_input("Enter Name")
            age = st.number_input("Enter Age", min_value=18, max_value=120, step=1)
            mobile = st.text_input("Enter Mobile Number")
            account_type = st.selectbox("Account Type", ["Savings", "Current"])
            password = st.text_input("Create Password", type="password")
            submitted_create = st.form_submit_button("Create Account")

        if submitted_create:
            if not name.strip() or not mobile.strip() or not password:
                st.error("Please fill in all fields.")
            else:
                acc_no = db.create_account(name.strip(), int(age), mobile.strip(), password, account_type)
                st.success("Account Created Successfully!")
                st.info(f"Your Account Number is **{acc_no}** — save it, you'll need it to log in.")
                time.sleep(4)
                st.rerun()

    with tab_admin:
        st.subheader("Admin Login")
        with st.form("admin_login_form"):
            username = st.text_input("Admin Username")
            admin_pw = st.text_input("Admin Password", type="password")
            admin_submit = st.form_submit_button("Login as Admin")

        if admin_submit:
            if db.verify_admin(username, admin_pw):
                st.session_state.is_admin = True
                st.success("Admin Login Successful")
                st.rerun()
            else:
                st.error("Invalid Admin Credentials")



# SCREEN: logged in as customer

def show_customer_dashboard():
    acc = st.session_state.logged_in_acc
    info = db.get_account(acc)

    if info is None:
        # account was deleted, or something odd happened — bounce back to login
        st.session_state.logged_in_acc = None
        st.rerun()

    st.sidebar.title("Customer Menu")
    st.sidebar.markdown(f"**{info['name']}**  \nAccount No: `{acc}` · {info['account_type']}")
    st.sidebar.divider()

    menu = st.sidebar.radio(
        "Choose an action",
        [
            "Check Balance",
            "Deposit Money",
            "Withdraw Money",
            "Transfer Money",
            "Transaction History",
            "Apply for Loan",
            "My Loans",
            "Open Fixed Deposit",
            "My Fixed Deposits",
            "View Profile",
            "Change Password",
            "Logout",
        ],
        label_visibility="collapsed",
    )

    st.title("Banking Management System")

    st.markdown("---")

    st.subheader(f"Welcome Back, {info['name']} 👋")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Current Balance",
            f"₹{info['balance']:,.2f}"
        )

    with col2:
        st.metric(
            "Account Type",
            info["account_type"]
        )

    loan_count = len(db.get_loans(acc))
    fd_count = len(db.get_fds(acc))

    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric(
            "CIBIL Score",
            info["cibil_score"]
        )

    with col4:
        st.metric(
            "Active Loans",
            loan_count
        )

    with col5:
        st.metric(
            "Fixed Deposits",
            fd_count
        )

    st.markdown("---")

    if menu == "Check Balance":
        st.subheader("Current Balance")
        st.metric("Balance", f"₹{info['balance']:.2f}")
        if info["account_type"] == "Savings":
            st.caption(f"Savings accounts earn {db.SAVINGS_INTEREST_RATE}% interest per year.")

    elif menu == "Deposit Money":

        st.subheader("Deposit Money")

        # Initialize session state
        if "confirm_deposit" not in st.session_state:
            st.session_state.confirm_deposit = False

        with st.form("deposit_form", clear_on_submit=True):

            amount = st.text_input(
                "Enter Deposit Amount",
                placeholder="Enter amount"
            )

            submitted = st.form_submit_button("Deposit")

        #Step1- User submits amount
        if submitted:

            if not amount.isdigit():
                st.error("Please enter a valid amount.")

            else:
                st.session_state.deposit_amount = int(amount)
                st.session_state.confirm_deposit = True

        # Step2- Confirmation (outside the form)
        if st.session_state.confirm_deposit:

            st.warning(
                f"Do you really want to deposit ₹{st.session_state.deposit_amount}?"
            )

            col1, col2 = st.columns(2)

            if col1.button("Confirm Deposit"):

                ok, msg = db.deposit(
                    acc,
                    st.session_state.deposit_amount
                )

                if ok:

                    # hide confirmation
                    st.session_state.confirm_deposit = False

                    # remove saved amount
                    st.session_state.pop("deposit_amount", None)

                    st.success(msg)

                    time.sleep(3)

                    st.rerun()

                else:
                    st.error(msg)

            if col2.button("Cancel"):

                st.session_state.confirm_deposit = False
                st.rerun()

    elif menu == "Withdraw Money":

        st.subheader("Withdraw Money")

        # Initialize session state
        if "confirm_withdraw" not in st.session_state:
            st.session_state.confirm_withdraw = False

        with st.form("withdraw_form", clear_on_submit=True):

            amount = st.text_input(
                "Enter Withdraw Amount",
                placeholder="Enter amount"
            )

            submitted = st.form_submit_button("Withdraw")

        #Step1- User submits amount
        if submitted:

            if not amount.isdigit():
                st.error("Please enter a valid amount.")

            else:
                st.session_state.withdraw_amount = int(amount)
                st.session_state.confirm_withdraw = True

        #Step2- Confirmation
        if st.session_state.confirm_withdraw:

            st.warning(
                f"Do you really want to withdraw ₹{st.session_state.withdraw_amount}?"
            )

            col1, col2 = st.columns(2)

            if col1.button("Confirm Withdraw"):

                ok, msg = db.transfer(
                    acc,
                    st.session_state.transfer_receiver,
                    st.session_state.transfer_amount
                )

                if ok:

                    # Hide confirmation immediately
                    st.session_state.confirm_transfer = False

                    # Clear stored transfer details
                    del st.session_state.transfer_receiver
                    del st.session_state.transfer_amount
                    del st.session_state.receiver_name

                    # Show success message
                    st.success(msg)

                    time.sleep(3)

                    st.rerun()

                else:
                    st.error(msg)

            if col2.button("Cancel"):

                st.session_state.confirm_withdraw = False
                st.rerun()

                

    elif menu == "Transfer Money":

        st.subheader("Transfer Money")

        # Initialize session state
        if "confirm_transfer" not in st.session_state:
            st.session_state.confirm_transfer = False

        with st.form("transfer_form", clear_on_submit=True):

            receiver = st.text_input("Enter Receiver Account Number")

            amount = st.text_input(
                "Enter Amount",
                placeholder="Enter amount"
            )

            submitted = st.form_submit_button("Transfer")

        #when user clicks Transfer
        if submitted:

            if not receiver.strip().isdigit():
                st.error("Please enter a valid receiver account number.")

            elif not amount.isdigit():
                st.error("Please enter a valid amount.")

            else:

                #fetching receiver details
                receiver_info = db.get_account(int(receiver))

                if receiver_info is None:

                    st.error("Receiver Account Not Found.")

                elif int(receiver) == acc:

                    st.error("You cannot transfer money to your own account.")

                else:

                    st.session_state.transfer_receiver = int(receiver)
                    st.session_state.receiver_name = receiver_info["name"]
                    st.session_state.transfer_amount = int(amount)
                    st.session_state.confirm_transfer = True



        # confirmation screen
        if st.session_state.confirm_transfer:

            with st.container(border=True):

                st.subheader("Transfer Confirmation")

                st.write(f"**From Account :** {acc}")
                st.write(f"**Receiver Account :** {st.session_state.transfer_receiver}")
                st.write(f"**Receiver Name :** {st.session_state.receiver_name}")
                st.write(f"**Amount :** ₹{st.session_state.transfer_amount:,}")

                col1, col2 = st.columns(2)

                if col1.button("Confirm Transfer"):

                    ok, msg = db.transfer(
                        acc,
                        st.session_state.transfer_receiver,
                        st.session_state.transfer_amount
                    )

                    if ok:

                        st.session_state.confirm_transfer = False

                        # Clear stored transfer details
                        del st.session_state.transfer_receiver
                        del st.session_state.transfer_amount
                        del st.session_state.receiver_name

                        st.success(msg)

                        time.sleep(3)

                        st.rerun()

                    else:
                        st.error(msg)

                if col2.button("Cancel"):

                    st.session_state.confirm_transfer = False
                    st.rerun()



    elif menu == "Transaction History":
        st.subheader("Transaction History")
        txns = db.get_transactions(acc)
        if not txns:
            st.info("No transactions yet.")
        else:
            df = pd.DataFrame(txns)
            st.markdown("**Mini Statement** (last 5)")
            st.dataframe(df.head(5), use_container_width=True, hide_index=True)
            with st.expander("View Full Statement"):
                st.dataframe(df, use_container_width=True, hide_index=True)
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Full Statement (CSV)", data=csv_data,
                                file_name=f"statement_{acc}.csv", mime="text/csv")
            



    elif menu == "Apply for Loan":

        st.subheader("Apply for a Loan")

        loan_amount = st.text_input(
            "Loan Amount",
            placeholder="Enter amount"
        )

        tenure = st.selectbox(
            "Tenure (months)",
            [6, 12, 24, 36, 60]
        )

        rate = db.LOAN_RATES[tenure]

        st.info(f"Interest Rate : {rate}% per annum")

        submitted = st.button("Apply for Loan")

        if submitted:

            if not loan_amount.isdigit():
                st.error("Please enter a valid amount.")

            else:

                account = db.get_account(acc)

                if account["cibil_score"] < 700:

                    st.error(
                        f"""
    Loan Rejected

    Your CIBIL Score : {account['cibil_score']}

    Minimum Required : 700
    """
                    )

                else:

                    emi = db.apply_for_loan(
                        acc,
                        int(loan_amount),
                        tenure
                    )

                    st.success(
                        f"""
    Loan Approved Successfully!

    CIBIL Score : {account['cibil_score']}

    Interest Rate : {rate}%

    Estimated EMI : ₹{emi:.2f}/month
    """
                    )
                    time.sleep(5)
                    st.rerun()

    elif menu == "My Loans":
        st.subheader("My Loans")
        loans = db.get_loans(acc)
        if not loans:
            st.info("No loan applications yet.")
        else:
            st.dataframe(pd.DataFrame(loans), use_container_width=True, hide_index=True)

    elif menu == "Open Fixed Deposit":

        st.subheader("Open a Fixed Deposit")

        principal = st.text_input(
            "Amount to Deposit",
            placeholder="Enter amount"
        )

        tenure = st.selectbox(
            "Tenure (months)",
            list(db.FD_RATES.keys())
        )

        rate = db.FD_RATES[tenure]

        st.info(f"Interest Rate : {rate}% per annum")

        submitted = st.button("Open Fixed Deposit")
        if submitted:

            if not principal.isdigit():
                st.error("Please enter a valid amount.")

            else:

                maturity, error = db.create_fd(
                    acc,
                    int(principal),
                    tenure
                )

                if error:
                    st.error(error)

                else:
                    st.success(
                        f"Fixed Deposit opened! Maturity amount: ₹{maturity:.2f}"
                    )
                    time.sleep(5)
                    st.rerun()

    elif menu == "My Fixed Deposits":
        st.subheader("My Fixed Deposits")
        fds = db.get_fds(acc)
        if not fds:
            st.info("No fixed deposits yet.")
        else:
            st.dataframe(pd.DataFrame(fds), use_container_width=True, hide_index=True)

    elif menu == "View Profile":
        st.subheader("Profile")
        st.write(f"**Account Number:** {acc}")
        st.write(f"**Name:** {info['name']}")
        st.write(f"**Age:** {info['age']}")
        st.write(f"**Mobile:** {info['mobile']}")
        st.write(f"**Account Type:** {info['account_type']}")

        #st.write(f"**CIBIL Score:** {info['cibil_score']}")

        score = info["cibil_score"]

        if score >= 800:
            rating = "Excellent"

        elif score >= 700:
            rating = "Good"

        elif score >= 600:
            rating = "Average"

        else:
            rating = "Poor"

        st.write(f"**CIBIL Score:** {score}")
        st.write(f"**Credit Rating:** {rating}")
        st.write(f"**Balance:** ₹{info['balance']:.2f}")

    elif menu == "Change Password":
        st.subheader("Change Password")

        with st.form("change_password_form", clear_on_submit=True):
            old_pw = st.text_input("Enter Old Password", type="password")
            new_pw = st.text_input("Enter New Password", type="password")
            submitted = st.form_submit_button("Change Password")

        if submitted:

            if not old_pw or not new_pw:
                st.error("Please fill in both password fields.")

            else:

                ok, msg = db.change_password(
                    acc,
                    old_pw,
                    new_pw
                )

                if ok:
                    st.success(msg)
                    time.sleep(4)      #wait for 2 seconds
                    st.rerun()
                else:
                    st.error(msg)

    elif menu == "Logout":
        st.session_state.logged_in_acc = None
        st.success("Logged Out Successfully")
        time.sleep(2)
        st.rerun()


#logged in as admin

def show_admin_dashboard():
    st.sidebar.title("Admin Menu")
    menu = st.sidebar.radio(
        "Choose a view",
        ["Bank Summary", "All Accounts", "Loan Approvals", "Logout"],
        label_visibility="collapsed",
    )

    st.title("Admin Dashboard")

    if menu == "Bank Summary":
        summary = db.get_bank_summary()
        col1, col2 = st.columns(2)
        col1.metric("Total Accounts", summary["total_accounts"])
        col2.metric("Total Bank Balance", f"₹{summary['total_balance']:.2f}")
        col3, col4 = st.columns(2)
        col3.metric("Pending Loans", summary["pending_loans"])
        col4.metric("Total Loans Issued", f"₹{summary['total_loans_issued']:.2f}")

    elif menu == "All Accounts":
        st.subheader("All Accounts")
        accounts = db.get_all_accounts()
        st.dataframe(pd.DataFrame(accounts), use_container_width=True, hide_index=True)

    elif menu == "Loan Approvals":
        st.subheader("Loan Approvals")
        loans = db.get_all_loans()
        pending = [l for l in loans if l["status"] == "Pending"]

        if not pending:
            st.info("No pending loan applications.")
        else:
            for loan in pending:
                with st.container(border=True):
                    st.write(
                        f"**Loan #{loan['id']}** — {loan['name']} (Acc {loan['acc_no']}) "
                        f"requested ₹{loan['loan_amount']:.2f} for {loan['tenure_months']} months "
                        f"(EMI ₹{loan['emi']:.2f})"
                    )
                    c1, c2 = st.columns(2)
                    if c1.button("Approve", key=f"approve_{loan['id']}"):

                        db.update_loan_status(loan["id"], "Approved")

                        st.success(
                            f"Loan of ₹{loan['loan_amount']:,.0f} for "
                            f"{loan['name']} has been approved successfully."
                        )

                        time.sleep(3)

                        st.rerun()
                    if c2.button("Reject", key=f"reject_{loan['id']}"):

                        db.update_loan_status(loan["id"], "Rejected")

                        st.success(
                            f"Loan of ₹{loan['loan_amount']:,.0f} for "
                            f"{loan['name']} has been rejected."
                        )

                        time.sleep(3)

                        st.rerun()

        with st.expander("View All Loans (any status)"):
            st.dataframe(pd.DataFrame(loans), use_container_width=True, hide_index=True)

    elif menu == "Logout":
        st.session_state.is_admin = False
        st.success("Logged Out Successfully")
        time.sleep(2)
        st.rerun()



#Main

if st.session_state.is_admin:
    show_admin_dashboard()
elif st.session_state.logged_in_acc is not None:
    show_customer_dashboard()
else:
    show_auth_screen()
