import sqlite3
import json
import openai
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key (either from environment variable or user input)
api_key = os.environ.get("OPENAI_API_KEY")

# Configure OpenAI
openai.api_key = api_key

def generate_enhanced_insight(name, category, risk_level, framework=None):
    """Generate an enhanced AI-powered insight based on the improved formula"""
    
    # If API key is available, use OpenAI to generate insights
    if api_key:
        try:
            prompt = f"""You are a cross-disciplinary AI governance advisor with deep expertise in real-world AI failures, cybersecurity breaches, risk audits, and compliance frameworks like the EU AI Act, GDPR, and NIST RMF.

Given the following control title, category, and risk tier, generate a "Life-Wise Insight": a concise, real-world explanation of why this control matters — especially in applied or regulated environments.

Include:
- A real incident, case study, or threat type (if applicable)
- A regulatory consequence or operational failure mode
- A sentence that helps the assessor understand **the consequences of weak compliance**
- Tone should be professional, advisory, and understandable to both legal and risk leaders

Control Title: "{name}"
Category: {category or 'General'}
Risk Tier: {risk_level or 'General'}
Framework: {framework or 'Multiple frameworks'}

Return only the Life-Wise Insight (2–3 sentences, no headings or bullets).
"""
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error generating enhanced insight for {name}: {e}")
            # Fall back to template-based insights
            return generate_template_insight(name, category, risk_level, framework)
    else:
        # Use template-based insights when API key is not available
        return generate_template_insight(name, category, risk_level, framework)

def generate_template_insight(name, category, risk_level, framework=None):
    """Generate a suitable insight based on templates when API is unavailable"""
    
    # Default insight for any control
    default_insight = f"Consider how {name} affects your AI system's overall governance posture. Inadequate implementation could lead to regulatory non-compliance and potential financial penalties. Organizations that neglect this control may face increased liability if AI-related incidents occur."
    
    # Real-world examples by category
    category_insights = {
        "Defensive Model Strengthening": "In 2018, researchers demonstrated how self-driving car systems could be fooled by placing specific stickers on road signs, causing dangerous misclassifications. Without robust anomaly detection, AI systems remain vulnerable to adversarial attacks that can lead to safety incidents and legal liability. Organizations deploying AI in safety-critical environments face heightened regulatory scrutiny under the EU AI Act if defensive controls are inadequate.",
        
        "Explainable AI": "The GDPR's 'right to explanation' has led to successful legal challenges against opaque AI systems, with some organizations facing fines exceeding €10M. Without sufficient explainability capabilities, AI decisions remain black boxes, making it virtually impossible to detect bias or demonstrate compliance to regulators. Teams that neglect this control often discover too late that their models contain hidden flaws that could have been identified through proper explanation techniques.",
        
        "Data Management": "A major healthcare AI project was abandoned after $62M in development when it was discovered the training data contained systematic biases that made the model unsafe for diverse populations. Poor data management practices not only lead to biased models but also create substantial regulatory exposure under privacy regulations like GDPR and CCPA. Organizations with weak data governance controls frequently discover compliance gaps during regulatory audits, often when it's too costly to remediate.",
        
        "Risk Assessment": "A financial services company faced a class-action lawsuit after its credit scoring AI disproportionately denied services to protected classes, a risk that proper assessment would have identified. Without comprehensive risk assessment, organizations deploy AI systems with unknown vulnerabilities that can manifest in harmful impacts to individuals or groups. Regulators increasingly expect documented risk assessments for high-risk AI systems, with organizations facing potential penalties if they cannot demonstrate due diligence.",
        
        "Testing": "A major tech company faced substantial reputational damage when its image recognition system exhibited racist behavior that comprehensive fairness testing would have caught. Inadequate testing of AI systems before deployment can lead to unexpected behaviors in production environments that harm users and damage trust. Organizations that rush AI deployment without rigorous testing often face costly post-deployment remediation and potential regulatory intervention.",
        
        "Governance": "After multiple AI ethics incidents, a global technology company established a governance board with authority to review high-risk projects, preventing several potential compliance violations. Strong governance frameworks provide the foundation for responsible AI by ensuring consistent oversight and accountability across the organization. Without formal governance structures, organizations often develop inconsistent AI practices that create significant compliance gaps and ethical risks.",
        
        "Vendor Management": "A financial institution was fined after a third-party AI vendor's model was found to violate fair lending regulations, despite the institution's belief that compliance was the vendor's responsibility. Third-party AI components introduce additional risks that require careful oversight, with regulators holding organizations accountable regardless of who developed the technology. Companies without robust vendor management processes often discover too late that their suppliers' AI systems don't meet their own compliance requirements.",
        
        "Ethics": "A healthcare AI system that prioritized patients based on past healthcare spending inadvertently discriminated against certain demographic groups, creating significant ethical concerns and potential legal exposure. Ethical considerations in AI extend beyond technical performance to encompass fairness, transparency, and societal impact across diverse stakeholder groups. Organizations that fail to embed ethics into their AI development lifecycle face increasing regulatory scrutiny and reputational damage when problems inevitably emerge."
    }
    
    # Risk level adjustments
    risk_prefix = ""
    if risk_level and ("high" in risk_level.lower() or "critical" in risk_level.lower()):
        risk_prefix = "As a high-risk control, failure here could have significant regulatory or reputational consequences. "
    
    # Framework references
    framework_suffix = ""
    if framework:
        if "EU AI" in framework:
            framework_suffix = " The EU AI Act specifically requires this control for high-risk AI systems, with potential penalties for non-compliance."
        elif "NIST" in framework:
            framework_suffix = " This aligns with NIST AI Risk Management Framework guidelines for responsible AI deployment."
        elif "ISO" in framework:
            framework_suffix = " This relates to ISO/IEC standards for AI systems, which are increasingly referenced by regulators."
    
    # Get the appropriate category insight or default
    insight = category_insights.get(category, default_insight)
    
    # For the template approach, we'll use the category-based insights without prefix/suffix
    # to keep them more generalizable
    return insight

# Connect to the database
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

# Get all controls
cursor.execute("SELECT id, control_name, description, category, framework, risk_level FROM controls")
rows = cursor.fetchall()

print(f"🔍 Found {len(rows)} controls that need enhanced insights...")

for idx, (control_id, name, description, category, framework, risk_level) in enumerate(rows):
    # Generate enhanced insight
    insight = generate_enhanced_insight(name, category, risk_level, framework)
    
    # Save to database
    cursor.execute("UPDATE controls SET life_wise_prompt = ? WHERE id = ?", (insight, control_id))
    
    # Commit every 10 records to avoid losing progress
    if idx % 10 == 0:
        conn.commit()
        print(f"✅ Processed {idx+1}/{len(rows)} controls...")
    
    # Add a small delay if using API to avoid rate limiting
    if api_key:
        time.sleep(0.5)

# Final commit
conn.commit()
conn.close()

print("\n✅ Enhanced Life-Wise Insights have been generated and saved to the database.")
print("✅ The insights will be displayed in the audit tool interface.")

# Print a sample insight
conn = sqlite3.connect("audit_controls.db")
cursor = conn.cursor()
cursor.execute("SELECT control_name, life_wise_prompt FROM controls WHERE life_wise_prompt IS NOT NULL LIMIT 1")
result = cursor.fetchone()
conn.close()

if result:
    print("\n✅ SAMPLE ENHANCED INSIGHT")
    print("Control:", result[0])
    print("Life-Wise Insight:", result[1])
else:
    print("\n⚠️ No insights found in database.")