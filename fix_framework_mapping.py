"""
Create a proper framework mapping table to match dropdown selections with database entries
"""

import sqlite3

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def setup_framework_mapping():
    """Create and populate the framework mapping table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create framework mapping table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS framework_mapping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        framework_name TEXT UNIQUE,
        search_pattern TEXT
    )
    ''')
    
    # Define mappings between dropdown options and actual database patterns
    framework_mappings = [
        ("EU AI Act (2023)", "%EU AI Law:%"),
        ("NIST AI RMF", "%NIST 800-%"),
        ("ISO/IEC 42001", "%ISO/IEC%"),
        ("GDPR for AI", "%GDPR:%"),
        ("MITRE ATLAS", "%MITRE ATLAS%"),
        ("OWASP Top 10 for LLMs", "%OWASP%"),
        ("UK FCA AI/ML Guidance", "%UK FCA%"),
        ("US Blueprint for AI Bill of Rights", "%US Blueprint%"),
        ("ISACA Audit Toolkit", "%ISACA%"),
        ("Canada Artificial Intelligence Act", "%Canada AI%"),
        ("Unified Framework (ASIMOV-AI)", "%")  # Default wildcard for unified framework
    ]
    
    # Insert or update mappings
    for name, pattern in framework_mappings:
        cursor.execute('''
        INSERT OR REPLACE INTO framework_mapping (framework_name, search_pattern)
        VALUES (?, ?)
        ''', (name, pattern))
    
    conn.commit()
    conn.close()
    
    print("✓ Framework mapping table created with 11 predefined frameworks")

def test_framework_query():
    """Test a query with the framework mapping"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the search pattern for EU AI Act
    cursor.execute("SELECT search_pattern FROM framework_mapping WHERE framework_name = ?", ("EU AI Act (2023)",))
    result = cursor.fetchone()
    pattern = result['search_pattern'] if result else "%"
    
    # Test the query
    cursor.execute("SELECT COUNT(*) as count FROM controls WHERE framework LIKE ?", (pattern,))
    count = cursor.fetchone()['count']
    
    print(f"✓ Found {count} controls matching EU AI Act pattern: '{pattern}'")
    
    # Get sample controls
    cursor.execute("""
    SELECT id, control_name, category, risk_level, framework
    FROM controls 
    WHERE framework LIKE ? 
    LIMIT 3
    """, (pattern,))
    
    controls = cursor.fetchall()
    print("\nSample controls:")
    for control in controls:
        print(f"- {control['control_name']} ({control['category']}, {control['risk_level']})")
    
    conn.close()

if __name__ == "__main__":
    setup_framework_mapping()
    test_framework_query()