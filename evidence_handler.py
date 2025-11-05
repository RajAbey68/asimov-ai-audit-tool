"""
Evidence Handler Module

This module handles the processing and storage of enhanced evidence artifacts:
- Notes & Observations
- URL References
- File Uploads
- Evidence Dates
"""

import os
import sqlite3
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename

# Set up evidence file upload directory
UPLOAD_FOLDER = 'evidence_files'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Create a database connection with row factory"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def save_evidence_notes(response_id, notes):
    """Save evidence notes to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE audit_responses SET evidence_notes = ? WHERE id = ?",
            (notes, response_id)
        )
        conn.commit()
        print(f"Saved evidence notes for response {response_id}")
        return True
    except Exception as e:
        print(f"Error saving evidence notes: {e}")
        return False
    finally:
        conn.close()

def save_evidence_date(response_id, evidence_date):
    """Save evidence date to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE audit_responses SET evidence_date = ? WHERE id = ?",
            (evidence_date, response_id)
        )
        conn.commit()
        print(f"Saved evidence date {evidence_date} for response {response_id}")
        return True
    except Exception as e:
        print(f"Error saving evidence date: {e}")
        return False
    finally:
        conn.close()

def save_evidence_urls(response_id, urls):
    """Save evidence URLs to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # First, delete existing URLs for this response
        cursor.execute("DELETE FROM evidence_urls WHERE response_id = ?", (response_id,))
        
        # Insert new URLs
        for url in urls:
            if url.strip():  # Only save non-empty URLs
                cursor.execute(
                    "INSERT INTO evidence_urls (response_id, url) VALUES (?, ?)",
                    (response_id, url.strip())
                )
        
        conn.commit()
        print(f"Saved {len(urls)} evidence URLs for response {response_id}")
        return True
    except Exception as e:
        print(f"Error saving evidence URLs: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def save_evidence_files(response_id, files):
    """Save uploaded evidence files"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                # Create a unique filename to prevent collisions
                original_filename = secure_filename(file.filename)
                file_extension = original_filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                
                # Create session subfolder if it doesn't exist
                session_folder = os.path.join(UPLOAD_FOLDER, f"response_{response_id}")
                if not os.path.exists(session_folder):
                    os.makedirs(session_folder)
                
                file_path = os.path.join(session_folder, unique_filename)
                file.save(file_path)
                
                # Store file reference in database
                cursor.execute(
                    """INSERT INTO evidence_files 
                       (response_id, filename, file_path, upload_date) 
                       VALUES (?, ?, ?, ?)""",
                    (
                        response_id,
                        original_filename,
                        file_path,
                        datetime.now().isoformat()
                    )
                )
                
                saved_files.append({
                    'original_name': original_filename,
                    'path': file_path
                })
        
        conn.commit()
        print(f"Saved {len(saved_files)} evidence files for response {response_id}")
        return saved_files
    except Exception as e:
        print(f"Error saving evidence files: {e}")
        conn.rollback()
        return []
    finally:
        conn.close()

def get_evidence_for_response(response_id):
    """Get all evidence artifacts for a response"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get basic response data
        cursor.execute(
            """SELECT id, evidence_notes, evidence_date 
               FROM audit_responses WHERE id = ?""",
            (response_id,)
        )
        response = cursor.fetchone()
        
        if not response:
            return None
        
        # Get URLs
        cursor.execute(
            "SELECT url FROM evidence_urls WHERE response_id = ?",
            (response_id,)
        )
        urls = [row['url'] for row in cursor.fetchall()]
        
        # Get files
        cursor.execute(
            """SELECT id, filename, file_path, upload_date 
               FROM evidence_files WHERE response_id = ?""",
            (response_id,)
        )
        files = [dict(row) for row in cursor.fetchall()]
        
        # Compile all evidence
        evidence = {
            'response_id': response_id,
            'evidence_notes': response['evidence_notes'],
            'evidence_date': response['evidence_date'],
            'evidence_urls': urls,
            'evidence_files': files
        }
        
        return evidence
    except Exception as e:
        print(f"Error getting evidence: {e}")
        return None
    finally:
        conn.close()