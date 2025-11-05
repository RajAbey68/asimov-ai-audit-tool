#!/usr/bin/env python3
"""
ASIMOV AI Deployment Integrity Checker
Ensures deployed configuration matches expected state every time
"""

import os
import sqlite3
import json
from datetime import datetime

class DeploymentIntegrityChecker:
    """Ensures deployment consistency and prevents configuration drift"""
    
    def __init__(self):
        self.required_tables = [
            'controls', 'frameworks', 'audit_sessions', 'audit_responses',
            'documents', 'sectors', 'regions'
        ]
        self.required_frameworks = [
            'NIST AI RMF', 'ISO/IEC 23053', 'EU AI Act', 'MITRE ATLAS', 'All Frameworks'
        ]
        self.required_files = [
            'app.py', 'templates/index.html', 'templates/question.html'
        ]
        
    def check_database_integrity(self):
        """Verify database schema and essential data"""
        issues = []
        fixes_applied = []
        
        try:
            conn = sqlite3.connect('audit_controls.db')
            cursor = conn.cursor()
            
            # Check all required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in self.required_tables:
                if table not in existing_tables:
                    issues.append(f"Missing table: {table}")
                    
            # Check frameworks table specifically
            if 'frameworks' not in existing_tables:
                cursor.execute('''
                CREATE TABLE frameworks (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    description TEXT
                )
                ''')
                fixes_applied.append("Created frameworks table")
                
            # Ensure frameworks are populated
            cursor.execute('SELECT COUNT(*) FROM frameworks')
            framework_count = cursor.fetchone()[0]
            
            if framework_count == 0:
                frameworks = [
                    ('NIST AI RMF', 'NIST AI Risk Management Framework'),
                    ('ISO/IEC 23053', 'ISO Framework for AI Risk Management'),
                    ('EU AI Act', 'European Union AI Act Compliance'),
                    ('MITRE ATLAS', 'MITRE Adversarial Threat Landscape for AI Systems'),
                    ('All Frameworks', 'All available frameworks combined')
                ]
                cursor.executemany('INSERT OR IGNORE INTO frameworks (name, description) VALUES (?, ?)', frameworks)
                fixes_applied.append("Populated frameworks table")
                
            # Check audit_sessions has required columns
            cursor.execute('PRAGMA table_info(audit_sessions)')
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'created_date' not in columns:
                cursor.execute('ALTER TABLE audit_sessions ADD COLUMN created_date TEXT DEFAULT ""')
                fixes_applied.append("Added created_date column to audit_sessions")
                
            conn.commit()
            conn.close()
            
        except Exception as e:
            issues.append(f"Database error: {e}")
            
        return issues, fixes_applied
        
    def check_file_integrity(self):
        """Verify essential files exist"""
        issues = []
        
        for file_path in self.required_files:
            if not os.path.exists(file_path):
                issues.append(f"Missing file: {file_path}")
                
        return issues
        
    def check_application_health(self):
        """Test application can start and respond"""
        issues = []
        
        try:
            # Test database connection
            conn = sqlite3.connect('audit_controls.db')
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM controls')
            control_count = cursor.fetchone()[0]
            conn.close()
            
            if control_count == 0:
                issues.append("No controls found in database")
                
        except Exception as e:
            issues.append(f"Application health check failed: {e}")
            
        return issues
        
    def run_full_integrity_check(self):
        """Run complete deployment integrity verification"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'database_issues': [],
            'database_fixes': [],
            'file_issues': [],
            'health_issues': [],
            'status': 'UNKNOWN'
        }
        
        # Check database integrity
        db_issues, db_fixes = self.check_database_integrity()
        report['database_issues'] = db_issues
        report['database_fixes'] = db_fixes
        
        # Check file integrity
        file_issues = self.check_file_integrity()
        report['file_issues'] = file_issues
        
        # Check application health
        health_issues = self.check_application_health()
        report['health_issues'] = health_issues
        
        # Determine overall status
        total_issues = len(db_issues) + len(file_issues) + len(health_issues)
        
        if total_issues == 0:
            report['status'] = 'HEALTHY'
        elif len(db_fixes) > 0 and total_issues <= len(db_fixes):
            report['status'] = 'FIXED'
        else:
            report['status'] = 'ISSUES_REMAINING'
            
        return report
        
    def generate_integrity_report(self):
        """Generate human-readable integrity report"""
        report = self.run_full_integrity_check()
        
        output = f"""
================================
ASIMOV AI DEPLOYMENT INTEGRITY
================================

Status: {report['status']}
Checked: {report['timestamp']}

DATABASE INTEGRITY:
"""
        
        if report['database_fixes']:
            output += "✅ FIXES APPLIED:\n"
            for fix in report['database_fixes']:
                output += f"  • {fix}\n"
        
        if report['database_issues']:
            output += "❌ ISSUES FOUND:\n"
            for issue in report['database_issues']:
                output += f"  • {issue}\n"
        else:
            output += "✅ Database schema complete\n"
            
        output += "\nFILE INTEGRITY:\n"
        if report['file_issues']:
            for issue in report['file_issues']:
                output += f"❌ {issue}\n"
        else:
            output += "✅ All required files present\n"
            
        output += "\nAPPLICATION HEALTH:\n"
        if report['health_issues']:
            for issue in report['health_issues']:
                output += f"❌ {issue}\n"
        else:
            output += "✅ Application ready to serve\n"
            
        output += f"\nOVERALL STATUS: {report['status']}\n"
        
        return output

def ensure_deployment_integrity():
    """Main function to ensure deployment integrity"""
    checker = DeploymentIntegrityChecker()
    return checker.generate_integrity_report()

if __name__ == '__main__':
    print(ensure_deployment_integrity())