"""
Add Evidence Date Column Migration

This script adds an evidence_date column to the audit_responses table
to track when a control was last verified or tested.
"""

import sqlite3

def add_evidence_date_column():
    """Add evidence_date column to audit_responses table"""
    
    print("Starting database migration: Adding evidence_date column to audit_responses table...")
    
    # Connect to the database
    conn = sqlite3.connect('audit_controls.db')
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(audit_responses)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'evidence_date' not in columns:
            # Add the new column
            cursor.execute('''
            ALTER TABLE audit_responses 
            ADD COLUMN evidence_date TEXT
            ''')
            
            conn.commit()
            print("✅ Successfully added evidence_date column to audit_responses table")
        else:
            print("Column 'evidence_date' already exists in audit_responses table")
            
    except Exception as e:
        print(f"❌ Error adding evidence_date column: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    add_evidence_date_column()