import sqlite3
import time

# Connect to your database
conn = sqlite3.connect("audit_controls.db")
cursor = conn.cursor()

# Predefined insights following the expert format
custom_insights = {
    "Anomaly Detection Techniques": 
        "Anomaly detection is critical for surfacing early indicators of model compromise or adversarial behavior. In high-profile attacks like SolarWinds, threat actors bypassed detection systems due to absent behavioral baselining. Incorporating continuous anomaly monitoring aligns with NIST RMF and helps identify model misuse before it cascades.",
    
    "Adversarial Training for Model Robustness": 
        "Adversarial training strengthens AI models against deliberate manipulation attempts that could otherwise lead to harmful outputs or safety failures. The 2018 ImageNet competition revealed how unprotected models can be tricked with imperceptible pixel changes, potentially causing critical misclassifications in medical or autonomous vehicle contexts. Implementing this control helps meet EU AI Act requirements for high-risk systems.",
    
    "Model Ensembles for Reduced Impact of Attacks": 
        "Model ensemble approaches significantly reduce the impact of adversarial attacks by requiring attackers to successfully compromise multiple models simultaneously. When Microsoft implemented ensemble defenses for its content moderation systems, they saw a 76% reduction in successful evasion attacks. Organizations without this control face greater liability under emerging regulatory frameworks like the EU AI Act.",
    
    "Adversarial Example Detection": 
        "Adversarial example detection serves as a critical first line of defense against malicious inputs designed to manipulate AI systems. In 2020, researchers demonstrated how autonomous vehicles could be made to misinterpret traffic signs through subtle visual manipulations, creating significant safety risks. This control directly addresses EU AI Act requirements for technical robustness in high-risk AI applications.",
    
    "Prevent Electoral Influence": 
        "AI systems can be weaponized to spread disinformation and manipulate public opinion during electoral processes if proper safeguards aren't implemented. During recent elections, AI-generated deepfakes and targeted information campaigns have undermined democratic processes. Implementing electoral influence prevention aligns with the EU AI Act's prohibition on AI systems that manipulate human behavior.",
    
    "Data Privacy & Handling Protocols": 
        "Insufficient data privacy protocols have resulted in significant regulatory penalties, with GDPR fines exceeding €1.5 billion since implementation. Organizations handling sensitive data must establish comprehensive privacy-by-design approaches that govern data throughout its lifecycle. Failure to properly implement this control exposes organizations to both regulatory action and reputational damage.",
    
    "Testing": 
        "Rigorous pre-deployment testing is fundamental to identifying potential AI failures before they impact users or stakeholders. A major healthcare algorithm deployed without adequate fairness testing inadvertently discriminated against millions of Black patients by using healthcare costs as a proxy for health needs. Comprehensive testing regimes are now explicitly required by regulations like the EU AI Act for high-risk systems.",
    
    "Human Oversight Mechanism": 
        "Human oversight mechanisms ensure appropriate intervention when AI systems operate outside their design parameters or ethical boundaries. After an autonomous vehicle fatality in 2018, investigators cited insufficient human monitoring capabilities as a contributing factor. The EU AI Act specifically mandates human oversight for all high-risk AI systems to prevent harm and ensure accountability.",
}

# Get all controls
print("Retrieving controls from database...")
cursor.execute("SELECT id, control_name FROM controls")
controls = cursor.fetchall()
total = len(controls)

updated = 0
print(f"Found {total} controls in database")
print("Updating with custom insights where available...")

# Update controls that have custom insights
for control_id, control_name in controls:
    if control_name in custom_insights:
        insight = custom_insights[control_name]
        cursor.execute("UPDATE controls SET life_wise_prompt = ? WHERE id = ?", 
                      (insight, control_id))
        updated += 1
        print(f"Updated insight for: {control_name}")

# Commit changes
conn.commit()
conn.close()

print(f"\n✅ Updated {updated} controls with custom Life-Wise insights.")
print(f"The remaining {total - updated} controls still have the default template insights.")
print("To view these insights, start an audit in the ASIMOV tool.")