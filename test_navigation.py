"""
Simple navigation test script for ASIMOV AI Governance Audit Tool
Tests if users can move through multiple questions using the Next button
"""

import requests
from bs4 import BeautifulSoup
import time
import uuid

# Configuration
BASE_URL = "http://localhost:5000"

def test_navigation():
    """Test that users can navigate through multiple questions"""
    session = requests.Session()
    
    # Step 1: Get the home page
    print("1. Getting the home page...")
    home_resp = session.get(f"{BASE_URL}/")
    assert home_resp.status_code == 200
    
    # Step 2: Create a new audit session
    print("2. Creating a new audit session...")
    audit_name = f"Test Audit {time.strftime('%Y%m%d-%H%M%S')}"
    data = {
        'session_name': audit_name,
        'framework_filter': 'EU AI Act (2023)',
        'category_filter': '',
        'risk_level_filter': '',
        'sector_filter': '',
        'region_filter': ''
    }
    
    audit_resp = session.post(f"{BASE_URL}/start-audit", data=data, allow_redirects=True)
    assert audit_resp.status_code == 200
    
    # Extract session ID from URL
    session_id = audit_resp.url.split('/audit/')[1].split('/question/')[0]
    print(f"   Created session with ID: {session_id}")
    
    # Step 3: Navigate through questions
    current_question = 0
    max_questions = 5  # Try to navigate through 5 questions
    
    while current_question < max_questions:
        print(f"3. On question {current_question}...")
        
        # Get the current question page
        q_url = f"{BASE_URL}/audit/{session_id}/question/{current_question}"
        q_resp = session.get(q_url)
        
        # Check if we're still on a question page or redirected to summary
        if '/summary' in q_resp.url:
            print("   Redirected to summary page - no more questions.")
            break
            
        # Ensure we're on the question page
        assert q_resp.status_code == 200
        assert f"Question {current_question + 1}" in q_resp.text
        
        # Get the form action
        soup = BeautifulSoup(q_resp.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            print(f"   ERROR: No form found on question {current_question}")
            break
            
        form_action = form.get('action')
        print(f"   Form action: {form_action}")
        
        # Prepare data for submission
        submit_data = {
            'response_score': '3',
            'reference_text': f'Test evidence for question {current_question}',
            'next_question': 'true'
        }
        
        # Submit the form
        print(f"   Submitting answer for question {current_question}...")
        submit_resp = session.post(f"{BASE_URL}{form_action}", data=submit_data, allow_redirects=True)
        
        # Check if we're redirected to summary
        if '/summary' in submit_resp.url:
            print("   Redirected to summary page after submission.")
            break
        
        # Should be redirected to next question
        next_question = current_question + 1
        expected_path = f"/audit/{session_id}/question/{next_question}"
        
        if expected_path in submit_resp.url:
            print(f"   Successfully navigated to question {next_question}")
            current_question = next_question
        else:
            print(f"   ERROR: Unexpected redirect to {submit_resp.url}")
            break
    
    print(f"Navigation test completed. Navigated through {current_question} questions.")
    
    if current_question >= 2:
        print("✅ TEST PASSED: Successfully navigated through multiple questions!")
        return True
    else:
        print("❌ TEST FAILED: Could not navigate through multiple questions.")
        return False

if __name__ == "__main__":
    print("Running ASIMOV AI Governance Audit Tool Navigation Test")
    test_navigation()