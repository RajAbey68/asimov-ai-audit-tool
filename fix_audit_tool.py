"""
This script fixes database issues and ensures the ASIMOV Audit Tool can function properly.
"""

import sqlite3
import datetime

# Connect to the database
conn = sqlite3.connect('audit_controls.db')
cursor = conn.cursor()

# 1. Make sure audit_sessions table has the correct structure
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

# 2. Create a test audit session for MVP testing
test_session_id = "test-mvp-session-1"
test_session_name = "MVP Test Audit"
framework = "EU AI Act (2023)"
framework_pattern = "%EU AI Act%"
category = "Defensive Model Strengthening"
risk_level = "High Risk"
sector = "Financial Services"
region = "EU"

try:
    # First try to delete any existing session with this ID
    cursor.execute("DELETE FROM audit_sessions WHERE session_id = ?", (test_session_id,))
    
    # Then insert the test session
    cursor.execute('''
    INSERT INTO audit_sessions (
        session_id, session_name, framework_filter, framework_pattern, 
        category_filter, risk_level_filter, sector_filter, region_filter
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        test_session_id,
        test_session_name,
        framework,
        framework_pattern,
        category,
        risk_level,
        sector,
        region
    ))
    print(f"Created test audit session with ID: {test_session_id}")
except Exception as e:
    print(f"Error creating test session: {e}")

# 3. Create framework_mapping table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS framework_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_name TEXT UNIQUE,
    search_pattern TEXT
)
''')

# 4. Insert standardized frameworks
frameworks = [
    ("EU AI Act (2023)", "%EU AI%"),
    ("GDPR", "%GDPR%"),
    ("NIST AI RMF", "%NIST%"),
    ("ISO/IEC 42001", "%ISO%"),
    ("ISACA AI Audit Toolkit", "%ISACA%"),
    ("MITRE ATLAS", "%MITRE%"),
    ("OWASP Top 10 for LLMs", "%OWASP%"),
    ("Microsoft Responsible AI", "%Microsoft%"),
    ("Ada Lovelace Institute", "%Ada%"),
    ("Unified Framework (ASIMOV-AI)", "%ASIMOV%")
]

for name, pattern in frameworks:
    try:
        cursor.execute("INSERT OR REPLACE INTO framework_mapping (framework_name, search_pattern) VALUES (?, ?)", 
                      (name, pattern))
    except:
        print(f"Error inserting framework mapping for {name}")

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database setup complete for ASIMOV Audit Tool MVP testing!")