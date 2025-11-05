import sqlite3

conn = sqlite3.connect('audit_controls.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    control_id INTEGER,
    framework TEXT,
    category TEXT,
    response_score INTEGER,
    reference_text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Create a table to store audit sessions
cursor.execute('''
CREATE TABLE IF NOT EXISTS audit_sessions (
    session_id TEXT PRIMARY KEY,
    session_name TEXT,
    framework_filter TEXT,
    category_filter TEXT,
    risk_level_filter TEXT,
    session_date DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("✅ Database tables created.")