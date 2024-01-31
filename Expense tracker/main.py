
from databases import initialize_wallet, login_user, register_user, validate_positive_number
from main_logic import add_deposit, add_expense, view_deposit, get_total_expenses, deposit_to_wallet, view_expenses, view_wallet_balance, get_total_deposit
import logging


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
