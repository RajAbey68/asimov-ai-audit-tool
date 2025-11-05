import sqlite3
import pandas as pd
import os

# Connect to your existing audit_controls.db
conn = sqlite3.connect("audit_controls.db")
cursor = conn.cursor()

# Read all control names and descriptions
cursor.execute("SELECT id, control_name, description, category, framework FROM controls")
rows = cursor.fetchall()

# Create placeholder insights
lifewise_data = []
for row in rows:
    control_id, name, desc, category, framework = row
    
    # Basic templated insight
    insight = f"Consider how '{name}' applies in real-world settings for {framework or 'multiple frameworks'}. Have you seen risks in {category or 'this domain'}?"

    lifewise_data.append({
        "control_name": name,
        "life_wise_prompt": insight
    })

# Save to Excel
df = pd.DataFrame(lifewise_data)
df.to_excel("lifewise_insights.xlsx", index=False)

conn.close()
print("✅ lifewise_insights.xlsx generated with insights for all controls.")