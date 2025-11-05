# lifewise_insight_engine.py

import os
from openai import OpenAI

def generate_lifewise_insight(control_title, risk_level, sector, region, frameworks):
    """
    Generates a high-integrity, context-aware Life-Wise Insight for a given AI governance control.
    This version is formatted specifically for reliable copy-paste into Replit.
    """
    
    # Load your OpenAI API key (ensure this is stored in Replit secrets)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OpenAI API key required for insight generation. Please configure OPENAI_API_KEY."
    
    client = OpenAI(api_key=api_key)

    # Build the system-level instruction to ensure realism and domain accuracy
    system_prompt = f"""
You are a senior AI governance advisor. Your job is to evaluate AI audit controls using real-world references and sector-specific context.

Generate a short, audit-quality Life-Wise Insight for the following control:

- Control: {control_title}
- Risk Level: {risk_level}
- Sector: {sector}
- Region: {region}
- Frameworks: {', '.join(frameworks)}

Rules:
- Limit to under 200 words
- Reference public reports, real regulatory actions, or best practices
- Avoid fabricated events or statistics
- Prioritize insights useful to legal, audit, and governance stakeholders
- Draw from guidance by NIST, ISO, EU AI Act, FCA, ICO, MITRE, OWASP, CDEI, or NHS AI Lab
- Do not reference fictional companies or private case studies
- Highlight governance impact (e.g., audit exposure, policy adaptation, retraining)

Respond with only the rewritten Life-Wise Insight.
    """

    # Call OpenAI API with GPT-4o model (updated API syntax)
    response = client.chat.completions.create(
        model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please generate a Life-Wise Insight for the control '{control_title}'."}
        ],
        temperature=0.5,
        max_tokens=300
    )

    # Extract and return the response text
    insight = response.choices[0].message.content.strip() if response.choices[0].message.content else "Unable to generate insight."
    return insight


# Test for display metadata correctness
def test_control_metadata_display():
    control = "AI Fairness Certification & Standards"
    risk_level = "High Risk"
    sector = "Healthcare"
    region = "EU"
    frameworks = ["EU AI Act", "ISO 42001"]

    metadata_display = f"""
    Control: {control}
    Risk Level: {risk_level}
    Sector: {sector}
    Region: {region}
    Frameworks: {', '.join(frameworks)}
    """

    assert control in metadata_display, "Control title missing from metadata display"
    assert risk_level in metadata_display, "Risk level missing from metadata display"
    assert sector in metadata_display, "Sector missing from metadata display"
    assert region in metadata_display, "Region missing from metadata display"
    for fw in frameworks:
        assert fw in metadata_display, f"Framework '{fw}' missing from metadata display"

    print("\n✅ Metadata Display Verified:\n")
    print(metadata_display)


# Example use case for manual testing
if __name__ == "__main__":
    control = "AI Fairness Certification & Standards"
    risk = "High"
    sector = "Financial Services"
    region = "UK"
    frameworks = ["EU AI Act", "ISO/IEC 42001", "FCA AI Guidelines"]

    result = generate_lifewise_insight(control, risk, sector, region, frameworks)
    print("\nGenerated Life-Wise Insight:\n")
    print(result)
    
    # Test metadata display
    test_control_metadata_display()