from datetime import datetime  # datetime imported and bound as datetime
import getpass  # for password user due to IDE for now enabled
import logging
import mysql.connector  # imported from library mysql
import bcrypt  # importing lib for hash password

# Create a MySQL database connection
conn = mysql.connector.connect(
    host="YOUR_LOCAL_HOSTNAME",
    user="YOUR_LOCAL_USERNAME",
    password="YOUR_LOCAL_PASSWORD",
    database="YOUR_LOCAL_DATABASE"
)
cursor = conn.cursor()


# Configure the logging system
logging.basicConfig(filename='expense_tracker.log', level=logging.INFO)


def register_user():
    """Register a new user."""
    username = input("Enter your username: ")
    password = input("Enter your password: ")  # Use getpass to hide the password
    hashed_password = hash_password(password)

    try:
        # Check if the username is already taken
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = %s', (username,))
        if cursor.fetchone()[0] > 0:
            print("Error: This username is already taken.")
            return

        # Add the new user to the database
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        conn.commit()
        logging.info("User registered: %s", username)
        print("Registration successful!")

    except mysql.connector.Error as err:
        logging.error("MySQL Error during registration: %s", err)
        print("Error occurred during registration. Check the logs for details.")


def login_user():
    """Log in an existing user."""
    username = input("Enter your username: ")
    password = input("Enter your password: ")  # Use getpass to hide the password
    hashed_password = hash_password(password)

    try:
        # Check if the username and password match
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = %s AND password = %s', (username, hashed_password))
        if cursor.fetchone()[0] > 0:
            logging.info("User logged in: %s", username)
            print("Login successful!")
        else:
            print("Error: Incorrect username or password.")

    except mysql.connector.Error as err:
        logging.error("MySQL Error during login: %s", err)
        print("Error occurred during login. Check the logs for details.")


# Function to hash passwords during registration
def hash_password(password):
    """Hash a password."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


# Function to check hashed password during login
def check_password(input_password, hashed_password):
    """Check if a password"""
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)


def validate_positive_number(amount):
    """Validate a positive"""
    try:
        amount = float(amount)
        if amount < 0:
            raise ValueError("Amount must be a positive number.")
        return amount
    except ValueError as exc:
        raise ValueError("Invalid input. Please enter a valid positive number.") from exc


def add_deposit(amount, category, description=""):
    """Add a new deposit to the database and update the wallet balance."""
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add the deposit to the database
    cursor.execute('''
        INSERT INTO deposit (amount, category, description, date)
        VALUES (%s, %s, %s, %s)
    ''', (amount, category, description, date))

    # Update the wallet balance
    cursor.execute('UPDATE wallet SET balance = balance + %s', (amount,))
    conn.commit()

    print("Deposit added successfully!")


def add_expense(amount, category, description=""):
    """Add a new expense to the database and deduct from the wallet."""
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if there's sufficient balance in the wallet
    wallet_balances = view_wallet_balance()

    if amount > wallet_balances:
        print("Error: Insufficient funds in the wallet.")
    else:
        # Add the expense to the database
        cursor.execute('''
            INSERT INTO expenses (amount, category, description, date)
            VALUES (%s, %s, %s, %s)
        ''', (amount, category, description, date))

        # Deduct the expense from the wallet
        cursor.execute('UPDATE wallet SET balance = balance - %s', (amount,))
        conn.commit()

        print("Expense added successfully!")


def view_deposit():
    """View all deposit in the database."""
    cursor.execute('SELECT * FROM deposit')
    deposit = cursor.fetchall()

    if not deposit:
        print("No deposits found.")
    else:
        print("ID | Amount | Category | Description | Date")
        print("------------------------------------------")
        for deposits in deposit:
            print(f"{deposits[0]} | {deposits[1]} | {deposits[2]} | {deposits[3]} | {deposits[4]}")


def view_expenses():
    """View all expenses in the database."""
    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()

    if not expenses:
        print("No expenses found.")
    else:
        print("ID | Amount | Category | Description | Date")
        print("------------------------------------------")
        for expense in expenses:
            print(f"{expense[0]} | {expense[1]} | {expense[2]} | {expense[3]} | {expense[4]}")


def get_total_deposit():
    """Calculate and return the total deposits."""
    cursor.execute('SELECT SUM(amount) FROM deposit')
    total_deposit = cursor.fetchone()[0]
    return total_deposit if total_deposit else 0.0


def get_total_expenses():
    """Calculate and return the total expenses."""
    cursor.execute('SELECT SUM(amount) FROM expenses')
    total_expense = cursor.fetchone()[0]
    return total_expense if total_expense else 0.0


def initialize_wallet():
    """Initialize the wallet with a default balance if it doesn't exist."""
    cursor.execute('SELECT COUNT(*) FROM wallet')
    wallet_exists = cursor.fetchone()[0]

    if not wallet_exists:
        initial_balance = 0.0  # Set your desired initial balance
        cursor.execute('INSERT INTO wallet (balance) VALUES (%s)', (initial_balance,))
        conn.commit()


