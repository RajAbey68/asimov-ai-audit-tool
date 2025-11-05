"""
Test for View Previous Audits functionality
"""

import requests
import sqlite3

def test_audits_page():
    """Test the /audits route works properly"""
    
    print("🧪 Testing View Previous Audits functionality")
    print("=" * 50)
    
    # Test 1: Check if /audits page loads
    try:
        response = requests.get("http://localhost:5001/audits")
        if response.status_code == 200:
            print("✅ /audits page loads successfully")
            
            # Check if the page contains expected content
            if "Previous AI Governance Audits" in response.text:
                print("✅ Page contains correct heading")
            else:
                print("❌ Page missing expected heading")
                
            # Check if it shows the empty state or audit list
            if "No previous audits found" in response.text or "Audit Name" in response.text:
                print("✅ Page shows appropriate content (empty state or audit list)")
            else:
                print("❌ Page content unexpected")
                
        else:
            print(f"❌ /audits page failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing /audits page: {e}")
    
    # Test 2: Create a test audit and verify it appears in the list
    try:
        session = requests.Session()
        
        # Create a test audit
        data = {
            'audit_name': 'Test Audit for Verification',
            'framework_filter': 'All Frameworks',
            'category_filter': 'All Categories',
            'risk_level_filter': 'All Risk Levels',
            'sector_filter': 'Technology',
            'region_filter': 'United States'
        }
        
        response = session.post("http://localhost:5001/start-audit", data=data)
        
        if response.status_code in [200, 302]:
            print("✅ Test audit created successfully")
            
            # Now check if it appears in the audits list
            response = session.get("http://localhost:5001/audits")
            if "Test Audit for Verification" in response.text:
                print("✅ New audit appears in the audits list")
            else:
                print("❌ New audit not found in audits list")
        else:
            print("❌ Failed to create test audit")
            
    except Exception as e:
        print(f"❌ Error testing audit creation: {e}")
    
    # Test 3: Check database has audit sessions
    try:
        conn = sqlite3.connect('audit_controls.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM audit_sessions')
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            print(f"✅ Database contains {count} audit sessions")
        else:
            print("❌ No audit sessions found in database")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print("=" * 50)
    print("🏁 Test completed")

if __name__ == "__main__":
    test_audits_page()