import sqlite3

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def fix_framework_filtering():
    """
    Fixes framework filtering by updating the query approach in app.py
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check what frameworks are actually in the dropdown
    cursor.execute("SELECT DISTINCT framework FROM controls")
    all_frameworks = cursor.fetchall()
    
    print("Frameworks in database:")
    for i, fw in enumerate(all_frameworks[:10]):  # Show just the first 10
        print(f"{i+1}. {fw['framework'][:80]}...")
    
    # Now create a simpler framework tag for each control
    print("\nAdding framework_tag column for simpler filtering...")
    
    try:
        # Add a new column if it doesn't exist
        cursor.execute("ALTER TABLE controls ADD COLUMN framework_tag TEXT")
        print("Added framework_tag column")
    except sqlite3.OperationalError:
        print("framework_tag column already exists")
    
    # Update the framework_tag column with simplified tags
    cursor.execute("SELECT id, framework FROM controls")
    controls = cursor.fetchall()
    
    # Common framework prefixes to extract
    framework_prefixes = [
        "EU AI", "GDPR", "NIST", "ISO", "SCF", "COSO", "COBIT", 
        "FAIR", "HITRUST", "HIPAA", "SOC"
    ]
    
    updated = 0
    for control in controls:
        # Extract the main framework name for easier filtering
        framework_text = control['framework']
        tag = "Unified Framework"  # Default tag
        
        # Try to extract the framework from the text
        for prefix in framework_prefixes:
            if prefix in framework_text:
                tag = prefix
                break
                
        # Special case for EU AI Law/Act
        if "EU AI Law" in framework_text or "EU AI Act" in framework_text:
            tag = "EU AI Act"
            
        cursor.execute("UPDATE controls SET framework_tag = ? WHERE id = ?", 
                      (tag, control['id']))
        updated += 1
    
    conn.commit()
    print(f"Updated {updated} controls with framework tags")
    
    # Confirm the update worked
    cursor.execute("SELECT DISTINCT framework_tag FROM controls")
    tags = cursor.fetchall()
    
    print("\nAvailable framework tags for filtering:")
    for tag in tags:
        print(f"- {tag['framework_tag']}")
    
    conn.close()
    print("\nFramework filtering fix completed!")

if __name__ == "__main__":
    fix_framework_filtering()