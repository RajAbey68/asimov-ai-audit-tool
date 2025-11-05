import os
import json
import sqlite3
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_connection():
    """Create and return a database connection with row factory."""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def generate_real_world_insight(control_name, category, risk_level):
    """
    Generate a real-world insight for a control using OpenAI API
    with specific instructions to include actual incidents and regulations
    """
    try:
        # Create a detailed prompt that asks for real-world examples
        prompt = f"""
        Create a concise and impactful Life-Wise Insight for the AI governance control: '{control_name}' 
        (Category: {category}, Risk Level: {risk_level}).
        
        The insight MUST include:
        1. At least one SPECIFIC real-world incident or case study where this control was lacking (naming actual companies/organizations when applicable)
        2. Concrete consequences that resulted from the failure (legal, financial, ethical, or reputational damage)
        3. Relevant regulatory frameworks that mandate or recommend this control (such as specific EU AI Act articles or NIST recommendations)
        4. The business/practical value of implementing this control properly
        
        Format:
        - 3-5 sentences total
        - Begin with a clear statement of why this control matters
        - Include dates and quantifiable impacts where possible
        - Make the insight accessible to non-technical stakeholders
        
        The insight should read as expert advice from a governance professional, not generic boilerplate text.
        """
        
        # Call OpenAI API for insight generation
        response = client.chat.completions.create(
            model="gpt-4o",  # Using the latest model for best results
            messages=[
                {"role": "system", "content": "You are an AI governance expert specializing in providing concrete, real-world insights about control implementations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        # Extract and return the generated insight
        insight = response.choices[0].message.content.strip()
        
        return insight
    
    except Exception as e:
        print(f"Error generating insight for {control_name}: {e}")
        # Return a fallback insight if API call fails
        return f"{control_name} helps organizations implement responsible AI practices. Without proper {control_name.lower()}, organizations may face regulatory compliance issues and reputational risks. Notable incidents include facial recognition system biases and AI decision-making failures in financial services. This control aligns with EU AI Act transparency requirements and NIST AI Risk Management Framework guidelines."

def update_database_with_insights():
    """
    Update the database with real-world insights for controls that don't have specific examples yet
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all controls
    cursor.execute("SELECT id, control_name, category, risk_level FROM controls")
    controls = cursor.fetchall()
    
    # Prepare for batch update
    update_count = 0
    print(f"Found {len(controls)} controls to potentially update")
    
    # Create life_wise_prompt column if it doesn't exist
    try:
        cursor.execute("SELECT life_wise_prompt FROM controls LIMIT 1")
    except sqlite3.OperationalError:
        print("Adding life_wise_prompt column to controls table")
        cursor.execute("ALTER TABLE controls ADD COLUMN life_wise_prompt TEXT")
    
    # Check existing insights to avoid regenerating good ones
    for control in controls:
        control_id = control['id']
        control_name = control['control_name']
        category = control['category']
        risk_level = control['risk_level']
        
        # Check if control already has a custom insight mentioning real incidents
        cursor.execute("SELECT life_wise_prompt FROM controls WHERE id = ?", (control_id,))
        existing_insight = cursor.fetchone()
        
        existing_text = existing_insight['life_wise_prompt'] if existing_insight and existing_insight['life_wise_prompt'] else ""
        
        # Determine if we need to regenerate this insight
        needs_update = False
        
        # If empty or using generic template (check for common template phrases)
        if (not existing_text or 
            "essential for responsible AI deployment" in existing_text or
            "real-world incidents have demonstrated" in existing_text or
            len(existing_text) < 50):
            needs_update = True
        
        if needs_update:
            print(f"Generating new insight for: {control_name}")
            new_insight = generate_real_world_insight(control_name, category, risk_level)
            
            # Update the database
            cursor.execute(
                "UPDATE controls SET life_wise_prompt = ? WHERE id = ?",
                (new_insight, control_id)
            )
            update_count += 1
            
            # Commit every 10 updates to avoid transaction issues
            if update_count % 10 == 0:
                conn.commit()
                print(f"Progress: {update_count} controls updated")
    
    # Final commit
    conn.commit()
    print(f"Completed: {update_count} controls updated with real-world insights")
    conn.close()

if __name__ == "__main__":
    update_database_with_insights()