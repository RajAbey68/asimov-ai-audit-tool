"""
Comprehensive Test Suite for ASIMOV AI Governance Audit Tool

This script runs automated tests for all major functionality:
1. Home page and framework selection
2. Start Audit button
3. Question navigation (Next/Previous)
4. Question submission
5. PDF export
6. Summary page generation
7. View All Audits functionality

Results are displayed in a clear, structured format.
"""

import sqlite3
import requests
import json
import uuid
import time
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "http://localhost:5000"
TEST_SESSION_ID = f"test-{uuid.uuid4()}"
TEST_AUDIT_NAME = f"Test Audit {time.strftime('%Y-%m-%d %H:%M:%S')}"

# Test results storage
test_results = []

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def extract_csrf_token(html_content):
    """Extract CSRF token from HTML content if present"""
    soup = BeautifulSoup(html_content, 'html.parser')
    csrf_token = None
    try:
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
    except Exception as e:
        print(f"Error extracting CSRF token: {e}")
    return csrf_token

def log_test_result(component, test_name, test_steps, expected_result, actual_result, status):
    """Log a test result"""
    result = {
        "component": component,
        "test_name": test_name,
        "test_steps": test_steps,
        "expected_result": expected_result,
        "actual_result": actual_result,
        "status": status
    }
    test_results.append(result)
    return result

def test_home_page_load():
    """Test 1: Verify the home page loads correctly"""
    try:
        response = requests.get(f"{BASE_URL}/")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for framework dropdown and start button
        framework_dropdown = soup.find('select', {'name': 'framework_filter'})
        start_button = soup.find('button', {'type': 'submit'})
        
        if response.status_code == 200 and framework_dropdown and start_button:
            status = "PASS"
            actual_result = "Page loaded with status 200, framework dropdown and start button found"
        else:
            status = "FAIL"
            actual_result = f"Page loaded with status {response.status_code}, framework dropdown: {bool(framework_dropdown)}, start button: {bool(start_button)}"
    except Exception as e:
        status = "FAIL"
        actual_result = f"Exception: {str(e)}"
    
    return log_test_result(
        "Home Page", 
        "Home Page Load", 
        "GET request to '/'",
        "Page loads with framework dropdown and Start Audit button",
        actual_result,
        status
    )

def test_framework_dropdown():
    """Test 2: Verify the framework dropdown has all expected frameworks"""
    try:
        response = requests.get(f"{BASE_URL}/")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get all option values from framework dropdown
        framework_dropdown = soup.find('select', {'name': 'framework_filter'})
        options = framework_dropdown.find_all('option')
        frameworks = [option.text for option in options if option.get('value')]
        
        # Expected frameworks
        expected_frameworks = [
            "NIST AI RMF", 
            "EU AI Act", 
            "ISO 42001",
            "UK AI Regulation",
            "OECD AI Principles",
            "Singapore AI Governance"
        ]
        
        # Check if at least some expected frameworks are present
        found_frameworks = [f for f in expected_frameworks if any(f in framework for framework in frameworks)]
        
        if len(found_frameworks) >= 3:  # At least 3 expected frameworks should be present
            status = "PASS"
            actual_result = f"Found frameworks: {', '.join(frameworks)}"
        else:
            status = "FAIL"
            actual_result = f"Found only {len(found_frameworks)} of expected frameworks: {', '.join(frameworks)}"
    except Exception as e:
        status = "FAIL"
        actual_result = f"Exception: {str(e)}"
    
    return log_test_result(
        "Home Page", 
        "Framework Dropdown Content", 
        "Check options in framework_filter dropdown",
        "Dropdown contains expected AI governance frameworks",
        actual_result,
        status
    )

def test_start_audit_button():
    """Test 3: Verify the Start Audit button works"""
    try:
        # Step 1: Get the home page
        response = requests.get(f"{BASE_URL}/")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract CSRF token if present
        csrf_token = extract_csrf_token(response.text)
        
        # Step 2: Submit the form to start an audit
        form_data = {
            'session_name': TEST_AUDIT_NAME,
            'framework_filter': 'Any',
            'category_filter': 'Any',
            'risk_level_filter': 'Any',
            'sector_filter': 'Any',
            'region_filter': 'Any'
        }
        
        if csrf_token:
            form_data['csrf_token'] = csrf_token
        
        start_response = requests.post(
            f"{BASE_URL}/start-audit", 
            data=form_data,
            allow_redirects=False
        )
        
        # Check if redirected to a question page
        if start_response.status_code in [302, 303]:
            redirect_url = start_response.headers.get('Location', '')
            if '/question/0' in redirect_url:
                status = "PASS"
                actual_result = f"Redirected to {redirect_url}"
            else:
                status = "FAIL"
                actual_result = f"Redirected to unexpected URL: {redirect_url}"
        else:
            status = "FAIL"
            actual_result = f"Response code {start_response.status_code}, not redirected"
    except Exception as e:
        status = "FAIL"
        actual_result = f"Exception: {str(e)}"
    
    return log_test_result(
        "Home Page", 
        "Start Audit Button", 
        "POST to '/start-audit' with form data",
        "Redirects to first question page",
        actual_result,
        status
    )

