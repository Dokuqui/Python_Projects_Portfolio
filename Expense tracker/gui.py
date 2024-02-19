import tkinter as tk
from tkinter import messagebox, simpledialog
from databases import conn, cursor, register_user, login_user, initialize_wallet
from main_logic import add_deposit, add_expense, view_deposit, get_total_expenses, view_expenses, view_wallet_balance, get_total_deposit
from csv_export import export_expenses, export_deposits

# Create a tkinter window
window = tk.Tk()
window.title("Expense Tracker")

# Set the window size and background color
window.geometry("600x400")
window.config(bg="#f0f0f0")

# Initialize the wallet
initialize_wallet()

def handle_registration():
    def register():
        username = entry_username.get()
        password = entry_password.get()

        if username and password:
            register_user(username, password)
            registration_window.destroy()  # Close the registration window after successful registration

    registration_window = tk.Toplevel(window)
    registration_window.title("Register")
    registration_window.geometry("300x200")
    registration_window.config(bg="#f0f0f0")

    label_username = tk.Label(registration_window, text="Username:", bg="#f0f0f0")
    label_username.pack(pady=5)
    entry_username = tk.Entry(registration_window)
    entry_username.pack(pady=5)

    label_password = tk.Label(registration_window, text="Password:", bg="#f0f0f0")
    label_password.pack(pady=5)
    entry_password = tk.Entry(registration_window, show="*")
    entry_password.pack(pady=5)

    button_register = tk.Button(registration_window, text="Register", command=register, bg="#4CAF50", fg="white")
    button_register.pack(pady=5)


# Function to handle user login
def handle_login():
    def login():
        username = entry_username.get()
        password = entry_password.get()

        if username and password:
            success, message = login_user(username, password)
            if success:
                logged_in_username.config(text=f"Logged in as: {username}")
                login_window.destroy()
            else:
                messagebox.showerror("Login Error", message)

    login_window = tk.Toplevel(window)
    login_window.title("Login")
    login_window.geometry("300x200")
    login_window.config(bg="#f0f0f0")

    label_username = tk.Label(login_window, text="Username:", bg="#f0f0f0")
    label_username.pack(pady=5)
    entry_username = tk.Entry(login_window)
    entry_username.pack(pady=5)

    label_password = tk.Label(login_window, text="Password:", bg="#f0f0f0")
    label_password.pack(pady=5)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack(pady=5)

    button_login = tk.Button(login_window, text="Login", command=login, bg="#4CAF50", fg="white")
    button_login.pack(pady=5)

# Function to add a deposit
def handle_deposit():
    amount = simpledialog.askfloat("Deposit", "Enter the deposit amount:")
    category = simpledialog.askstring("Deposit", "Enter the deposit category:")
    description = simpledialog.askstring("Deposit", "Enter a description (optional):")

    if amount and category:
        add_deposit(amount, category, description)

# Function to add an expense
def handle_expense():
    amount = simpledialog.askfloat("Expense", "Enter the expense amount:")
    category = simpledialog.askstring("Expense", "Enter the expense category:")
    description = simpledialog.askstring("Expense", "Enter a description (optional):")

    if amount and category:
        add_expense(amount, category, description)

# Function to view deposits
def handle_view_deposits():
    deposits = view_deposit()

    if not deposits:
        messagebox.showinfo("View Deposits", "No deposits found.")
    else:
        deposit_info = "ID | Amount | Category | Description | Date\n"
        for deposit in deposits:
            deposit_info += f"{deposit[0]} | {deposit[1]} | {deposit[2]} | {deposit[3]} | {deposit[4]}\n"

        messagebox.showinfo("View Deposits", deposit_info)

# Function to view expenses
def handle_view_expenses():
    expenses = view_expenses()

    if not expenses:
        messagebox.showinfo("View Expenses", "No expenses found.")
    else:
        expense_info = "ID | Amount | Category | Description | Date\n"
        for expense in expenses:
            expense_info += f"{expense[0]} | {expense[1]} | {expense[2]} | {expense[3]} | {expense[4]}\n"

        messagebox.showinfo("View Expenses", expense_info)

# Function to view total deposits
def handle_view_total_deposits():
    total_deposits = get_total_deposit()
    messagebox.showinfo("Total Deposits", f"Total Deposits: {total_deposits:.2f}")

# Function to view total expenses
def handle_view_total_expenses():
    total_expenses = get_total_expenses()
    messagebox.showinfo("Total Expenses", f"Total Expenses: {total_expenses:.2f}")

# Function to view wallet balance
def handle_view_wallet_balance():
    wallet_balance = view_wallet_balance()
    messagebox.showinfo("Wallet Balance", f"Current Wallet Balance: {wallet_balance:.2f}")

# Function to update wallet balance label
def update_wallet_balance_label():
    wallet_balance = view_wallet_balance()
    wallet_balance_label.config(text=f"Wallet Balance: {wallet_balance:.2f}")

# Create and style labels
label_frame = tk.LabelFrame(window, text="Expense Tracker", bg="#f0f0f0", padx=10, pady=10)
label_frame.pack(expand=True, fill="both")

# Create labels and align them in a grid
labels = [
    ("Register", handle_registration),
    ("Login", handle_login),
    ("Add Deposit", handle_deposit),
    ("Add Expense", handle_expense),
    ("View Deposits", handle_view_deposits),
    ("View Expenses", handle_view_expenses),
    ("View Total Deposits", handle_view_total_deposits),
    ("View Total Expenses", handle_view_total_expenses),
    ("View Wallet Balance", handle_view_wallet_balance),
    ("Export Expenses", lambda: export_expenses(view_expenses)),  # Pass view_expenses function
    ("Export Deposits", lambda: export_deposits(view_deposit))  # Pass view_deposit function
]

for i, (text, command) in enumerate(labels):
    label = tk.Label(label_frame, text=text, bg="#f0f0f0", font=("Helvetica", 12))
    label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

    button = tk.Button(label_frame, text="Go", command=command, width=5, height=1, bg="#4CAF50", fg="white")
    button.grid(row=i, column=1, padx=10, pady=5, sticky="e")

# Create and style label to show wallet balance
wallet_balance_label = tk.Label(window, text="Wallet Balance: 0.00", bg="#f0f0f0", font=("Helvetica", 12))
wallet_balance_label.place(relx=0.5, rely=0.9, anchor="center")

# Label to display logged-in username
logged_in_username = tk.Label(window, text="", bg="#f0f0f0", font=("Helvetica", 12))
logged_in_username.place(relx=0.7, rely=0.1, anchor="center")

# Update wallet balance label
update_wallet_balance_label()

# Run the tkinter event loop
window.mainloop()
