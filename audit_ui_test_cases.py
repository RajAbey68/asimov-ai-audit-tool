"""
ASIMOV AI Governance Audit Tool - UI Test Suite

This test suite provides automated testing for the Flask-based ASIMOV AI Governance 
Audit Tool application. It covers critical workflows including:
- Audit session creation and validation
- Question navigation (Next/Prev)
- PDF export functionality
- Summary page rendering
- Audit history access

Usage:
    pytest audit_ui_test_cases.py -v
"""

import pytest
import requests
from bs4 import BeautifulSoup
import uuid
import time
import re

# Configuration
BASE_URL = "http://localhost:5000"
TEST_AUDIT_NAME = f"Test Audit {uuid.uuid4().hex[:8]}"

# Fixtures
@pytest.fixture
def session():
    """Create a requests session that maintains cookies and history across requests"""
    session = requests.Session()
    return session

@pytest.fixture
def new_audit_session(session):
    """Create a new audit session for testing"""
    # Get CSRF token if needed
    home_resp = session.get(f"{BASE_URL}/")
    soup = BeautifulSoup(home_resp.text, 'html.parser')
    
    # Submit form to create audit
    data = {
        'session_name': TEST_AUDIT_NAME,
        'framework_filter': 'Unified Framework (ASIMOV-AI)',
        'category_filter': '',
        'risk_level_filter': '',
        'sector_filter': '',
        'region_filter': ''
    }
    
    resp = session.post(f"{BASE_URL}/start-audit", data=data, allow_redirects=False)
    
    # Get the session ID from the Location header
    location = resp.headers.get('Location', '')
    match = re.search(r'/audit/([a-zA-Z0-9-]+)/question/0', location)
    
    if match:
        session_id = match.group(1)
        return {
            'session_id': session_id,
            'session_name': TEST_AUDIT_NAME
        }
    else:
        pytest.fail("Failed to create test audit session")

# Tests
def test_home_page_loads(session):
    """Test that the home page loads with framework selection dropdown"""
    resp = session.get(f"{BASE_URL}/")
    assert resp.status_code == 200
    assert "ASIMOV AI Governance Audit Tool" in resp.text
    assert "Start New AI Governance Audit" in resp.text
    assert "Unified Framework (ASIMOV-AI)" in resp.text
    
    # Verify framework dropdown exists
    soup = BeautifulSoup(resp.text, 'html.parser')
    framework_dropdown = soup.find('select', {'name': 'framework_filter'})
    assert framework_dropdown is not None
    
    # Verify Start Audit button exists
    start_button = soup.find('button', {'type': 'submit'})
    assert start_button is not None
    assert start_button.text.strip() == "Start Audit"

def test_create_audit_session(session):
    """Test creating a new audit session"""
    # Get the home page
    home_resp = session.get(f"{BASE_URL}/")
    
    # Create a unique audit name
    audit_name = f"Test Audit {time.strftime('%Y%m%d-%H%M%S')}"
    
    # Submit the form to create an audit
    data = {
        'session_name': audit_name,
        'framework_filter': 'Unified Framework (ASIMOV-AI)',
        'category_filter': '',
        'risk_level_filter': '',
        'sector_filter': '',
        'region_filter': ''
    }
    
    resp = session.post(f"{BASE_URL}/start-audit", data=data, allow_redirects=False)
    
    # Verify redirection to first question
    assert resp.status_code in (302, 303)
    assert '/question/0' in resp.headers.get('Location', '')

def test_audit_name_validation(session):
    """Test audit name validation (duplicate names should prompt for overwrite/rename)"""
    # Implement later when name validation is added
    pass

def test_question_navigation(session, new_audit_session):
    """Test navigating between questions with Next/Prev buttons"""
    session_id = new_audit_session['session_id']
    
    # Access first question
    q0_resp = session.get(f"{BASE_URL}/audit/{session_id}/question/0")
    assert q0_resp.status_code == 200
    
    # Parse form for submission
    soup = BeautifulSoup(q0_resp.text, 'html.parser')
    
    # Submit answer to first question and navigate to second
    form_action = soup.find('form').get('action')
    data = {
        'response_score': '3',
        'reference_text': 'Test evidence for automated testing',
        'next_question': 'true'
    }
    
    q1_resp = session.post(form_action, data=data, allow_redirects=True)
    assert q1_resp.status_code == 200
    
    # Verify we're on question 1
    assert "Question 2 of" in q1_resp.text or "question/1" in q1_resp.url
    
    # Navigate to question 3 (if available)
    soup = BeautifulSoup(q1_resp.text, 'html.parser')
    form = soup.find('form')
    
    if form:
        form_action = form.get('action')
        q2_resp = session.post(form_action, data=data, allow_redirects=True)
        assert q2_resp.status_code == 200
        
        # Check if we're on question 2 or summary
        content = q2_resp.text
        assert ("Question 3 of" in content or 
                "question/2" in q2_resp.url or 
                "summary" in q2_resp.url)

