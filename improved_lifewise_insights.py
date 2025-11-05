"""
Improved Life-Wise Insights Generator using the ASIMOV-AI approach
- Focuses on real-world incidents and practical impacts
- Uses the consolidated prompt from expert guidance
- Limits to 200 words for clarity and impact
"""

import os
from openai import OpenAI

def get_api_key():
    """Get OpenAI API key from environment variables"""
    api_key = os.environ.get("OPENAI_API_KEY")
    return api_key

def generate_insight(control_text, pillar="", sector="", region=""):
    """Generate a Life-Wise Insight using the consolidated prompt format"""
    
    # Use the consolidated prompt format provided
    prompt = f"""
You are an AI governance strategist operating under the ASIMOV-AI Unified Risk Framework.

Your task is to generate a 2–3 sentence **Life-Wise Insight** (under 200 words) for the following AI audit control:

📌 Control: "{control_text}"
📊 ASIMOV Pillar: {pillar}
🏢 Sector: {sector or "All"}
🌍 Region: {region or "Global"}

Your insight must:
- Explain **why this control matters in the real world**
- Include a known failure, risk scenario, regulatory action, or breach (real or plausible)
- Be useful to **legal, risk, or compliance leaders**, not technical engineers
- Be clear, consequential, and sector-aware when applicable
- Preferably be inspired by the following sources:

📚 Documents and Frameworks:
- EU AI Act (2023)
- GDPR (Articles 13–22)
- NIST AI Risk Management Framework (v1.0, 2023)
- ISO/IEC 42001 – AI Management Systems
- ISACA AI Audit Toolkit
- MITRE ATLAS (Adversarial Threats)
- OWASP Top 10 for LLMs
- Microsoft Security & Copilot Blogs (2023–24)
- Ada Lovelace Institute and SHERPA Project Guidance
- UK ICO, FCA AI Papers, MHRA Guidelines, NHS AI Reports
- Harvard Berkman Klein Center AI Ethics Blog
- CISA, Lawfare, Oxford Internet Institute, IAPP, DeepMind

🧠 Your goal is to draw on the **practical, societal, legal or reputational risks** from these sources to help a non-technical team *understand the consequence of neglecting this control.*

❌ Do not quote laws or policies directly.  
❌ Do not explain what the control "is."  
✅ Do offer a **real-world insight**, as if from an experienced AI risk advisor in audit or governance.

Return only the insight. No preamble, no explanation, no citations.
"""
    
    # Get API key
    api_key = get_api_key()
    
    # If API key is not available, return a fallback message
    if not api_key:
        return f"Error: OpenAI API key not found"
    
    try:
        # Initialize OpenAI client
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024
        # do not change this unless explicitly requested by the user
        client = OpenAI(api_key=api_key)
        
        # Generate insight using OpenAI with the consolidated format
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        # Extract insight from response
        if response and response.choices and len(response.choices) > 0 and response.choices[0].message and response.choices[0].message.content:
            insight = response.choices[0].message.content.strip()
            return insight
        else:
            # Fallback if we can't extract the insight
            return "Error generating insight. Please try again."
        
    except Exception as e:
        # Handle any errors
        return f"Error generating insight: {str(e)}"

# Example usage
if __name__ == "__main__":
    test_control = "Anomaly Detection Techniques"
    test_pillar = "Defensive Model Strengthening"
    test_sector = "Financial Services"
    test_region = "EU"
    
    insight = generate_insight(test_control, test_pillar, test_sector, test_region)
    print(f"Insight for '{test_control}':")
    print(insight)