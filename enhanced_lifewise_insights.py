"""
Enhanced Life-Wise Insights Generator using the improved ASIMOV-AI approach
"""

import os
from openai import OpenAI

# List of approved frameworks and sources we should reference
APPROVED_SOURCES = [
    "EU AI Act (2023)",
    "GDPR Articles 13–22",
    "NIST AI RMF (v1.0)",
    "ISO/IEC 42001 – AI Management Systems",
    "ISACA AI Audit Toolkit",
    "MITRE ATLAS (Adversarial Tactics)",
    "OWASP Top 10 for LLMs",
    "Microsoft Security Blog & Responsible AI",
    "Ada Lovelace Institute, SHERPA Project",
    "NHS/MHRA case reviews, FCA enforcement reports",
    "Lawfare Blog, IAPP, Oxford Internet Institute"
]

def get_api_key():
    """Get OpenAI API key from environment variables"""
    api_key = os.environ.get("OPENAI_API_KEY")
    return api_key

def generate_insight(control_text, pillar="", sector="", region=""):
    """Generate a Life-Wise Insight using the enhanced format with real-world examples"""
    
    # Use the exact prompt format provided
    prompt = f"""
You are a senior AI governance strategist using the ASIMOV-AI Unified Framework.

Your task is to generate a 2–3 sentence **Life-Wise Insight** (under 200 words) for the following AI audit control:

📌 Control: "{control_text}"  
📊 ASIMOV Pillar: {pillar}  
🏢 Sector: {sector or "All"}  
🌍 Region: {region or "Global"}

The insight must:
- Highlight why this control matters in **real-world legal, compliance, ethical, or operational terms**
- Be relevant for non-technical audiences (legal, audit, risk)
- Reference risks, breaches, or consequences that have occurred or are plausible
- Use real incident examples or risk scenarios when relevant
- Preferably be inspired by one or more of these frameworks or expert sources:

🧠 Preferred Sources:
- EU AI Act (2023)
- GDPR Articles 13–22
- NIST AI RMF (v1.0)
- ISO/IEC 42001 – AI Management Systems
- ISACA AI Audit Toolkit
- MITRE ATLAS (Adversarial Tactics)
- OWASP Top 10 for LLMs
- Microsoft Security Blog & Responsible AI
- Ada Lovelace Institute, SHERPA Project
- NHS/MHRA case reviews, FCA enforcement reports
- Lawfare Blog, IAPP, Oxford Internet Institute

❌ Avoid quoting policies or frameworks directly.  
✅ Instead, provide a useful insight that would help a real compliance or governance team understand the **risk, urgency, or real-world impact** of weak implementation.

Return only the Life-Wise Insight text. No titles, citations, or explanations.
"""
    
    # Get API key
    api_key = get_api_key()
    
    # If API key is not available, return a fallback message
    if not api_key:
        # This should never be displayed to end users - we'll use our local fallback system
        return f"Error: OpenAI API key not found"
    
    try:
        # Initialize OpenAI client
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024
        # do not change this unless explicitly requested by the user
        client = OpenAI(api_key=api_key)
        
        # Generate insight using OpenAI with the exact format from the example
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
    test_control = "Adversarial Training for Model Robustness"
    test_pillar = "Technical Resilience"
    test_sector = "Financial Services"
    test_region = "EU"
    
    insight = generate_insight(test_control, test_pillar, test_sector, test_region)
    print(f"Insight for '{test_control}':")
    print(insight)