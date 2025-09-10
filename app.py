from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend which doesn't require a GUI
import io
import base64
from database import Database
from expense import Expense

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a random string
db = Database()

@app.route('/')
def index():
    expenses = db.get_all_expenses()
    total_amount = sum(expense.amount for expense in expenses)
    categories = db.get_all_categories()
    
    # Generate the summary data
    category_summary = db.get_expense_summary_by_category()
    
    # Generate pie chart for categories
    if category_summary:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(
            category_summary.values(), 
            labels=category_summary.keys(),
            autopct='%1.1f%%',
            startangle=90,
            shadow=True
        )
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        category_chart = base64.b64encode(img.getvalue()).decode('utf8')
        plt.close()
    else:
        category_chart = None
    
    # Calculate date range for the past month
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Get daily expenses for the past month
    daily_summary = db.get_expense_summary_by_date_range(start_date, end_date)
    
    # Generate line chart for daily expenses
    if daily_summary:
        dates = list(daily_summary.keys())
        amounts = list(daily_summary.values())
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(dates, amounts, marker='o')
        ax.set_xlabel('Date')
        ax.set_ylabel('Amount')
        ax.set_title('Daily Expenses for the Past Month')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        daily_chart = base64.b64encode(img.getvalue()).decode('utf8')
        plt.close()
    else:
        daily_chart = None
    
    return render_template(
        'index.html', 
        expenses=expenses, 
        total_amount=total_amount,
        categories=categories,
        category_chart=category_chart,
        daily_chart=daily_chart
    )

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    categories = db.get_all_categories()
    
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount'))
            category = request.form.get('category')
            description = request.form.get('description')
            date_str = request.form.get('date')
            
            # Parse date string into datetime object
            date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()
            
            expense = Expense(amount=amount, category=category, description=description, date=date)
            db.add_expense(expense)
            
            flash('Expense added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error adding expense: {str(e)}', 'danger')
    
    return render_template('add.html', categories=categories)

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    expense = db.get_expense_by_id(expense_id)
    if not expense:
        flash('Expense not found!', 'danger')
        return redirect(url_for('index'))
    
    categories = db.get_all_categories()
    
    if request.method == 'POST':
        try:
            expense.amount = float(request.form.get('amount'))
            expense.category = request.form.get('category')
            expense.description = request.form.get('description')
            date_str = request.form.get('date')
            
            # Parse date string into datetime object
            expense.date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()
            
            db.update_expense(expense)
            
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating expense: {str(e)}', 'danger')
    
    return render_template('add.html', expense=expense, categories=categories)

@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    try:
        db.delete_expense(expense_id)
        flash('Expense deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting expense: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/report')
def report():
    # Get date range from query parameters, default to last 30 days
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    # Get expenses for the date range
    expenses = [exp for exp in db.get_all_expenses() 
                if start_date <= exp.date <= end_date]
    
    total_amount = sum(expense.amount for expense in expenses)
    
    # Group expenses by category
    category_summary = {}
    for expense in expenses:
        if expense.category not in category_summary:
            category_summary[expense.category] = 0
        category_summary[expense.category] += expense.amount
    
    # Generate pie chart for categories
    if category_summary:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(
            list(category_summary.values()), 
            labels=list(category_summary.keys()),
            autopct='%1.1f%%',
            startangle=90,
            shadow=True
        )
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Convert plot to PNG image
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        category_chart = base64.b64encode(img.getvalue()).decode('utf8')
        plt.close()
    else:
        category_chart = None
    
    return render_template(
        'report.html',
        expenses=expenses,
        total_amount=total_amount,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        category_summary=category_summary,
        category_chart=category_chart
    )

@app.route('/api/expenses')
def get_expenses():
    expenses = db.get_all_expenses()
    return jsonify([expense.to_dict() for expense in expenses])

if __name__ == '__main__':
    app.run(debug=True)
