"""
Roadmap Management System for ASIMOV AI Governance Audit Tool

This module provides functionality for managing implementation roadmaps for AI governance controls.
Features include:
- Creating and managing roadmaps
- Adding controls to implementation backlog
- Planning implementation sprints
- Tracking implementation progress
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import datetime
import uuid
import json

# Create Blueprint
roadmap_bp = Blueprint('roadmap', __name__)

# Database helper function
def get_db_connection():
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if they don't exist
def initialize_roadmap_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create roadmaps table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmaps (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            owner TEXT,
            status TEXT DEFAULT 'Active'
        )
    ''')
    
    # Create sprints table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sprints (
            id TEXT PRIMARY KEY,
            roadmap_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'Planned',
            FOREIGN KEY (roadmap_id) REFERENCES roadmaps (id)
        )
    ''')
    
    # Create backlog items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS backlog_items (
            id TEXT PRIMARY KEY,
            roadmap_id TEXT NOT NULL,
            sprint_id TEXT,
            control_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Backlog',
            priority TEXT DEFAULT 'Medium',
            assigned_to TEXT,
            effort_estimate INTEGER,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (roadmap_id) REFERENCES roadmaps (id),
            FOREIGN KEY (sprint_id) REFERENCES sprints (id),
            FOREIGN KEY (control_id) REFERENCES controls (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize tables at import time
initialize_roadmap_tables()

# Routes
@roadmap_bp.route('/list')
def list_roadmaps():
    """Display a list of all roadmaps"""
    conn = get_db_connection()
    # Handle both old and new database schemas
    try:
        roadmaps = conn.execute('SELECT * FROM roadmaps ORDER BY created_date DESC').fetchall()
    except sqlite3.OperationalError:
        # Fallback for databases without created_date column
        roadmaps = conn.execute('SELECT * FROM roadmaps ORDER BY id').fetchall()
    conn.close()
    
    return render_template('roadmap/list.html', roadmaps=roadmaps)

@roadmap_bp.route('/create', methods=['GET', 'POST'])
def create_roadmap():
    """Create a new roadmap"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        owner = request.form.get('owner')
        
        if not name:
            flash('Roadmap name is required')
            return redirect(url_for('roadmap.create_roadmap'))
        
        roadmap_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO roadmaps (id, name, description, owner) VALUES (?, ?, ?, ?)',
            (roadmap_id, name, description, owner)
        )
        conn.commit()
        conn.close()
        
        flash(f'Roadmap "{name}" created successfully')
        return redirect(url_for('roadmap.view_roadmap', roadmap_id=roadmap_id))
    
    return render_template('roadmap/create.html')

@roadmap_bp.route('/<roadmap_id>')
def view_roadmap(roadmap_id):
    """View a specific roadmap with its sprints and backlog"""
    conn = get_db_connection()
    
    # Get roadmap details
    roadmap = conn.execute('SELECT * FROM roadmaps WHERE id = ?', (roadmap_id,)).fetchone()
    if not roadmap:
        conn.close()
        flash('Roadmap not found')
        return redirect(url_for('roadmap.list_roadmaps'))
    
    # Get sprints for this roadmap
    sprints = conn.execute(
        'SELECT * FROM sprints WHERE roadmap_id = ? ORDER BY start_date ASC',
        (roadmap_id,)
    ).fetchall()
    
    # Get backlog items
    backlog_items = conn.execute('''
        SELECT bi.*, c.control_name 
        FROM backlog_items bi
        LEFT JOIN controls c ON bi.control_id = c.id
        WHERE bi.roadmap_id = ? AND bi.sprint_id IS NULL
        ORDER BY 
            CASE bi.priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
                ELSE 4
            END,
            bi.created_date ASC
    ''', (roadmap_id,)).fetchall()
    
    conn.close()
    
    return render_template(
        'roadmap/view.html',
        roadmap=roadmap,
        sprints=sprints,
        backlog_items=backlog_items
    )

