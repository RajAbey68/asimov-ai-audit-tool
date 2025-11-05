"""
Test cycling through multiple controls to verify Life-Wise Insights for each question
"""

import requests
import re
import time
import sqlite3

# Configuration
BASE_URL = "http://172.31.128.97:5000"
TEST_SESSION_ID = "sequential-test-session"  # We'll create this for testing
NUM_CONTROLS_TO_TEST = 10  # Test at least 10 controls

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_test_session():
    """Create a test session specifically for cycling through controls"""
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
        "Sequential Navigation Test",
        "Unified Framework (ASIMOV-AI)",  # Framework that matches all controls
        "%",
        "",  # No category filter
        "",  # No risk level filter
        "",  # No sector filter
        ""   # No region filter
    ))
    
    conn.commit()
    conn.close()
    
    return TEST_SESSION_ID

def get_control_count():
    """Check how many controls match our criteria"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # For our test session with Unified Framework (wildcard), this gets all controls
    cursor.execute("SELECT COUNT(*) as count FROM controls")
    count = cursor.fetchone()['count']
    
    conn.close()
    return count

def test_sequential_navigation():
    """Test navigating through multiple controls sequentially"""
    print("\n🧪 SEQUENTIAL NAVIGATION TEST")
    print("=" * 60)
    
    # Create a test session
    session_id = create_test_session()
    print(f"✅ Created test session with ID: {session_id}")
    
    # Get the total number of controls for this session
    total_controls = get_control_count()
    print(f"✅ Found {total_controls} total controls")
    
    # Determine how many to test
    num_to_test = min(NUM_CONTROLS_TO_TEST, total_controls)
    print(f"✅ Will test navigation through {num_to_test} controls")
    
    # Track Life-Wise Insights for each control
    insights = []
    
    # Start with the first question
    current_index = 0
    
    # Test accessing each control
    while current_index < num_to_test:
        print(f"\n🔍 Testing question {current_index + 1} of {num_to_test}")
        
        # Access the current question
        question_url = f"{BASE_URL}/audit/{session_id}/question/{current_index}"
        response = requests.get(question_url)
        
        if response.status_code != 200:
            print(f"❌ Failed to access question {current_index}: Status code {response.status_code}")
            break
        
        # Parse the control name from the page
        control_name_match = re.search(r'<h4[^>]*>([^<]+)</h4>', response.text)
        control_name = control_name_match.group(1) if control_name_match else f"Control {current_index}"
        
        # Extract the Life-Wise Insight text
        insight_pattern = r'<div[^>]*class="card-body"[^>]*>\s*<p>\s*<strong>Life-Wise Insight:</strong>\s*(.*?)\s*</p>'
        insight_match = re.search(insight_pattern, response.text, re.DOTALL)
        insight_text = insight_match.group(1) if insight_match else "No insight found"
        
        # Check if it's a real-world example (not just quoting laws)
        has_real_world = False
        real_world_terms = ["incident", "breach", "attack", "failure", "compromise", "2023", "organization"]
        
        for term in real_world_terms:
            if term in insight_text.lower():
                has_real_world = True
                break
        
        # Store control and insight information
        insights.append({
            "index": current_index,
            "control": control_name,
            "insight": insight_text[:100] + "..." if len(insight_text) > 100 else insight_text,
            "has_real_world": has_real_world
        })
        
        # Submit an answer and move to the next question
        submit_data = {
            "response": "Yes",
            "evidence": f"Test evidence for {control_name}",
            "confidence": "3"
        }
        
        submit_url = f"{BASE_URL}/audit/{session_id}/question/{current_index}/submit"
        submit_response = requests.post(submit_url, data=submit_data)
        
        # Check if we were redirected to the next question or summary
        if "/question/" in submit_response.url:
            next_index = int(submit_response.url.split("/question/")[1])
            if next_index > current_index:
                print(f"✅ Successfully navigated to question {next_index}")
                current_index = next_index
            else:
                print(f"❌ Navigation error: Redirected to previous question {next_index}")
                break
        elif "/summary" in submit_response.url:
            print("✅ Reached summary page (end of questions)")
            break
        else:
            print(f"❌ Unexpected redirect: {submit_response.url}")
            break
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 SEQUENTIAL NAVIGATION RESULTS")
    print("=" * 60)
    
    real_world_count = sum(1 for insight in insights if insight["has_real_world"])
    success_rate = (real_world_count / len(insights)) * 100 if insights else 0
    
    print(f"Controls tested: {len(insights)}")
    print(f"Controls with real-world insights: {real_world_count}")
    print(f"Success rate: {success_rate:.1f}%")
    
    print("\nSample insights:")
    for i, insight in enumerate(insights):
        status = "✅" if insight["has_real_world"] else "❌"
        print(f"{status} Control {i+1}: {insight['control']}")
        print(f"   Insight: {insight['insight']}")
    
    print("\n" + "=" * 60)
    if success_rate >= 90:
        print("✅ TEST PASSED: At least 90% of controls have real-world insights")
    else:
        print("❌ TEST FAILED: Less than 90% of controls have real-world insights")
    
    return insights

if __name__ == "__main__":
    test_sequential_navigation()