import sqlite3

def update_framework_matching():
    """
    Update the controls table to improve framework matching
    """
    # Connect to database
    conn = sqlite3.connect('audit_controls.db')
    cursor = conn.cursor()

    # Create a simple view for framework filtering
    try:
        cursor.execute("""
        CREATE VIEW IF NOT EXISTS framework_filtered_controls AS
        SELECT c.*,
               CASE
                   WHEN framework LIKE '%EU AI%' THEN 'EU AI Act'
                   WHEN framework LIKE '%GDPR%' THEN 'GDPR'
                   WHEN framework LIKE '%NIST%' THEN 'NIST'
                   WHEN framework LIKE '%ISO%' THEN 'ISO'
                   WHEN framework LIKE '%SCF%' THEN 'SCF'
                   WHEN framework LIKE '%COBIT%' THEN 'COBIT'
                   WHEN framework LIKE '%FAIR%' THEN 'FAIR'
                   WHEN framework LIKE '%SOC%' THEN 'SOC'
                   WHEN framework LIKE '%HIPAA%' THEN 'HIPAA'
                   WHEN framework LIKE '%HITRUST%' THEN 'HITRUST'
                   ELSE 'Other'
               END as simple_framework
        FROM controls c
        """)
        print("Created framework_filtered_controls view")
    except sqlite3.OperationalError as e:
        print(f"Error creating view: {e}")
        # Try to drop and recreate
        try:
            cursor.execute("DROP VIEW IF EXISTS framework_filtered_controls")
            cursor.execute("""
            CREATE VIEW framework_filtered_controls AS
            SELECT c.*,
                   CASE
                       WHEN framework LIKE '%EU AI%' THEN 'EU AI Act'
                       WHEN framework LIKE '%GDPR%' THEN 'GDPR'
                       WHEN framework LIKE '%NIST%' THEN 'NIST'
                       WHEN framework LIKE '%ISO%' THEN 'ISO'
                       WHEN framework LIKE '%SCF%' THEN 'SCF'
                       WHEN framework LIKE '%COBIT%' THEN 'COBIT'
                       WHEN framework LIKE '%FAIR%' THEN 'FAIR'
                       WHEN framework LIKE '%SOC%' THEN 'SOC'
                       WHEN framework LIKE '%HIPAA%' THEN 'HIPAA'
                       WHEN framework LIKE '%HITRUST%' THEN 'HITRUST'
                       ELSE 'Other'
                   END as simple_framework
            FROM controls c
            """)
            print("Successfully recreated framework_filtered_controls view")
        except sqlite3.OperationalError as e2:
            print(f"Error recreating view: {e2}")

    conn.commit()
    conn.close()
    print("Done updating framework matching")

if __name__ == "__main__":
    update_framework_matching()