@roadmap_bp.route('/<roadmap_id>/create-sprint', methods=['POST'])
def create_sprint(roadmap_id):
    """Create a new sprint for a roadmap"""
    name = request.form.get('name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    if not name:
        flash('Sprint name is required')
        return redirect(url_for('roadmap.view_roadmap', roadmap_id=roadmap_id))
    
    sprint_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO sprints (id, roadmap_id, name, description, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)',
        (sprint_id, roadmap_id, name, description, start_date, end_date)
    )
    conn.commit()
    conn.close()
    
    flash(f'Sprint "{name}" created successfully')
    return redirect(url_for('roadmap.view_roadmap', roadmap_id=roadmap_id))

@roadmap_bp.route('/<roadmap_id>/sprint/<sprint_id>')
def view_sprint(roadmap_id, sprint_id):
    """View a specific sprint with all its items"""
    conn = get_db_connection()
    
    # Get roadmap details
    roadmap = conn.execute('SELECT * FROM roadmaps WHERE id = ?', (roadmap_id,)).fetchone()
    
    # Get sprint details
    sprint = conn.execute('SELECT * FROM sprints WHERE id = ?', (sprint_id,)).fetchone()
    if not sprint:
        conn.close()
        flash('Sprint not found')
        return redirect(url_for('roadmap.view_roadmap', roadmap_id=roadmap_id))
    
    # Get all backlog items assigned to this sprint
    backlog_items = conn.execute('''
        SELECT bi.*, c.control_name 
        FROM backlog_items bi
        LEFT JOIN controls c ON bi.control_id = c.id
        WHERE bi.sprint_id = ?
        ORDER BY 
            CASE bi.status
                WHEN 'To Do' THEN 1
                WHEN 'In Progress' THEN 2
                WHEN 'Done' THEN 3
                WHEN 'Implemented' THEN 4
                ELSE 5
            END,
            CASE bi.priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
                ELSE 4
            END
    ''', (sprint_id,)).fetchall()
    
    # Get all sprints for this roadmap (for moving items)
    sprints = conn.execute('SELECT * FROM sprints WHERE roadmap_id = ?', (roadmap_id,)).fetchall()
    
    # Get all controls for adding to sprint
    controls = conn.execute('SELECT id, control_name FROM controls').fetchall()
    
    conn.close()
    
    return render_template(
        'roadmap/view_sprint.html',
        roadmap=roadmap,
        sprint=sprint,
        backlog_items=backlog_items,
        sprints=sprints,
        controls=controls
    )

@roadmap_bp.route('/<roadmap_id>/backlog')
def view_backlog(roadmap_id):
    """View the backlog for a roadmap"""
    conn = get_db_connection()
    
    # Get roadmap details
    roadmap = conn.execute('SELECT * FROM roadmaps WHERE id = ?', (roadmap_id,)).fetchone()
    if not roadmap:
        conn.close()
        flash('Roadmap not found')
        return redirect(url_for('roadmap.list_roadmaps'))
    
    # Get all backlog items for this roadmap
    backlog_items = conn.execute('''
        SELECT bi.*, c.control_name 
        FROM backlog_items bi
        LEFT JOIN controls c ON bi.control_id = c.id
        WHERE bi.roadmap_id = ?
        ORDER BY 
            CASE bi.status
                WHEN 'Backlog' THEN 1
                WHEN 'Ready' THEN 2
                WHEN 'In Progress' THEN 3
                WHEN 'Done' THEN 4
                WHEN 'Implemented' THEN 5
                ELSE 6
            END,
            CASE bi.priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                WHEN 'Low' THEN 3
                ELSE 4
            END
    ''', (roadmap_id,)).fetchall()
    
    # Get all sprints for this roadmap (for moving items)
    sprints = conn.execute('SELECT * FROM sprints WHERE roadmap_id = ?', (roadmap_id,)).fetchall()
    
    # Get all controls for adding to backlog
    controls = conn.execute('SELECT id, control_name FROM controls').fetchall()
    
    conn.close()
    
    return render_template(
        'roadmap/backlog.html',
        roadmap=roadmap,
        backlog_items=backlog_items,
        sprints=sprints,
        controls=controls
    )

