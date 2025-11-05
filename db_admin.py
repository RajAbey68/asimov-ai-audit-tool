from flask import Flask, render_template, request, redirect, url_for, send_file, flash, Blueprint
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
from db_manager import DatabaseManager

# Create a Blueprint for the database admin interface
db_admin = Blueprint('db_admin', __name__, url_prefix='/db_admin')

# Initialize the database manager
db_manager = DatabaseManager()

@db_admin.route('/')
def index():
    """Database admin home page with overview."""
    # Get database info
    db_info = db_manager.get_database_info()
    
    # Get high-level stats
    controls_count = db_manager.get_table_count('controls')
    responses_count = db_manager.get_table_count('responses')
    sessions_count = db_manager.get_table_count('audit_sessions')
    
    # Get framework coverage
    framework_coverage = db_manager.get_framework_coverage()
    
    # Get category coverage
    category_coverage = db_manager.get_category_coverage()
    
    return render_template('db_admin/index.html', 
                          db_info=db_info,
                          controls_count=controls_count,
                          responses_count=responses_count, 
                          sessions_count=sessions_count,
                          framework_coverage=framework_coverage,
                          category_coverage=category_coverage)

@db_admin.route('/tables/<table_name>')
def view_table(table_name):
    """View contents of a specific table."""
    # Safe list of allowed tables
    allowed_tables = ['controls', 'responses', 'audit_sessions']
    
    if table_name not in allowed_tables:
        flash(f"Table '{table_name}' is not accessible")
        return redirect(url_for('db_admin.index'))
    
    # Get table info
    columns = db_manager.get_table_info(table_name)
    
    # Get records with pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    # Get total records count
    total_records = db_manager.get_table_count(table_name)
    
    # Get paginated records
    query = f"SELECT * FROM {table_name} LIMIT ? OFFSET ?"
    records = db_manager.execute_query(query, (per_page, offset))
    
    # Calculate total pages
    total_pages = (total_records + per_page - 1) // per_page
    
    return render_template('db_admin/table.html',
                          table_name=table_name,
                          columns=columns,
                          records=records,
                          total_records=total_records,
                          page=page,
                          per_page=per_page,
                          total_pages=total_pages)

@db_admin.route('/query', methods=['GET', 'POST'])
def custom_query():
    """Execute custom SQL queries."""
    results = None
    query = ""
    error = None
    
    if request.method == 'POST':
        query = request.form.get('query', '')
        
        # Check for dangerous operations
        dangerous_ops = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'UPDATE', 'INSERT', 'PRAGMA']
        if any(op in query.upper() for op in dangerous_ops):
            error = "For safety, DELETE, DROP, UPDATE and other data-modifying operations are not allowed in this interface"
        else:
            try:
                # Execute the query
                results = db_manager.execute_query(query)
                
                # If we get here, the query was successful
                if not results:
                    results = []
                    
            except Exception as e:
                error = f"Query error: {str(e)}"
    
    return render_template('db_admin/query.html',
                          query=query,
                          results=results,
                          error=error)

@db_admin.route('/export', methods=['GET', 'POST'])
def export_data():
    """Export data from the database."""
    if request.method == 'POST':
        export_type = request.form.get('export_type')
        file_format = request.form.get('file_format', 'csv')
        
        if export_type == 'table':
            table_name = request.form.get('table_name')
            query = f"SELECT * FROM {table_name}"
            
            if file_format == 'csv':
                filename = db_manager.export_to_csv(query, filename=f"{table_name}.csv")
            else:
                filename = db_manager.export_to_json(query, filename=f"{table_name}.json")
                
            if filename:
                return send_file(filename, as_attachment=True)
            else:
                flash("Error exporting data")
                
        elif export_type == 'audit':
            session_id = request.form.get('session_id')
            filename = db_manager.export_audit_report(session_id, file_format)
            
            if filename:
                return send_file(filename, as_attachment=True)
            else:
                flash("Error exporting audit report")
                
        elif export_type == 'custom':
            query = request.form.get('query')
            
            # Check for dangerous operations
            dangerous_ops = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'UPDATE', 'INSERT', 'PRAGMA']
            if any(op in query.upper() for op in dangerous_ops):
                flash("For safety, DELETE, DROP, UPDATE and other data-modifying operations are not allowed")
            else:
                try:
                    if file_format == 'csv':
                        filename = db_manager.export_to_csv(query)
                    else:
                        filename = db_manager.export_to_json(query)
                        
                    if filename:
                        return send_file(filename, as_attachment=True)
                    else:
                        flash("Error exporting data")
                except Exception as e:
                    flash(f"Export error: {str(e)}")
    
    # Get tables for dropdown
    tables = [
        {'name': 'controls', 'count': db_manager.get_table_count('controls')},
        {'name': 'responses', 'count': db_manager.get_table_count('responses')},
        {'name': 'audit_sessions', 'count': db_manager.get_table_count('audit_sessions')}
    ]
    
    # Get audit sessions for dropdown
    sessions_query = "SELECT session_id, session_name, session_date FROM audit_sessions ORDER BY session_date DESC"
    sessions = db_manager.execute_query(sessions_query)
    
    return render_template('db_admin/export.html',
                          tables=tables,
                          sessions=sessions)

@db_admin.route('/analysis')
def analysis():
    """Display analytical reports from the audit data."""
    # Get framework coverage
    framework_coverage = db_manager.get_framework_coverage()
    
    # Get category coverage
    category_coverage = db_manager.get_category_coverage()
    
    # Get risk distribution
    risk_distribution = db_manager.get_risk_distribution()
    
    # Get list of audit sessions for dropdown
    sessions_query = "SELECT session_id, session_name, session_date FROM audit_sessions ORDER BY session_date DESC"
    sessions = db_manager.execute_query(sessions_query)
    
    return render_template('db_admin/analysis.html',
                          framework_coverage=framework_coverage,
                          category_coverage=category_coverage,
                          risk_distribution=risk_distribution,
                          sessions=sessions)

@db_admin.route('/audit_analysis/<session_id>')
def audit_analysis(session_id):
    """Display detailed analysis for a specific audit."""
    # Get audit stats
    stats = db_manager.get_audit_stats(session_id)
    
    # Get framework compliance
    framework_compliance = db_manager.get_framework_compliance(session_id)
    
    # Get category compliance
    category_compliance = db_manager.get_category_compliance(session_id)
    
    # Get gap analysis (controls scored 2 or less)
    gap_query = """
    SELECT 
        r.control_id, r.response_score, r.reference_text,
        c.control_name, c.category, c.framework, c.description
    FROM responses r
    JOIN controls c ON r.control_id = c.id
    WHERE r.session_id = ? AND r.response_score <= 2
    ORDER BY r.response_score, c.category
    """
    gaps = db_manager.execute_query(gap_query, (session_id,))
    
    return render_template('db_admin/audit_analysis.html',
                          stats=stats,
                          framework_compliance=framework_compliance,
                          category_compliance=category_compliance,
                          gaps=gaps,
                          session_id=session_id)

@db_admin.route('/optimize', methods=['POST'])
def optimize_database():
    """Optimize the database by vacuuming."""
    success = db_manager.vacuum_database()
    
    if success:
        flash("Database successfully optimized")
    else:
        flash("Error optimizing database")
        
    return redirect(url_for('db_admin.index'))