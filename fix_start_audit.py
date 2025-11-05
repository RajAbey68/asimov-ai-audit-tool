"""
This script fixes the start audit functionality by ensuring
the correct tables are used and properly structured.
"""

import sqlite3
import uuid
import datetime

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def fix_audit_sessions():
    """Fix the audit_sessions table structure and create a test session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create a consistent audit_sessions table structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_sessions (
            session_id TEXT PRIMARY KEY,
            session_name TEXT,
            framework_filter TEXT,
            framework_pattern TEXT,
            category_filter TEXT,
            risk_level_filter TEXT,
            sector_filter TEXT,
            region_filter TEXT
        )
    ''')
    
    # Create a test session for direct access
    session_id = "test-mvp-session-1"
    framework_filter = "EU AI Act (2023)"
    framework_pattern = "%EU AI Act%"
    category_filter = "Defensive Model Strengthening"
    risk_level_filter = "High Risk"
    sector_filter = "Financial Services"
    region_filter = "EU"
    
    # First check if it already exists
    cursor.execute('SELECT * FROM audit_sessions WHERE session_id = ?', (session_id,))
    if cursor.fetchone() is None:
        # If it doesn't exist, create it
        cursor.execute('''
            INSERT INTO audit_sessions (
                session_id, session_name, framework_filter, framework_pattern,
                category_filter, risk_level_filter, sector_filter, region_filter
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, 
            f"Test MVP Session - {datetime.datetime.now().strftime('%Y-%m-%d')}",
            framework_filter,
            framework_pattern,
            category_filter, 
            risk_level_filter,
            sector_filter,
            region_filter
        ))
    
    conn.commit()
    conn.close()
    
    print("✅ Fixed audit_sessions table and created test session")

if __name__ == "__main__":
    fix_audit_sessions()