import sqlite3
import os
from datetime import datetime
from expense import Expense

class Database:
    def __init__(self, db_path="expenses.db"):
        self.db_path = db_path
        self.initialize()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create expenses table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL
            )
        ''')
        
        # Create categories table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Insert default categories if they don't exist
        default_categories = ["Food", "Transportation", "Housing", "Utilities", "Entertainment", "Healthcare", "Other"]
        for category in default_categories:
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
            
        conn.commit()
        conn.close()
    
    def add_expense(self, expense):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
            (expense.amount, expense.category, expense.description, expense.date.strftime("%Y-%m-%d"))
        )
        
        expense_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return expense_id
    
    def get_all_expenses(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        expenses = []
        
        for row in cursor.fetchall():
            expense = Expense(
                id=row["id"],
                amount=row["amount"],
                category=row["category"],
                description=row["description"],
                date=datetime.strptime(row["date"], "%Y-%m-%d")
            )
            expenses.append(expense)
        
        conn.close()
        return expenses
    
    def get_expense_by_id(self, expense_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM expenses WHERE id=?", (expense_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        expense = Expense(
            id=row["id"],
            amount=row["amount"],
            category=row["category"],
            description=row["description"],
            date=datetime.strptime(row["date"], "%Y-%m-%d")
        )
        
        conn.close()
        return expense
    
    def update_expense(self, expense):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE expenses SET amount=?, category=?, description=?, date=? WHERE id=?",
            (expense.amount, expense.category, expense.description, expense.date.strftime("%Y-%m-%d"), expense.id)
        )
        
        conn.commit()
        conn.close()
    
    def delete_expense(self, expense_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_categories(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row["name"] for row in cursor.fetchall()]
        
        conn.close()
        return categories
    
    def get_expense_summary_by_category(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        """)
        
        summary = {}
        for row in cursor.fetchall():
            summary[row["category"]] = row["total"]
        
        conn.close()
        return summary
    
    def get_expense_summary_by_date_range(self, start_date, end_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date, SUM(amount) as total
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date
        """, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        
        summary = {}
        for row in cursor.fetchall():
            summary[row["date"]] = row["total"]
        
        conn.close()
        return summary
