#!/usr/bin/env python3
"""
ASIMOV AI Governance Audit Tool - Deployment Entry Point
This file ensures proper deployment on Replit with the correct application.
"""

# Import the main application from app.py
from app import app

if __name__ == "__main__":
    # Run the application on port 5000 for deployment
    app.run(host="0.0.0.0", port=5000, debug=False)