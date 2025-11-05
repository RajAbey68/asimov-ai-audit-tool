"""
Complete inventory of all buttons and their functions in the ASIMOV AI Governance Audit Tool
This script crawls all pages, identifies buttons, and tests their functionality
"""

import requests
import re
from bs4 import BeautifulSoup
import sqlite3

# Configuration
BASE_URL = "http://172.31.128.97:5000"
TEST_SESSION_ID = "button-test-session"

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_test_session():
    """Create a test session for button testing"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert or replace test session
    cursor.execute('''
    INSERT OR REPLACE INTO audit_sessions (
        session_id, session_name, framework_filter, framework_pattern,
        category_filter, risk_level_filter, sector_filter, region_filter
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        TEST_SESSION_ID,
        "Button Test Session",
        "Unified Framework (ASIMOV-AI)",
        "%",
        "",
        "",
        "",
        ""
    ))
    
    conn.commit()
    conn.close()
    
    return TEST_SESSION_ID

def extract_buttons(html_content, page_name):
    """Extract all buttons from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all buttons, inputs of type button/submit, and anchor tags with btn class
    buttons = []
    
    # Standard buttons
    for button in soup.find_all('button'):
        btn_text = button.text.strip()
        btn_type = button.get('type', 'button')
        btn_class = button.get('class', [])
        btn_id = button.get('id', '')
        btn_name = button.get('name', '')
        
        # Skip empty buttons
        if not btn_text and not btn_id and not btn_name:
            continue
            
        buttons.append({
            'type': 'button',
            'text': btn_text,
            'button_type': btn_type,
            'class': ' '.join(btn_class) if isinstance(btn_class, list) else btn_class,
            'id': btn_id,
            'name': btn_name,
            'page': page_name
        })
    
    # Input buttons
    for input_btn in soup.find_all('input', type=re.compile(r'button|submit')):
        btn_value = input_btn.get('value', '')
        btn_type = input_btn.get('type', '')
        btn_class = input_btn.get('class', [])
        btn_id = input_btn.get('id', '')
        btn_name = input_btn.get('name', '')
        
        buttons.append({
            'type': 'input',
            'text': btn_value,
            'button_type': btn_type,
            'class': ' '.join(btn_class) if isinstance(btn_class, list) else btn_class,
            'id': btn_id,
            'name': btn_name,
            'page': page_name
        })
    
    # Links with btn class
    for link in soup.find_all('a', class_=re.compile(r'btn|button')):
        link_text = link.text.strip()
        link_href = link.get('href', '')
        link_class = link.get('class', [])
        link_id = link.get('id', '')
        
        buttons.append({
            'type': 'link',
            'text': link_text,
            'href': link_href,
            'class': ' '.join(link_class) if isinstance(link_class, list) else link_class,
            'id': link_id,
            'page': page_name
        })
    
    # Additional: Find anything that looks like a button but might not be caught above
    for elem in soup.find_all(class_=re.compile(r'btn|button')):
        if elem.name not in ['button', 'input', 'a']:
            elem_text = elem.text.strip()
            elem_class = elem.get('class', [])
            elem_id = elem.get('id', '')
            
            buttons.append({
                'type': elem.name,
                'text': elem_text,
                'class': ' '.join(elem_class) if isinstance(elem_class, list) else elem_class,
                'id': elem_id,
                'page': page_name
            })
    
    return buttons

def analyze_button_function(button):
    """Analyze what a button does based on its attributes"""
    function = "Unknown"
    
    # Check button text for common actions
    text = button.get('text', '').lower()
    btn_type = button.get('button_type', '').lower()
    btn_class = button.get('class', '').lower()
    btn_id = button.get('id', '').lower()
    btn_name = button.get('name', '').lower()
    
    # Navigation buttons
    if 'next' in text or 'next' in btn_id or 'next' in btn_name:
        function = "Navigation: Next question"
    elif 'prev' in text or 'previous' in text or 'back' in text or 'prev' in btn_id:
        function = "Navigation: Previous question"
    elif 'home' in text or 'home' in btn_id:
        function = "Navigation: Return to home page"
    
    # Action buttons
    elif 'start' in text or 'begin' in text:
        function = "Action: Start new audit"
    elif 'submit' in text or 'save' in text or btn_type == 'submit':
        function = "Action: Submit/Save response"
    elif 'export' in text or 'pdf' in text or 'download' in text:
        function = "Action: Export to PDF"
    elif 'delete' in text or 'remove' in text:
        function = "Action: Delete item"
    elif 'add' in text or 'create' in text or 'new' in text:
        function = "Action: Add/Create new item"
    elif 'edit' in text or 'update' in text or 'modify' in text:
        function = "Action: Edit/Update item"
    elif 'view' in text or 'show' in text or 'display' in text:
        function = "Action: View details"
    elif 'filter' in text or 'search' in text:
        function = "Action: Filter/Search"
    elif 'reset' in text or 'clear' in text:
        function = "Action: Reset/Clear form"
    elif 'compare' in text:
        function = "Action: Compare audits"
    elif 'summary' in text or 'results' in text:
        function = "Navigation: View summary/results"
    elif 'audit' in text and ('list' in text or 'all' in text or 'view' in text):
        function = "Navigation: View all audits"
    
    # For links, use the href to determine function
    if button['type'] == 'link' and 'href' in button:
        href = button['href']
        if href == '/':
            function = "Navigation: Home page"
        elif '/question/' in href:
            function = "Navigation: Specific question"
        elif '/summary' in href:
            function = "Navigation: Summary page"
        elif '/export' in href or '/pdf' in href:
            function = "Action: Export/Download"
        elif '/audit/' in href and not ('/question/' in href or '/summary' in href):
            function = "Navigation: View audit"
    
    return function

