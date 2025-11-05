"""
Test Evidence Features

This script tests the enhanced evidence features for the ASIMOV AI Governance Audit Tool:
1. Evidence Notes (free text)
2. URL References (multiple URLs)
3. File Uploads (document evidence)
4. Date Picker (last audit date)

Run with: python test_evidence_features.py
"""

import unittest
import sqlite3
import os
import tempfile
import shutil
import requests
import time
from datetime import datetime
from io import BytesIO

# Base URL for the application (adjust as needed)
BASE_URL = "http://localhost:5000"

class TestEvidenceFeatures(unittest.TestCase):
    """Test case for enhanced evidence features"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a test session
        self.session_id = f"test-evidence-{int(time.time())}"
        self.test_files_dir = tempfile.mkdtemp()
        
        # Create a test database connection
        self.conn = sqlite3.connect('audit_controls.db')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Create a test session in the database
        self.cursor.execute('''
        INSERT OR REPLACE INTO audit_sessions (
            session_id, 
            session_name, 
            framework_filter, 
            framework_pattern,
            category_filter, 
            risk_level_filter, 
            sector_filter, 
            region_filter
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.session_id,
            "Test Evidence Features",
            "EU AI Act (2023)",
            "%EU AI Act%",
            "",
            "",
            "",
            ""
        ))
        self.conn.commit()
        
        # Create a test response with no evidence
        self.cursor.execute('''
        INSERT INTO audit_responses (
            session_id,
            control_id,
            response,
            evidence,
            confidence,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            self.session_id,
            1,  # First control
            "Test response",
            "",
            3,  # Mostly compliant
            datetime.now().isoformat()
        ))
        self.conn.commit()
        self.response_id = self.cursor.lastrowid
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test session from database
        self.cursor.execute("DELETE FROM audit_responses WHERE session_id = ?", (self.session_id,))
        self.cursor.execute("DELETE FROM audit_sessions WHERE session_id = ?", (self.session_id,))
        self.conn.commit()
        self.conn.close()
        
        # Remove test files directory
        shutil.rmtree(self.test_files_dir, ignore_errors=True)
    
    def create_test_file(self, filename, content="Test file content"):
        """Create a test file in the temporary directory"""
        file_path = os.path.join(self.test_files_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path
    
    def test_1_evidence_notes(self):
        """Test 1: Evidence Notes Field"""
        print("\n🧪 TEST 1: Evidence Notes Field")
        
        # Test adding evidence notes
        evidence_notes = "These are test notes for the audit evidence. The control has been verified through documentation review and interviews."
        
        # Update the response with evidence notes
        self.cursor.execute('''
        UPDATE audit_responses
        SET evidence_notes = ?
        WHERE id = ?
        ''', (evidence_notes, self.response_id))
        self.conn.commit()
        
        # Verify notes were saved
        self.cursor.execute("SELECT evidence_notes FROM audit_responses WHERE id = ?", (self.response_id,))
        result = self.cursor.fetchone()
        
        self.assertEqual(result['evidence_notes'], evidence_notes, "Evidence notes not saved correctly")
        print("✅ Evidence notes field works correctly")
    
    def test_2_url_references(self):
        """Test 2: URL References"""
        print("\n🧪 TEST 2: URL References")
        
        # Test adding URL references
        test_urls = [
            "https://example.com/evidence1.pdf",
            "https://testdomain.org/documentation.html",
            "https://evidence-portal.com/audit/12345"
        ]
        
        # Add URLs to the evidence_urls table
        for url in test_urls:
            self.cursor.execute('''
            INSERT INTO evidence_urls (
                response_id,
                url
            ) VALUES (?, ?)
            ''', (self.response_id, url))
        self.conn.commit()
        
        # Verify URLs were saved
        self.cursor.execute("SELECT url FROM evidence_urls WHERE response_id = ?", (self.response_id,))
        results = self.cursor.fetchall()
        saved_urls = [row['url'] for row in results]
        
        for url in test_urls:
            self.assertIn(url, saved_urls, f"URL {url} not found in saved URLs")
        
        print(f"✅ URL references work correctly ({len(saved_urls)} URLs saved)")
    
    def test_3_evidence_date(self):
        """Test 3: Evidence Date Picker"""
        print("\n🧪 TEST 3: Evidence Date Picker")
        
        # Test adding evidence date
        test_date = "2023-09-15"  # ISO format: YYYY-MM-DD
        
        # Update the response with evidence date
        self.cursor.execute('''
        UPDATE audit_responses
        SET evidence_date = ?
        WHERE id = ?
        ''', (test_date, self.response_id))
        self.conn.commit()
        
        # Verify date was saved
        self.cursor.execute("SELECT evidence_date FROM audit_responses WHERE id = ?", (self.response_id,))
        result = self.cursor.fetchone()
        
        self.assertEqual(result['evidence_date'], test_date, "Evidence date not saved correctly")
        print("✅ Evidence date picker works correctly")
    
    def test_4_file_uploads(self):
        """Test 4: File Uploads"""
        print("\n🧪 TEST 4: File Uploads")
        
        # Create test files
        test_files = [
            ("test_doc.pdf", "PDF Test Content"),
            ("evidence.docx", "Word Document Content"),
            ("screenshot.png", "PNG Image Content")
        ]
        
        file_paths = []
        for filename, content in test_files:
            file_path = self.create_test_file(filename, content)
            file_paths.append(file_path)
            
            # Add file reference to database
            self.cursor.execute('''
            INSERT INTO evidence_files (
                response_id,
                filename,
                file_path,
                upload_date
            ) VALUES (?, ?, ?, ?)
            ''', (
                self.response_id, 
                filename, 
                file_path,
                datetime.now().isoformat()
            ))
        self.conn.commit()
        
        # Verify files were saved
        self.cursor.execute("SELECT filename FROM evidence_files WHERE response_id = ?", (self.response_id,))
        results = self.cursor.fetchall()
        saved_filenames = [row['filename'] for row in results]
        
        for filename, _ in test_files:
            self.assertIn(filename, saved_filenames, f"File {filename} not found in saved files")
        
        print(f"✅ File upload references work correctly ({len(saved_filenames)} files saved)")

def run_tests():
    """Run all evidence feature tests"""
    print("\n" + "=" * 60)
    print("🧪 ASIMOV AI Governance Audit Tool - Evidence Features Test Suite")
    print("=" * 60)
    
    # Run the tests
    suite = unittest.TestSuite()
    suite.addTest(TestEvidenceFeatures("test_1_evidence_notes"))
    suite.addTest(TestEvidenceFeatures("test_2_url_references"))
    suite.addTest(TestEvidenceFeatures("test_3_evidence_date"))
    suite.addTest(TestEvidenceFeatures("test_4_file_uploads"))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report results
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {result.testsRun} tests run")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"❌ Errors: {len(result.errors)}")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()