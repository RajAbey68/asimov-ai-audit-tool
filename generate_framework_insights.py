"""
Life-Wise Insights Generator
Generates insights based on selected industry sector and region using OpenAI GPT-4
"""

import os
import sqlite3
from openai import OpenAI

# List of approved frameworks we should reference
APPROVED_FRAMEWORKS = [
    "EU AI Act (2023)",
    "GDPR (especially Articles 13–22)",
    "NIST AI Risk Management Framework (AI RMF v1.0, 2023)",
    "ISO/IEC 42001 – AI Management Systems",
    "ISACA AI Audit Toolkit",
    "OWASP Top 10 for LLMs",
    "MITRE ATLAS (Adversarial Threats & Red Teaming for AI)",
    "Microsoft Responsible AI Guidelines & Security Blogs (2023–2024)",
    "SHERPA Project (AI Ethics & Governance for EU)",
    "Ada Lovelace Institute Guidance (UK, 2023–2024)"
]

def get_api_key():
    """Get OpenAI API key from environment variables"""
    api_key = os.environ.get("OPENAI_API_KEY")
    return api_key

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def generate_insight(control_text, selected_sector="", selected_region=""):
    """Generate a Life-Wise Insight using OpenAI API"""
    
    # Use the exact prompt format provided
    prompt = f"""
You are an AI governance advisor.

Generate a Life-Wise Insight for the control:
"{control_text}"

Context:
- Industry Sector: {selected_sector}
- Region: {selected_region}

Tailor your response to the selected sector or region when relevant, using practical examples or regulations (e.g., HIPAA, GDPR, sector-specific AI risks).
"""

    # Get API key
    api_key = get_api_key()
    
    # If API key is not available, return a placeholder message
    if not api_key:
        return f"Life-Wise Insight for {control_text} would be generated here using the OpenAI API. It would be tailored to {selected_sector or 'all sectors'} and {selected_region or 'all regions'}."
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Generate insight using OpenAI
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are an AI governance expert who provides insights based on the following frameworks only: {', '.join(APPROVED_FRAMEWORKS)}. Keep insights concise, practical and reference real incidents or use cases where appropriate."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        
        # Extract insight from response
        insight = response.choices[0].message.content.strip()
        return insight
        
    except Exception as e:
        # Handle any errors gracefully
        return f"Error generating insight: {str(e)}"

def update_insight_in_database(control_id, insight):
    """Update the insight for a control in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the insights column exists, if not create it
    try:
        cursor.execute("SELECT insights FROM controls LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE controls ADD COLUMN insights TEXT")
    
    # Update the insight for this control
    cursor.execute(
        "UPDATE controls SET insights = ? WHERE id = ?", 
        (insight, control_id)
    )
    
    conn.commit()
    conn.close()

def generate_insights_for_all_controls():
    """Generate insights for all controls in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all controls
    cursor.execute("SELECT id, control_name, category, sector FROM controls")
    controls = cursor.fetchall()
    conn.close()
    
    for control in controls:
        control_id = control['id']
        control_text = control['control_name']
        sector = control['sector'] or ""
        
        # Generate insight for this control
        insight = generate_insight(control_text, sector)
        
        # Update the insight in the database
        update_insight_in_database(control_id, insight)
        
    return f"Generated insights for {len(controls)} controls"

if __name__ == "__main__":
    # This can be used to pre-generate all insights
    results = generate_insights_for_all_controls()
    print(results)