#!/usr/bin/env python3
"""
ASIMOV AI Governance Audit Tool - Deployment Script
This script runs the Flask application for deployment
"""

import os
import sys

# Ensure the database is loaded before starting the app
try:
    # Check if database exists, if not create it
    if not os.path.exists('audit_controls.db'):
        print("Initializing database...")
        import main
        print("Database initialized successfully")
    
    # Start the Flask application
    print("Starting ASIMOV AI Governance Audit Tool...")
    from app import app
    
    # Get port from environment variable (Replit sets this for deployment)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=False)
    
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)