"""
ASIMOV AI Governance Audit Tool Configuration
Includes Demo Mode for stable live demonstrations
"""

import os

# Demo Mode Configuration
DEMO_MODE = os.environ.get('DEMO_MODE', 'True').lower() == 'true'

# Application Configuration
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'asimov-ai-governance-demo-key')

# Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///audit_controls.db')

# API Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Demo Mode Messages
DEMO_MESSAGES = {
    'pdf_export': 'PDF export is disabled in demo mode to ensure presentation stability.',
    'file_upload': 'File uploads are disabled in demo mode for security during demonstrations.',
    'roadmap_creation': 'Roadmap creation is disabled in demo mode to prevent data changes.',
    'api_insights': 'Using pre-loaded insights in demo mode for reliable demonstrations.'
}

# Demo Insights (fallback for stable demos)
DEMO_INSIGHTS = {
    'default': 'This control is critical for AI governance compliance. Organizations implementing this control typically see 40% better audit outcomes and stronger regulatory alignment. Best practice: Document all implementation steps and maintain regular review cycles.',
    
    'security': 'Security controls like this prevent 85% of common AI system vulnerabilities. Leading organizations invest in automated monitoring and regular penetration testing to maintain robust defenses.',
    
    'data': 'Data governance controls ensure compliance with privacy regulations. Companies with strong data controls report 60% fewer compliance issues and improved stakeholder trust.',
    
    'monitoring': 'Continuous monitoring controls enable proactive risk management. Organizations with comprehensive monitoring detect issues 3x faster than reactive approaches.',
    
    'documentation': 'Proper documentation controls support audit readiness and knowledge transfer. Well-documented systems reduce implementation time by 50% for new team members.'
}