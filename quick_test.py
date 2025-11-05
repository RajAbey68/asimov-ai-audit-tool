"""
Quick Test for ASIMOV AI Governance Audit Tool
Tests the main functionality without complex interactions
"""

import requests
import sqlite3

def test_home_page():
    """Test if home page loads"""
    try:
        response = requests.get("http://localhost:5001/")
        if response.status_code == 200:
            print("✅ Home page loads successfully")
            return True
        else:
            print(f"❌ Home page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Home page error: {e}")
        return False

def test_database():
    """Test if database has controls"""
    try:
        conn = sqlite3.connect('audit_controls.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM controls')
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            print(f"✅ Database has {count} controls")
            return True
        else:
            print("❌ Database is empty")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_start_audit():
    """Test starting an audit"""
    try:
        # Get home page first
        session = requests.Session()
        response = session.get("http://localhost:5001/")
        
        # Try to start an audit
        data = {
            'audit_name': 'Test Audit',
            'framework_filter': 'All Frameworks',
            'category_filter': 'All Categories',
            'risk_level_filter': 'All Risk Levels',
            'sector_filter': 'Technology',
            'region_filter': 'United States'
        }
        
        response = session.post("http://localhost:5001/start-audit", data=data)
        
        if response.status_code in [200, 302]:
            print("✅ Audit can be started successfully")
            return True
        else:
            print(f"❌ Start audit failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Start audit error: {e}")
        return False

def run_quick_tests():
    """Run all quick tests"""
    print("🧪 Running Quick Tests for ASIMOV AI Governance Audit Tool")
    print("=" * 60)
    
    tests = [
        test_home_page,
        test_database,
        test_start_audit
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is working properly.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")

if __name__ == "__main__":
    run_quick_tests()