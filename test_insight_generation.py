"""
Test script to verify that Life-Wise Insights are different across controls
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import time
import uuid
import re

# Configuration
BASE_URL = "http://localhost:5000"

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def extract_insight(html_content):
    """Extract the Life-Wise Insight from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    insight_div = soup.find('div', class_='card-body bg-light')
    
    if insight_div:
        # Try to find the insight paragraph
        insights_section = insight_div.get_text() if insight_div else ""
        if "Life-Wise Insight:" in insights_section:
            # Extract the insight text after the label
            insight_text = insights_section.split("Life-Wise Insight:", 1)[1].strip()
            return insight_text
    
    return None

def test_insights_differ_across_controls():
    """Test if Life-Wise Insights are different across controls"""
    print("Testing if Life-Wise Insights differ across controls...")
    
    # Create a session
    session = requests.Session()
    
    # Create a new audit session
    audit_name = f"Insight Test {time.strftime('%Y%m%d-%H%M%S')}"
    data = {
        'session_name': audit_name,
        'framework_filter': 'EU AI Act (2023)',
        'category_filter': '',
        'risk_level_filter': '',
        'sector_filter': '',
        'region_filter': ''
    }
    
    # Start the audit
    print(f"Creating new audit session: {audit_name}")
    start_resp = session.post(f"{BASE_URL}/start-audit", data=data, allow_redirects=True)
    
    # Extract session ID from URL
    session_id = start_resp.url.split('/audit/')[1].split('/question/')[0]
    print(f"Created session with ID: {session_id}")
    
    # Check multiple questions and collect insights
    insights = {}
    question_count = 5  # Check first 5 questions
    
    for i in range(question_count):
        # Get the question page
        q_url = f"{BASE_URL}/audit/{session_id}/question/{i}"
        print(f"Checking question {i+1}...")
        q_resp = session.get(q_url)
        
        # Extract the control name and insight
        soup = BeautifulSoup(q_resp.text, 'html.parser')
        control_name_h2 = soup.find('h2')
        control_name = control_name_h2.text if control_name_h2 else f"Control {i+1}"
        
        insight = extract_insight(q_resp.text)
        insights[control_name] = insight
        
        print(f"Control: {control_name}")
        if insight:
            print(f"Insight: {insight[:100]}...\n")
        else:
            print("Insight: None found\n")
    
    # Compare all insights to see if they're different
    unique_insights = set(insights.values())
    print(f"Found {len(unique_insights)} unique insights out of {len(insights)} controls")
    
    # Check if all insights are the same
    if len(unique_insights) == 1:
        print("❌ FAIL: All insights are identical!")
        print(f"Repeated insight: {next(iter(unique_insights))[:100]}...")
        return False
    
    # Check if we have at least some unique insights
    if len(unique_insights) < len(insights) / 2:
        print(f"⚠️ WARNING: Only {len(unique_insights)} unique insights out of {len(insights)} controls")
        return False
    
    print("✅ PASS: Insights are different across controls")
    return True

def check_insight_generation_method():
    """Check how insights are generated in the application code"""
    # Look for the implementation of get_sector_specific_insight function
    try:
        with open('app.py', 'r') as f:
            app_code = f.read()
            
        # Find the function implementation
        pattern = r'def get_sector_specific_insight\([^)]*\):(.*?)def'
        match = re.search(pattern, app_code, re.DOTALL)
        
        if match:
            implementation = match.group(1).strip()
            print("\nInsight generation implementation:")
            for line in implementation.split('\n')[:10]:  # Show first 10 lines
                print(line)
            
            # Check if falling back to hardcoded insights
            if "return f\"A 2023 industry analysis revealed" in implementation:
                print("\n⚠️ Found generic fallback insight that doesn't use control-specific information!")
            
            # Check if using the API
            if "api_key" in implementation.lower() or "openai" in implementation.lower():
                print("\n✅ Using API for dynamic insight generation")
        else:
            print("\n❌ Could not find get_sector_specific_insight implementation")
            
    except Exception as e:
        print(f"\n❌ Error analyzing code: {str(e)}")

def test_fallback_insights():
    """Test the fallback insights to see if they differ by control category or name"""
    print("\nTesting fallback insights...")
    
    # Get some different control categories from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM controls LIMIT 5")
    categories = [row['category'] for row in cursor.fetchall()]
    
    # Get control names from different categories
    test_controls = []
    for category in categories:
        cursor.execute("SELECT control_name, category FROM controls WHERE category = ? LIMIT 1", (category,))
        control = cursor.fetchone()
        if control:
            test_controls.append(dict(control))
    
    conn.close()
    
    # Import the function directly if possible
    try:
        import sys
        sys.path.append('.')
        from app import get_sector_specific_insight
        
        print("\nTesting insights for different controls:")
        insights = {}
        
        for control in test_controls:
            name = control['control_name']
            category = control['category']
            
            insight = get_sector_specific_insight(name, category, "High", "", "")
            insights[name] = insight
            
            print(f"\nControl: {name} (Category: {category})")
            if insight:
                print(f"Insight: {insight[:150]}...\n")
            else:
                print("Insight: None found\n")
        
        # Check if insights differ
        unique_insights = set(insights.values())
        print(f"Generated {len(unique_insights)} unique insights for {len(insights)} controls")
        
        if len(unique_insights) == 1:
            print("❌ FAIL: All fallback insights are identical!")
            return False
        
        if len(unique_insights) >= len(insights) * 0.8:
            print("✅ PASS: Most fallback insights are unique")
            return True
        else:
            print(f"⚠️ WARNING: Only {len(unique_insights)} unique insights out of {len(insights)} controls")
            return False
            
    except ImportError:
        print("❌ Could not import get_sector_specific_insight function directly")
        return False

if __name__ == "__main__":
    print("Running Life-Wise Insights Generation Test")
    print("==========================================\n")
    
    # First check the implementation
    check_insight_generation_method()
    
    # Test the insights through the UI
    ui_test_result = test_insights_differ_across_controls()
    
    # Test the fallback insights directly
    fallback_test_result = test_fallback_insights()
    
    print("\nTest Summary:")
    print("=============")
    print(f"UI Test Passed: {'Yes' if ui_test_result else 'No'}")
    print(f"Fallback Insights Test Passed: {'Yes' if fallback_test_result else 'No'}")
    
    if not ui_test_result:
        print("\nRecommended fix:")
        print("1. Check get_sector_specific_insight implementation in app.py")
        print("2. Make sure it uses the control name and category to generate unique insights")
        print("3. If using a fallback, make sure it has conditional logic based on control properties")