"""
Simple launcher for the ASIMOV AI Governance Audit Tool on port 5001
"""
from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)