@roadmap_bp.route('/<roadmap_id>/add-to-backlog', methods=['POST'])
def add_to_backlog(roadmap_id):
    """Add a new item to the roadmap backlog"""
    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority', 'Medium')
    control_id = request.form.get('control_id')
    sprint_id = request.form.get('sprint_id')
    status = request.form.get('status', 'Backlog')
    
    if not title:
        flash('Item title is required')
        return redirect(url_for('roadmap.view_backlog', roadmap_id=roadmap_id))
    
    # If control_id is empty string, set to None
    if control_id == '':
        control_id = None
    
    item_id = str(uuid.uuid4())
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO backlog_items (id, roadmap_id, sprint_id, control_id, title, description, priority, status) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (item_id, roadmap_id, sprint_id, control_id, title, description, priority, status)
    )
    conn.commit()
    conn.close()
    
    if sprint_id:
        flash(f'Item "{title}" added to sprint successfully')
        return redirect(url_for('roadmap.view_sprint', roadmap_id=roadmap_id, sprint_id=sprint_id))
    else:
        flash(f'Item "{title}" added to backlog successfully')
        return redirect(url_for('roadmap.view_backlog', roadmap_id=roadmap_id))

@roadmap_bp.route('/<roadmap_id>/update-backlog', methods=['POST'])
def update_backlog(roadmap_id):
    """Update a backlog item"""
    item_id = request.form.get('item_id')
    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority')
    control_id = request.form.get('control_id')
    assigned_to = request.form.get('assigned_to')
    effort_estimate = request.form.get('effort_estimate')
    sprint_id = request.form.get('sprint_id')
    
    # If control_id is empty string, set to None
    if control_id == '':
        control_id = None
    
    # If effort_estimate is empty string, set to None
    if effort_estimate == '':
        effort_estimate = None
    
    conn = get_db_connection()
    
    conn.execute(
        '''UPDATE backlog_items 
           SET title = ?, description = ?, priority = ?, control_id = ?, 
               assigned_to = ?, effort_estimate = ? 
           WHERE id = ?''',
        (title, description, priority, control_id, assigned_to, effort_estimate, item_id)
    )
    conn.commit()
    
    # Get the current sprint_id for redirection
    current_sprint = conn.execute('SELECT sprint_id FROM backlog_items WHERE id = ?', (item_id,)).fetchone()
    current_sprint_id = current_sprint['sprint_id'] if current_sprint else None
    
    conn.close()
    
    flash('Item updated successfully')
    
    # Redirect based on where the item is
    if sprint_id:
        return redirect(url_for('roadmap.view_sprint', roadmap_id=roadmap_id, sprint_id=sprint_id))
    elif current_sprint_id:
        return redirect(url_for('roadmap.view_sprint', roadmap_id=roadmap_id, sprint_id=current_sprint_id))
    else:
        return redirect(url_for('roadmap.view_backlog', roadmap_id=roadmap_id))

@roadmap_bp.route('/<roadmap_id>/update-sprint/<sprint_id>', methods=['POST'])
def update_sprint(roadmap_id, sprint_id):
    """Update a sprint"""
    status = request.form.get('status')
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE sprints SET status = ? WHERE id = ?',
        (status, sprint_id)
    )
    conn.commit()
    conn.close()
    
    flash('Sprint status updated successfully')
    return redirect(url_for('roadmap.view_sprint', roadmap_id=roadmap_id, sprint_id=sprint_id))