def create_test_session():
    """Create a test session for direct access"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if test session already exists
        cursor.execute('SELECT * FROM audit_sessions WHERE session_id = ?', (TEST_SESSION_ID,))
        existing_session = cursor.fetchone()
        
        if existing_session:
            # Delete existing session responses
            cursor.execute('DELETE FROM audit_responses WHERE session_id = ?', (TEST_SESSION_ID,))
            # Update existing session
            cursor.execute('''
                UPDATE audit_sessions 
                SET session_name = ?, framework_filter = ?, category_filter = ?, risk_level_filter = ?, session_date = CURRENT_TIMESTAMP
                WHERE session_id = ?
            ''', (TEST_AUDIT_NAME, 'Any', 'Any', 'Any', TEST_SESSION_ID))
        else:
            # Create new test session
            cursor.execute('''
                INSERT INTO audit_sessions 
                (session_id, session_name, framework_filter, category_filter, risk_level_filter, sector_filter, region_filter)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (TEST_SESSION_ID, TEST_AUDIT_NAME, 'Any', 'Any', 'Any', 'Any', 'Any'))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating test session: {e}")
        return False

def test_direct_session_access():
    """Test 4: Test direct access to a specific session"""
    try:
        # Create a test session first
        if create_test_session():
            # Try to access the session directly
            response = requests.get(f"{BASE_URL}/audit/{TEST_SESSION_ID}/question/0")
            
            if response.status_code == 200 and "AI Governance Control" in response.text:
                status = "PASS"
                actual_result = "Successfully accessed test session question page"
            else:
                status = "FAIL"
                actual_result = f"Failed to access test session, status: {response.status_code}"
        else:
            status = "FAIL"
            actual_result = "Failed to create test session"
    except Exception as e:
        status = "FAIL"
        actual_result = f"Exception: {str(e)}"
    
    return log_test_result(
        "Question Access", 
        "Direct Session Access", 
        f"GET request to '/audit/{TEST_SESSION_ID}/question/0'",
        "Question page loads successfully",
        actual_result,
        status
    )

def test_question_navigation(session_id):
    """Test 5: Verify Next and Previous buttons work"""
    try:
        # Step 1: Access first question
        response = requests.get(f"{BASE_URL}/audit/{session_id}/question/0")
        first_page_content = response.text
        
        # Step 2: Submit answer and move to next question
        csrf_token = extract_csrf_token(response.text)
        
        form_data = {
            'response': 'Yes',
            'evidence': 'Test evidence',
            'response_score': '3'
        }
        
        if csrf_token:
            form_data['csrf_token'] = csrf_token
        
        submit_response = requests.post(
            f"{BASE_URL}/audit/{session_id}/question/0/submit", 
            data=form_data,
            allow_redirects=True
        )
        
        # Step 3: Verify we're on question 1
        if "/question/1" in submit_response.url:
            # Step 4: Go back to question 0
            prev_response = requests.get(f"{BASE_URL}/audit/{session_id}/question/0")
            
            if prev_response.status_code == 200:
                status = "PASS"
                actual_result = "Successfully navigated to next question and back"
            else:
                status = "FAIL"
                actual_result = f"Failed to navigate back, status: {prev_response.status_code}"
        else:
            status = "FAIL"
            actual_result = f"Not redirected to question 1, URL: {submit_response.url}"
    except Exception as e:
        status = "FAIL"
        actual_result = f"Exception: {str(e)}"
    
    return log_test_result(
        "Question Navigation", 
        "Next/Previous Navigation", 
        "Submit question 0, then navigate back",
        "Navigate forward to question 1, then back to question 0",
        actual_result,
        status
    )

def test_export_pdf(session_id):
    """Test 6: Verify PDF export functionality"""
    try:
        # Access the export URL
        response = requests.get(f"{BASE_URL}/audit/{session_id}/question/0/export")
        
        # Check if response is a PDF
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' in content_type.lower():
            # Check if it's not empty
            if len(response.content) > 100:  # Arbitrary minimum size
                status = "PASS"
                actual_result = f"PDF exported, size: {len(response.content)} bytes"
            else:
                status = "PASS WITH CONCERN"
                actual_result = f"PDF exported but size is small: {len(response.content)} bytes"
        else:
            status = "FAIL"
            actual_result = f"Response is not a PDF, content type: {content_type}"
    except Exception as e:
        status = "FAIL"
        actual_result = f"Exception: {str(e)}"
    
    return log_test_result(
        "Question Page", 
        "Export to PDF", 
        f"GET request to '/audit/{session_id}/question/0/export'",
        "PDF file is generated and downloaded",
        actual_result,
        status
    )

def test_view_summary(session_id):
    """Test 7: Verify summary page displays correctly"""
    try:
        response = requests.get(f"{BASE_URL}/audit/{session_id}/summary")
        
        if response.status_code == 200 and "Compliance Score" in response.text:
            status = "PASS"
            actual_result = "Summary page loaded successfully"
        else:
            status = "FAIL"
            actual_result = f"Failed to load summary page, status: {response.status_code}"
    except Exception as e:
        status = "FAIL"
        actual_result = f"Exception: {str(e)}"
    
    return log_test_result(
        "Summary Page", 
        "Summary Display", 
        f"GET request to '/audit/{session_id}/summary'",
        "Summary page loads with compliance scores",
        actual_result,
        status
    )

def test_view_all_audits():
    """Test 8: Verify View All Audits functionality"""
    try:
        response = requests.get(f"{BASE_URL}/audits")
        
        if response.status_code == 200 and "Previous AI Governance Audits" in response.text:
            status = "PASS"
            actual_result = "Audits list page loaded successfully"
        else:
            status = "FAIL"
            actual_result = f"Failed to load audits list, status: {response.status_code}"
    except Exception as e:
        status = "FAIL"
        actual_result = f"Exception: {str(e)}"
    
    return log_test_result(
        "Audit History", 
        "View All Audits", 
        "GET request to '/audits'",
        "Displays list of past audit sessions",
        actual_result,
        status
    )

def format_test_results():
    """Format test results for display"""
    output = """
