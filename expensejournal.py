# Import libraries
import json
import os
import sqlite3
from datetime import datetime
import pandas as pd
# GUI libraries
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

# Global variables
expenses = []
categories = ['groceries', 'transportation', 'utilities', 'entertainment']

# Load expenses from JSON
def load_expenses():
    global expenses
    if os.path.exists('expenses.json'):
        try:
            with open('expenses.json', 'r') as file:
                expenses = json.load(file)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error loading expenses.")
            expenses = []

# Save expenses to JSON
def save_expenses():
    with open('expenses.json', 'w') as file:
        json.dump(expenses, file)

# Load categories from JSON
def load_categories():
    global categories
    if os.path.exists('categories.json'):
        try:
            with open('categories.json', 'r') as file:
                categories = json.load(file)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error loading categories.")
            categories = ['groceries', 'transportation', 'utilities', 'entertainment']

# Save categories to JSON
def save_categories():
    with open('categories.json', 'w') as file:
        json.dump(categories, file)

# Add a new category
def add_category(category):
    if category not in categories:
        categories.append(category)
        save_categories()
        return True
    return False

# Add expense
def add_expense(amount, description, date, category):
    try:
        amount = float(amount)
        datetime.strptime(date, '%Y-%m-%d')  # Ensure date format is correct
        if category not in categories:
            if not add_category(category):
                return "Category already exists."
        expense = {
            'amount': amount,
            'description': description,
            'date': date,
            'category': category
        }
        expenses.append(expense)
        save_expenses()
        return "Expense added successfully!"
    except ValueError:
        return "Invalid input. Please ensure amount is a number and date is in YYYY-MM-DD format."

# Edit expense
def edit_expense(index, amount, description, date, category):
    try:
        amount = float(amount)
        datetime.strptime(date, '%Y-%m-%d')  # Ensure date format is correct
        if category not in categories:
            if not add_category(category):
                return "Category already exists."
        expenses[index] = {
            'amount': amount,
            'description': description,
            'date': date,
            'category': category
        }
        save_expenses()
        return "Expense updated successfully!"
    except ValueError:
        return "Invalid input. Please ensure amount is a number and date is in YYYY-MM-DD format."

# Delete expense
def delete_expense(index):
    if 0 <= index < len(expenses):
        del expenses[index]
        save_expenses()
        return "Expense deleted successfully."
    return "Invalid index."

# Show summary
def show_summary():
    if not expenses:
        return "No expenses recorded."
    
    total = sum(exp['amount'] for exp in expenses)
    summary = f"Total expenses: ${total:.2f}\n"
    
    category_totals = {}
    for exp in expenses:
        cat = exp['category']
        category_totals[cat] = category_totals.get(cat, 0) + exp['amount']
    
    for cat, amt in category_totals.items():
        summary += f"{cat.capitalize()}: ${amt:.2f}\n"
    
    dates = [datetime.strptime(exp['date'], '%Y-%m-%d') for exp in expenses]
    total_days = (max(dates) - min(dates)).days + 1
    avg_daily_expense = total / total_days
    summary += f"Average daily expense: ${avg_daily_expense:.2f}\n"
    
    highest_expense = max(expenses, key=lambda x: x['amount'])
    lowest_expense = min(expenses, key=lambda x: x['amount'])
    summary += f"Highest expense: ${highest_expense['amount']:.2f} on {highest_expense['date']}, Description: {highest_expense['description']}\n"
    summary += f"Lowest expense: ${lowest_expense['amount']:.2f} on {lowest_expense['date']}, Description: {lowest_expense['description']}\n"
    
    summary += "\nCategory Statistics:\n"
    for cat, total in category_totals.items():
        percentage = (total / total) * 100
        summary += f"{cat.capitalize()}: ${total:.2f} ({percentage:.2f}% of total spending)\n"
    
    return summary

# Export to Excel
def export_to_excel():
    if not expenses:
        return "No expenses to export."
    
    df = pd.DataFrame(expenses)
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                           filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        df.to_excel(file_path, index=False, engine='openpyxl')
        return f"Expenses exported to '{file_path}'."
    return "Export cancelled."

