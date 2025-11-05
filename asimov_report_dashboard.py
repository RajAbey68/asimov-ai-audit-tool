"""
ASIMOV Report Dashboard - Advanced Analytics and Visualization
Creates comprehensive reporting dashboard for AI governance audit results
"""

from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
import io
import base64
from collections import defaultdict, Counter

def get_db_connection():
    """Create database connection with row factory"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def analyze_audit_coverage():
    """Analyze overall audit coverage across all sessions"""
    conn = get_db_connection()
    
    # Get response distribution
    response_distribution = conn.execute("""
        SELECT response, COUNT(*) as count
        FROM audit_responses
        WHERE response IS NOT NULL
        GROUP BY response
        ORDER BY count DESC
    """).fetchall()
    
    # Get framework coverage with improved parsing
    framework_coverage = conn.execute("""
        SELECT 
            CASE 
                WHEN c.framework LIKE '%EU AI%' OR c.framework LIKE '%EU Law%' THEN 'EU AI Act'
                WHEN c.framework LIKE '%NIST%' THEN 'NIST AI RMF'
                WHEN c.framework LIKE '%ISO%' THEN 'ISO/IEC Standards'
                WHEN c.framework LIKE '%SCF%' THEN 'Secure Controls Framework'
                WHEN c.framework LIKE '%MITRE%' THEN 'MITRE ATLAS'
                WHEN c.framework LIKE '%GDPR%' THEN 'GDPR'
                WHEN c.framework LIKE '%OWASP%' THEN 'OWASP'
                ELSE 'Other Frameworks'
            END as framework_name,
            COUNT(ar.id) as responses,
            COUNT(DISTINCT ar.session_id) as sessions,
            COUNT(c.id) as total_controls
        FROM controls c
        LEFT JOIN audit_responses ar ON c.id = ar.control_id
        GROUP BY framework_name
        ORDER BY total_controls DESC
    """).fetchall()
    
    # Get pillar analysis based on category patterns
    pillar_analysis = conn.execute("""
        SELECT 
            CASE 
                WHEN c.category LIKE '%Security%' OR c.category LIKE '%Defense%' OR c.category LIKE '%Attack%' THEN 'S - Security'
                WHEN c.category LIKE '%Data%' OR c.category LIKE '%Privacy%' OR c.category LIKE '%Information%' THEN 'A - Accountability'
                WHEN c.category LIKE '%Monitor%' OR c.category LIKE '%Detect%' OR c.category LIKE '%Audit%' THEN 'M - Monitoring'
                WHEN c.category LIKE '%Transparency%' OR c.category LIKE '%Explainable%' OR c.category LIKE '%Interpret%' THEN 'I - Interpretability'
                WHEN c.category LIKE '%Oversight%' OR c.category LIKE '%Governance%' OR c.category LIKE '%Management%' THEN 'O - Oversight'
                WHEN c.category LIKE '%Validation%' OR c.category LIKE '%Test%' OR c.category LIKE '%Verification%' THEN 'V - Verification'
                ELSE 'General Controls'
            END as pillar,
            COUNT(ar.id) as responses,
            AVG(CASE WHEN ar.response_score IS NOT NULL THEN ar.response_score ELSE 0 END) as avg_score
        FROM controls c
        LEFT JOIN audit_responses ar ON c.id = ar.control_id
        GROUP BY pillar
        ORDER BY responses DESC
    """).fetchall()
    
    conn.close()
    
    return {
        'response_distribution': [dict(row) for row in response_distribution],
        'framework_coverage': [dict(row) for row in framework_coverage],
        'pillar_analysis': [dict(row) for row in pillar_analysis]
    }

def get_session_detailed_report(session_id):
    """Generate detailed report for a specific audit session"""
    conn = get_db_connection()
    
    # Get session information
    session_info = conn.execute("""
        SELECT session_name, framework_filter, category_filter, 
               risk_level_filter, sector_filter, region_filter, session_date
        FROM audit_sessions 
        WHERE session_id = ?
    """, (session_id,)).fetchone()
    
    if not session_info:
        conn.close()
        return None
    
    # Get control responses with full details
    control_responses = conn.execute("""
        SELECT 
            c.id,
            c.name as control_name,
            c.category,
            c.risk_level,
            c.framework,
            c.control_question,
            ar.response_score,
            ar.response,
            ar.comments,
            ar.evidence_notes,
            ar.evidence_date,
            ar.created_date as response_date,
            CASE 
                WHEN c.category LIKE '%Security%' OR c.category LIKE '%Defense%' OR c.category LIKE '%Attack%' THEN 'S - Security'
                WHEN c.category LIKE '%Data%' OR c.category LIKE '%Privacy%' OR c.category LIKE '%Information%' THEN 'A - Accountability'
                WHEN c.category LIKE '%Monitor%' OR c.category LIKE '%Detect%' OR c.category LIKE '%Audit%' THEN 'M - Monitoring'
                WHEN c.category LIKE '%Transparency%' OR c.category LIKE '%Explainable%' OR c.category LIKE '%Interpret%' THEN 'I - Interpretability'
                WHEN c.category LIKE '%Oversight%' OR c.category LIKE '%Governance%' OR c.category LIKE '%Management%' THEN 'O - Oversight'
                WHEN c.category LIKE '%Validation%' OR c.category LIKE '%Test%' OR c.category LIKE '%Verification%' THEN 'V - Verification'
                ELSE 'General Controls'
            END as asimov_pillar
        FROM controls c
        LEFT JOIN audit_responses ar ON c.id = ar.control_id AND ar.session_id = ?
        ORDER BY c.id
    """, (session_id,)).fetchall()
    
    # Calculate statistics
    total_controls = len(control_responses)
    answered_controls = sum(1 for row in control_responses if row['response'] is not None)
    completion_percentage = (answered_controls / total_controls * 100) if total_controls > 0 else 0
    
    # Calculate compliance score (4-5 are compliant)
    scored_responses = [row for row in control_responses if row['response_score'] is not None]
    compliant_responses = sum(1 for row in scored_responses if row['response_score'] >= 4)
    compliance_percentage = (compliant_responses / len(scored_responses) * 100) if scored_responses else 0
    
    # Risk analysis
    high_risk_controls = [row for row in control_responses if row['risk_level'] == 'High Risk']
    high_risk_answered = sum(1 for row in high_risk_controls if row['response'] is not None)
    high_risk_compliant = sum(1 for row in high_risk_controls if row['response_score'] and row['response_score'] >= 4)
    
    # Evidence analysis
    evidence_count = sum(1 for row in control_responses if row['evidence_notes'] or row['evidence_date'])
    
    # Pillar breakdown
    pillar_stats = defaultdict(lambda: {'total': 0, 'answered': 0, 'compliant': 0})
    for row in control_responses:
        pillar = row['asimov_pillar']
        pillar_stats[pillar]['total'] += 1
        if row['response'] is not None:
            pillar_stats[pillar]['answered'] += 1
        if row['response_score'] and row['response_score'] >= 4:
            pillar_stats[pillar]['compliant'] += 1
    
    conn.close()
    
    return {
        'session_info': dict(session_info),
        'control_responses': [dict(row) for row in control_responses],
        'statistics': {
            'total_controls': total_controls,
            'answered_controls': answered_controls,
            'completion_percentage': round(completion_percentage, 1),
            'compliance_percentage': round(compliance_percentage, 1),
            'high_risk_controls': len(high_risk_controls),
            'high_risk_answered': high_risk_answered,
            'high_risk_compliant': high_risk_compliant,
            'evidence_count': evidence_count
        },
        'pillar_stats': dict(pillar_stats)
    }

def generate_risk_heatmap_data():
    """Generate data for ASIMOV pillars vs risk level heatmap"""
    conn = get_db_connection()
    
    heatmap_data = conn.execute("""
        SELECT 
            CASE 
                WHEN c.category LIKE '%Security%' OR c.category LIKE '%Defense%' OR c.category LIKE '%Attack%' THEN 'Security'
                WHEN c.category LIKE '%Data%' OR c.category LIKE '%Privacy%' OR c.category LIKE '%Information%' THEN 'Accountability'
                WHEN c.category LIKE '%Monitor%' OR c.category LIKE '%Detect%' OR c.category LIKE '%Audit%' THEN 'Monitoring'
                WHEN c.category LIKE '%Transparency%' OR c.category LIKE '%Explainable%' OR c.category LIKE '%Interpret%' THEN 'Interpretability'
                WHEN c.category LIKE '%Oversight%' OR c.category LIKE '%Governance%' OR c.category LIKE '%Management%' THEN 'Oversight'
                WHEN c.category LIKE '%Validation%' OR c.category LIKE '%Test%' OR c.category LIKE '%Verification%' THEN 'Verification'
                ELSE 'General'
            END as pillar,
            c.risk_level,
            COUNT(*) as total_controls,
            COUNT(ar.id) as answered_controls,
            AVG(CASE WHEN ar.response_score IS NOT NULL THEN ar.response_score ELSE 0 END) as avg_score,
            SUM(CASE WHEN ar.response_score >= 4 THEN 1 ELSE 0 END) as compliant_controls
        FROM controls c
        LEFT JOIN audit_responses ar ON c.id = ar.control_id
        GROUP BY pillar, c.risk_level
        ORDER BY pillar, c.risk_level
    """).fetchall()
    
    conn.close()
    
    return [dict(row) for row in heatmap_data]

def export_session_csv(session_id):
    """Export session data to CSV format"""
    report_data = get_session_detailed_report(session_id)
    if not report_data:
        return None
    
    # Create DataFrame
    df_data = []
    for control in report_data['control_responses']:
        df_data.append({
            'Control_ID': control['id'],
            'Control_Name': control['control_name'],
            'ASIMOV_Pillar': control['asimov_pillar'],
            'Category': control['category'],
            'Risk_Level': control['risk_level'],
            'Framework': control['framework'],
            'Response_Score': control['response_score'] or '',
            'Response_Status': control['response'] or 'Not Answered',
            'Comments': control['comments'] or '',
            'Evidence_Notes': control['evidence_notes'] or '',
            'Evidence_Date': control['evidence_date'] or '',
            'Response_Date': control['response_date'] or ''
        })
    
    df = pd.DataFrame(df_data)
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    csv_content = output.getvalue()
    output.close()
    
    return csv_content

# Flask routes for the dashboard
def create_report_routes(app):
    """Add report dashboard routes to the Flask app"""
    
    @app.route('/reports')
    @app.route('/report')
    def report_home():
        """ASIMOV Report dashboard home page"""
        # Get all audit sessions
        conn = get_db_connection()
        sessions = conn.execute("""
            SELECT session_id, session_name, session_date, 
                   framework_filter, sector_filter
            FROM audit_sessions 
            ORDER BY session_date DESC
        """).fetchall()
        conn.close()
        
        # Get overall analytics
        analytics = analyze_audit_coverage()
        
        return render_template('report/dashboard.html', 
                             sessions=[dict(s) for s in sessions],
                             analytics=analytics)
    
    @app.route('/report/<session_id>')
    def session_report(session_id):
        """Detailed report for specific audit session"""
        report_data = get_session_detailed_report(session_id)
        
        if not report_data:
            return "Audit session not found", 404
        
        # Get risk heatmap data
        heatmap_data = generate_risk_heatmap_data()
        
        return render_template('report/session_detail.html',
                             session_id=session_id,
                             report=report_data,
                             heatmap_data=heatmap_data)
    
    @app.route('/report/<session_id>/export/csv')
    def export_csv(session_id):
        """Export session report as CSV"""
        csv_content = export_session_csv(session_id)
        
        if not csv_content:
            return "Session not found", 404
        
        # Create response
        output = io.BytesIO()
        output.write(csv_content.encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'asimov_report_{session_id[:8]}.csv'
        )
    
    @app.route('/api/report/analytics')
    def api_analytics():
        """API endpoint for analytics data"""
        return jsonify(analyze_audit_coverage())
    
    @app.route('/api/report/heatmap')
    def api_heatmap():
        """API endpoint for risk heatmap data"""
        return jsonify(generate_risk_heatmap_data())

if __name__ == "__main__":
    # Test the analytics
    analytics = analyze_audit_coverage()
    print("📊 ASIMOV Report Analytics:")
    print(json.dumps(analytics, indent=2))