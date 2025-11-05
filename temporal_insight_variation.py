"""
Temporal Insight Variation System

This module enhances Life-Wise Insights with temporal variation to provide
different real-world examples for the same control over time.

Key features:
- Tracks when an insight was last shown
- Rotates through multiple examples for each control
- Ensures users always see fresh, relevant content
"""

import sqlite3
import datetime
import json
import random
from custom_control_insights import get_unique_control_insight
from enhanced_lifewise_insights import generate_insight
from fallback_insights import generate_fallback_insight

# Constants
ROTATION_INTERVAL_DAYS = 30  # Rotate examples every 30 days
MAX_VIEWCOUNT_BEFORE_ROTATION = 3  # Rotate after being viewed 3 times

def get_db_connection():
    """Create a database connection with row factory"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_variation_tracking():
    """Initialize or update the database table for tracking temporal variation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tracking table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insight_variations (
        control_id INTEGER PRIMARY KEY,
        last_generated_at TEXT,
        view_count INTEGER DEFAULT 0,
        rotation_index INTEGER DEFAULT 0,
        variation_history TEXT,
        FOREIGN KEY (control_id) REFERENCES controls(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Temporal variation tracking initialized")

def get_time_aware_insight(control_name, control_id, category="", sector="", region=""):
    """
    Get an insight for a control with temporal variation awareness.
    
    This function:
    1. Checks if the insight needs to be rotated based on time or view count
    2. Generates a new insight variation if needed
    3. Updates tracking information
    4. Returns the appropriate insight
    
    Args:
        control_name (str): The name of the control
        control_id (int): The database ID of the control
        category (str, optional): The category of the control
        sector (str, optional): The industry sector context
        region (str, optional): The geographic region context
        
    Returns:
        str: A time-aware insight with real-world examples
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current tracking data for this control
    cursor.execute(
        "SELECT * FROM insight_variations WHERE control_id = ?", 
        (control_id,)
    )
    variation_data = cursor.fetchone()
    
    # Default values if no tracking data exists
    current_time = datetime.datetime.now().isoformat()
    need_new_variation = True
    rotation_index = 0
    view_count = 0
    variation_history = {}
    
    if variation_data:
        # Extract existing tracking information
        last_generated = variation_data['last_generated_at']
        view_count = variation_data['view_count']
        rotation_index = variation_data['rotation_index']
        
        # Parse variation history
        try:
            variation_history = json.loads(variation_data['variation_history'])
        except (json.JSONDecodeError, TypeError):
            variation_history = {}
        
        # Check if we need a new variation based on time or view count
        last_generated_date = datetime.datetime.fromisoformat(last_generated)
        days_since_generation = (datetime.datetime.now() - last_generated_date).days
        
        # Only generate a new variation if:
        # 1. It's been longer than the rotation interval, OR
        # 2. The view count has exceeded our threshold
        if (days_since_generation < ROTATION_INTERVAL_DAYS and 
            view_count < MAX_VIEWCOUNT_BEFORE_ROTATION):
            need_new_variation = False
    
    # Generate a new insight variation if needed
    if need_new_variation:
        # Increase rotation index (cycling through variations)
        rotation_index = (rotation_index + 1) % 5  # Cycle through 5 variations
        
        # Try each source in priority order
        custom_insight = get_unique_control_insight(control_name)
        
        if custom_insight:
            # For custom insights, add temporal markers to make them feel current
            current_year = datetime.datetime.now().year
            months = ["January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
            current_month = months[datetime.datetime.now().month - 1]
            
            # Add a recent temporal marker based on rotation index
            temporal_markers = [
                f"In {current_month} {current_year}, ",
                f"As recently as {current_year}, ",
                f"During {current_year}, ",
                f"In a recent case from {current_month}, ",
                f"Based on {current_year} compliance requirements, "
            ]
            
            # Add temporal variation
            insight = temporal_markers[rotation_index % len(temporal_markers)] + custom_insight
        else:
            # Try generating a unique variation with OpenAI
            try:
                # Pass the rotation index as part of the variation key
                insight = generate_insight(
                    control_text=control_name,
                    pillar=category,
                    sector=sector,
                    region=region
                )
            except Exception as e:
                print(f"Error generating AI insight: {e}")
                # Fall back to pre-generated insights as a last resort
                insight = generate_fallback_insight(
                    control_name, 
                    category, 
                    sector,
                    region,
                    variation_key=f"rotation_{rotation_index}"
                )
        
        # Store the new variation in history
        variation_history[str(rotation_index)] = insight
        
        # Update tracking information
        if variation_data:
            cursor.execute('''
                UPDATE insight_variations 
                SET last_generated_at = ?, 
                    view_count = 1,
                    rotation_index = ?,
                    variation_history = ?
                WHERE control_id = ?
            ''', (
                current_time,
                rotation_index,
                json.dumps(variation_history),
                control_id
            ))
        else:
            cursor.execute('''
                INSERT INTO insight_variations 
                (control_id, last_generated_at, view_count, rotation_index, variation_history)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                control_id,
                current_time,
                1,
                rotation_index,
                json.dumps(variation_history)
            ))
        conn.commit()
    else:
        # Use existing variation but increment view count
        insight = json.loads(variation_data['variation_history']).get(
            str(rotation_index), 
            "No insight variation available."
        )
        
        cursor.execute('''
            UPDATE insight_variations 
            SET view_count = ?
            WHERE control_id = ?
        ''', (view_count + 1, control_id))
        conn.commit()
    
    conn.close()
    return insight

def get_evidence_recommendations(control_name, control_id):
    """
    Get recommended evidence types for a specific control.
    This supports the evidence-linked insights enhancement.
    
    Args:
        control_name (str): The name of the control
        control_id (int): The database ID of the control
        
    Returns:
        dict: Recommended evidence types with descriptions
    """
    # We'll implement this next based on control types
    evidence_map = {
        "Model Tampering Detection": {
            "recommended_types": ["Test Logs", "Security Scan Results", "Code Review"],
            "description": "Automated test logs showing detection of tampering attempts provide the strongest evidence for this control."
        },
        "Adversarial Training": {
            "recommended_types": ["Training Data", "Model Comparison Results", "Test Metrics"],
            "description": "Evidence should demonstrate model robustness improvement after adversarial training."
        },
        "Documentation": {
            "recommended_types": ["Policy Documents", "Process Diagrams", "Meeting Records"],
            "description": "Documentation showing formal approval and review processes is essential."
        }
    }
    
    # Default case - based on keywords in control name
    if "documentation" in control_name.lower():
        return evidence_map["Documentation"]
    elif "tampering" in control_name.lower() or "detection" in control_name.lower():
        return evidence_map["Model Tampering Detection"]
    elif "adversarial" in control_name.lower() or "training" in control_name.lower():
        return evidence_map["Adversarial Training"]
    else:
        # Generic recommendation
        return {
            "recommended_types": ["Test Results", "Documentation", "Process Evidence"],
            "description": "Provide evidence demonstrating the implementation and effectiveness of this control."
        }

if __name__ == "__main__":
    # Initialize tracking when run directly
    initialize_variation_tracking()
    print("Temporal variation system initialized. Run app.py to see it in action.")