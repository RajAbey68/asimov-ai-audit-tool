#!/usr/bin/env python3
"""
ASIMOV AI Governance Audit Tool - Live Deployment
Forces deployment to use the correct working application
"""

import os
import sys

# Force reload of the working application
if 'app' in sys.modules:
    del sys.modules['app']

from app import app

# Add deployment-specific routes for health check
@app.route('/health')
def health_check():
    return "ASIMOV AI Governance Audit Tool - Running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting ASIMOV AI on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)