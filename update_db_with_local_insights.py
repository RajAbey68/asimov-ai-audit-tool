import sqlite3
import time

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
cursor.execute("SELECT id, control_name, description, category, framework, risk_level FROM controls WHERE life_wise_prompt IS NULL OR life_wise_prompt = ''")
rows = cursor.fetchall()

print(f"🔍 Found {len(rows)} controls needing insights...")

# Create templates based on category and risk level
def generate_insight_by_category(name, category, risk_level, framework):
    """Generate a suitable insight based on control category"""
    
    # Default insight for any control
    default_insight = f"Consider how this control affects your AI system's overall governance posture. What documentation do you have that demonstrates compliance?"
    
    # Category-based insights
    category_insights = {
        "Defensive Model Strengthening": "Neglecting this control could leave your AI models vulnerable to adversarial attacks or manipulation, potentially resulting in misleading outputs or service disruptions.",
        
        "Explainable AI": "Without proper explainability, AI decisions remain black boxes to users and regulators. This could violate transparency requirements in regulations like the EU AI Act or create trust issues with end users.",
        
        "Data Management": "Poor data management practices can lead to biased models, privacy violations, and regulatory non-compliance. Consider how you're documenting data lineage and quality assurance processes.",
        
        "Risk Assessment": "Inadequate risk assessment may blind you to potential harms until they materialize. Proactively identifying and mitigating risks is central to responsible AI development.",
        
        "Testing": "Insufficient testing of AI systems before deployment can lead to unexpected behaviors, performance degradation, or harmful outputs in production environments.",
        
        "Governance": "Strong governance frameworks provide the foundation for responsible AI. Without them, accountability gaps and inconsistent practices can emerge across your organization.",
        
        "Vendor Management": "Third-party AI components introduce additional risks that require careful oversight. How are you ensuring your vendors maintain the same standards you've established internally?",
        
        "Ethics": "Ethical considerations in AI extend beyond technical performance to societal impact. Have you considered how this control addresses potential harms to different stakeholder groups?"
    }
    
    # Risk level adjustments
    risk_prefix = ""
    if risk_level and "high" in risk_level.lower():
        risk_prefix = "As a high-risk control, failure here could have significant regulatory or reputational consequences. "
    
    # Framework references
    framework_suffix = ""
    if framework:
        if "EU AI" in framework:
            framework_suffix = " This aligns with EU AI Act requirements for high-risk systems."
        elif "NIST" in framework:
            framework_suffix = " This aligns with NIST AI Risk Management Framework guidelines."
        elif "ISO" in framework:
            framework_suffix = " This relates to ISO/IEC standards for AI systems."
    
    # Get the appropriate category insight or default
    insight = category_insights.get(category, default_insight)
    
    # Combine elements
    return f"{risk_prefix}{insight}{framework_suffix}"

for idx, (control_id, name, description, category, framework, risk_level) in enumerate(rows):
    try:
        # Generate insight based on metadata
        insight = generate_insight_by_category(name, category, risk_level, framework)
        
        # Save the insight to the DB
        cursor.execute("UPDATE controls SET life_wise_prompt = ? WHERE id = ?", (insight, control_id))
        conn.commit()
        
        print(f"✅ [{idx+1}/{len(rows)}] Insight added to: {name[:50]}...")
        
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