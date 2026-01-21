from flask import Flask, request, jsonify
from flask_cors import CORS
import db_helper
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for Streamlit frontend

# Valid categories
VALID_CATEGORIES = [
    'FOOD', 'RENT', 'TRANSPORT', 'GROCERIES', 'UTILITIES',
    'ENTERTAINMENT', 'HEALTH', 'EDUCATION', 'SHOPPING', 'TRAVEL', 'OTHER'
]

@app.route('/expenses', methods=['POST'])
def create_expense():
    """
    Create a new expense
    Request body: {amount, category, description, date}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        amount = data.get('amount')
        category = data.get('category')
        expense_date = data.get('date')  # Frontend sends 'date'
        description = data.get('description', '')
        
        # Validation
        if amount is None:
            return jsonify({"error": "amount is required"}), 400
        
        if not category:
            return jsonify({"error": "category is required"}), 400
        
        if not expense_date:
            return jsonify({"error": "date is required"}), 400
        
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({"error": "amount must be greater than 0"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "amount must be a valid number"}), 400
        
        # Validate category
        category = category.upper()
        if category not in VALID_CATEGORIES:
            return jsonify({"error": f"category must be one of: {', '.join(VALID_CATEGORIES)}"}), 400
        
        # Add expense (with duplicate detection)
        result = db_helper.add_expense(amount, category, expense_date, description)
        
        # Return appropriate status code
        if result['status'] == 'duplicate':
            return jsonify(result), 200  # 200 for idempotent behavior
        else:
            return jsonify(result), 201  # 201 for created
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/expenses', methods=['GET'])
def get_expenses():
    """
    Get list of expenses
    Query parameters:
    - category: filter by category (optional)
    - sort: 'date_desc' to sort by date descending (optional)
    """
    try:
        # Get query parameters
        category = request.args.get('category')
        sort = request.args.get('sort')
        
        # Validate category if provided
        if category:
            category = category.upper()
            if category not in VALID_CATEGORIES:
                return jsonify({"error": f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"}), 400
        
        # Determine sorting
        sort_by_date_desc = (sort == 'date_desc')
        
        # Get expenses from database
        expenses = db_helper.get_expenses(category=category, sort_by_date_desc=sort_by_date_desc)
        
        # Calculate total
        total = db_helper.get_total_expenses(category=category)
        
        return jsonify({
            "expenses": expenses,
            "total": total,
            "count": len(expenses)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Expense Tracker API is running"}), 200


@app.route('/categories', methods=['GET'])
def get_categories():
    """Get list of valid categories"""
    return jsonify({"categories": VALID_CATEGORIES}), 200

@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """
    Delete an expense by ID
    Path parameter: expense_id
    """
    try:
        # Delete expense
        deleted = db_helper.delete_expense(expense_id)
        
        if deleted:
            return jsonify({
                "message": "Expense deleted successfully",
                "id": expense_id
            }), 200
        else:
            return jsonify({"error": "Expense not found"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



