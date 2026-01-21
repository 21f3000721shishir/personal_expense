import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional

DB_PATH = "expenses.db"

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """Initialize database and create table if not exists"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # First, check if description column exists
    cursor.execute("PRAGMA table_info(personal_expenses)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'description' not in columns and 'personal_expenses' in [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        # Add description column to existing table
        cursor.execute("ALTER TABLE personal_expenses ADD COLUMN description TEXT")
        conn.commit()
    
    # Create table if not exists (with description column)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personal_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL CHECK (
                category IN (
                    'FOOD',
                    'RENT',
                    'TRANSPORT',
                    'GROCERIES',
                    'UTILITIES',
                    'ENTERTAINMENT',
                    'HEALTH',
                    'EDUCATION',
                    'SHOPPING',
                    'TRAVEL',
                    'OTHER'
                )
            ),
            description TEXT,
            expense_date DATE NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def check_duplicate(amount: float, category: str, expense_date: str, description: str, time_window_minutes: int = 5) -> Optional[Dict]:
    """
    Check if a similar expense exists within the time window (duplicate detection for idempotency)
    Returns the existing expense if found, None otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Calculate time threshold
    time_threshold = (datetime.now() - timedelta(minutes=time_window_minutes)).strftime('%Y-%m-%d %H:%M:%S')
    
    query = """
        SELECT id, amount, category, description, expense_date, created_at
        FROM personal_expenses
        WHERE amount = ?
        AND category = ?
        AND expense_date = ?
        AND (description = ? OR (description IS NULL AND ? IS NULL))
        AND created_at >= ?
        ORDER BY created_at DESC
        LIMIT 1
    """
    
    cursor.execute(query, (amount, category, expense_date, description, description, time_threshold))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def add_expense(amount: float, category: str, expense_date: str, description: str = None) -> Dict:
    """
    Add a new expense to the database with duplicate detection
    Returns the created (or existing duplicate) expense
    """
    # Check for duplicates
    existing = check_duplicate(amount, category, expense_date, description)
    if existing:
        return {
            "status": "duplicate",
            "expense": existing,
            "message": "Duplicate expense detected. Returning existing record."
        }
    
    # Insert new expense
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO personal_expenses (amount, category, description, expense_date)
        VALUES (?, ?, ?, ?)
    """, (amount, category, description, expense_date))
    
    expense_id = cursor.lastrowid
    conn.commit()
    
    # Fetch the created expense
    cursor.execute("""
        SELECT id, amount, category, description, expense_date, created_at
        FROM personal_expenses
        WHERE id = ?
    """, (expense_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return {
        "status": "created",
        "expense": dict(row),
        "message": "Expense created successfully."
    }

def get_expenses(category: Optional[str] = None, sort_by_date_desc: bool = False) -> List[Dict]:
    """
    Get expenses with optional filtering and sorting
    
    Args:
        category: Filter by category (optional)
        sort_by_date_desc: Sort by date descending (newest first)
    
    Returns:
        List of expense dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, amount, category, description, expense_date, created_at FROM personal_expenses"
    params = []
    
    # Add category filter
    if category:
        query += " WHERE category = ?"
        params.append(category)
    
    # Add sorting
    if sort_by_date_desc:
        query += " ORDER BY expense_date DESC, created_at DESC"
    else:
        query += " ORDER BY expense_date ASC, created_at ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_total_expenses(category: Optional[str] = None) -> float:
    """
    Calculate total of expenses (optionally filtered by category)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT SUM(amount) as total FROM personal_expenses"
    params = []
    
    if category:
        query += " WHERE category = ?"
        params.append(category)
    
    cursor.execute(query, params)
    result = cursor.fetchone()
    conn.close()
    
    return result['total'] if result['total'] else 0.0

def delete_expense(expense_id: int) -> bool:
    """
    Delete an expense by ID
    
    Args:
        expense_id: ID of the expense to delete
    
    Returns:
        True if deleted successfully, False if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if expense exists
    cursor.execute("SELECT id FROM personal_expenses WHERE id = ?", (expense_id,))
    if not cursor.fetchone():
        conn.close()
        return False
    
    # Delete the expense
    cursor.execute("DELETE FROM personal_expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    
    return True

# Initialize database on import
init_db()