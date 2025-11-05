"""
Create a test session with a fixed ID for direct access
This will let users bypass the problematic form submission
"""

import sqlite3
import datetime

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_test_session():
    """Create a test session with a fixed ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create a test session for direct access
    session_id = "direct-test-session"
    test_name = f"Direct Test Session {datetime.datetime.now().strftime('%Y-%m-%d')}"
    
    # Make sure the table exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_sessions (
        session_id TEXT PRIMARY KEY,
        session_name TEXT,
        framework_filter TEXT, 
        framework_pattern TEXT,
        category_filter TEXT,
        risk_level_filter TEXT,
        sector_filter TEXT,
        region_filter TEXT,
        session_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # First check if it already exists
    cursor.execute('SELECT * FROM audit_sessions WHERE session_id = ?', (session_id,))
    if cursor.fetchone():
        # If it exists, update it
        cursor.execute('''
        UPDATE audit_sessions SET
            session_name = ?,
            framework_filter = ?,
            framework_pattern = ?,
            category_filter = ?,
            risk_level_filter = ?,
            sector_filter = ?,
            region_filter = ?
        WHERE session_id = ?
        ''', (
            test_name,
            "EU AI Act (2023)",
            "%EU AI Law:%",
            "Defensive Model Strengthening",
            "High Risk",
            "Financial Services",
            "EU",
            session_id
        ))
    else:
        # If it doesn't exist, create it
        cursor.execute('''
        INSERT INTO audit_sessions (
            session_id, session_name, framework_filter, framework_pattern,
            category_filter, risk_level_filter, sector_filter, region_filter
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            test_name,
            "EU AI Act (2023)",
            "%EU AI Law:%",
            "Defensive Model Strengthening",
            "High Risk",
            "Financial Services",
            "EU"
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Created test session: {test_name}")
    print(f"✓ Direct access URL: http://172.31.128.97:5000/audit/{session_id}/question/0")

if __name__ == "__main__":
    create_test_session()