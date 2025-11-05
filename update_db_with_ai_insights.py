import sqlite3
import openai
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to get API key from environment or ask the user
def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY environment variable not found.")
        api_key = input("Please enter your OpenAI API key: ")
    return api_key

# Set up OpenAI API
openai.api_key = get_api_key()

# Connect to your existing database
conn = sqlite3.connect("audit_controls.db")
cursor = conn.cursor()

# Check if life_wise_prompt column exists in controls table
cursor.execute("PRAGMA table_info(controls)")
columns = cursor.fetchall()
has_insight_column = any(col[1] == 'life_wise_prompt' for col in columns)

# Add the column if it doesn't exist
if not has_insight_column:
    print("Adding life_wise_prompt column to controls table...")
    cursor.execute("ALTER TABLE controls ADD COLUMN life_wise_prompt TEXT")
    conn.commit()

# Pull all controls without a life_wise_prompt
cursor.execute("SELECT id, control_name, description, category, framework FROM controls WHERE life_wise_prompt IS NULL OR life_wise_prompt = ''")
rows = cursor.fetchall()

print(f"🔍 Found {len(rows)} controls needing insights...")

for idx, (control_id, name, description, category, framework) in enumerate(rows):
    # 🧠 Prompt for GPT-4
    prompt = f"""
You are a cross-disciplinary AI governance strategist. Your task is to generate a Life-Wise Insight — a short, real-world reflection — for an AI audit control.

Focus on:
- Why this control matters
- What can go wrong if ignored
- Real-world consequences or reference to regulations (e.g., GDPR, EU AI Act, NIST)

Control Name: {name}
Control Description: {description or name}
Category: {category or 'N/A'}
Framework Reference: {framework or 'Multiple frameworks'}

Return only the insight text. No explanation.
"""

    try:
        # Using the updated OpenAI API format
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=120
        )

        insight = response.choices[0].message.content.strip()

        # Save the insight to the DB
        cursor.execute("UPDATE controls SET life_wise_prompt = ? WHERE id = ?", (insight, control_id))
        conn.commit()

        print(f"✅ [{idx+1}/{len(rows)}] Insight added to: {name[:50]}...")

        time.sleep(1.5)  # Respectful pacing for API limits

    except Exception as e:
        print(f"⚠️ Failed on control {control_id}: {e}")
        continue

conn.close()
print("✅ All insights generated and saved directly to the database.")
print("✅ The insights will be displayed automatically in the audit tool.")

# Print a test case
conn = sqlite3.connect("audit_controls.db")
cursor = conn.cursor()
cursor.execute("SELECT control_name, life_wise_prompt FROM controls WHERE life_wise_prompt IS NOT NULL LIMIT 1")
result = cursor.fetchone()
conn.close()

if result:
    print("\n✅ TEST CASE RESULT")
    print("Control:", result[0])
    print("Life-Wise Insight:", result[1])
else:
    print("\n⚠️ No insights found in database yet.")