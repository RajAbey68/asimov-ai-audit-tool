#!/usr/bin/env python3
"""
ASIMOV AI Demo 1 Validation Suite
Comprehensive testing to lock down stable demo baseline
"""

import requests
import json
import sqlite3
from datetime import datetime

class Demo1Validator:
    """Validates Demo 1 is ready for lockdown"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'overall_status': 'UNKNOWN'
        }
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        self.test_results['tests'].append({
            'test': test_name,
            'status': status,
            'details': details
        })
        print(f"{'✅' if status == 'PASS' else '❌'} {test_name}: {details}")
        
    def test_homepage_load(self):
        """Test 1: Homepage loads with complete UI"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                html = response.text
                required_elements = [
                    "ASIMOV AI Governance Audit Tool",
                    "Start New AI Governance Audit", 
                    "framework_reference",
                    "Start Audit"
                ]
                
                missing = [elem for elem in required_elements if elem not in html]
                
                if not missing:
                    self.log_test("Homepage Load", "PASS", "All UI elements present")
                    return True
                else:
                    self.log_test("Homepage Load", "FAIL", f"Missing: {missing}")
                    return False
            else:
                self.log_test("Homepage Load", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Homepage Load", "FAIL", str(e))
            return False
            
    def test_database_integrity(self):
        """Test 2: Database has all required data"""
        try:
            conn = sqlite3.connect('audit_controls.db')
            cursor = conn.cursor()
            
            # Check controls exist
            cursor.execute('SELECT COUNT(*) FROM controls')
            controls_count = cursor.fetchone()[0]
            
            # Check frameworks exist
            cursor.execute('SELECT COUNT(*) FROM frameworks')
            frameworks_count = cursor.fetchone()[0]
            
            conn.close()
            
            if controls_count > 0 and frameworks_count > 0:
                self.log_test("Database Integrity", "PASS", 
                            f"{controls_count} controls, {frameworks_count} frameworks")
                return True
            else:
                self.log_test("Database Integrity", "FAIL", 
                            f"Controls: {controls_count}, Frameworks: {frameworks_count}")
                return False
                
        except Exception as e:
            self.log_test("Database Integrity", "FAIL", str(e))
            return False
            
    def test_audit_creation(self):
        """Test 3: Can create new audit session"""
        try:
            # Test POST to start-audit endpoint
            data = {
                'session_name': 'Demo1_Test_Session',
                'framework_filter': 'NIST AI RMF',
                'category_filter': '',
                'risk_filter': '',
                'sector_filter': 'All Sectors',
                'region_filter': 'All Regions'
            }
            
            response = requests.post(f"{self.base_url}/start-audit", 
                                   data=data, timeout=10, allow_redirects=False)
            
            if response.status_code in [200, 302]:  # Success or redirect
                self.log_test("Audit Creation", "PASS", "Session created successfully")
                return True
            else:
                self.log_test("Audit Creation", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Audit Creation", "FAIL", str(e))
            return False
            
    def test_framework_dropdown(self):
        """Test 4: Framework dropdown populated correctly"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            html = response.text
            
            expected_frameworks = [
                "NIST AI Risk Management Framework",
                "EU AI Act",
                "MITRE ATLAS"
            ]
            
            found_frameworks = [fw for fw in expected_frameworks if fw in html]
            
            if len(found_frameworks) >= 2:  # At least 2 frameworks visible
                self.log_test("Framework Dropdown", "PASS", 
                            f"Found {len(found_frameworks)} frameworks")
                return True
            else:
                self.log_test("Framework Dropdown", "FAIL", 
                            f"Only found {len(found_frameworks)} frameworks")
                return False
                
        except Exception as e:
            self.log_test("Framework Dropdown", "FAIL", str(e))
            return False
            
    def test_previous_audits_page(self):
        """Test 5: Previous audits page accessible"""
        try:
            response = requests.get(f"{self.base_url}/audits", timeout=5)
            
            if response.status_code == 200:
                self.log_test("Previous Audits Page", "PASS", "Page loads correctly")
                return True
            else:
                self.log_test("Previous Audits Page", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Previous Audits Page", "FAIL", str(e))
            return False
            
    def run_full_validation(self):
        """Run complete Demo 1 validation suite"""
        print("🔍 ASIMOV AI Demo 1 Validation Suite")
        print("=" * 45)
        
        tests = [
            self.test_homepage_load,
            self.test_database_integrity, 
            self.test_framework_dropdown,
            self.test_previous_audits_page,
            self.test_audit_creation
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
                
        # Determine overall status
        success_rate = passed_tests / total_tests
        
        if success_rate >= 0.8:  # 80% pass rate
            self.test_results['overall_status'] = 'DEMO_READY'
            status_message = "READY FOR DEMO 1 LOCKDOWN"
        elif success_rate >= 0.6:
            self.test_results['overall_status'] = 'NEEDS_MINOR_FIXES'
            status_message = "MINOR FIXES NEEDED"
        else:
            self.test_results['overall_status'] = 'NEEDS_MAJOR_FIXES'
            status_message = "MAJOR FIXES REQUIRED"
            
        print("\n" + "=" * 45)
        print(f"Demo 1 Status: {status_message}")
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate*100:.0f}%)")
        print("=" * 45)
        
        return self.test_results

def validate_demo1():
    """Main validation function"""
    validator = Demo1Validator()
    return validator.run_full_validation()

if __name__ == '__main__':
    results = validate_demo1()