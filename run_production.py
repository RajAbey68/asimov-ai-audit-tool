#!/usr/bin/env python3
"""
ASIMOV AI Governance Audit Tool - Production Server
Ensures deployment matches the working console application
"""

import os
import sys
from pathlib import Path

# Ensure we're in the correct directory
os.chdir(Path(__file__).parent)

# Set environment for production
os.environ['FLASK_ENV'] = 'production'

# Import and run the exact same application that works in console
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting ASIMOV AI Production Server on port {port}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"💾 Database: {'✅ Found' if os.path.exists('audit_controls.db') else '❌ Missing'}")
    
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)