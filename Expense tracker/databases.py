import getpass  # for password user due to IDE for now enabled
import logging
import mysql.connector  # imported from library mysql
import bcrypt  # importing lib for hash password


# Create a MySQL database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Krys1234!",
    database="expense_tracker"
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
        # Retrieve the hashed password from the database for the given username
        cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
        stored_password = cursor.fetchone()

        if stored_password and check_password(password, stored_password[0]):
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


def initialize_wallet():
    """Initialize the wallet with a default balance if it doesn't exist."""
    cursor.execute('SELECT COUNT(*) FROM wallet')
    wallet_exists = cursor.fetchone()[0]

    if not wallet_exists:
        initial_balance = 0.0  # Set your desired initial balance
        cursor.execute('INSERT INTO wallet (balance) VALUES (%s)', (initial_balance,))
        conn.commit()


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


def validate_positive_number(amount):
    """Validate a positive"""
    try:
        amount = float(amount)
        if amount < 0:
            raise ValueError("Amount must be a positive number.")
        return amount
    except ValueError as exc:
        raise ValueError("Invalid input. Please enter a valid positive number.") from exc
