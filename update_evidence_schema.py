"""
Update Evidence Schema Migration

This script updates the database schema to support enhanced evidence features:
1. Evidence date
2. Evidence notes
3. Evidence URLs
4. File evidence references
"""

import sqlite3

def update_evidence_schema():
    """Update database schema for enhanced evidence features"""
    
    print("Starting database schema update for enhanced evidence features...")
    
    # Connect to the database
    conn = sqlite3.connect('audit_controls.db')
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(audit_responses)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Add evidence_date column if it doesn't exist
        if 'evidence_date' not in columns:
            cursor.execute('ALTER TABLE audit_responses ADD COLUMN evidence_date TEXT')
            print("✅ Added evidence_date column")
        
        # Add evidence_notes column if it doesn't exist
        if 'evidence_notes' not in columns:
            cursor.execute('ALTER TABLE audit_responses ADD COLUMN evidence_notes TEXT')
            print("✅ Added evidence_notes column")
        
        # Create evidence_urls table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS evidence_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id INTEGER,
            url TEXT NOT NULL,
            FOREIGN KEY (response_id) REFERENCES audit_responses(id)
        )
        ''')
        print("✅ Created evidence_urls table")
        
        # Create evidence_files table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS evidence_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id INTEGER,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            FOREIGN KEY (response_id) REFERENCES audit_responses(id)
        )
        ''')
        print("✅ Created evidence_files table")
        
        conn.commit()
        print("✅ Successfully updated database schema for enhanced evidence features")
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    update_evidence_schema()