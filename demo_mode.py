"""
Bulletproof Demo Mode for ASIMOV AI Governance Audit Tool
Ensures stable, reliable presentations without any technical issues
"""

import os
import sqlite3
from datetime import datetime, timedelta
import json

# Demo Mode Configuration
DEMO_MODE = True  # Set to False for full production features

class DemoModeManager:
    def __init__(self):
        self.demo_data_loaded = False
        
    def is_demo_mode(self):
        """Check if we're in demo mode"""
        return DEMO_MODE
        
    def get_demo_insights(self, control_name="", category=""):
        """Return reliable demo insights that always work"""
        insights = {
            'security': "Security controls like this prevent 85% of common AI system vulnerabilities. Leading organizations report significant risk reduction through automated monitoring and regular security assessments.",
            
            'data': "Data governance controls ensure compliance with privacy regulations like GDPR and CCPA. Companies with strong data controls report 60% fewer compliance issues and improved stakeholder trust.",
            
            'monitoring': "Continuous monitoring controls enable proactive risk management. Organizations with comprehensive monitoring detect anomalies 3x faster than reactive approaches, reducing potential impact by 70%.",
            
            'documentation': "Proper documentation controls support audit readiness and knowledge transfer. Well-documented systems reduce implementation time by 50% for new team members and ensure regulatory compliance.",
            
            'training': "Training and awareness controls build organizational AI governance capability. Companies investing in comprehensive training programs see 40% better compliance outcomes across all control areas.",
            
            'default': "This control is critical for AI governance compliance. Organizations implementing robust controls typically see 40% better audit outcomes and stronger regulatory alignment. Best practice: Document all implementation steps and maintain regular review cycles."
        }
        
        # Match control to appropriate insight
        control_lower = control_name.lower()
        category_lower = category.lower()
        
        if any(word in control_lower for word in ['security', 'attack', 'defense', 'robust']):
            return insights['security']
        elif any(word in control_lower for word in ['data', 'privacy', 'information']):
            return insights['data']
        elif any(word in control_lower for word in ['monitor', 'detect', 'anomaly']):
            return insights['monitoring']
        elif any(word in control_lower for word in ['document', 'record', 'report']):
            return insights['documentation']
        elif any(word in control_lower for word in ['train', 'awareness', 'education']):
            return insights['training']
        else:
            return insights['default']
    
    def create_demo_session(self):
        """Create a pre-populated demo session for reliable demonstrations"""
        try:
            conn = sqlite3.connect('audit_controls.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Create demo session
            demo_session_id = "demo-session-2025"
            demo_name = "ASIMOV Demo: Technology Sector AI Governance Audit"
            
            # Check if demo session already exists
            existing = cursor.execute(
                "SELECT session_id FROM audit_sessions WHERE session_id = ?",
                (demo_session_id,)
            ).fetchone()
            
            if not existing:
                cursor.execute("""
                    INSERT INTO audit_sessions 
                    (session_id, session_name, framework_filter, category_filter, risk_level_filter, 
                     sector_filter, region_filter, session_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    demo_session_id,
                    demo_name,
                    "EU AI Law",
                    "All Categories", 
                    "All Risk Levels",
                    "Technology",
                    "United States",
                    datetime.now().isoformat()
                ))
                
                # Add some demo responses for first few questions
                demo_responses = [
                    {
                        'control_id': 1,
                        'response_score': 4,
                        'response': 'Implemented',
                        'comments': 'Comprehensive anomaly detection system deployed using machine learning algorithms.',
                        'evidence_notes': 'System monitors 15 key behavioral patterns with 95% accuracy rate.',
                        'evidence_date': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                    },
                    {
                        'control_id': 2, 
                        'response_score': 3,
                        'response': 'Partial',
                        'comments': 'Adversarial training implemented for core models, expanding to additional systems.',
                        'evidence_notes': 'Monthly adversarial testing conducted with external security firm.',
                        'evidence_date': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
                    },
                    {
                        'control_id': 3,
                        'response_score': 5,
                        'response': 'Fully Compliant',
                        'comments': 'Model ensemble approach successfully reduces attack impact by 80%.',
                        'evidence_notes': 'Ensemble of 5 models with different architectures provides robust defense.',
                        'evidence_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                    }
                ]
                
                for response in demo_responses:
                    cursor.execute("""
                        INSERT INTO audit_responses 
                        (session_id, control_id, response_score, response, comments, evidence_notes, evidence_date, created_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        demo_session_id,
                        response['control_id'],
                        response['response_score'],
                        response['response'],
                        response['comments'],
                        response['evidence_notes'],
                        response['evidence_date'],
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                
            conn.close()
            return demo_session_id
            
        except Exception as e:
            print(f"Demo session creation failed: {e}")
            return None
    
    def get_demo_status_message(self):
        """Return demo mode status message"""
        if DEMO_MODE:
            return {
                'status': 'demo',
                'message': '🎯 Demo Mode Active - Optimized for stable presentations',
                'features_disabled': ['File uploads', 'PDF export', 'External API calls'],
                'demo_session_available': True
            }
        return {'status': 'production'}
    
    def safe_pdf_export_message(self):
        """Return safe message for PDF export in demo mode"""
        return {
            'success': False,
            'demo_mode': True,
            'message': 'PDF export is disabled in demo mode to ensure presentation stability. In production, this feature generates comprehensive audit reports.'
        }
    
    def safe_file_upload_message(self):
        """Return safe message for file uploads in demo mode"""
        return {
            'success': False,
            'demo_mode': True,
            'message': 'File uploads are disabled in demo mode for security during presentations. In production, users can upload evidence documents, screenshots, and compliance artifacts.'
        }

# Global demo manager instance
demo_manager = DemoModeManager()

def is_demo_mode():
    """Quick check for demo mode"""
    return demo_manager.is_demo_mode()

def get_safe_insight(control_name="", category=""):
    """Get a safe, reliable insight for demos"""
    if is_demo_mode():
        return demo_manager.get_demo_insights(control_name, category)
    else:
        # In production, use the regular insight generation
        from fallback_insights import generate_fallback_insight
        return generate_fallback_insight(control_name, category)

def create_demo_session():
    """Create demo session if in demo mode"""
    if is_demo_mode():
        return demo_manager.create_demo_session()
    return None