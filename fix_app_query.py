import re

def modify_app_py():
    """
    Modify app.py to use the improved framework filtering
    """
    with open('app.py', 'r') as file:
        content = file.read()
    
    # Find the question route and modify the SQL query
    question_route_pattern = r'@app\.route\(\'/audit/<session_id>/question/<int:question_index>\'\)(.*?)def question\(session_id, question_index\):(.*?)# Build query for controls based on filters(.*?)query = "SELECT \* FROM controls WHERE 1=1"(.*?)if audit_session\[\'framework_filter\'\]:(.*?)query \+= " AND framework LIKE \?"(.*?)params\.append\(f"%{audit_session\[\'framework_filter\'\]}%"\)'
    
    replacement = """@app.route('/audit/<session_id>/question/<int:question_index>')
def question(session_id, question_index):
    \"\"\"Display a specific audit question\"\"\"
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the audit session
    cursor.execute('SELECT * FROM audit_sessions WHERE session_id = ?', (session_id,))
    audit_session = cursor.fetchone()
    
    if not audit_session:
        conn.close()
        flash('Audit session not found')
        return redirect(url_for('index'))
    
    # Check if our improved view exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='framework_filtered_controls'")
    has_view = cursor.fetchone() is not None
    
    # Build query for controls based on filters
    # Use our improved view if available
    if has_view:
        query = "SELECT * FROM framework_filtered_controls WHERE 1=1"
    else:
        query = "SELECT * FROM controls WHERE 1=1"
    params = []
    
    if audit_session['framework_filter']:
        # For the Unified Framework, include all controls
        if audit_session['framework_filter'] == "Unified Framework (ASIMOV-AI)":
            # No additional filter needed for unified framework
            pass
        else:
            # Try to use the framework_filtered_controls view
            if has_view:
                # Extract framework name for matching
                if "EU AI" in audit_session['framework_filter']:
                    framework_name = "EU AI Act"
                else:
                    parts = audit_session['framework_filter'].split()
                    framework_name = parts[0] if parts else ""
                
                query += " AND simple_framework = ?"
                params.append(framework_name)
            else:
                # Fall back to the original method
                query += " AND framework LIKE ?"
                params.append(f"%{audit_session['framework_filter']}%")"""
    
    try:
        new_content = re.sub(question_route_pattern, replacement, content, flags=re.DOTALL)
        
        # Write the updated content back
        with open('app.py', 'w') as file:
            file.write(new_content)
        
        print("Successfully updated app.py with improved framework filtering")
        return True
    except Exception as e:
        print(f"Error updating app.py: {e}")
        return False

if __name__ == "__main__":
    modify_app_py()