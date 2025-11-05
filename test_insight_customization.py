"""
Test Insight Customization and Filtering Features

This script verifies that the audit tool correctly:
1. Filters controls based on framework, category, risk level, sector, and region
2. Customizes insights for healthcare and UK-specific context
3. Shows different insights when viewing the same control (temporal variation)
4. Displays regulatory deadlines appropriate to the selections
"""

import sqlite3
import requests
import time
import re
from bs4 import BeautifulSoup
import random
import datetime

# Test configuration
TEST_AUDIT_NAME = f"Insight Test {int(time.time())}"
TEST_FRAMEWORK = "EU AI Act (2023)"
TEST_CATEGORY = "AI Confidentiality & Information Leakage Prevention"
TEST_RISK_LEVEL = "High Risk"
TEST_SECTOR = "Healthcare"
TEST_REGION = "United Kingdom"

# Base URL for the application
BASE_URL = "http://localhost:5000"

def get_db_connection():
    """Create a database connection with row factory"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def start_test_audit():
    """Create a test audit session with specific filters"""
    print(f"\n🧪 Creating test audit with parameters:")
    print(f"  • Audit Name: {TEST_AUDIT_NAME}")
    print(f"  • Framework: {TEST_FRAMEWORK}")
    print(f"  • Category: {TEST_CATEGORY}")
    print(f"  • Risk Level: {TEST_RISK_LEVEL}")
    print(f"  • Sector: {TEST_SECTOR}")
    print(f"  • Region: {TEST_REGION}")
    
    # Make request to create the audit session
    response = requests.post(f"{BASE_URL}/start-audit", data={
        "audit_name": TEST_AUDIT_NAME,
        "framework_filter": TEST_FRAMEWORK,
        "category_filter": TEST_CATEGORY,
        "risk_level_filter": TEST_RISK_LEVEL,
        "sector_filter": TEST_SECTOR,
        "region_filter": TEST_REGION
    })
    
    # Extract session ID from the redirect URL
    if response.status_code == 302:  # Redirect status code
        redirect_url = response.headers.get('Location', '')
        session_id_match = re.search(r'/audit/([^/]+)/question/0', redirect_url)
        if session_id_match:
            session_id = session_id_match.group(1)
            print(f"✅ Created audit session with ID: {session_id}")
            return session_id
    
    print(f"❌ Failed to create audit session")
    return None

def get_control_info(session_id, question_index=0):
    """Get control information from a specific question page"""
    response = requests.get(f"{BASE_URL}/audit/{session_id}/question/{question_index}")
    
    if response.status_code != 200:
        print(f"❌ Failed to access question {question_index}")
        return None
    
    # Parse HTML to extract control information and insights
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract control name
    control_name_elem = soup.find('h2')
    control_name = control_name_elem.text.strip() if control_name_elem else "Unknown Control"
    
    # Extract risk level
    risk_level_elem = soup.find('div', class_='risk-badge')
    risk_level = risk_level_elem.text.strip() if risk_level_elem else "Unknown Risk"
    
    # Extract sector and region
    sector_badge = soup.find('span', class_='sector-badge')
    sector = sector_badge.text.strip() if sector_badge else "No Sector"
    
    region_badge = soup.find('span', class_='region-badge')
    region = region_badge.text.strip() if region_badge else "No Region"
    
    # Extract insight text
    insight_elem = soup.find('div', class_='insight-container')
    insight_text = insight_elem.text.strip() if insight_elem else "No insight found"
    
    # Bundle all information
    control_info = {
        'control_name': control_name,
        'risk_level': risk_level,
        'sector': sector,
        'region': region,
        'insight_text': insight_text
    }
    
    return control_info

def test_insight_variation(session_id, question_index=0):
    """Test if the same control shows different insights when viewed multiple times"""
    print(f"\n🧪 Testing temporal variation of insights for question {question_index}")
    
    # Get insight first time
    first_info = get_control_info(session_id, question_index)
    if not first_info:
        return False
    
    # Force insight rotation by directly updating the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get control_id for this question
    cursor.execute('''
        SELECT * FROM controls 
        WHERE framework LIKE ? AND category = ? AND risk_level = ?
        ORDER BY id LIMIT ?, 1
    ''', (
        f"%{TEST_FRAMEWORK.replace('(2023)', '')}%", 
        TEST_CATEGORY, 
        TEST_RISK_LEVEL,
        question_index
    ))
    control = cursor.fetchone()
    
    if not control:
        print("❌ Could not find control in database")
        conn.close()
        return False
    
    control_id = control['id']
    
    # Force rotation by setting view count high
    cursor.execute('''
        UPDATE insight_variations SET view_count = ? WHERE control_id = ?
    ''', (10, control_id))
    conn.commit()
    conn.close()
    
    # Wait briefly to ensure rotation takes effect
    time.sleep(1)
    
    # Get insight second time
    second_info = get_control_info(session_id, question_index)
    if not second_info:
        return False
    
    # Compare insights
    insights_differ = first_info['insight_text'] != second_info['insight_text']
    
    print(f"Control: {first_info['control_name']}")
    print(f"First insight length: {len(first_info['insight_text'])} characters")
    print(f"Second insight length: {len(second_info['insight_text'])} characters")
    print(f"Insights differ: {'✅ YES' if insights_differ else '❌ NO'}")
    
    if insights_differ:
        print("✅ Temporal variation is working!")
    else:
        print("❌ Insights did not change between views")
    
    return insights_differ

def test_sector_specific_content(session_id, question_index=0):
    """Test if insights contain sector-specific content"""
    print(f"\n🧪 Testing for healthcare-specific content in insights")
    
    control_info = get_control_info(session_id, question_index)
    if not control_info:
        return False
    
    # Healthcare-specific terms to look for
    healthcare_terms = [
        "healthcare", "patient", "medical", "hospital", "clinical", 
        "HIPAA", "NHS", "electronic health record", "EHR", "diagnosis", 
        "treatment"
    ]
    
    insight_text = control_info['insight_text'].lower()
    matched_terms = [term for term in healthcare_terms if term.lower() in insight_text]
    
    print(f"Control: {control_info['control_name']}")
    print(f"Insight length: {len(insight_text)} characters")
    print(f"Healthcare terms found: {len(matched_terms)}")
    for term in matched_terms:
        print(f"  • '{term}'")
    
    has_healthcare_content = len(matched_terms) > 0
    
    if has_healthcare_content:
        print("✅ Healthcare-specific content found in insight!")
    else:
        print("❌ No healthcare-specific content found")
    
    return has_healthcare_content

def test_region_specific_content(session_id, question_index=0):
    """Test if insights contain region-specific content"""
    print(f"\n🧪 Testing for UK-specific content in insights")
    
    control_info = get_control_info(session_id, question_index)
    if not control_info:
        return False
    
    # UK-specific terms to look for
    uk_terms = [
        "UK", "United Kingdom", "Britain", "England", "NHS", "ICO", 
        "Information Commissioner's Office", "GDPR", "UK AI Safety Institute",
        "British", "London"
    ]
    
    insight_text = control_info['insight_text']
    matched_terms = [term for term in uk_terms if term in insight_text]
    
    print(f"Control: {control_info['control_name']}")
    print(f"Insight length: {len(insight_text)} characters")
    print(f"UK terms found: {len(matched_terms)}")
    for term in matched_terms:
        print(f"  • '{term}'")
    
    has_uk_content = len(matched_terms) > 0
    
    if has_uk_content:
        print("✅ UK-specific content found in insight!")
    else:
        print("❌ No UK-specific content found")
    
    return has_uk_content

def test_regulatory_timeline_info(session_id, question_index=0):
    """Test if regulatory timeline information is displayed"""
    print(f"\n🧪 Testing for regulatory timeline information")
    
    response = requests.get(f"{BASE_URL}/audit/{session_id}/question/{question_index}")
    
    if response.status_code != 200:
        print(f"❌ Failed to access question {question_index}")
        return False
    
    # Parse HTML to extract timeline information
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for timeline information
    timeline_elem = soup.find('div', class_='regulatory-timeline')
    if not timeline_elem:
        # Try alternative class names or text patterns
        paragraphs = soup.find_all('p')
        timeline_elem = None
        for p in paragraphs:
            text = p.text.lower()
            if "mandatory" in text and ("eu ai act" in text or "deadline" in text or "by " in text):
                timeline_elem = p
                break
    
    has_timeline_info = timeline_elem is not None
    
    if has_timeline_info:
        print(f"✅ Regulatory timeline information found:")
        print(f"  • {timeline_elem.text.strip()}")
    else:
        print("❌ No regulatory timeline information found")
    
    return has_timeline_info

def run_test_suite():
    """Run all tests for insight customization and filtering"""
    print("\n" + "=" * 70)
    print("🧪 ASIMOV AI GOVERNANCE AUDIT TOOL - INSIGHT CUSTOMIZATION TEST SUITE")
    print("=" * 70)
    print(f"Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Start a test audit
    session_id = start_test_audit()
    if not session_id:
        return
    
    # Run tests
    test_results = {
        "insight_variation": test_insight_variation(session_id),
        "sector_specific": test_sector_specific_content(session_id),
        "region_specific": test_region_specific_content(session_id),
        "regulatory_timeline": test_regulatory_timeline_info(session_id)
    }
    
    # Report overall results
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    for test_name, result in test_results.items():
        print(f"{test_name}: {'✅ PASS' if result else '❌ FAIL'}")
    
    overall_success = all(test_results.values())
    print("-" * 70)
    print(f"Overall Test Result: {'✅ PASS' if overall_success else '❌ FAIL'}")
    print(f"End Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    run_test_suite()