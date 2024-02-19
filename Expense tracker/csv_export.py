# csv_export.py
from tkinter import messagebox

import csv

def export_csv(data, filename):
    """Export data to a CSV file."""
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Amount", "Category", "Description", "Date"])
        writer.writerows(data)

def export_expenses(view_expenses):
    expenses = view_expenses()
    if expenses:
        filename = "expenses.csv"
        export_csv(expenses, filename)
        messagebox.showinfo("Export Expenses", f"Expenses exported to {filename}")
    else:
        messagebox.showinfo("Export Expenses", "No expenses found.")

def export_deposits(view_deposit):
    deposits = view_deposit()
    if deposits:
        filename = "deposits.csv"
        export_csv(deposits, filename)
        messagebox.showinfo("Export Deposits", f"Deposits exported to {filename}")
    else:
        messagebox.showinfo("Export Deposits", "No deposits found.")
