"""
Targeted test for controls that previously had issues with generating unique insights
This test focuses specifically on the controls that were failing in the extensive test
"""

import sqlite3
import requests
import json
import time
import random

PROBLEM_CONTROLS = [
    {"id": 4, "name": "Prevent Electoral Influence"},
    {"id": 12, "name": "Transfer Attack Testing"},
    {"id": 20, "name": "Enhanced Dataset Access"},
    {"id": 21, "name": "Prioritize Human Rights in AI"},
    {"id": 38, "name": "High-Risk Monitoring Log Retention"},
    {"id": 63, "name": "Technical Documentation Maintenance"},
    {"id": 66, "name": "Secure AI Training Data Sources"},
    {"id": 228, "name": "AI System Malfunction Tracking"},
    {"id": 240, "name": "Data Validation & Use of Robust Models"},
    {"id": 241, "name": "Testing & Documentation on Errors & Limitations"}
]

# Base URL for local testing
BASE_URL = "http://localhost:5000"

def test_specific_control_insights(control_id, control_name):
    """Test generating unique insights for a specific control"""
    print(f"\nTesting control #{control_id}: {control_name}")
    
    # Make two calls to the insight generator API (reduced from three for speed)
    insights = []
    for i in range(2):
        data = {
            "control_name": control_name,
            "category": "Testing Category",
            "risk_level": "High",
            "sector": "Financial Services",
            "region": "Europe"
        }
        
        response = requests.post(
            f"{BASE_URL}/generate-insight",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            insight = result.get("insight", "")
            insights.append(insight)
            print(f"  → Insight {i+1} (first 50 chars): {insight[:50]}...")
            # No delay between requests to speed up the test
        else:
            print(f"  → Error generating insight {i+1}: {response.status_code}")
    
    # Check if insights are unique
    unique_insights = set(insights)
    is_success = len(unique_insights) == len(insights)
    
    if is_success:
        print(f"  ✅ SUCCESS: Generated {len(unique_insights)} unique insights")
        return True
    else:
        print(f"  ❌ FAILED: Generated only {len(unique_insights)} unique insights out of {len(insights)}")
        return False

def run_tests():
    """Run tests for all problem controls"""
    print("Testing Unique Insight Generation for Problem Controls")
    print("=" * 70)
    
    success_count = 0
    total_count = len(PROBLEM_CONTROLS)
    
    for control in PROBLEM_CONTROLS:
        success = test_specific_control_insights(control["id"], control["name"])
        if success:
            success_count += 1
    
    success_rate = (success_count / total_count) * 100
    
    print("\n" + "=" * 70)
    print(f"Test Results: {success_count}/{total_count} controls passed ({success_rate:.1f}%)")
    print("=" * 70)
    
    if success_count == total_count:
        print("✅ ALL TESTS PASSED - Problem controls now generate unique insights!")
        return True
    else:
        print(f"❌ SOME TESTS FAILED - {total_count - success_count} controls still have issues")
        return False

if __name__ == "__main__":
    run_tests()