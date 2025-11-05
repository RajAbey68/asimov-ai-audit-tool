"""
This script updates the question route to apply sector and region filters
"""

def apply_sector_filter(app_py_content):
    """Update the question route in app.py to apply sector and region filters"""
    
    # Find the location of the query building code
    start_idx = app_py_content.find("    # Build query for controls based on filters")
    if start_idx == -1:
        return app_py_content
        
    # Find the end of the query building block
    end_idx = app_py_content.find("query += \" ORDER BY id\"", start_idx)
    if end_idx == -1:
        return app_py_content
    
    # Extract the current filtering code
    end_of_block = app_py_content.find("\n", end_idx) + 1
    before_code = app_py_content[:start_idx]
    filtering_code = """    # Build query for controls based on filters
    query = "SELECT * FROM controls WHERE 1=1"
    params = []
    
    if audit_session['framework_filter']:
        query += " AND framework LIKE ?"
        params.append(f"%{audit_session['framework_filter']}%")
    
    if audit_session['category_filter']:
        query += " AND category = ?"
        params.append(audit_session['category_filter'])
    
    if audit_session['risk_level_filter']:
        query += " AND risk_level = ?"
        params.append(audit_session['risk_level_filter'])
    
    # Apply sector filter if it exists
    if 'sector_filter' in audit_session and audit_session['sector_filter']:
        query += " AND (sector = ? OR sector IS NULL)"
        params.append(audit_session['sector_filter'])
    
    query += " ORDER BY id"
"""
    after_code = app_py_content[end_of_block:]
    
    # Create updated content
    updated_content = before_code + filtering_code + after_code
    
    return updated_content

# Example of how to use this
if __name__ == "__main__":
    with open("app.py", "r") as file:
        content = file.read()
    
    updated_content = apply_sector_filter(content)
    
    with open("app.py", "w") as file:
        file.write(updated_content)