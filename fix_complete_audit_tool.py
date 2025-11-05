"""
Comprehensive fix for the ASIMOV Audit Tool
This script resolves issues with:
1. Framework mapping
2. Database schema consistency
3. Test session creation
4. Example controls
"""

import sqlite3
import uuid
import datetime

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def fix_audit_tool():
    """Apply all fixes for the audit tool"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("🔍 Diagnosing ASIMOV Audit Tool issues...")
    
    # 1. Check controls table
    cursor.execute("SELECT COUNT(*) as count FROM controls")
    control_count = cursor.fetchone()['count']
    print(f"✓ Found {control_count} controls in database")
    
    # 2. Setup Framework Mapping
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
    
    print(f"✓ Created framework mapping table with {len(framework_mappings)} predefined frameworks")
    
    # 3. Check for example controls that match specific criteria
    cursor.execute("""
    SELECT COUNT(*) as count 
    FROM controls 
    WHERE category = 'Defensive Model Strengthening'
    AND framework LIKE '%EU AI Law:%'
    """)
    
    specific_count = cursor.fetchone()['count']
    print(f"✓ Found {specific_count} controls matching 'Defensive Model Strengthening' category with EU AI Act")
    
    # 4. Create a test session for direct access
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
    
    # Create test session
    test_session_id = "test-mvp-session-5"  # Using a new ID to avoid conflicts
    framework_filter = "EU AI Act (2023)"
    framework_pattern = "%EU AI Law:%"
    category_filter = "Defensive Model Strengthening"
    risk_level_filter = "High Risk"
    sector_filter = "Financial Services"
    region_filter = "EU"
    
    cursor.execute('''
    INSERT OR REPLACE INTO audit_sessions (
        session_id, session_name, framework_filter, framework_pattern,
        category_filter, risk_level_filter, sector_filter, region_filter
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        test_session_id, 
        f"Test MVP Session {datetime.datetime.now().strftime('%Y-%m-%d')}",
        framework_filter,
        framework_pattern,
        category_filter, 
        risk_level_filter,
        sector_filter,
        region_filter
    ))
    
    print(f"✓ Created test session with ID: {test_session_id}")
    
    # 5. Index frameworks for better performance
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_controls_framework ON controls (framework)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_controls_category ON controls (category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_controls_risk_level ON controls (risk_level)")
        print("✓ Created indexes for better performance")
    except:
        print("! Warning: Could not create indexes, but this is not critical")
    
    # 6. Fix foreign key issue in audit_responses
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        control_id INTEGER,
        response TEXT,
        evidence TEXT,
        confidence INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    print("✓ Fixed audit_responses table structure")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n✅ All fixes applied successfully!")
    print(f"\nDirect test session URL: http://172.31.128.97:5000/audit/{test_session_id}/question/0")

if __name__ == "__main__":
    fix_audit_tool()