# Export to text file
def export_to_text():
    if not expenses:
        return "No expenses to export."
    
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                           filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, 'w') as file:
            for exp in expenses:
                file.write(f"Date: {exp['date']}, Amount: ${exp['amount']:.2f}, Description: {exp['description']}, Category: {exp['category']}\n")
        return f"Expenses exported to '{file_path}'."
    return "Export cancelled."

# Export to SQLite
def export_to_sqlite():
    if not expenses:
        return "No expenses to export."
    
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (amount REAL, description TEXT, date TEXT, category TEXT)''')
    c.execute('DELETE FROM expenses')  # Clear existing data
    
    for exp in expenses:
        c.execute('INSERT INTO expenses VALUES (?, ?, ?, ?)',
                  (exp['amount'], exp['description'], exp['date'], exp['category']))
    
    conn.commit()
    conn.close()
    
    return "Expenses exported to 'expenses.db'."

# GUI functions (main)
def add_expense_gui():
    amount = simpledialog.askstring("Input", "Enter amount spent:")
    description = simpledialog.askstring("Input", "Enter description of purchase:")
    date = simpledialog.askstring("Input", "Enter date (YYYY-MM-DD):")
    category = simpledialog.askstring("Input", f"Enter category from the list {categories}:").lower()
    message = add_expense(amount, description, date, category)
    messagebox.showinfo("Result", message)

def edit_expense_gui():
    index = simpledialog.askinteger("Input", "Enter the index of the expense to edit:")
    if index is not None and 0 <= index < len(expenses):
        amount = simpledialog.askstring("Input", f"New amount (current: ${expenses[index]['amount']}):") or expenses[index]['amount']
        description = simpledialog.askstring("Input", f"New description (current: {expenses[index]['description']}):") or expenses[index]['description']
        date = simpledialog.askstring("Input", f"New date (YYYY-MM-DD, current: {expenses[index]['date']}):") or expenses[index]['date']
        category = simpledialog.askstring("Input", f"New category (current: {expenses[index]['category']}):") or expenses[index]['category']
        message = edit_expense(index, amount, description, date, category)
        messagebox.showinfo("Result", message)
    else:
        messagebox.showerror("Error", "Invalid index.")

def delete_expense_gui():
    index = simpledialog.askinteger("Input", "Enter the index of the expense to delete:")
    message = delete_expense(index)
    messagebox.showinfo("Result", message)

def show_summary_gui():
    summary = show_summary()
    messagebox.showinfo("Summary", summary)

def export_data_gui():
    choice = simpledialog.askstring("Export", "Choose format (excel, text, sqlite):").lower()
    if choice == 'excel':
        message = export_to_excel()
    elif choice == 'text':
        message = export_to_text()
    elif choice == 'sqlite':
        message = export_to_sqlite()
    else:
        message = "Invalid choice."
    messagebox.showinfo("Result", message)

def add_category_gui():
    new_category = simpledialog.askstring("Input", "Enter new category name:").strip().lower()
    if add_category(new_category):
        messagebox.showinfo("Result", f"Category '{new_category}' added.")
    else:
        messagebox.showinfo("Result", f"Category '{new_category}' already exists.")

# Setup GUI
def setup_gui():
    root = tk.Tk()
    root.title("Expense Tracker")

    tk.Button(root, text="Add Expense", command=add_expense_gui).pack(pady=5)
    tk.Button(root, text="Edit Expense", command=edit_expense_gui).pack(pady=5)
    tk.Button(root, text="Delete Expense", command=delete_expense_gui).pack(pady=5)
    tk.Button(root, text="Add Category", command=add_category_gui).pack(pady=5)
    tk.Button(root, text="Show Summary", command=show_summary_gui).pack(pady=5)
    tk.Button(root, text="Export Data", command=export_data_gui).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

    load_expenses()
    load_categories()
    
    root.mainloop()

# Run
if __name__ == "__main__":
    setup_gui()
