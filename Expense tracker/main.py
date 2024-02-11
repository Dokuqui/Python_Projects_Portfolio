from databases import initialize_wallet, login_user, register_user, validate_positive_number
from main_logic import add_deposit, add_expense, view_deposit, get_total_expenses, view_expenses, view_wallet_balance, get_total_deposit
import logging


initialize_wallet()

while True:
    print("\nExpense Tracker Menu:")
    print("1. Register User")
    print("2. Log In")
    print("3. View Wallet Balance")
    print("4. Add Deposit")
    print("5. View Deposits")
    print("6. View Total Deposits")
    print("7. Add Expense")
    print("8. View Expenses")
    print("9. View Total Expenses")
    print("10. View Total Balance")
    print("11. Exit")

    choice = input("Enter your choice (1-12): ")

    try:

        if choice == '1':
            register_user()

        elif choice == '2':
            login_user()

        elif choice == '3':
            wallet_balance = view_wallet_balance()
            print(f"\nCurrent Wallet Balance: {wallet_balance:.2f}")

        elif choice == '4':
            deposit_amount = validate_positive_number(float(input("Enter the deposit amount: ")))
            deposit_category = input("Enter the deposit category: ")
            deposit_description = input("Enter a description (optional): ")
            add_deposit(deposit_amount, deposit_category, deposit_description)

        elif choice == '5':
            view_deposit()

        elif choice == '6':
            total_deposits = get_total_deposit()
            print(f"\nTotal Deposits: {total_deposits:.2f}")

        elif choice == '7':
            expenses_amount = float(input("Enter the expense amount: "))
            expenses_category = input("Enter the expense category: ")
            expenses_description = input("Enter a description (optional): ")
            add_expense(expenses_amount, expenses_category, expenses_description)

        elif choice == '8':
            view_expenses()

        elif choice == '9':
            total_expenses = get_total_expenses()
            print(f"\nTotal Expenses: {total_expenses:.2f}")

        elif choice == '10':
            total_balance = view_wallet_balance() + get_total_deposit() - get_total_expenses()
            print(f"\nTotal Balance: {total_balance:.2f}")

        elif choice == '11':
            print("Exiting Expense Tracker. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 12.")

    except ValueError as ve:
        logging.error("ValueError occurred: %s", str(ve), exc_info=True)
    except Exception as e:
        logging.error("An unexpected error occurred: %s", str(e), exc_info=True)
