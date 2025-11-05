"""
Quick test to verify Life-Wise Insights are working correctly
This script tests a single control to confirm the insights show real-world examples
"""

import os
from openai import OpenAI

def test_real_world_insights():
    """Test that insights are using the real-world format"""
    print("\n🧪 Testing Life-Wise Insights Generation")
    print("=" * 60)
    
    # Test parameters
    control_name = "Anomaly Detection Techniques"
    category = "Defensive Model Strengthening"
    sector = "Financial Services"
    region = "EU"
    
    # Get API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OpenAI API key not found in environment variables")
        return False
    
    try:
        # Initialize the client
        client = OpenAI(api_key=api_key)
        
        # Use the consolidated prompt format
        prompt = f"""
You are an AI governance strategist operating under the ASIMOV-AI Unified Risk Framework.

Your task is to generate a 2–3 sentence **Life-Wise Insight** (under 200 words) for the following AI audit control:

📌 Control: "{control_name}"
📊 ASIMOV Pillar: {category}
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
        
        # Generate the insight
        print("Generating Life-Wise Insight for 'Anomaly Detection Techniques'...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        # Get the insight from the response
        insight = response.choices[0].message.content.strip()
        
        print("\n" + "=" * 60)
        print("LIFE-WISE INSIGHT:")
        print(insight)
        print("=" * 60)
        
        # Check if it's using the new format (mentions real incidents, not just laws)
        uses_new_format = True
        
        # Check if it's quoting laws directly
        if "according to" in insight.lower() and "article" in insight.lower():
            uses_new_format = False
        
        # Check if it has buzzwords that indicate real-world focus
        real_world_terms = ["incident", "breach", "attack", "failure", "compromise", "vulnerable"]
        has_real_world_terms = any(term in insight.lower() for term in real_world_terms)
        
        if uses_new_format and has_real_world_terms:
            print("\n✅ SUCCESS: Life-Wise Insight is using the correct format with real-world examples")
            return True
        else:
            print("\n❌ FAILURE: Life-Wise Insight is not using the correct format")
            if not uses_new_format:
                print("   - Appears to be quoting laws directly")
            if not has_real_world_terms:
                print("   - Does not include references to real-world incidents")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_real_world_insights()