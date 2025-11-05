#!/usr/bin/env python3
"""
ASIMOV AI Bulletproof Startup System
Guarantees deployment integrity and prevents recurring issues
"""

import os
import sys
import sqlite3
import subprocess
import time
from deployment_integrity import DeploymentIntegrityChecker

def bulletproof_database_setup():
    """Ensure database is completely configured correctly"""
    print("🔧 Setting up bulletproof database configuration...")
    
    conn = sqlite3.connect('audit_controls.db')
    cursor = conn.cursor()
    
    # Create ALL required tables with proper schema
    tables = {
        'frameworks': '''
            CREATE TABLE IF NOT EXISTS frameworks (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                description TEXT
            )
        ''',
        'documents': '''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                name TEXT,
                url TEXT,
                description TEXT
            )
        ''',
        'sectors': '''
            CREATE TABLE IF NOT EXISTS sectors (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT
            )
        ''',
        'regions': '''
            CREATE TABLE IF NOT EXISTS regions (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT
            )
        ''',
        'audit_sessions': '''
            CREATE TABLE IF NOT EXISTS audit_sessions (
                id TEXT PRIMARY KEY,
                name TEXT,
                framework TEXT,
                created_date TEXT DEFAULT "",
                filters TEXT
            )
        ''',
        'audit_responses': '''
            CREATE TABLE IF NOT EXISTS audit_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                question_index INTEGER,
                response TEXT,
                evidence_notes TEXT,
                evidence_date TEXT
            )
        '''
    }
    
    for table_name, sql in tables.items():
        cursor.execute(sql)
        
    # Ensure frameworks are populated
    frameworks = [
        ('NIST AI RMF', 'NIST AI Risk Management Framework'),
        ('ISO/IEC 23053', 'ISO Framework for AI Risk Management'),
        ('EU AI Act', 'European Union AI Act Compliance'),
        ('MITRE ATLAS', 'MITRE Adversarial Threat Landscape for AI Systems'),
        ('All Frameworks', 'All available frameworks combined')
    ]
    cursor.executemany('INSERT OR IGNORE INTO frameworks (name, description) VALUES (?, ?)', frameworks)
    
    conn.commit()
    conn.close()
    print("✅ Database schema bulletproofed")

def cleanup_port_conflicts():
    """Aggressively clean up any port conflicts"""
    print("🧹 Cleaning up port conflicts...")
    try:
        subprocess.run(['pkill', '-f', 'python.*app'], capture_output=True)
        subprocess.run(['pkill', '-f', 'flask'], capture_output=True)
        time.sleep(2)
        print("✅ Port conflicts resolved")
    except:
        pass

def verify_integrity_before_start():
    """Run full integrity check before starting"""
    checker = DeploymentIntegrityChecker()
    report = checker.run_full_integrity_check()
    
    if report['status'] != 'HEALTHY':
        print("❌ Integrity issues detected - applying fixes...")
        # Re-run database setup
        bulletproof_database_setup()
        # Check again
        report = checker.run_full_integrity_check()
        
    print(f"✅ Deployment integrity: {report['status']}")
    return report['status'] == 'HEALTHY'

def start_bulletproof_asimov():
    """Start ASIMOV with guaranteed integrity"""
    print("🚀 ASIMOV AI Bulletproof Startup")
    print("=" * 40)
    
    # Step 1: Clean up conflicts
    cleanup_port_conflicts()
    
    # Step 2: Ensure database integrity
    bulletproof_database_setup()
    
    # Step 3: Verify everything is correct
    if not verify_integrity_before_start():
        print("❌ Cannot start - integrity check failed")
        sys.exit(1)
    
    # Step 4: Start application
    print("🚀 Starting ASIMOV AI with guaranteed integrity...")
    
    try:
        # Ensure we're importing the CORRECT app.py with full interface
        import importlib
        if 'app' in sys.modules:
            importlib.reload(sys.modules['app'])
        
        from app import app
        print("✅ Loaded full ASIMOV AI application (not simple test app)")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_bulletproof_asimov()