import sqlite3

"""
This script resolves database table structure issues by recreating the audit_sessions
table with the correct schema to match app.py's expected structure.
"""

def fix_audit_sessions_table():
    # Connect to database
    conn = sqlite3.connect('audit_controls.db')
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_sessions'")
    if cursor.fetchone():
        # Drop the existing table to recreate with proper structure
        print("Dropping existing audit_sessions table...")
        cursor.execute("DROP TABLE audit_sessions")
    
    # Create the audit_sessions table with the proper structure
    print("Creating audit_sessions table with correct schema...")
    cursor.execute('''
        CREATE TABLE audit_sessions (
            id TEXT PRIMARY KEY,
            framework_filter TEXT,
            category_filter TEXT,
            risk_level_filter TEXT,
            sector_filter TEXT,
            region_filter TEXT,
            created_at TEXT,
            session_name TEXT
        )
    ''')
    
    # Commit changes and close
    conn.commit()
    conn.close()
    print("Database schema fixed successfully!")

if __name__ == "__main__":
    fix_audit_sessions_table()