"""
Comprehensive Test Suite for ALL ASIMOV AI Governance Audit Tool Functions
Tests every button, menu item, and function to ensure complete functionality
"""

import requests
import time
import json
from urllib.parse import urljoin
import sqlite3

BASE_URL = "http://localhost:5001"

class CompleteSystemTest:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.session_id = None
        
    def log_test(self, category, test_name, status, details=""):
        """Log test result with categorization"""
        result = {
            'category': category,
            'test': test_name,
            'status': status,
            'details': details
        }
        self.results.append(result)
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
        print(f"  {icon} {test_name}: {details}")
        
    def test_navigation_menu(self):
        """Test 1: All navigation menu items"""
        print("\n🧭 Testing Navigation Menu")
        print("-" * 40)
        
        # Test Home link
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200 and "ASIMOV AI Governance" in response.text:
                self.log_test("Navigation", "Home Menu Link", "PASS", "Home page loads")
            else:
                self.log_test("Navigation", "Home Menu Link", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Navigation", "Home Menu Link", "FAIL", f"Error: {str(e)}")
            
        # Test View Previous Audits link
        try:
            response = self.session.get(f"{BASE_URL}/audits")
            if response.status_code == 200:
                self.log_test("Navigation", "View Previous Audits Menu", "PASS", "Audit list loads")
            else:
                self.log_test("Navigation", "View Previous Audits Menu", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Navigation", "View Previous Audits Menu", "FAIL", f"Error: {str(e)}")
            
        # Test Implementation Roadmaps link
        try:
            response = self.session.get(f"{BASE_URL}/roadmap/list")
            if response.status_code == 200:
                self.log_test("Navigation", "Implementation Roadmaps Menu", "PASS", "Roadmap page loads")
            else:
                self.log_test("Navigation", "Implementation Roadmaps Menu", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Navigation", "Implementation Roadmaps Menu", "FAIL", f"Error: {str(e)}")
    
    def test_home_page_functionality(self):
        """Test 2: All home page form elements and buttons"""
        print("\n🏠 Testing Home Page Functionality")
        print("-" * 40)
        
        # Test form elements presence
        try:
            response = self.session.get(f"{BASE_URL}/")
            
            required_elements = [
                ('session_name', 'Audit Name Field'),
                ('framework_filter', 'Framework Filter Dropdown'),
                ('category_filter', 'Category Filter Dropdown'),
                ('risk_level_filter', 'Risk Level Filter Dropdown'),
                ('sector_filter', 'Industry Sector Dropdown'),
                ('region_filter', 'Region Filter Dropdown')
            ]
            
            for element_name, display_name in required_elements:
                if element_name in response.text:
                    self.log_test("Home Page", display_name, "PASS", "Element present")
                else:
                    self.log_test("Home Page", display_name, "FAIL", "Element missing")
                    
        except Exception as e:
            self.log_test("Home Page", "Form Elements Check", "FAIL", f"Error: {str(e)}")
            
        # Test Start Audit button functionality
        try:
            audit_data = {
                'audit_name': f'Complete Test Audit {int(time.time())}',
                'framework_filter': 'All Frameworks',
                'category_filter': 'All Categories',
                'risk_level_filter': 'All Risk Levels',
                'sector_filter': 'Technology',
                'region_filter': 'United States'
            }
            
            response = self.session.post(f"{BASE_URL}/start-audit", data=audit_data)
            
            if response.status_code in [200, 302]:
                # Extract session ID for later tests
                if response.history and '/audit/' in response.url:
                    self.session_id = response.url.split('/audit/')[1].split('/question/')[0]
                    self.log_test("Home Page", "Start Audit Button", "PASS", f"Session created: {self.session_id[:8]}...")
                else:
                    self.log_test("Home Page", "Start Audit Button", "FAIL", "No valid redirect")
            else:
                self.log_test("Home Page", "Start Audit Button", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Home Page", "Start Audit Button", "FAIL", f"Error: {str(e)}")
    
    def test_question_interface_buttons(self):
        """Test 3: All question interface buttons and functions"""
        print("\n❓ Testing Question Interface")
        print("-" * 40)
        
        if not self.session_id:
            self.log_test("Question Interface", "All Tests", "SKIP", "No valid session available")
            return
            
        # Test question page loads
        try:
            response = self.session.get(f"{BASE_URL}/audit/{self.session_id}/question/0")
            if response.status_code == 200:
                self.log_test("Question Interface", "Question Page Load", "PASS", "Page loads successfully")
                
                # Test response buttons presence
                response_elements = [
                    ('response_score', 'Response Score Selector'),
                    ('comments', 'Comments Field'),
                    ('evidence_notes', 'Evidence Notes Field'),
                    ('evidence_date', 'Evidence Date Field')
                ]
                
                for element, name in response_elements:
                    if element in response.text:
                        self.log_test("Question Interface", name, "PASS", "Element present")
                    else:
                        self.log_test("Question Interface", name, "FAIL", "Element missing")
            else:
                self.log_test("Question Interface", "Question Page Load", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Question Interface", "Question Page Load", "FAIL", f"Error: {str(e)}")
            
        # Test question submission
        try:
            submit_data = {
                'response_score': '3',
                'response': 'Partial',
                'comments': 'Test submission for functionality verification',
                'evidence_notes': 'Test evidence notes',
                'evidence_date': '2025-05-25'
            }
            
            response = self.session.post(f"{BASE_URL}/audit/{self.session_id}/question/0/submit", data=submit_data)
            if response.status_code in [200, 302]:
                self.log_test("Question Interface", "Submit Response Button", "PASS", "Response submitted")
            else:
                self.log_test("Question Interface", "Submit Response Button", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Question Interface", "Submit Response Button", "FAIL", f"Error: {str(e)}")
            
        # Test Next Question button (through navigation)
        try:
            response = self.session.get(f"{BASE_URL}/audit/{self.session_id}/question/1")
            if response.status_code == 200:
                self.log_test("Question Interface", "Next Question Navigation", "PASS", "Navigation works")
            else:
                self.log_test("Question Interface", "Next Question Navigation", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Question Interface", "Next Question Navigation", "FAIL", f"Error: {str(e)}")
            
        # Test Previous Question button
        try:
            response = self.session.get(f"{BASE_URL}/audit/{self.session_id}/question/0")
            if response.status_code == 200:
                self.log_test("Question Interface", "Previous Question Navigation", "PASS", "Navigation works")
            else:
                self.log_test("Question Interface", "Previous Question Navigation", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Question Interface", "Previous Question Navigation", "FAIL", f"Error: {str(e)}")
    
    def test_export_functionality(self):
        """Test 4: Export and download functions"""
        print("\n📄 Testing Export Functionality")
        print("-" * 40)
        
        if not self.session_id:
            self.log_test("Export", "All Tests", "SKIP", "No valid session available")
            return
            
        # Test PDF export
        try:
            response = self.session.get(f"{BASE_URL}/audit/{self.session_id}/question/0/export")
            if response.status_code == 200:
                self.log_test("Export", "PDF Export Button", "PASS", f"PDF generated ({len(response.content)} bytes)")
            elif response.status_code == 404:
                self.log_test("Export", "PDF Export Button", "FAIL", "Export endpoint not found")
            else:
                self.log_test("Export", "PDF Export Button", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Export", "PDF Export Button", "FAIL", f"Error: {str(e)}")
    
    def test_summary_functionality(self):
        """Test 5: Summary page and its functions"""
        print("\n📊 Testing Summary Functionality")
        print("-" * 40)
        
        if not self.session_id:
            self.log_test("Summary", "All Tests", "SKIP", "No valid session available")
            return
            
        try:
            response = self.session.get(f"{BASE_URL}/audit/{self.session_id}/summary")
            if response.status_code == 200:
                self.log_test("Summary", "Summary Page Load", "PASS", "Page loads")
                
                # Check for summary elements
                summary_features = [
                    ('completion_percentage', 'Completion Percentage'),
                    ('compliance_percentage', 'Compliance Percentage'),
                    ('summary', 'Summary Content')
                ]
                
                for feature, name in summary_features:
                    if feature in response.text.lower():
                        self.log_test("Summary", name, "PASS", "Feature present")
                    else:
                        self.log_test("Summary", name, "FAIL", "Feature missing")
            else:
                self.log_test("Summary", "Summary Page Load", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Summary", "Summary Page Load", "FAIL", f"Error: {str(e)}")
    
    def test_audit_history_functions(self):
        """Test 6: Audit history and management functions"""
        print("\n📋 Testing Audit History Functions")
        print("-" * 40)
        
        try:
            response = self.session.get(f"{BASE_URL}/audits")
            if response.status_code == 200:
                self.log_test("Audit History", "Audit List Page", "PASS", "Page loads")
                
                if "Previous AI Governance Audits" in response.text:
                    self.log_test("Audit History", "Page Header", "PASS", "Correct header displayed")
                else:
                    self.log_test("Audit History", "Page Header", "FAIL", "Header missing")
                    
                # Check if audit list shows content or empty state
                if "No previous audits" in response.text or "Test Audit" in response.text or "Audit Name" in response.text:
                    self.log_test("Audit History", "Audit List Content", "PASS", "Appropriate content shown")
                else:
                    self.log_test("Audit History", "Audit List Content", "FAIL", "No recognizable content")
            else:
                self.log_test("Audit History", "Audit List Page", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Audit History", "Audit List Page", "FAIL", f"Error: {str(e)}")
    
    def test_roadmap_functionality(self):
        """Test 7: Roadmap management functions"""
        print("\n🗺️ Testing Roadmap Functionality")
        print("-" * 40)
        
        try:
            response = self.session.get(f"{BASE_URL}/roadmap/list")
            if response.status_code == 200:
                self.log_test("Roadmap", "Roadmap List Page", "PASS", "Page loads")
                
                # Check for roadmap features
                if "Implementation Roadmaps" in response.text or "roadmap" in response.text.lower():
                    self.log_test("Roadmap", "Page Content", "PASS", "Roadmap content present")
                else:
                    self.log_test("Roadmap", "Page Content", "FAIL", "No roadmap content")
            else:
                self.log_test("Roadmap", "Roadmap List Page", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Roadmap", "Roadmap List Page", "FAIL", f"Error: {str(e)}")
            
        # Test roadmap creation page
        try:
            response = self.session.get(f"{BASE_URL}/roadmap/create")
            if response.status_code == 200:
                self.log_test("Roadmap", "Create Roadmap Page", "PASS", "Creation page loads")
            else:
                self.log_test("Roadmap", "Create Roadmap Page", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Roadmap", "Create Roadmap Page", "FAIL", f"Error: {str(e)}")
    
    def test_insights_generation(self):
        """Test 8: Life-Wise Insights functionality"""
        print("\n💡 Testing Life-Wise Insights")
        print("-" * 40)
        
        # Test insight generation endpoint
        try:
            insight_data = {
                'control_name': 'Anomaly Detection Techniques',
                'category': 'Defensive Model Strengthening',
                'sector': 'Technology',
                'region': 'United States'
            }
            
            response = self.session.post(f"{BASE_URL}/generate-new-insight", json=insight_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('insight'):
                    self.log_test("Insights", "Generate New Insight", "PASS", f"Insight generated ({len(data['insight'])} chars)")
                else:
                    self.log_test("Insights", "Generate New Insight", "FAIL", "No insight in response")
            else:
                self.log_test("Insights", "Generate New Insight", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Insights", "Generate New Insight", "FAIL", f"Error: {str(e)}")
    
    def test_database_integrity(self):
        """Test 9: Database functionality and integrity"""
        print("\n🗄️ Testing Database Integrity")
        print("-" * 40)
        
        try:
            conn = sqlite3.connect('audit_controls.db')
            cursor = conn.cursor()
            
            # Test controls table
            cursor.execute('SELECT COUNT(*) FROM controls')
            control_count = cursor.fetchone()[0]
            if control_count > 0:
                self.log_test("Database", "Controls Table", "PASS", f"{control_count} controls loaded")
            else:
                self.log_test("Database", "Controls Table", "FAIL", "No controls found")
                
            # Test audit sessions table
            cursor.execute('SELECT COUNT(*) FROM audit_sessions')
            session_count = cursor.fetchone()[0]
            self.log_test("Database", "Audit Sessions Table", "PASS", f"{session_count} sessions in database")
            
            # Test audit responses table
            cursor.execute('SELECT COUNT(*) FROM audit_responses')
            response_count = cursor.fetchone()[0]
            self.log_test("Database", "Audit Responses Table", "PASS", f"{response_count} responses recorded")
            
            conn.close()
            
        except Exception as e:
            self.log_test("Database", "Database Connection", "FAIL", f"Error: {str(e)}")
    
    def run_complete_test_suite(self):
        """Run all tests and generate comprehensive report"""
        print("🚀 COMPLETE ASIMOV AI GOVERNANCE AUDIT TOOL TEST SUITE")
        print("=" * 70)
        print("Testing ALL functions, buttons, and menu items...")
        
        # Run all test categories
        self.test_navigation_menu()
        self.test_home_page_functionality()
        self.test_question_interface_buttons()
        self.test_export_functionality()
        self.test_summary_functionality()
        self.test_audit_history_functions()
        self.test_roadmap_functionality()
        self.test_insights_generation()
        self.test_database_integrity()
        
        # Generate comprehensive report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate final test report with categorized results"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 70)
        
        # Categorize results
        categories = {}
        for result in self.results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
            
            categories[cat]['total'] += 1
            if result['status'] == 'PASS':
                categories[cat]['passed'] += 1
            elif result['status'] == 'FAIL':
                categories[cat]['failed'] += 1
            else:
                categories[cat]['skipped'] += 1
        
        # Print category summaries
        total_tests = len(self.results)
        total_passed = sum(1 for r in self.results if r['status'] == 'PASS')
        total_failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        total_skipped = sum(1 for r in self.results if r['status'] == 'SKIP')
        
        for category, stats in categories.items():
            success_rate = (stats['passed'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"{category:20} | {stats['passed']:2}/{stats['total']:2} passed ({success_rate:5.1f}%)")
        
        print("-" * 70)
        overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        print(f"{'OVERALL':20} | {total_passed:2}/{total_tests:2} passed ({overall_success_rate:5.1f}%)")
        print(f"{'':20} | Failed: {total_failed}, Skipped: {total_skipped}")
        
        # Final assessment
        print("\n" + "=" * 70)
        critical_categories = ['Navigation', 'Home Page', 'Question Interface']
        critical_failures = [r for r in self.results if r['category'] in critical_categories and r['status'] == 'FAIL']
        
        if overall_success_rate >= 90:
            print("🎉 EXCELLENT: System is fully ready for production use!")
        elif overall_success_rate >= 80 and not critical_failures:
            print("✅ GOOD: System is ready for demo with minor issues to address")
        elif overall_success_rate >= 70:
            print("⚠️  ACCEPTABLE: System has core functionality but needs improvement")
        else:
            print("❌ NEEDS WORK: Multiple critical issues require attention")
            
        if critical_failures:
            print(f"🚨 CRITICAL ISSUES in: {[f['test'] for f in critical_failures[:3]]}")
        
        print("=" * 70)
        
        return {
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_failed,
            'skipped': total_skipped,
            'success_rate': overall_success_rate,
            'categories': categories,
            'demo_ready': overall_success_rate >= 80 and not critical_failures
        }

if __name__ == "__main__":
    tester = CompleteSystemTest()
    results = tester.run_complete_test_suite()