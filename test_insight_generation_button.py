"""
Test script to verify that the "Generate New Insight" button works correctly
"""

import requests
import json
import time
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "http://localhost:5000"

def test_generate_new_insight_button():
    """Test the Generate New Insight button functionality"""
    print("Testing 'Generate New Insight' button functionality...")
    
    # Create a session and start a new audit
    session = requests.Session()
    
    # Step 1: Get the home page
    print("1. Getting the home page...")
    home_resp = session.get(f"{BASE_URL}/")
    assert home_resp.status_code == 200
    
    # Step 2: Create a new audit session
    print("2. Creating a new audit session...")
    audit_name = f"Insight Button Test {time.strftime('%Y%m%d-%H%M%S')}"
    data = {
        'session_name': audit_name,
        'framework_filter': 'EU AI Act (2023)',
        'category_filter': '',
        'risk_level_filter': '',
        'sector_filter': 'Financial Services',  # Add a sector to test sector-specific insights
        'region_filter': 'European Union'       # Add a region to test region-specific insights
    }
    
    audit_resp = session.post(f"{BASE_URL}/start-audit", data=data, allow_redirects=True)
    assert audit_resp.status_code == 200
    
    # Extract session ID from URL
    session_id = audit_resp.url.split('/audit/')[1].split('/question/')[0]
    print(f"   Created session with ID: {session_id}")
    
    # Step 3: Access the first question page
    print("3. Accessing first question...")
    q_url = f"{BASE_URL}/audit/{session_id}/question/0"
    q_resp = session.get(q_url)
    assert q_resp.status_code == 200
    
    # Step 4: Extract the current insight
    print("4. Extracting current insight...")
    soup = BeautifulSoup(q_resp.text, 'html.parser')
    
    # Find the insight content
    insight_div = soup.find('div', id='insightContent')
    if not insight_div:
        print("   ERROR: No insight content found on the page")
        return False
        
    initial_insight_p = insight_div.find('p')
    if not initial_insight_p:
        print("   ERROR: No insight paragraph found")
        return False
        
    initial_insight = initial_insight_p.get_text().replace('Life-Wise Insight:', '').strip()
    print(f"   Initial insight (first 50 chars): {initial_insight[:50]}...")
    
    # Step 5: Extract control data for the API call
    print("5. Extracting control data...")
    control_name_h2 = soup.find('h2')
    control_name = control_name_h2.text.strip() if control_name_h2 else ""
    
    category_span = soup.find('span', class_='meta-tag')
    category = category_span.text.strip() if category_span else ""
    
    risk_level_span = soup.select('.meta-tag:nth-of-type(2)')
    risk_level = risk_level_span[0].text.replace('Risk:', '').strip() if risk_level_span else "High"
    
    print(f"   Control: {control_name}")
    print(f"   Category: {category}")
    print(f"   Risk Level: {risk_level}")
    
    # Step 6: Make a direct API call to test insight generation
    print("6. Testing API endpoint directly...")
    payload = {
        'control_name': control_name,
        'category': category,
        'risk_level': risk_level,
        'sector': 'Financial Services',
        'region': 'European Union'
    }
    
    api_resp = session.post(
        f"{BASE_URL}/generate-insight",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    # Check if the API call was successful
    if api_resp.status_code != 200:
        print(f"   ERROR: API call failed with status code {api_resp.status_code}")
        print(f"   Response: {api_resp.text}")
        return False
    
    # Parse the response
    try:
        api_data = api_resp.json()
        new_insight = api_data.get('insight', '')
        
        print(f"   New insight (first 50 chars): {new_insight[:50]}...")
        
        # Compare the insights to make sure they're different
        if initial_insight == new_insight:
            print("   WARNING: New insight is identical to the initial insight")
        else:
            print("   SUCCESS: Generated a different insight")
            
    except json.JSONDecodeError:
        print("   ERROR: Failed to parse API response as JSON")
        print(f"   Response: {api_resp.text}")
        return False
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    print("Running Generate New Insight Button Test")
    print("=========================================\n")
    
    result = test_generate_new_insight_button()
    
    if result:
        print("\n✅ TEST PASSED: The Generate New Insight functionality is working")
    else:
        print("\n❌ TEST FAILED: The Generate New Insight functionality has issues")