================================================
🧪 ASIMOV AI GOVERNANCE AUDIT TOOL - TEST REPORT
================================================

Summary:
"""
    
    pass_count = sum(1 for r in test_results if r['status'] == 'PASS')
    fail_count = sum(1 for r in test_results if r['status'] == 'FAIL')
    warn_count = sum(1 for r in test_results if 'CONCERN' in r['status'])
    
    output += f"✅ Passed: {pass_count}/{len(test_results)}\n"
    output += f"❌ Failed: {fail_count}/{len(test_results)}\n"
    output += f"⚠️ Warnings: {warn_count}/{len(test_results)}\n\n"
    
    output += "Detailed Results:\n"
    
    current_component = None
    for result in test_results:
        if current_component != result['component']:
            current_component = result['component']
            output += f"\n🔹 {current_component}\n"
            output += "-" * 50 + "\n"
        
        status_icon = "✅" if result['status'] == 'PASS' else "⚠️" if 'CONCERN' in result['status'] else "❌"
        output += f"{status_icon} {result['test_name']}\n"
        output += f"  Test Steps: {result['test_steps']}\n"
        output += f"  Expected Result: {result['expected_result']}\n"
        output += f"  Actual Result: {result['actual_result']}\n"
        output += f"  Status: {result['status']}\n\n"
    
    output += "================================================\n"
    return output

def run_all_tests():
    """Run all tests in sequence"""
    # Home page tests
    test_home_page_load()
    test_framework_dropdown()
    test_start_audit_button()
    
    # Create and test a fixed session
    create_test_session()
    test_direct_session_access()
    test_question_navigation(TEST_SESSION_ID)
    test_export_pdf(TEST_SESSION_ID)
    test_view_summary(TEST_SESSION_ID)
    test_view_all_audits()
    
    # Print formatted results
    print(format_test_results())
    return test_results

if __name__ == "__main__":
    print("🧪 Starting ASIMOV AI Governance Audit Tool Test Suite")
    run_all_tests()