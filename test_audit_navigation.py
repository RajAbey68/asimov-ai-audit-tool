"""
Automated Test Unit (ATU) for ASIMOV AI Governance Audit Tool
Tests the basic navigation and insight generation functionality
"""

import requests
import random
import time
import re
import sqlite3
from bs4 import BeautifulSoup

# Base URL for the application
BASE_URL = "http://localhost:5000"

def get_random_framework_category():
    """Get random framework and category from database for testing"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get available frameworks
    cursor.execute("SELECT DISTINCT framework FROM controls")
    frameworks = [row['framework'] for row in cursor.fetchall()]
    
    # Get available categories
    cursor.execute("SELECT DISTINCT category FROM controls")
    categories = [row['category'] for row in cursor.fetchall()]
    
    # Get available risk levels
    cursor.execute("SELECT DISTINCT risk_level FROM controls")
    risk_levels = [row['risk_level'] for row in cursor.fetchall()]
    
    conn.close()
    
    # Return random selections
    return {
        'framework': random.choice(frameworks) if frameworks else "",
        'category': random.choice(categories) if categories else "",
        'risk_level': random.choice(risk_levels) if risk_levels else ""
    }

def test_home_page():
    """Test that the home page loads correctly"""
    print("Testing home page...")
    response = requests.get(f"{BASE_URL}/")
    
    if response.status_code == 200:
        print("✓ Home page loaded successfully")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if the framework selection dropdown exists
        if soup.select('select[name="framework_filter"]'):
            print("✓ Framework filter dropdown found")
        else:
            print("✗ Framework filter dropdown not found")
            
        # Check that the Start Audit button exists
        if soup.select('button[type="submit"]'):
            print("✓ Start Audit button found")
        else:
            print("✗ Start Audit button not found")
            
        return True
    else:
        print(f"✗ Home page failed to load: {response.status_code}")
        return False

def start_audit_with_random_criteria():
    """Start an audit with random criteria and return the session ID"""
    print("Starting audit with random criteria...")
    
    # Get random selections
    selections = get_random_framework_category()
    print(f"Selected framework: {selections['framework']}")
    print(f"Selected category: {selections['category']}")
    print(f"Selected risk level: {selections['risk_level']}")
    
    # Send the POST request to start an audit
    data = {
        'framework_filter': selections['framework'],
        'category_filter': selections['category'],
        'risk_level_filter': selections['risk_level'],
        'sector_filter': 'Financial Services',  # Default sector for testing
        'region_filter': 'EU',  # Default region for testing
    }
    
    response = requests.post(f"{BASE_URL}/start_audit", data=data, allow_redirects=False)
    
    if response.status_code == 302:  # Redirect status
        # Get the redirect location
        redirect_url = response.headers.get('Location')
        
        # Extract session ID from URL if it exists
        match = re.search(r"/audit/([^/]+)/", redirect_url)
        if match:
            session_id = match.group(1)
            print(f"✓ Audit started successfully with session ID: {session_id}")
            return session_id
        else:
            print(f"✗ Failed to extract session ID from redirect URL: {redirect_url}")
            return None
    else:
        print(f"✗ Failed to start audit: {response.status_code}")
        return None

def test_question_page(session_id, question_index):
    """Test accessing a specific question page"""
    print(f"Testing question page {question_index}...")
    
    response = requests.get(f"{BASE_URL}/audit/{session_id}/question/{question_index}")
    
    if response.status_code == 200:
        print(f"✓ Question {question_index} loaded successfully")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if the Life-Wise Insight section exists
        insight_section = soup.select('.insight-box')
        if insight_section:
            insight_text = insight_section[0].get_text().strip()
            print(f"✓ Life-Wise Insight found: {insight_text[:80]}...")
        else:
            print("✗ Life-Wise Insight section not found")
        
        # Check for Next button
        next_button = soup.select('button[name="next_question"]')
        if next_button:
            print("✓ Next button found")
        else:
            print("✗ Next button not found")
            
        return True
    else:
        print(f"✗ Question {question_index} failed to load: {response.status_code}")
        return False

def submit_answer_and_go_next(session_id, question_index):
    """Submit an answer for the current question and go to the next one"""
    print(f"Submitting answer for question {question_index}...")
    
    data = {
        'response': f"Test response for question {question_index}",
        'evidence': f"Test evidence for question {question_index}",
        'response_score': random.choice([1, 2, 3, 4]),
        'next_question': 'true'
    }
    
    response = requests.post(
        f"{BASE_URL}/audit/{session_id}/question/{question_index}/submit", 
        data=data,
        allow_redirects=False
    )
    
    if response.status_code == 302:
        redirect_url = response.headers.get('Location')
        print(f"✓ Answer submitted successfully, redirecting to: {redirect_url}")
        
        # Extract the next question index
        match = re.search(r"/question/(\d+)", redirect_url)
        if match:
            next_index = int(match.group(1))
            print(f"✓ Next question index: {next_index}")
            return next_index
        else:
            print(f"✗ Failed to extract next question index from redirect URL")
            return None
    else:
        print(f"✗ Failed to submit answer: {response.status_code}")
        return None

def run_full_test():
    """Run a full test of the audit process"""
    print("="*50)
    print("ASIMOV AI Governance Audit Tool - Automated Test")
    print("="*50)
    
    # Test home page
    if not test_home_page():
        print("✗ Home page test failed, aborting further tests")
        return
    
    # Start a new audit
    session_id = start_audit_with_random_criteria()
    if not session_id:
        print("✗ Failed to start audit, aborting further tests")
        return
    
    # Test first question page
    if not test_question_page(session_id, 0):
        print("✗ Failed to access first question, aborting further tests")
        return
    
    # Submit answer and go to next question
    next_index = submit_answer_and_go_next(session_id, 0)
    if next_index is None:
        print("✗ Failed to proceed to next question, aborting further tests")
        return
    
    # Test second question page
    if not test_question_page(session_id, next_index):
        print("✗ Failed to access second question, test incomplete")
        return
    
    print("="*50)
    print("✓ All tests passed successfully!")
    print("="*50)

if __name__ == "__main__":
    run_full_test()