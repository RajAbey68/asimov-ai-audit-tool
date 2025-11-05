"""
Automated Test Cases for the ASIMOV AI Governance Audit Tool

This script contains test functions for verifying that each feature
of the audit tool works correctly, including:
1. Start Audit functionality
2. Next/Prev button navigation
3. Export to PDF
4. Summary page generation
5. Life-Wise Insights generation
"""

import sqlite3
import requests
import time
import os
import json
from urllib.parse import urljoin

# Base URL for the application
BASE_URL = "http://172.31.128.97:5000"

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def test_home_page():
    """Test that the home page loads correctly"""
    print("\n🧪 TEST CASE: Home Page")
    
    response = requests.get(BASE_URL)
    success = response.status_code == 200 and "AI Governance Audit Tool" in response.text
    
    if success:
        print("✅ Home page loads successfully")
    else:
        print("❌ Home page failed to load")
        
    return success

def test_start_audit():
    """Test that the start audit function works correctly"""
    print("\n🧪 TEST CASE: Start Audit")
    
    # Create session data
    session_data = {
        "session_name": "Test Case Audit",
        "framework_filter": "Unified Framework (ASIMOV-AI)",
        "category_filter": "",
        "risk_level_filter": "",
        "sector_filter": "",
        "region_filter": ""
    }
    
    # Submit the form
    response = requests.post(f"{BASE_URL}/start_audit", data=session_data)
    
    # Check if we were redirected to the question page
    success = response.status_code == 200 and "/question/0" in response.url
    
    if success:
        print(f"✅ Start audit successful, redirected to: {response.url}")
        # Extract session ID from URL
        parts = response.url.split('/')
        if len(parts) >= 3:
            session_id = parts[-3]
            print(f"   Session ID: {session_id}")
            return session_id
    else:
        print(f"❌ Start audit failed with status code: {response.status_code}")
        return None

def test_direct_session_access():
    """Test direct access to a test session"""
    print("\n🧪 TEST CASE: Direct Session Access")
    
    session_id = "direct-test-session"
    response = requests.get(f"{BASE_URL}/audit/{session_id}/question/0")
    
    success = response.status_code == 200 and "Audit Question" in response.text
    
    if success:
        print(f"✅ Direct session access successful for session: {session_id}")
        return session_id
    else:
        print(f"❌ Direct session access failed with status code: {response.status_code}")
        return None

def test_question_navigation(session_id):
    """Test navigation between questions"""
    print("\n🧪 TEST CASE: Question Navigation")
    
    # Test first question
    response = requests.get(f"{BASE_URL}/audit/{session_id}/question/0")
    first_ok = response.status_code == 200 and "Audit Question" in response.text
    
    if first_ok:
        print("✅ First question loaded successfully")
        
        # Extract the control name from the response
        control_name = None
        # More robust parsing would be needed in a real test
        
        # Submit an answer
        answer_data = {
            "response": "Yes",
            "evidence": "Test evidence",
            "confidence": 4
        }
        
        submit_response = requests.post(
            f"{BASE_URL}/audit/{session_id}/question/0/submit", 
            data=answer_data
        )
        
        # Check if we were redirected to the next question
        submit_ok = submit_response.status_code == 200 and "/question/1" in submit_response.url
        
        if submit_ok:
            print("✅ Answer submitted and navigation to next question successful")
            return True
        else:
            print("❌ Answer submission or navigation failed")
            return False
    else:
        print(f"❌ Question loading failed with status code: {response.status_code}")
        return False

def test_lifewise_insights(session_id):
    """Test the Life-Wise Insights generation"""
    print("\n🧪 TEST CASE: Life-Wise Insights")
    
    response = requests.get(f"{BASE_URL}/audit/{session_id}/question/0")
    
    # Check if we have a Life-Wise Insight that matches our criteria
    insight_present = response.status_code == 200 and "Life-Wise Insight:" in response.text
    
    # Check if it's NOT using the old format (quoting laws directly)
    old_format = False
    if "according to" in response.text.lower() and "article" in response.text.lower():
        old_format = True
    
    if insight_present and not old_format:
        print("✅ Life-Wise Insight present and appears to use the new format")
        return True
    elif insight_present and old_format:
        print("❌ Life-Wise Insight is using the old format (quoting laws directly)")
        return False
    else:
        print("❌ Life-Wise Insight not found on the page")
        return False

def test_export_pdf(session_id):
    """Test exporting a question to PDF"""
    print("\n🧪 TEST CASE: Export to PDF")
    
    response = requests.get(f"{BASE_URL}/audit/{session_id}/question/0/export-pdf")
    
    # Check if we got a PDF response
    success = response.status_code == 200 and response.headers.get('Content-Type', '').startswith('application/pdf')
    
    if success:
        print("✅ PDF export successful")
        return True
    else:
        print(f"❌ PDF export failed with status code: {response.status_code}")
        return False

def test_summary_page(session_id):
    """Test the summary page"""
    print("\n🧪 TEST CASE: Summary Page")
    
    response = requests.get(f"{BASE_URL}/audit/{session_id}/summary")
    
    success = response.status_code == 200 and "Audit Summary" in response.text
    
    if success:
        print("✅ Summary page loads successfully")
        return True
    else:
        print(f"❌ Summary page failed to load with status code: {response.status_code}")
        return False

def run_all_tests():
    """Run all test cases"""
    print("\n🔍 ASIMOV AI Governance Audit Tool - Automated Test Suite")
    print("=" * 60)
    
    # Test home page
    home_ok = test_home_page()
    
    # Test direct session access (our most reliable path)
    session_id = test_direct_session_access()
    
    if not session_id:
        print("\n❌ Cannot continue tests without a valid session")
        return
    
    # Test question navigation
    nav_ok = test_question_navigation(session_id)
    
    # Test Life-Wise Insights
    insights_ok = test_lifewise_insights(session_id)
    
    # Test export to PDF
    pdf_ok = test_export_pdf(session_id)
    
    # Test summary page
    summary_ok = test_summary_page(session_id)
    
    # Print overall results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Home Page: {'✅' if home_ok else '❌'}")
    print(f"Direct Session Access: {'✅' if session_id else '❌'}")
    print(f"Question Navigation: {'✅' if nav_ok else '❌'}")
    print(f"Life-Wise Insights: {'✅' if insights_ok else '❌'}")
    print(f"Export to PDF: {'✅' if pdf_ok else '❌'}")
    print(f"Summary Page: {'✅' if summary_ok else '❌'}")
    
    # Try the start audit functionality last (it's been problematic)
    print("\nAttempting Start Audit test (this has been problematic)...")
    start_session_id = test_start_audit()
    print(f"Start Audit: {'✅' if start_session_id else '❌'}")
    
    print("\n" + "=" * 60)
    test_url = f"{BASE_URL}/audit/{session_id}/question/0"
    print(f"✅ For manual testing, visit: {test_url}")

if __name__ == "__main__":
    run_all_tests()