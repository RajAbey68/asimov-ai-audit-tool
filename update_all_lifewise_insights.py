import sqlite3
import os
import time
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Get OpenAI API key from environment
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("OPENAI_API_KEY not found in environment variables.")
    api_key = input("Please enter your OpenAI API key: ")

# Configure OpenAI
openai.api_key = api_key

def generate_expert_insight(control_name, category, risk_level, description):
    """Generate an improved Life-Wise Insight using the expert prompt format"""
    
    prompt = f"""You are an AI governance advisor with expertise in cybersecurity, risk management, legal compliance, and regulatory frameworks.

Your task is to generate a Life-Wise Insight for the following AI audit control.

The insight should:
- Be concise (2–3 sentences)
- Reference real-world risks, known incidents, or regulatory expectations
- Explain why this control matters, especially in high-risk, legal, or operational contexts
- Be understandable by legal, compliance, or executive stakeholders

Include:
- A potential consequence of ignoring the control
- Optional references to frameworks like EU AI Act, GDPR, NIST RMF, ISO/IEC 42001, or OECD AI Principles

Use a neutral, advisory tone.

---
Control Title: {control_name}
Category: {category or 'General'}
Risk Tier: {risk_level or 'General'}
Description: {description or control_name}
---

Return only the Life-Wise Insight."""

    try:
        # Call the OpenAI API for the improved insight
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Fallback to a template-based response if API call fails
        return generate_fallback_insight(control_name, category, risk_level)

def generate_fallback_insight(control_name, category, risk_level):
    """Generate a fallback insight when API is not available"""
    
    # Base template for all controls
    template = f"Implementing {control_name} is essential for maintaining AI system integrity and regulatory compliance. "
    
    # Category-specific additions
    category_insights = {
        "Defensive Model Strengthening": "Without robust protections, AI models remain vulnerable to adversarial attacks that can compromise system integrity and user safety. Organizations that deploy AI systems without proper defensive controls may face substantial liability if security incidents occur.",
        
        "Explainable AI": "AI systems lacking explainability create significant compliance and liability risks as regulatory frameworks increasingly require transparency in automated decision-making. Organizations unable to explain their AI's decisions may face regulatory penalties under legislation like the EU AI Act and GDPR.",
        
        "Data Management": "Poor data governance leads to biased models and potential privacy violations that create substantial legal and reputational risks. Organizations must maintain rigorous data quality standards to ensure compliance with regulations like GDPR and avoid discriminatory outcomes.",
        
        "Risk Assessment": "Failure to conduct proper risk assessments leaves organizations blind to potential harms from AI deployment and vulnerable to regulatory penalties. NIST RMF and other governance frameworks explicitly require comprehensive risk assessment for high-risk AI applications.",
    }
    
    # Add category-specific content if available
    if category in category_insights:
        template += category_insights[category]
    else:
        template += "Neglecting this control creates significant governance gaps and potential compliance issues. Regular assessment against established frameworks like NIST RMF helps ensure appropriate safeguards are in place."
    
    # Add risk level context if available
    if risk_level and "high" in risk_level.lower():
        template += " As a high-risk control, extra scrutiny from regulators and stakeholders should be expected."
    
    return template

# Connect to the database
print("Connecting to database...")
conn = sqlite3.connect("audit_controls.db")
cursor = conn.cursor()

# Check if life_wise_prompt column exists
cursor.execute("PRAGMA table_info(controls)")
columns = cursor.fetchall()
has_insight_column = any(col[1] == 'life_wise_prompt' for col in columns)

if not has_insight_column:
    print("Adding life_wise_prompt column to controls table...")
    cursor.execute("ALTER TABLE controls ADD COLUMN life_wise_prompt TEXT")
    conn.commit()

# Get all controls
print("Retrieving controls from database...")
cursor.execute("SELECT id, control_name, category, risk_level, description FROM controls")
all_controls = cursor.fetchall()
total_controls = len(all_controls)

print(f"Found {total_controls} controls to update with improved insights.")
print("Starting update process... (this may take some time)")

# Process controls in batches to show progress
for i, control in enumerate(all_controls):
    control_id, name, category, risk_level, description = control
    
    # Show progress
    if i % 10 == 0 or i == total_controls - 1:
        print(f"Processing control {i+1}/{total_controls}: {name[:50]}...")
    
    # Generate insight
    insight = generate_expert_insight(name, category, risk_level, description)
    
    # Update database
    cursor.execute("UPDATE controls SET life_wise_prompt = ? WHERE id = ?", 
                  (insight, control_id))
    
    # Commit every 10 records
    if i % 10 == 9:
        conn.commit()
        print(f"Committed batch. Progress: {i+1}/{total_controls}")
    
    # Pause between API calls to avoid rate limiting
    if api_key and i < total_controls - 1:
        time.sleep(1)

# Final commit
conn.commit()

# Get a sample of updated insights
print("\nSample of updated insights:")
cursor.execute("""
    SELECT control_name, life_wise_prompt 
    FROM controls 
    WHERE life_wise_prompt IS NOT NULL 
    LIMIT 3
""")
samples = cursor.fetchall()

for name, insight in samples:
    print(f"\nControl: {name}")
    print(f"Life-Wise Insight: {insight}")

conn.close()
print("\n✅ All Life-Wise Insights have been updated with the improved format.")
print("The insights will appear in the audit interface when conducting assessments.")