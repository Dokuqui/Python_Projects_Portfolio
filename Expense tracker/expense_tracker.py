from datetime import datetime  # datetime imported and bound as datetime
import mysql.connector  # imported from library mysql

# Create a MySQL database connection
conn = mysql.connector.connect(
    host="YOUR_LOCAL_HOSTNAME",
    user="YOUR_LOCAL_USERNAME",
    password="YOUR_LOCAL_PASSWORD",
    database="YOUR_LOCAL_DATABASE"
)
cursor = conn.cursor()


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


initialize_wallet()


while True:
    print("\nExpense Tracker Menu:")
    print("1. Deposit to Wallet")
    print("2. View Wallet Balance")
    print("3. Add Deposit")
    print("4. View Deposits")
    print("5. View Total Deposits")
    print("6. Add Expense")
    print("7. View Expenses")
    print("8. View Total Expenses")
    print("9. View Total Balance")
    print("10. Exit")

    choice = input("Enter your choice (1-10): ")

    if choice == '1':
        deposit_amount = float(input("Enter the deposit amount: "))
        deposit_to_wallet(deposit_amount)

    elif choice == '2':
        wallet_balance = view_wallet_balance()
        print(f"\nCurrent Wallet Balance: {wallet_balance:.2f}")

    elif choice == '3':
        deposit_amount = float(input("Enter the deposit amount: "))
        deposit_category = input("Enter the deposit category: ")
        deposit_description = input("Enter a description (optional): ")
        add_deposit(deposit_amount, deposit_category, deposit_description)
        deposit_to_wallet(deposit_amount)

    elif choice == '4':
        view_deposit()

    elif choice == '5':
        total_deposits = get_total_deposit()
        print(f"\nTotal Deposits: {total_deposits:.2f}")

    elif choice == '6':
        expenses_amount = float(input("Enter the expense amount: "))
        expenses_category = input("Enter the expense category: ")
        expenses_description = input("Enter a description (optional): ")
        add_expense(expenses_amount, expenses_category, expenses_description)

    elif choice == '7':
        view_expenses()

    elif choice == '8':
        total_expenses = get_total_expenses()
        print(f"\nTotal Expenses: {total_expenses:.2f}")

    elif choice == '9':
        total_balance = view_wallet_balance() + get_total_deposit() - get_total_expenses()
        print(f"\nTotal Balance: {total_balance:.2f}")

    elif choice == '10':
        print("Exiting Expense Tracker. Goodbye!")
        break

    else:
        print("Invalid choice. Please enter a number between 1 and 10.")
