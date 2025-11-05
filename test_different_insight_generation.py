"""
Test script to verify the Generate New Insight button functionality

This test specifically targets the issue with generating the same insight multiple times
by testing direct API calls to the /generate-insight endpoint
"""

import requests
import json
import time
from bs4 import BeautifulSoup
import random

def test_insight_button():
    """Test if the Generate New Insight button produces different insights each time"""
    print("Testing Generate New Insight Button Functionality")
    print("=" * 60)
    
    # Start a new audit session
    session = requests.Session()
    
    # 1. Get the home page
    print("1. Getting the home page...")
    response = session.get("http://localhost:5000/")
    if response.status_code != 200:
        print(f"ERROR: Failed to get home page, status code: {response.status_code}")
        return False
    
    # 2. Start a new audit with random parameters
    print("2. Creating a new audit session...")
    frameworks = ["EU AI Act (2023)", "NIST AI Risk Management Framework (AI RMF v1.0)"]
    audit_name = f"Test Audit {random.randint(1000, 9999)}"
    
    response = session.post("http://localhost:5000/start-audit", data={
        "framework_filter": random.choice(frameworks),
        "category_filter": "Any",
        "risk_level_filter": "Any",
        "sector_filter": "",
        "region_filter": "",
        "audit_name": audit_name
    })
    
    if response.status_code != 200 and response.status_code != 302:
        print(f"ERROR: Failed to start audit, status code: {response.status_code}")
        return False
    
    # Get the session ID from the redirect URL
    session_id = response.url.split("/")[-3]
    print(f"   Created session with ID: {session_id}")
    
    # 3. Get the first question page
    print("3. Getting first question page...")
    response = session.get(response.url)
    if response.status_code != 200:
        print(f"ERROR: Failed to get question page, status code: {response.status_code}")
        return False
    
    # Parse the page to get control information
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get control name from the h2 tag
    control_name = soup.find('h2').text.strip()
    
    # Get category from hidden input
    category_input = soup.find('input', {'name': 'category'})
    category = category_input['value'] if category_input else ""
    
    # Get risk level from meta tags (if present)
    risk_level = "High"  # Default
    meta_tags = soup.find_all('span', class_='meta-tag')
    for tag in meta_tags:
        if 'Risk:' in tag.text:
            risk_level = tag.text.replace('Risk:', '').strip()
    
    print(f"   Control Name: {control_name}")
    print(f"   Category: {category}")
    print(f"   Risk Level: {risk_level}")
    
    # 4. Get the original insight from the page
    insight_div = soup.find('div', id='insightContent')
    original_insight = insight_div.find('p').text.strip() if insight_div and insight_div.find('p') else ""
    print(f"4. Original insight: {original_insight[:50]}...")
    
    # 5. Make 3 consecutive API calls to /generate-insight and compare results
    print("5. Testing generate-insight endpoint with 3 consecutive calls...")
    insights = []
    
    for i in range(3):
        response = session.post(
            "http://localhost:5000/generate-insight",
            json={
                "control_name": control_name,
                "category": category,
                "risk_level": risk_level,
                "sector": "",
                "region": ""
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"ERROR: Failed to generate insight, status code: {response.status_code}")
            return False
        
        data = response.json()
        new_insight = data.get('insight', '')
        insights.append(new_insight)
        print(f"   Call {i+1} returned: {new_insight[:50]}...")
        
        # Add a small delay to ensure different timestamps
        time.sleep(0.5)
    
    # 6. Check if all insights are different
    unique_insights = set(insights)
    print(f"6. Number of unique insights: {len(unique_insights)} out of 3")
    
    if len(unique_insights) < 3:
        print("❌ FAILED: Not all insights were unique")
        print("   Comparing insights for similarity:")
        for i, insight in enumerate(insights):
            print(f"   Insight {i+1} (first 100 chars): {insight[:100]}")
        return False
    else:
        print("✅ PASSED: All 3 insights were unique")
        return True

if __name__ == "__main__":
    if test_insight_button():
        print("\nOverall Result: ✅ PASSED - Generate New Insight button generates unique insights")
    else:
        print("\nOverall Result: ❌ FAILED - Generate New Insight button is not generating unique insights")