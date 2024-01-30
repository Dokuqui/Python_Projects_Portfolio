from datetime import datetime  # datetime imported and bound as datetime
import mysql.connector  # imported from library mysql

# Create a MySQL database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Krys1234!",
    database="expense_tracker"
)
cursor = conn.cursor()


def add_expense(amounts, categories, descriptions=""):
    """Add a new expense to the database."""
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO expenses (amount, category, description, date)
        VALUES (%s, %s, %s, %s)
    ''', (amounts, categories, descriptions, date))
    conn.commit()
    print("Expense added successfully!")


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


def get_total_expenses():
    """Calculate and return the total expenses."""
    cursor.execute('SELECT SUM(amount) FROM expenses')
    total_expense = cursor.fetchone()[0]
    return total_expense if total_expense else 0.0


while True:
    print("\nExpense Tracker Menu:")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. View Total Expenses")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        amount = float(input("Enter the expense amount: "))
        category = input("Enter the expense category: ")
        description = input("Enter a description (optional): ")
        add_expense(amount, category, description)

    elif choice == '2':
        view_expenses()

    elif choice == '3':
        total_expenses = get_total_expenses()
        print(f"\nTotal Expenses: {total_expenses:.2f}")

    elif choice == '4':
        print("Exiting Expense Tracker. Goodbye!")
        break

    else:
        print("Invalid choice. Please enter a number between 1 and 4.")
