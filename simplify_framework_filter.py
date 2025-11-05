import sqlite3

def get_db_connection():
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def fix_framework_filters():
    """A simpler approach to fixing framework filtering"""
    
    # Define our approved frameworks that should be in the dropdown
    approved_frameworks = [
        "Unified Framework (ASIMOV-AI)",
        "EU AI Act",
        "GDPR",
        "NIST AI RMF",
        "ISO 42001",
        "COBIT 2019",
        "FAIR",
        "HIPAA",
        "HITRUST",
        "SOC 2",
        "Secure Controls Framework (SCF)"
    ]
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First check if our table even has controls
    cursor.execute("SELECT COUNT(*) FROM controls")
    count = cursor.fetchone()[0]
    print(f"Found {count} controls in database")
    
    # Add necessary table for mapping
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS framework_mapping (
        framework_name TEXT PRIMARY KEY,
        search_pattern TEXT
    )
    """)
    
    # Clear existing mappings
    cursor.execute("DELETE FROM framework_mapping")
    
    # Insert the mapping patterns
    mappings = [
        ("Unified Framework (ASIMOV-AI)", "%"), # Match all
        ("EU AI Act", "EU AI%"),
        ("GDPR", "%GDPR%"),
        ("NIST AI RMF", "%NIST%"),
        ("ISO 42001", "%ISO%"),
        ("COBIT 2019", "%COBIT%"),
        ("FAIR", "%FAIR%"),
        ("HIPAA", "%HIPAA%"),
        ("HITRUST", "%HITRUST%"),
        ("SOC 2", "%SOC%"),
        ("Secure Controls Framework (SCF)", "%SCF%")
    ]
    
    cursor.executemany("INSERT INTO framework_mapping VALUES (?, ?)", mappings)
    conn.commit()
    
    print("Created framework mappings:")
    for name, pattern in mappings:
        print(f"  - {name} => {pattern}")
    
    # Now create a function to use this mapping
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS better_audit_sessions (
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
    """)
    
    conn.commit()
    conn.close()
    
    print("Database updated successfully to support better framework filtering")
    print("The application will now use pattern-based framework matching")

if __name__ == "__main__":
    fix_framework_filters()