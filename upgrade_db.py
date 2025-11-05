import sqlite3

def upgrade_database():
    """
    Upgrade the database schema to match the expected structure in the code.
    """
    conn = sqlite3.connect('audit_controls.db')
    cursor = conn.cursor()
    
    # Check if audit_sessions table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_sessions'")
    if cursor.fetchone():
        print("Found audit_sessions table, preparing for upgrade...")
        
        # Create a new table with the proper schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_sessions_new (
                session_id TEXT PRIMARY KEY,
                session_name TEXT,
                framework_filter TEXT,
                category_filter TEXT,
                risk_level_filter TEXT,
                sector_filter TEXT,
                region_filter TEXT,
                session_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Copy data from old table to new table (if any)
        try:
            cursor.execute('''
                INSERT INTO audit_sessions_new (
                    session_id, 
                    session_name, 
                    framework_filter, 
                    category_filter, 
                    risk_level_filter, 
                    sector_filter, 
                    region_filter
                )
                SELECT 
                    id, 
                    session_name, 
                    framework_filter, 
                    category_filter, 
                    risk_level_filter, 
                    sector_filter, 
                    region_filter
                FROM audit_sessions
            ''')
            print(f"Migrated {cursor.rowcount} audit sessions to new schema")
        except sqlite3.Error as e:
            print(f"Error migrating data: {e}")
        
        # Drop old table and rename new table
        cursor.execute("DROP TABLE audit_sessions")
        cursor.execute("ALTER TABLE audit_sessions_new RENAME TO audit_sessions")
        print("Renamed new table to audit_sessions")
    else:
        # Create the table with the proper schema if it doesn't exist
        print("Creating audit_sessions table with proper schema...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_sessions (
                session_id TEXT PRIMARY KEY,
                session_name TEXT,
                framework_filter TEXT,
                category_filter TEXT,
                risk_level_filter TEXT,
                sector_filter TEXT,
                region_filter TEXT,
                session_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Check audit_responses table and ensure it's using session_id correctly
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            control_id INTEGER,
            response TEXT,
            evidence TEXT,
            confidence INTEGER,
            created_at TEXT,
            FOREIGN KEY (session_id) REFERENCES audit_sessions(session_id),
            FOREIGN KEY (control_id) REFERENCES controls(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database schema upgrade completed successfully!")

if __name__ == "__main__":
    upgrade_database()