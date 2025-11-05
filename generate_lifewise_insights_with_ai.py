import sqlite3
import pandas as pd
import os
import openai
from dotenv import load_dotenv

# Load environment variables if available
load_dotenv()

# Get API key (either from environment variable or user input)
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("Please set your OPENAI_API_KEY environment variable or provide it below")
    api_key = input("Enter your OpenAI API key: ")

# Configure OpenAI
openai.api_key = api_key

# Connect to your existing audit_controls.db
conn = sqlite3.connect("audit_controls.db")
cursor = conn.cursor()

# Read all control names and descriptions
cursor.execute("SELECT id, control_name, description, category, framework FROM controls")
rows = cursor.fetchall()

def generate_ai_insight(name, desc, category, framework):
    """Generate an AI-powered insight for a control"""
    try:
        messages = [
            {"role": "system", "content": "You are an AI governance expert providing practical, real-world insights about AI controls and governance."},
            {"role": "user", "content": f"""
            Create a brief, practical "Life-Wise Insight" for the following AI governance control. 
            Focus on real-world implementation challenges, examples of what can go wrong, and questions an auditor should ask.
            Keep it concise (2-3 sentences), conversational and thought-provoking.
            
            Control Name: {name}
            Description: {desc}
            Category: {category or 'N/A'}
            Framework Reference: {framework or 'Multiple frameworks'}
            """}
        ]
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error generating insight for {name}: {e}")
        return f"Consider how '{name}' applies in real-world settings. Have you documented all your processes around this control?"

print("Generating AI-powered lifewise insights...")
lifewise_data = []

for i, row in enumerate(rows):
    control_id, name, desc, category, framework = row
    
    print(f"Processing control {i+1}/{len(rows)}: {name}")
    
    # Generate AI insight
    insight = generate_ai_insight(name, desc, category, framework)
    
    lifewise_data.append({
        "control_name": name,
        "life_wise_prompt": insight
    })

# Save to Excel
df = pd.DataFrame(lifewise_data)
df.to_excel("lifewise_insights.xlsx", index=False)

conn.close()
print("✅ lifewise_insights.xlsx generated with AI-powered insights for all controls.")