def view_wallet_balance():
    """View the current balance in the wallet."""
    cursor.execute('SELECT balance FROM wallet LIMIT 1')
    balance = cursor.fetchone()[0]
    return balance if balance else 0.0


def deposit_to_wallet(amount):
    """Deposit money into the wallet."""
    cursor.execute('UPDATE wallet SET balance = balance + %s', (amount,))
    conn.commit()
    print("Deposit successful!")


def expense_from_wallet(amount):
    """Expense money from the wallet."""
    current_balance = view_wallet_balance()

    if amount > current_balance:
        print("Error: Insufficient funds in the wallet.")
    else:
        cursor.execute('UPDATE wallet SET balance = balance - %s', (amount,))
        conn.commit()
        print("Expense successful!")


def perform_transaction(operations):
    """Perform the transaction."""
    try:
        for operation in operations:
            # Execute database operation
            cursor.execute(operation)
        # Commit all changes if no errors occurred
        conn.commit()
        print("Transaction successful!")
    except Exception as ex:
        # Rollback changes if an error occurred
        conn.rollback()
        print(f"Transaction failed: {str(ex)}")


initialize_wallet()

while True:
    print("\nExpense Tracker Menu:")
    print("1. Register User")
    print("2. Log In")
    print("3. Deposit to Wallet")
    print("4. View Wallet Balance")
    print("5. Add Deposit")
    print("6. View Deposits")
    print("7. View Total Deposits")
    print("8. Add Expense")
    print("9. View Expenses")
    print("10. View Total Expenses")
    print("11. View Total Balance")
    print("12. Exit")

    choice = input("Enter your choice (1-12): ")

    try:

        if choice == '1':
            register_user()

        elif choice == '2':
            login_user()

        elif choice == '3':
            deposit_amount = validate_positive_number(float(input("Enter the deposit amount: ")))
            deposit_to_wallet(deposit_amount)

        elif choice == '4':
            wallet_balance = view_wallet_balance()
            print(f"\nCurrent Wallet Balance: {wallet_balance:.2f}")

        elif choice == '5':
            deposit_amount = float(input("Enter the deposit amount: "))
            deposit_category = input("Enter the deposit category: ")
            deposit_description = input("Enter a description (optional): ")
            add_deposit(deposit_amount, deposit_category, deposit_description)
            deposit_to_wallet(deposit_amount)

        elif choice == '6':
            view_deposit()

        elif choice == '7':
            total_deposits = get_total_deposit()
            print(f"\nTotal Deposits: {total_deposits:.2f}")

        elif choice == '8':
            expenses_amount = float(input("Enter the expense amount: "))
            expenses_category = input("Enter the expense category: ")
            expenses_description = input("Enter a description (optional): ")
            add_expense(expenses_amount, expenses_category, expenses_description)

        elif choice == '9':
            view_expenses()

        elif choice == '10':
            total_expenses = get_total_expenses()
            print(f"\nTotal Expenses: {total_expenses:.2f}")

        elif choice == '11':
            total_balance = view_wallet_balance() + get_total_deposit() - get_total_expenses()
            print(f"\nTotal Balance: {total_balance:.2f}")

        elif choice == '12':
            print("Exiting Expense Tracker. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 12.")

    except ValueError as ve:
        logging.error("ValueError occurred: %s", str(ve), exc_info=True)
    except Exception as e:
        logging.error("An unexpected error occurred: %s", str(e), exc_info=True)