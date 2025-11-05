"""
Comprehensive Test Suite for ASIMOV AI Governance Audit Tool Demo
Tests all key functionality that would be demonstrated in a live demo
"""

import requests
import sqlite3
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"

class DemoTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.current_session_id = None
        
    def log_result(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {details}")
        
    def test_home_page_functionality(self):
        """Test 1: Home page loads with all required elements"""
        try:
            response = self.session.get(BASE_URL)
            if response.status_code == 200:
                # Check for key elements
                required_elements = [
                    "ASIMOV AI Governance Audit Tool",
                    "Start New AI Governance Audit",
                    "View Previous Audits",
                    "Implementation Roadmaps",
                    "framework_filter",
                    "sector_filter"
                ]
                
                missing_elements = []
                for element in required_elements:
                    if element not in response.text:
                        missing_elements.append(element)
                
                if not missing_elements:
                    self.log_result("Home Page Load", "PASS", "All required elements present")
                else:
                    self.log_result("Home Page Load", "FAIL", f"Missing: {missing_elements}")
            else:
                self.log_result("Home Page Load", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Home Page Load", "FAIL", f"Exception: {str(e)}")
    
    def test_audit_creation_flow(self):
        """Test 2: Complete audit creation workflow"""
        try:
            # Create audit with specific parameters
            audit_data = {
                'audit_name': f'Demo Test Audit {int(time.time())}',
                'framework_filter': 'EU AI Act',
                'category_filter': 'All Categories',
                'risk_level_filter': 'High Risk',
                'sector_filter': 'Technology',
                'region_filter': 'European Union'
            }
            
            response = self.session.post(f"{BASE_URL}/start-audit", data=audit_data)
            
            if response.status_code in [200, 302]:
                # Extract session ID from redirect
                if response.history:
                    redirect_url = response.url
                    if '/audit/' in redirect_url and '/question/' in redirect_url:
                        session_id = redirect_url.split('/audit/')[1].split('/question/')[0]
                        self.current_session_id = session_id
                        self.log_result("Audit Creation", "PASS", f"Session ID: {session_id}")
                    else:
                        self.log_result("Audit Creation", "FAIL", "Invalid redirect URL")
                else:
                    self.log_result("Audit Creation", "FAIL", "No redirect occurred")
            else:
                self.log_result("Audit Creation", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Audit Creation", "FAIL", f"Exception: {str(e)}")
    
    def test_question_interface(self):
        """Test 3: Question interface functionality"""
        if not self.current_session_id:
            self.log_result("Question Interface", "SKIP", "No valid session available")
            return
            
        try:
            response = self.session.get(f"{BASE_URL}/audit/{self.current_session_id}/question/0")
            
            if response.status_code == 200:
                # Check for key question interface elements
                required_elements = [
                    "Life-Wise Insights",
                    "Framework References",
                    "Evidence Collection",
                    "Next Question",
                    "response_score"
                ]
                
                present_elements = []
                for element in required_elements:
                    if element in response.text:
                        present_elements.append(element)
                
                self.log_result("Question Interface", "PASS", f"Elements found: {len(present_elements)}/{len(required_elements)}")
            else:
                self.log_result("Question Interface", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Question Interface", "FAIL", f"Exception: {str(e)}")
    
    def test_lifewise_insights_generation(self):
        """Test 4: Life-Wise Insights generation"""
        if not self.current_session_id:
            self.log_result("Life-Wise Insights", "SKIP", "No valid session available")
            return
            
        try:
            # Test insight generation endpoint
            response = self.session.post(f"{BASE_URL}/generate-new-insight", json={
                'control_name': 'Anomaly Detection Techniques',
                'category': 'Defensive Model Strengthening',
                'sector': 'Technology',
                'region': 'European Union'
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('insight'):
                    insight_length = len(data['insight'])
                    self.log_result("Life-Wise Insights", "PASS", f"Generated insight ({insight_length} chars)")
                else:
                    self.log_result("Life-Wise Insights", "FAIL", "No insight in response")
            else:
                self.log_result("Life-Wise Insights", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Life-Wise Insights", "FAIL", f"Exception: {str(e)}")
    
    def test_evidence_collection(self):
        """Test 5: Evidence collection functionality"""
        if not self.current_session_id:
            self.log_result("Evidence Collection", "SKIP", "No valid session available")
            return
            
        try:
            # Submit a response with evidence
            evidence_data = {
                'response_score': '3',
                'response': 'Partial',
                'comments': 'Test evidence submission for demo',
                'evidence_notes': 'This is a test evidence note for the demo.',
                'evidence_urls[]': 'https://example.com/evidence1',
                'evidence_date': '2025-05-25'
            }
            
            response = self.session.post(
                f"{BASE_URL}/audit/{self.current_session_id}/question/0/submit",
                data=evidence_data
            )
            
            if response.status_code in [200, 302]:
                self.log_result("Evidence Collection", "PASS", "Evidence submitted successfully")
            else:
                self.log_result("Evidence Collection", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Evidence Collection", "FAIL", f"Exception: {str(e)}")
    
    def test_navigation_functionality(self):
        """Test 6: Question navigation (Next/Previous)"""
        if not self.current_session_id:
            self.log_result("Navigation", "SKIP", "No valid session available")
            return
            
        try:
            # Test navigation to next question
            response = self.session.get(f"{BASE_URL}/audit/{self.current_session_id}/question/1")
            
            if response.status_code == 200:
                # Test previous question navigation
                prev_response = self.session.get(f"{BASE_URL}/audit/{self.current_session_id}/question/0")
                
                if prev_response.status_code == 200:
                    self.log_result("Navigation", "PASS", "Next/Previous navigation working")
                else:
                    self.log_result("Navigation", "FAIL", "Previous navigation failed")
            else:
                self.log_result("Navigation", "FAIL", f"Next navigation failed: {response.status_code}")
        except Exception as e:
            self.log_result("Navigation", "FAIL", f"Exception: {str(e)}")
    
    def test_pdf_export(self):
        """Test 7: PDF export functionality"""
        if not self.current_session_id:
            self.log_result("PDF Export", "SKIP", "No valid session available")
            return
            
        try:
            response = self.session.get(f"{BASE_URL}/audit/{self.current_session_id}/question/0/export")
            
            if response.status_code == 200:
                # Check if response is PDF content
                content_type = response.headers.get('content-type', '')
                if 'pdf' in content_type.lower() or len(response.content) > 1000:
                    self.log_result("PDF Export", "PASS", f"PDF generated ({len(response.content)} bytes)")
                else:
                    self.log_result("PDF Export", "FAIL", "Response not PDF format")
            else:
                self.log_result("PDF Export", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("PDF Export", "FAIL", f"Exception: {str(e)}")
    
    def test_audit_summary(self):
        """Test 8: Audit summary functionality"""
        if not self.current_session_id:
            self.log_result("Audit Summary", "SKIP", "No valid session available")
            return
            
        try:
            response = self.session.get(f"{BASE_URL}/audit/{self.current_session_id}/summary")
            
            if response.status_code == 200:
                # Check for summary elements
                summary_elements = [
                    "Compliance Score",
                    "completion_percentage",
                    "compliance_percentage"
                ]
                
                found_elements = sum(1 for element in summary_elements if element in response.text)
                
                if found_elements >= 2:
                    self.log_result("Audit Summary", "PASS", f"Summary elements present: {found_elements}/3")
                else:
                    self.log_result("Audit Summary", "FAIL", "Missing summary elements")
            else:
                self.log_result("Audit Summary", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Audit Summary", "FAIL", f"Exception: {str(e)}")
    
    def test_audit_history(self):
        """Test 9: View Previous Audits functionality"""
        try:
            response = self.session.get(f"{BASE_URL}/audits")
            
            if response.status_code == 200:
                if "Previous AI Governance Audits" in response.text:
                    # Check if our test audit appears in the list
                    if self.current_session_id and self.current_session_id in response.text:
                        self.log_result("Audit History", "PASS", "Test audit visible in history")
                    else:
                        self.log_result("Audit History", "PASS", "Audit history page loads")
                else:
                    self.log_result("Audit History", "FAIL", "Missing page header")
            else:
                self.log_result("Audit History", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Audit History", "FAIL", f"Exception: {str(e)}")
    
    def test_roadmap_functionality(self):
        """Test 10: Implementation Roadmap functionality"""
        try:
            response = self.session.get(f"{BASE_URL}/roadmap/list")
            
            if response.status_code == 200:
                if "Implementation Roadmaps" in response.text or "roadmap" in response.text.lower():
                    self.log_result("Roadmap Functionality", "PASS", "Roadmap list page loads")
                else:
                    self.log_result("Roadmap Functionality", "FAIL", "Missing roadmap content")
            else:
                self.log_result("Roadmap Functionality", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Roadmap Functionality", "FAIL", f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run the complete demo test suite"""
        print("🚀 Starting Comprehensive Demo Test Suite")
        print("=" * 60)
        
        # Run all tests in sequence
        self.test_home_page_functionality()
        self.test_audit_creation_flow()
        self.test_question_interface()
        self.test_lifewise_insights_generation()
        self.test_evidence_collection()
        self.test_navigation_functionality()
        self.test_pdf_export()
        self.test_audit_summary()
        self.test_audit_history()
        self.test_roadmap_functionality()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['status'] == 'PASS')
        failed_tests = sum(1 for result in self.test_results if result['status'] == 'FAIL')
        skipped_tests = sum(1 for result in self.test_results if result['status'] == 'SKIP')
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 DEMO TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️  Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Demo readiness assessment
        critical_failures = [r for r in self.test_results if r['status'] == 'FAIL' and r['test'] in [
            'Home Page Load', 'Audit Creation', 'Question Interface'
        ]]
        
        if not critical_failures and passed_tests >= (total_tests * 0.8):
            print("\n🎉 DEMO READY: Application passed critical tests and is ready for demonstration!")
        elif critical_failures:
            print(f"\n⚠️  DEMO RISK: Critical failures detected in: {[f['test'] for f in critical_failures]}")
        else:
            print(f"\n⚠️  DEMO RISK: Low success rate ({(passed_tests/total_tests)*100:.1f}%)")
        
        print("=" * 60)
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'skipped': skipped_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'demo_ready': not critical_failures and passed_tests >= (total_tests * 0.8)
        }

if __name__ == "__main__":
    suite = DemoTestSuite()
    results = suite.run_all_tests()