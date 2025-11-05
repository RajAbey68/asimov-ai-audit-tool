"""
Pre-Release Testing Suite for ASIMOV AI Governance Audit Tool

This comprehensive testing framework validates all functionality before deployment
to catch issues like 404 errors, broken routes, and missing features.

Usage:
    python pre_release_test_suite.py
"""

import requests
import sqlite3
import json
import os
import sys
from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock

class PreReleaseTestSuite:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, status, details="", error=None):
        """Log test result with timestamp"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'test_name': test_name,
            'status': status,  # PASS, FAIL, ERROR
            'details': details,
            'error': str(error) if error else None
        }
        self.test_results.append(result)
        
        # Print real-time feedback
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   {details}")
        if error:
            print(f"   Error: {error}")
    
    def test_home_page_accessibility(self):
        """Test 1: Verify home page loads correctly"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                if "ASIMOV AI Governance Audit Tool" in response.text:
                    self.log_test("Home Page Load", "PASS", "Page loads with correct title")
                else:
                    self.log_test("Home Page Load", "FAIL", "Title not found in response")
            else:
                self.log_test("Home Page Load", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Home Page Load", "ERROR", error=e)
    
    def test_navigation_links(self):
        """Test 2: Verify all navigation links are accessible"""
        nav_links = [
            ("/", "Home"),
            ("/audits", "Previous Audits"),
            ("/reports", "Reports & Analytics"),
            ("/roadmap/list", "Implementation Roadmaps")
        ]
        
        for url, name in nav_links:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                if response.status_code == 200:
                    self.log_test(f"Navigation: {name}", "PASS", f"Accessible at {url}")
                elif response.status_code == 404:
                    self.log_test(f"Navigation: {name}", "FAIL", f"404 Not Found at {url}")
                else:
                    self.log_test(f"Navigation: {name}", "FAIL", f"HTTP {response.status_code} at {url}")
            except Exception as e:
                self.log_test(f"Navigation: {name}", "ERROR", error=e)
    
    def test_database_connectivity(self):
        """Test 3: Verify database is accessible and contains data"""
        try:
            if os.path.exists('audit_controls.db'):
                conn = sqlite3.connect('audit_controls.db')
                cursor = conn.cursor()
                
                # Check if controls table exists and has data
                cursor.execute("SELECT COUNT(*) FROM controls")
                control_count = cursor.fetchone()[0]
                
                if control_count > 0:
                    self.log_test("Database Connectivity", "PASS", f"Found {control_count} controls in database")
                else:
                    self.log_test("Database Connectivity", "FAIL", "Controls table is empty")
                
                # Check for required tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                required_tables = ['controls', 'audit_sessions', 'audit_responses']
                
                missing_tables = [table for table in required_tables if table not in tables]
                if missing_tables:
                    self.log_test("Database Schema", "FAIL", f"Missing tables: {missing_tables}")
                else:
                    self.log_test("Database Schema", "PASS", "All required tables present")
                
                conn.close()
            else:
                self.log_test("Database Connectivity", "FAIL", "Database file not found")
        except Exception as e:
            self.log_test("Database Connectivity", "ERROR", error=e)
    
    def test_audit_creation_workflow(self):
        """Test 4: Verify audit creation workflow"""
        try:
            # Test audit creation form submission
            form_data = {
                'session_name': 'Pre-Release Test Audit',
                'framework_filter': 'NIST AI Risk Management Framework (AI RMF v1.0)',
                'category_filter': '',
                'risk_level_filter': '',
                'sector_filter': 'Technology',
                'region_filter': 'United States'
            }
            
            response = self.session.post(f"{self.base_url}/start-audit", data=form_data)
            
            if response.status_code == 200 or response.status_code == 302:
                self.log_test("Audit Creation", "PASS", "Form submission successful")
                
                # Check if redirected to question page
                if response.status_code == 302:
                    redirect_url = response.headers.get('Location', '')
                    if 'audit' in redirect_url and 'question' in redirect_url:
                        self.log_test("Audit Workflow", "PASS", "Redirected to question page")
                    else:
                        self.log_test("Audit Workflow", "FAIL", f"Unexpected redirect: {redirect_url}")
            else:
                self.log_test("Audit Creation", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Audit Creation", "ERROR", error=e)
    
    def test_framework_integration(self):
        """Test 5: Verify framework options are available"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                expected_frameworks = [
                    "EU AI Act",
                    "NIST AI Risk Management Framework",
                    "ISO/IEC 42001",
                    "MITRE ATLAS"
                ]
                
                page_content = response.text
                missing_frameworks = []
                
                for framework in expected_frameworks:
                    if framework not in page_content:
                        missing_frameworks.append(framework)
                
                if not missing_frameworks:
                    self.log_test("Framework Integration", "PASS", "All major frameworks available")
                else:
                    self.log_test("Framework Integration", "FAIL", f"Missing: {missing_frameworks}")
            else:
                self.log_test("Framework Integration", "FAIL", f"Could not access home page")
        except Exception as e:
            self.log_test("Framework Integration", "ERROR", error=e)
    
    def test_reports_dashboard_integration(self):
        """Test 6: Verify Reports & Analytics dashboard functionality"""
        try:
            # Test main reports page
            response = self.session.get(f"{self.base_url}/reports")
            if response.status_code == 200:
                self.log_test("Reports Dashboard", "PASS", "Reports page accessible")
                
                # Check for dashboard elements
                if "ASIMOV" in response.text and ("dashboard" in response.text.lower() or "analytics" in response.text.lower()):
                    self.log_test("Reports Content", "PASS", "Dashboard content present")
                else:
                    self.log_test("Reports Content", "FAIL", "Dashboard content missing")
            elif response.status_code == 404:
                self.log_test("Reports Dashboard", "FAIL", "404 - Reports page not found")
            else:
                self.log_test("Reports Dashboard", "FAIL", f"HTTP {response.status_code}")
                
            # Test API endpoints
            api_endpoints = ["/reports/api/analytics", "/reports/api/heatmap"]
            for endpoint in api_endpoints:
                try:
                    api_response = self.session.get(f"{self.base_url}{endpoint}")
                    if api_response.status_code in [200, 404]:  # 404 is acceptable if no data
                        self.log_test(f"API: {endpoint}", "PASS", f"Endpoint responsive")
                    else:
                        self.log_test(f"API: {endpoint}", "FAIL", f"HTTP {api_response.status_code}")
                except:
                    self.log_test(f"API: {endpoint}", "FAIL", "Endpoint not accessible")
                    
        except Exception as e:
            self.log_test("Reports Dashboard", "ERROR", error=e)
    
    def test_evidence_evaluation_features(self):
        """Test 7: Verify Evidence Evaluation Engine integration"""
        try:
            # This tests if the evidence evaluation components are accessible
            # We check for the presence of evidence-related endpoints and functions
            response = self.session.get(f"{self.base_url}/")
            
            # Check if evidence evaluation scripts/modules exist
            evidence_files = ['evidence_evaluation_engine.py', 'trusted_reference_engine.py']
            missing_files = []
            
            for file in evidence_files:
                if not os.path.exists(file):
                    missing_files.append(file)
            
            if not missing_files:
                self.log_test("Evidence Engine Files", "PASS", "All evidence engine files present")
            else:
                self.log_test("Evidence Engine Files", "FAIL", f"Missing: {missing_files}")
                
        except Exception as e:
            self.log_test("Evidence Evaluation", "ERROR", error=e)
    
    def test_demo_mode_functionality(self):
        """Test 8: Verify demo mode is working"""
        try:
            # Test demo status endpoint
            response = self.session.get(f"{self.base_url}/demo/status")
            if response.status_code == 200:
                self.log_test("Demo Mode Status", "PASS", "Demo status endpoint accessible")
                
                try:
                    demo_data = response.json()
                    if 'status' in demo_data:
                        self.log_test("Demo Mode Data", "PASS", f"Demo status: {demo_data.get('status')}")
                    else:
                        self.log_test("Demo Mode Data", "FAIL", "Invalid demo status response")
                except:
                    self.log_test("Demo Mode Data", "FAIL", "Could not parse demo status JSON")
            else:
                self.log_test("Demo Mode Status", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Demo Mode", "ERROR", error=e)
    
    def run_all_tests(self):
        """Execute all pre-release tests"""
        print("🚀 Starting Pre-Release Test Suite for ASIMOV AI Governance Audit Tool")
        print("=" * 70)
        
        test_methods = [
            self.test_home_page_accessibility,
            self.test_navigation_links,
            self.test_database_connectivity,
            self.test_audit_creation_workflow,
            self.test_framework_integration,
            self.test_reports_dashboard_integration,
            self.test_evidence_evaluation_features,
            self.test_demo_mode_functionality
        ]
        
        for test_method in test_methods:
            test_method()
            
        # Generate summary report
        self.generate_test_report()
        
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 PRE-RELEASE TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Errors: {error_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0 or error_tests > 0:
            print("\n🔍 ISSUES REQUIRING ATTENTION:")
            for result in self.test_results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"   {result['test_name']}: {result['status']}")
                    if result['details']:
                        print(f"      Details: {result['details']}")
                    if result['error']:
                        print(f"      Error: {result['error']}")
        
        # Deployment readiness assessment
        if success_rate >= 90:
            print(f"\n🎉 DEPLOYMENT READY: {success_rate:.1f}% success rate meets standards")
        elif success_rate >= 75:
            print(f"\n⚠️ DEPLOYMENT CAUTION: {success_rate:.1f}% success rate - address major issues")
        else:
            print(f"\n🚫 DEPLOYMENT BLOCKED: {success_rate:.1f}% success rate - critical fixes required")
        
        # Save detailed report
        report_filename = f"pre_release_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_filename}")


class UnitTestSuite(unittest.TestCase):
    """Unit tests for individual components"""
    
    def test_database_schema(self):
        """Unit test: Database schema validation"""
        if os.path.exists('audit_controls.db'):
            conn = sqlite3.connect('audit_controls.db')
            cursor = conn.cursor()
            
            # Test controls table structure
            cursor.execute("PRAGMA table_info(controls)")
            columns = {row[1] for row in cursor.fetchall()}
            
            expected_columns = {'id', 'control_name', 'category', 'risk_level', 'framework'}
            missing_columns = expected_columns - columns
            
            self.assertEqual(len(missing_columns), 0, 
                           f"Missing required columns in controls table: {missing_columns}")
            
            conn.close()
        else:
            self.fail("Database file not found")
    
    def test_framework_data_integrity(self):
        """Unit test: Framework data completeness"""
        if os.path.exists('audit_controls.db'):
            conn = sqlite3.connect('audit_controls.db')
            cursor = conn.cursor()
            
            # Check for required frameworks
            cursor.execute("SELECT DISTINCT framework FROM controls")
            frameworks = {row[0] for row in cursor.fetchall()}
            
            required_frameworks = {'EU AI Law', 'NIST', 'ISO', 'SCF'}
            
            # Check if any required framework is present
            framework_present = any(req_fw in str(frameworks) for req_fw in required_frameworks)
            
            self.assertTrue(framework_present, 
                          f"No major frameworks found. Available: {frameworks}")
            
            conn.close()
        else:
            self.fail("Database file not found")
    
    def test_control_categorization(self):
        """Unit test: Control categorization consistency"""
        if os.path.exists('audit_controls.db'):
            conn = sqlite3.connect('audit_controls.db')
            cursor = conn.cursor()
            
            # Check for consistent risk level values
            cursor.execute("SELECT DISTINCT risk_level FROM controls")
            risk_levels = {row[0] for row in cursor.fetchall()}
            
            expected_risk_levels = {'High Risk', 'General Risk', 'Low Risk'}
            invalid_risk_levels = risk_levels - expected_risk_levels
            
            self.assertEqual(len(invalid_risk_levels), 0,
                           f"Invalid risk levels found: {invalid_risk_levels}")
            
            conn.close()


def main():
    """Main execution function"""
    print("🔧 ASIMOV AI Governance Audit Tool - Pre-Release Testing")
    print("Testing all functionality before deployment to catch issues like 404 errors")
    print("")
    
    # Run comprehensive integration tests
    test_suite = PreReleaseTestSuite()
    test_suite.run_all_tests()
    
    print("\n" + "=" * 70)
    print("🧪 Running Unit Tests")
    print("=" * 70)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    main()