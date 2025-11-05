"""
Enhanced Life-Wise Insights Generator using the ASIMOV-AI approach
"""

import os
from openai import OpenAI

# List of approved frameworks we should reference
APPROVED_FRAMEWORKS = [
    "Unified Framework (ASIMOV-AI)",
    "EU AI Act (2023)",
    "GDPR – Articles 13–22",
    "NIST AI RMF (v1.0)",
    "ISO/IEC 42001 – AI Management Systems",
    "ISACA AI Audit Toolkit",
    "MITRE ATLAS (Adversarial Threats)",
    "OWASP Top 10 for LLMs",
    "Microsoft Responsible AI & Endpoint Security Blogs",
    "Ada Lovelace Institute & SHERPA Project findings"
]

def get_api_key():
    """Get OpenAI API key from environment variables"""
    api_key = os.environ.get("OPENAI_API_KEY")
    return api_key

def generate_insight(control_text, sector="", region=""):
    """Generate a Life-Wise Insight using the exact format from the example"""
    
    # Use the exact prompt format provided
    prompt = f"""
You are a senior AI governance strategist working within the ASIMOV-AI Unified Risk Framework.

Your task is to generate a 2–3 sentence **Life-Wise Insight** for the following AI audit control:

"{control_text}"

🧠 The insight must:
- Explain why the control matters, using **real-world risks, consequences, or regulatory outcomes**
- Be clear and useful to **legal, compliance, and executive risk teams**
- Be written in **natural language**, not standards or policy language
- Reference sector-specific or region-specific risks **if relevant**

🎯 Sector context: {sector}  
🌍 Regional context: {region}

You may **preferably** draw from these widely recognised and commercially used frameworks:
- Unified Framework (ASIMOV-AI)
- EU AI Act (2023)
- GDPR – Articles 13–22
- NIST AI RMF (v1.0)
- ISO/IEC 42001 – AI Management Systems
- ISACA AI Audit Toolkit
- MITRE ATLAS (Adversarial Threats)
- OWASP Top 10 for LLMs
- Microsoft Responsible AI & Endpoint Security Blogs
- Ada Lovelace Institute & SHERPA Project findings

❌ Do NOT simply quote the framework language.  
✅ Instead, translate these ideas into **practical insight** for real-world AI governance.

Return only the insight text — no preamble, bullet points, or disclaimers.
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
            return "Unable to generate insight. Please check API configuration."
        
    except Exception as e:
        # Handle any errors
        return f"Error generating insight: {str(e)}"

# Example usage
if __name__ == "__main__":
    test_control = "Adversarial Training for Model Robustness"
    test_sector = "Financial Services"
    test_region = "EU"
    
    insight = generate_insight(test_control, test_sector, test_region)
    print(f"Insight for '{test_control}':")
    print(insight)