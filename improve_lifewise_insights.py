import sqlite3
import openai
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    print("WARNING: OPENAI_API_KEY not found in environment variables.")
    openai_api_key = input("Please enter your OpenAI API key: ")

openai.api_key = openai_api_key

def generate_improved_insight(control_name, category, risk_level, description):
    """Generate an improved Life-Wise Insight using the recommended prompt format"""
    
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
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Fallback to a template response if API fails
        return f"Implementing {control_name} is critical for regulatory compliance and operational resilience. Organizations that neglect this control face increased risk exposure and potential regulatory scrutiny. Establishing proper governance around this control aligns with frameworks like NIST RMF and EU AI Act requirements."

# Connect to the database
conn = sqlite3.connect("audit_controls.db")
cursor = conn.cursor()

# Check if any controls exist
cursor.execute("SELECT COUNT(*) FROM controls")
control_count = cursor.fetchone()[0]
print(f"Found {control_count} controls in the database.")

# Get a sample control to update with the improved insight
cursor.execute("SELECT id, control_name, category, risk_level, description FROM controls LIMIT 3")
sample_controls = cursor.fetchall()

for control in sample_controls:
    control_id, name, category, risk_level, description = control
    print(f"\nProcessing control: {name}")
    
    # Generate improved insight
    insight = generate_improved_insight(name, category, risk_level, description)
    
    print(f"Generated insight: {insight}")
    
    # Update the database with the new insight
    cursor.execute("UPDATE controls SET life_wise_prompt = ? WHERE id = ?", (insight, control_id))
    conn.commit()
    print(f"Updated control {control_id} with new insight")
    
    # Pause between API calls to avoid rate limiting
    time.sleep(1)

conn.commit()
conn.close()

print("\n✅ Sample insights have been updated in the database.")
print("To update all controls, modify this script to process all controls instead of just the sample.")
print("Use this as an example script to integrate with your workflow.")