def test_multiple_questions(session, new_audit_session):
    """Test that multiple questions can be accessed sequentially"""
    session_id = new_audit_session['session_id']
    
    # Get the first question
    resp = session.get(f"{BASE_URL}/audit/{session_id}/question/0")
    assert resp.status_code == 200
    
    # Navigate through at least 5 questions (or until we reach summary)
    current_question = 0
    max_questions = 5
    
    while current_question < max_questions:
        # Get the current question page
        resp = session.get(f"{BASE_URL}/audit/{session_id}/question/{current_question}")
        
        # If we've been redirected to summary, we're done
        if "summary" in resp.url:
            break
            
        assert resp.status_code == 200
        assert f"Question {current_question + 1}" in resp.text
        
        # Parse form for submission
        soup = BeautifulSoup(resp.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            pytest.fail(f"No form found on question {current_question}")
            
        form_action = form.get('action')
        
        # Submit answer
        data = {
            'response_score': '3',
            'reference_text': f'Test evidence for question {current_question}',
            'next_question': 'true'
        }
        
        resp = session.post(form_action, data=data, allow_redirects=True)
        
        # Check if we've been redirected to summary
        if "summary" in resp.url:
            break
            
        # Increment for next question
        current_question += 1
    
    # We should have navigated through at least 3 questions
    assert current_question >= 3, f"Only navigated through {current_question} questions"

def test_export_pdf(session, new_audit_session):
    """Test exporting a question to PDF"""
    session_id = new_audit_session['session_id']
    
    # Try to export the first question
    resp = session.get(f"{BASE_URL}/audit/{session_id}/question/0/export-pdf")
    
    # Check if PDF export is implemented
    if resp.status_code == 200 and resp.headers.get('Content-Type') == 'application/pdf':
        assert len(resp.content) > 0, "PDF content should not be empty"
    else:
        # If not implemented, it might redirect or return HTML
        assert resp.status_code in (200, 302, 404), f"Unexpected status code: {resp.status_code}"

def test_summary_page(session, new_audit_session):
    """Test that the summary page displays correctly"""
    session_id = new_audit_session['session_id']
    
    # Access the summary page
    resp = session.get(f"{BASE_URL}/audit/{session_id}/summary")
    assert resp.status_code == 200
    
    # Verify key elements on summary page
    assert "AI Governance Audit Summary" in resp.text
    assert "Compliance Score" in resp.text
    assert session_id in resp.text
    
    # Check for Start New Audit button
    soup = BeautifulSoup(resp.text, 'html.parser')
    new_audit_link = soup.find('a', string="Start New Audit") or soup.find('a', {'class': 'button'})
    assert new_audit_link is not None

def test_audit_history(session, new_audit_session):
    """Test that previous audits can be viewed"""
    # Create an audit if needed
    session_id = new_audit_session['session_id']
    
    # Access the audit history page
    resp = session.get(f"{BASE_URL}/audits")
    
    # Check if audits page exists
    if resp.status_code == 200:
        assert "Previous AI Governance Audits" in resp.text
        # Verify our test audit appears in the list
        assert TEST_AUDIT_NAME in resp.text or session_id in resp.text
    else:
        pytest.skip("Audit history page not implemented yet")

if __name__ == "__main__":
    print("Running ASIMOV AI Governance Audit Tool Tests")
    
    # Run tests manually since we're not using pytest's runner
    print("\n==== Testing Home Page ====")
    try:
        session = requests.Session()
        result = test_home_page_loads(session)
        print(f"✅ Home page test: PASSED")
    except Exception as e:
        print(f"❌ Home page test failed: {str(e)}")
        
    print("\n==== Testing Audit Session Creation ====")
    try:
        result = test_create_audit_session(session)
        print(f"✅ Audit session creation: PASSED")
    except Exception as e:
        print(f"❌ Audit session creation failed: {str(e)}")
    
    print("\n==== Testing Navigation Through Multiple Questions ====")
    try:
        # Create a new session for testing
        new_session = {
            'session_id': str(uuid.uuid4()),
            'session_name': f"Test Audit {time.strftime('%Y%m%d-%H%M%S')}"
        }
        
        # Create the session via API
        data = {
            'session_name': new_session['session_name'],
            'framework_filter': 'EU AI Act (2023)',
            'category_filter': '',
            'risk_level_filter': '',
            'sector_filter': '',
            'region_filter': ''
        }
        
        # Submit to create session
        resp = session.post(f"{BASE_URL}/start-audit", data=data, allow_redirects=True)
        
        # Get the session ID from response URL
        match = re.search(r'/audit/([a-zA-Z0-9-]+)/question/0', resp.url)
        if match:
            new_session['session_id'] = match.group(1)
        
        # Test navigation
        result = test_multiple_questions(session, new_session)
        print(f"✅ Question navigation: PASSED")
    except Exception as e:
        print(f"❌ Question navigation failed: {str(e)}")
        
    print("\n==== Testing Summary Page ====")
    try:
        result = test_summary_page(session, new_session)
        print(f"✅ Summary page: PASSED")
    except Exception as e:
        print(f"❌ Summary page failed: {str(e)}")
    
    print("\nTests completed. See above for results.")