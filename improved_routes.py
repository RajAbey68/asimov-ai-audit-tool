"""
Improved routes for ASIMOV AI Governance Audit Tool
with updated framework filtering support
"""

import datetime
import json
import sqlite3
import uuid
from flask import render_template, request, redirect, url_for, flash

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def question_route(session_id, question_index):
    """Display a specific audit question with improved framework filtering"""
    try:
        question_index = int(question_index)
    except ValueError:
        flash('Invalid question index')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the audit session
    cursor.execute('SELECT * FROM audit_sessions WHERE session_id = ?', (session_id,))
    audit_session = cursor.fetchone()
    
    if not audit_session:
        conn.close()
        flash('Audit session not found')
        return redirect(url_for('index'))
    
    # Build query for controls based on filters
    query = "SELECT * FROM controls WHERE 1=1"
    params = []
    
    # Improved framework filtering
    if audit_session['framework_filter']:
        # For the Unified Framework, include all controls
        if audit_session['framework_filter'] == "Unified Framework (ASIMOV-AI)":
            # No additional filter needed for unified framework
            pass
        else:
            # Try to use the framework_tag column for better filtering
            try:
                cursor.execute("PRAGMA table_info(controls)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'framework_tag' in columns:
                    # Extract first word of framework name for matching
                    if "EU AI" in audit_session['framework_filter']:
                        tag = "EU AI Act"
                    else:
                        tag = audit_session['framework_filter'].split(' ')[0]
                    
                    query += " AND framework_tag LIKE ?"
                    params.append(f"{tag}%")
                else:
                    # Fall back to the original method
                    query += " AND framework LIKE ?"
                    params.append(f"%{audit_session['framework_filter']}%")
            except Exception as e:
                print(f"Framework filtering error: {e}")
                # In case of error, use the original method
                query += " AND framework LIKE ?"
                params.append(f"%{audit_session['framework_filter']}%")
    
    # Other filters
    if audit_session['category_filter']:
        query += " AND category = ?"
        params.append(audit_session['category_filter'])
    
    if audit_session['risk_level_filter']:
        query += " AND risk_level = ?"
        params.append(audit_session['risk_level_filter'])
    
    # Apply sector filter if it exists
    if 'sector_filter' in audit_session and audit_session['sector_filter']:
        query += " AND (sector = ? OR sector IS NULL)"
        params.append(audit_session['sector_filter'])
    
    query += " ORDER BY id"
    
    cursor.execute(query, params)
    all_controls = cursor.fetchall()
    
    # Get previous answers for the audit
    cursor.execute('''
        SELECT control_id, response, evidence, confidence
        FROM audit_responses
        WHERE session_id = ?
    ''', (session_id,))
    
    responses = {row['control_id']: {
        'response': row['response'],
        'evidence': row['evidence'],
        'confidence': row['confidence']
    } for row in cursor.fetchall()}
    
    # If no controls match the current filters, show a message
    if len(all_controls) == 0:
        conn.close()
        flash('No audit controls found that match your selected filters. Please try different criteria.')
        return redirect(url_for('index'))
    
    # If we're trying to access a question beyond the available questions, redirect to summary
    if question_index >= len(all_controls):
        conn.close()
        return redirect(url_for('summary', session_id=session_id))
    
    # Get the current control
    control = all_controls[question_index]
    
    # Get the response for this control if it exists
    current_response = responses.get(control['id'], {
        'response': '',
        'evidence': '',
        'confidence': 3
    })
    
    # Apply sector and region context if available
    sector = audit_session['sector_filter'] if 'sector_filter' in audit_session else ""
    region = audit_session['region_filter'] if 'region_filter' in audit_session else ""
    
    # Generate a Life-Wise Insight for this control
    try:
        from app import get_sector_specific_insight
        insight = get_sector_specific_insight(
            control['control_name'], 
            control['category'], 
            control['risk_level'],
            sector,
            region
        )
    except Exception as e:
        insight = f"Error generating insight: {str(e)}"
    
    # Calculate progress
    progress = {
        'current': question_index + 1,
        'total': len(all_controls),
        'percentage': int(((question_index + 1) / len(all_controls)) * 100)
    }
    
    conn.close()
    
    return render_template(
        'question.html',
        session_id=session_id,
        question_index=question_index,
        control=control,
        response=current_response,
        progress=progress,
        insight=insight,
        sector=sector,
        region=region
    )