def check_if_button_works(button, session_id=None):
    """Try to determine if a button actually works"""
    # This is a simplified check - a real implementation would need to actually
    # click the button and verify the response
    
    # For now, just check if the button has enough information to work
    if button['type'] == 'link':
        return 'href' in button and button['href']
    elif button['type'] == 'button' or button['type'] == 'input':
        # If it's a submit button inside a form, it probably works
        return button.get('button_type') == 'submit' or button.get('name')
    
    return False

def inventory_home_page():
    """Inventory buttons on the home page"""
    response = requests.get(BASE_URL)
    if response.status_code != 200:
        return []
    
    return extract_buttons(response.text, "Home Page")

def inventory_question_page(session_id):
    """Inventory buttons on a question page"""
    response = requests.get(f"{BASE_URL}/audit/{session_id}/question/0")
    if response.status_code != 200:
        return []
    
    return extract_buttons(response.text, "Question Page")

def inventory_summary_page(session_id):
    """Inventory buttons on the summary page"""
    # First submit a question to get to the summary
    submit_data = {
        "response": "Yes",
        "evidence": "Test evidence",
        "confidence": "3"
    }
    
    submit_response = requests.post(
        f"{BASE_URL}/audit/{session_id}/question/0/submit", 
        data=submit_data
    )
    
    if '/summary' not in submit_response.url:
        # Try direct access
        summary_response = requests.get(f"{BASE_URL}/audit/{session_id}/summary")
        if summary_response.status_code != 200:
            return []
        return extract_buttons(summary_response.text, "Summary Page")
    
    return extract_buttons(submit_response.text, "Summary Page")

def inventory_all_audits_page():
    """Inventory buttons on the all audits page"""
    response = requests.get(f"{BASE_URL}/audits")
    if response.status_code != 200:
        return []
    
    return extract_buttons(response.text, "All Audits Page")

def run_button_inventory():
    """Run a complete inventory of all buttons in the application"""
    print("\n🔎 ASIMOV AI Governance Audit Tool - Button Inventory")
    print("=" * 60)
    
    # Create test session if needed
    session_id = create_test_session()
    print(f"✅ Created test session with ID: {session_id}")
    
    # Inventory buttons on home page
    home_buttons = inventory_home_page()
    print(f"Found {len(home_buttons)} buttons on home page")
    
    # Inventory buttons on question page
    question_buttons = inventory_question_page(session_id)
    print(f"Found {len(question_buttons)} buttons on question page")
    
    # Inventory buttons on summary page
    summary_buttons = inventory_summary_page(session_id)
    print(f"Found {len(summary_buttons)} buttons on summary page")
    
    # Inventory buttons on all audits page
    audit_list_buttons = inventory_all_audits_page()
    print(f"Found {len(audit_list_buttons)} buttons on all audits page")
    
    # Combine all buttons
    all_buttons = home_buttons + question_buttons + summary_buttons + audit_list_buttons
    
    # Analyze button functions
    for button in all_buttons:
        button['function'] = analyze_button_function(button)
        button['works'] = check_if_button_works(button, session_id)
    
    # Print button inventory by page
    print("\n" + "=" * 60)
    print("📋 BUTTON INVENTORY BY PAGE")
    print("=" * 60)
    
    pages = set(button['page'] for button in all_buttons)
    
    for page in pages:
        print(f"\n🔹 {page}")
        print("-" * 40)
        
        page_buttons = [b for b in all_buttons if b['page'] == page]
        for i, button in enumerate(page_buttons):
            status = "✅" if button['works'] else "❌"
            function = button['function']
            text = button.get('text', '[No text]')
            btn_type = button['type']
            
            print(f"{i+1}. {status} {text} ({btn_type}) - {function}")
    
    # Print potentially broken buttons
    broken_buttons = [b for b in all_buttons if not b['works']]
    if broken_buttons:
        print("\n" + "=" * 60)
        print("⚠️ POTENTIALLY BROKEN BUTTONS")
        print("=" * 60)
        
        for button in broken_buttons:
            print(f"❌ '{button.get('text', '[No text]')}' on {button['page']} - {button['function']}")
    
    # Return all buttons for further analysis
    return all_buttons

if __name__ == "__main__":
    buttons = run_button_inventory()