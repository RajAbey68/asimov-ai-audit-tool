"""
Quick Fix for Reports & Analytics Database Schema Issues
This addresses the missing response_score column that's causing 500 errors
"""

import sqlite3
import os

def fix_reports_database_schema():
    """Fix the database schema issues preventing reports from working"""
    if not os.path.exists('audit_controls.db'):
        print("❌ Database file not found")
        return False
    
    try:
        conn = sqlite3.connect('audit_controls.db')
        cursor = conn.cursor()
        
        # Check if response_score column exists
        cursor.execute("PRAGMA table_info(audit_responses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'response_score' not in columns:
            print("🔧 Adding missing response_score column...")
            cursor.execute("""
                ALTER TABLE audit_responses 
                ADD COLUMN response_score INTEGER DEFAULT NULL
            """)
            
            # Update existing records with calculated scores
            cursor.execute("""
                UPDATE audit_responses 
                SET response_score = CASE 
                    WHEN response = 'Yes' THEN 5 
                    WHEN response = 'Partial' THEN 3 
                    WHEN response = 'No' THEN 1 
                    ELSE NULL 
                END
                WHERE response_score IS NULL
            """)
            
            conn.commit()
            print("✅ Added response_score column and populated existing data")
        else:
            print("✅ response_score column already exists")
        
        # Verify the fix
        cursor.execute("SELECT COUNT(*) FROM audit_responses WHERE response_score IS NOT NULL")
        scored_responses = cursor.fetchone()[0]
        print(f"✅ {scored_responses} responses now have scores")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Reports & Analytics Database Schema Issues...")
    success = fix_reports_database_schema()
    if success:
        print("🎉 Database schema fixed! Reports & Analytics should now work.")
    else:
        print("❌ Failed to fix database schema.")