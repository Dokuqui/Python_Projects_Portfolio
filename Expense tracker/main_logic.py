from datetime import datetime
from databases import conn, cursor
# from gui import create_main_window


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