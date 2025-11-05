"""
Enhanced Insight Engine for ASIMOV AI Governance Audit Tool

This module combines multiple insight enhancement systems:
1. Temporal Variation - Shows different examples over time
2. Regulatory Timeline - Adds compliance deadline information
3. Evidence Recommendations - Suggests best evidence types

This unified approach creates a more dynamic, informative insight experience.
"""

from temporal_insight_variation import get_time_aware_insight, initialize_variation_tracking
from regulatory_timeline import RegulatoryTimeline
import sqlite3

# Initialize the systems
initialize_variation_tracking()
timeline_system = RegulatoryTimeline()

def get_db_connection():
    """Create a database connection with row factory"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_enhanced_insight(control_id, sector="", region=""):
    """
    Get a comprehensive enhanced insight with temporal variation,
    regulatory timeline information, and evidence recommendations.
    
    Args:
        control_id (int): The database ID of the control
        sector (str, optional): The industry sector context
        region (str, optional): The geographic region context
        
    Returns:
        dict: Enhanced insight with multiple information layers
    """
    # Get control details from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, control_name, category, risk_level FROM controls WHERE id = ?", 
        (control_id,)
    )
    control = cursor.fetchone()
    conn.close()
    
    if not control:
        return {
            "insight": "Control not found in database",
            "timeline_info": "",
            "evidence_types": []
        }
    
    control_name = control['control_name']
    category = control['category']
    # Handle SQLite Row object which doesn't support .get() method
    risk_level = control['risk_level'] if 'risk_level' in control.keys() else 'Medium'
    
    # Get the time-aware insight with variation
    insight_text = get_time_aware_insight(
        control_name=control_name,
        control_id=control_id,
        category=category,
        sector=sector,
        region=region
    )
    
    # Get regulatory timeline information
    timeline_info = timeline_system.get_timeline_message(
        control_name=control_name,
        category=category,
        risk_level=risk_level
    )
    
    # Get evidence recommendations (simplified version)
    evidence_types = get_evidence_recommendations(control_name, category)
    
    # Compile the complete enhanced insight
    return {
        "insight": insight_text,
        "timeline_info": timeline_info,
        "evidence_types": evidence_types
    }

def get_evidence_recommendations(control_name, category):
    """Get recommended evidence types for a control"""
    
    # Basic mapping of categories to evidence types
    category_evidence_map = {
        "Defensive Model Strengthening": [
            "Security test logs",
            "Model performance metrics",
            "Adversarial testing results"
        ],
        "Prompt Engineering Defense": [
            "Input validation documentation",
            "Prompt injection test results",
            "Security control implementation"
        ],
        "Audit and Logging": [
            "System logs",
            "Audit trail documentation",
            "Activity reports"
        ],
        "Model Governance": [
            "Governance committee minutes",
            "Decision documentation",
            "Policy documents"
        ],
        "Security Testing": [
            "Penetration test reports",
            "Vulnerability assessment results",
            "Red team exercises"
        ],
        "Model Documentation": [
            "Model cards",
            "Datasheets",
            "System design documentation"
        ],
        "Data Quality": [
            "Data quality metrics",
            "Data validation reports",
            "Bias assessment results"
        ],
        "Human Oversight": [
            "Human review protocols",
            "Decision override logs",
            "Training materials"
        ],
        "Explainability": [
            "Interpretability documentation",
            "Feature importance analysis",
            "End-user explanation artifacts"
        ],
        "Risk Assessment": [
            "Risk register",
            "Impact assessment documentation",
            "Mitigation planning"
        ]
    }
    
    # Keyword-based overrides for specific controls
    keyword_evidence_map = {
        "documentation": [
            "Policy documentation",
            "Process flow diagrams",
            "Review meeting minutes"
        ],
        "testing": [
            "Test scripts",
            "Test results",
            "Issue tracking logs"
        ],
        "monitoring": [
            "Monitoring dashboard screenshots",
            "Alert configuration",
            "Incident response logs"
        ],
        "training": [
            "Training materials",
            "Attendance records",
            "Knowledge assessment results"
        ]
    }
    
    # Get evidence based on category
    evidence_types = category_evidence_map.get(category, [])
    
    # Add keyword-based evidence if applicable
    control_lower = control_name.lower()
    for keyword, keyword_evidence in keyword_evidence_map.items():
        if keyword in control_lower and len(evidence_types) < 5:  # Limit to 5 evidence types
            # Add keyword evidence types not already included
            for evidence in keyword_evidence:
                if evidence not in evidence_types and len(evidence_types) < 5:
                    evidence_types.append(evidence)
    
    # If no evidence types are found, provide generic ones
    if not evidence_types:
        evidence_types = [
            "Documentation",
            "Test results",
            "Implementation evidence"
        ]
    
    return evidence_types

if __name__ == "__main__":
    # Test the enhanced insight engine with a specific control
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, control_name FROM controls LIMIT 1")
    test_control = cursor.fetchone()
    conn.close()
    
    if test_control:
        print("\n" + "=" * 70)
        print("🧪 ENHANCED INSIGHT ENGINE DEMO")
        print("=" * 70)
        
        control_id = test_control['id']
        control_name = test_control['control_name']
        
        print(f"📊 Control: {control_name} (ID: {control_id})")
        print("-" * 70)
        
        # Get enhanced insight
        enhanced = get_enhanced_insight(
            control_id=control_id,
            sector="Financial Services",
            region="EU"
        )
        
        print(f"✅ INSIGHT:")
        print(enhanced['insight'])
        print("\n✅ REGULATORY TIMELINE:")
        print(enhanced['timeline_info'] if enhanced['timeline_info'] else "No specific regulatory deadlines")
        print("\n✅ RECOMMENDED EVIDENCE TYPES:")
        for evidence in enhanced['evidence_types']:
            print(f"  • {evidence}")
    else:
        print("No controls found in database. Please run the data loader first.")