@roadmap_bp.route('/api/roadmaps/<roadmap_id>/backlog/move', methods=['POST'])
def move_backlog_item(roadmap_id):
    """Move a backlog item to a different status or sprint"""
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No JSON data provided"})
        
    # Handle JSON data safely
    item_id = data.get('item_id', None) if data else None
    status = data.get('status', None) if data else None
    sprint_id = data.get('sprint_id', None) if data else None
    
    if not item_id:
        return jsonify({"success": False, "error": "Item ID is required"})
    
    conn = get_db_connection()
    
    # Update the status
    if status:
        conn.execute(
            'UPDATE backlog_items SET status = ? WHERE id = ?',
            (status, item_id)
        )
    
    # Move to a sprint if specified
    if sprint_id:
        conn.execute(
            'UPDATE backlog_items SET sprint_id = ? WHERE id = ?',
            (sprint_id, item_id)
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@roadmap_bp.route('/<roadmap_id>/delete/<item_id>', methods=['POST'])
def delete_backlog_item(roadmap_id, item_id):
    """Delete a backlog item"""
    conn = get_db_connection()
    
    # Get the item information for a better flash message
    item = conn.execute('SELECT title, sprint_id FROM backlog_items WHERE id = ?', (item_id,)).fetchone()
    
    if not item:
        conn.close()
        flash('Item not found')
        return redirect(url_for('roadmap.view_backlog', roadmap_id=roadmap_id))
    
    conn.execute('DELETE FROM backlog_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    flash(f'Item "{item["title"]}" deleted successfully')
    
    # Redirect based on where the item was
    if item['sprint_id']:
        return redirect(url_for('roadmap.view_sprint', roadmap_id=roadmap_id, sprint_id=item['sprint_id']))
    else:
        return redirect(url_for('roadmap.view_backlog', roadmap_id=roadmap_id))

@roadmap_bp.route('/<roadmap_id>/delete-sprint/<sprint_id>', methods=['POST'])
def delete_sprint(roadmap_id, sprint_id):
    """Delete a sprint and move all its items back to backlog"""
    conn = get_db_connection()
    
    # Get sprint name for flash message
    sprint = conn.execute('SELECT name FROM sprints WHERE id = ?', (sprint_id,)).fetchone()
    
    if not sprint:
        conn.close()
        flash('Sprint not found')
        return redirect(url_for('roadmap.view_roadmap', roadmap_id=roadmap_id))
    
    # Move all items back to backlog
    conn.execute(
        'UPDATE backlog_items SET sprint_id = NULL, status = "Backlog" WHERE sprint_id = ?',
        (sprint_id,)
    )
    
    # Delete the sprint
    conn.execute('DELETE FROM sprints WHERE id = ?', (sprint_id,))
    conn.commit()
    conn.close()
    
    flash(f'Sprint "{sprint["name"]}" deleted successfully and all items moved to backlog')
    return redirect(url_for('roadmap.view_roadmap', roadmap_id=roadmap_id))

# Add an item to the roadmap from an audit control
@roadmap_bp.route('/add-from-control/<control_id>', methods=['POST'])
def add_from_control(control_id):
    """Add a control to a roadmap directly from the audit tool"""
    roadmap_id = request.form.get('roadmap_id')
    priority = request.form.get('priority', 'Medium')
    session_id = request.form.get('session_id', '')
    question_index = request.form.get('question_index', '0')
    
    if not roadmap_id:
        flash('No roadmap selected')
        return redirect(url_for('question', session_id=session_id, question_index=question_index))
    
    conn = get_db_connection()
    
    # Get control details
    control = conn.execute('SELECT * FROM controls WHERE id = ?', (control_id,)).fetchone()
    
    if not control:
        conn.close()
        flash('Control not found')
        return redirect(url_for('question', session_id=session_id, question_index=question_index))
    
    # Create a new backlog item
    item_id = str(uuid.uuid4())
    conn.execute(
        'INSERT INTO backlog_items (id, roadmap_id, control_id, title, description, priority, status) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (item_id, roadmap_id, control_id, control['control_name'], 
         f"Implement control: {control['description']}", priority, 'Backlog')
    )
    conn.commit()
    conn.close()
    
    flash(f'Control "{control["control_name"]}" added to implementation roadmap')
    
    # Redirect back to the question
    return redirect(url_for('question', session_id=session_id, question_index=question_index))