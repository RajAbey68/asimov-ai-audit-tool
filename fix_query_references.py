import re

def fix_field_names_in_app_py():
    """
    This script updates all references to database field names in app.py
    to match the actual database structure.
    """
    # Read the current app.py content
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Replace all instances of 'WHERE id = ?' with 'WHERE session_id = ?'
    content = re.sub(r"WHERE\s+id\s+=\s+\?", "WHERE session_id = ?", content)
    
    # Replace all instances of 'ON as1.id = ar.session_id' with 'ON as1.session_id = ar.session_id'
    content = re.sub(r"ON\s+as1\.id\s+=\s+ar\.session_id", "ON as1.session_id = ar.session_id", content)
    
    # Replace all instances of 'GROUP BY as1.id' with 'GROUP BY as1.session_id'
    content = re.sub(r"GROUP\s+BY\s+as1\.id", "GROUP BY as1.session_id", content)
    
    # Replace all instances of 'WHERE id IN' with 'WHERE session_id IN'
    content = re.sub(r"WHERE\s+id\s+IN", "WHERE session_id IN", content)
    
    # Write the updated content back to app.py
    with open('app.py', 'w') as f:
        f.write(content)
    
    print("Updated all database field references in app.py")

if __name__ == "__main__":
    fix_field_names_in_app_py()