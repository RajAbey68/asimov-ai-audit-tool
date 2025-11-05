"""
Trusted Reference Engine for ASIMOV-AI Evidence Evaluation
Integrates authoritative governance frameworks and sources for enhanced AI insights
"""

import json

class TrustedReferenceEngine:
    def __init__(self):
        self.reference_sources = {
            "governance_frameworks": [
                {
                    "title": "NIST AI Risk Management Framework",
                    "url": "https://www.nist.gov/itl/ai-risk-management-framework",
                    "scope": "Comprehensive AI risk management guidance",
                    "relevance": ["risk assessment", "governance", "management"]
                },
                {
                    "title": "ISO/IEC 42001 - AI Management Systems",
                    "url": "https://www.iso.org/standard/81228.html",
                    "scope": "International standard for AI management systems",
                    "relevance": ["management systems", "documentation", "certification"]
                },
                {
                    "title": "EU AI Act Overview",
                    "url": "https://artificialintelligenceact.eu/",
                    "scope": "European Union AI regulation framework",
                    "relevance": ["regulatory compliance", "high-risk AI", "transparency"]
                },
                {
                    "title": "OECD AI Principles",
                    "url": "https://oecd.ai/en/ai-principles",
                    "scope": "International AI governance principles",
                    "relevance": ["ethics", "human rights", "international standards"]
                }
            ],
            "security_frameworks": [
                {
                    "title": "MITRE ATLAS - AI Security Framework",
                    "url": "https://atlas.mitre.org/",
                    "scope": "AI security threats and mitigations",
                    "relevance": ["security", "threats", "adversarial attacks", "defense"]
                },
                {
                    "title": "OWASP Top 10 for Large Language Models",
                    "url": "https://owasp.org/www-project-top-10-for-large-language-model-applications/",
                    "scope": "LLM security vulnerabilities and controls",
                    "relevance": ["LLM security", "vulnerabilities", "application security"]
                },
                {
                    "title": "OpenAI Safety Best Practices",
                    "url": "https://platform.openai.com/docs/guides/safety-best-practices",
                    "scope": "AI safety implementation guidance",
                    "relevance": ["safety", "implementation", "best practices"]
                },
                {
                    "title": "Secure Controls Framework (SCF)",
                    "url": "https://securecontrolsframework.com/",
                    "scope": "Comprehensive cybersecurity control framework",
                    "relevance": ["cybersecurity", "controls", "compliance"]
                }
            ],
            "audit_frameworks": [
                {
                    "title": "ISACA AI Audit Toolkit",
                    "url": "https://www.isaca.org/go/ai-audit-toolkit",
                    "scope": "Professional AI audit methodology",
                    "relevance": ["audit", "assessment", "professional standards"]
                },
                {
                    "title": "OpenAI API Documentation",
                    "url": "https://platform.openai.com/docs/",
                    "scope": "Technical implementation guidance",
                    "relevance": ["technical implementation", "API usage"]
                }
            ]
        }
    
    def get_relevant_sources(self, control_category, control_name=""):
        """Get relevant reference sources based on control context"""
        relevant_sources = []
        
        # Normalize inputs for matching
        category_lower = control_category.lower()
        name_lower = control_name.lower()
        combined_text = f"{category_lower} {name_lower}"
        
        # Check all source categories
        for category, sources in self.reference_sources.items():
            for source in sources:
                # Check if any relevance keywords match
                for relevance_term in source['relevance']:
                    if relevance_term in combined_text:
                        if source not in relevant_sources:
                            relevant_sources.append(source)
                        break
        
        # Always include core governance frameworks
        governance_sources = self.reference_sources['governance_frameworks'][:3]  # Top 3
        for source in governance_sources:
            if source not in relevant_sources:
                relevant_sources.append(source)
        
        return relevant_sources[:6]  # Limit to 6 most relevant sources
    
    def generate_reference_context(self, control_category, control_name=""):
        """Generate reference context for AI prompt enhancement"""
        relevant_sources = self.get_relevant_sources(control_category, control_name)
        
        context = """
AUTHORITATIVE REFERENCE FRAMEWORKS:
When evaluating evidence, reference these trusted governance and security frameworks:

"""
        
        for source in relevant_sources:
            context += f"• {source['title']}\n"
            context += f"  URL: {source['url']}\n"
            context += f"  Scope: {source['scope']}\n\n"
        
        context += """
EVALUATION INSTRUCTIONS:
- Assess evidence against standards from these authoritative frameworks
- Reference specific framework requirements where applicable
- Ensure governance alignment with recognized industry standards
- Provide framework-specific recommendations when gaps are identified
"""
        
        return context
    
    def get_enhanced_system_prompt(self, control_category, control_name=""):
        """Generate enhanced system prompt with trusted references"""
        reference_context = self.generate_reference_context(control_category, control_name)
        
        system_prompt = f"""You are an AI governance auditor evaluating evidence for regulatory compliance.

{reference_context}

Your evaluation should:
1. Compare evidence against requirements from relevant frameworks above
2. Reference specific standards when identifying gaps or strengths
3. Provide framework-aligned recommendations for improvement
4. Ensure traceability to recognized governance authorities
5. Maintain professional audit standards throughout assessment

Summarize your evaluation in under 300 words with clear framework alignment."""

        return system_prompt
    
    def get_reference_json(self):
        """Get all reference sources as JSON for API context"""
        all_sources = []
        for category, sources in self.reference_sources.items():
            all_sources.extend(sources)
        
        return {
            "reference_sources": all_sources,
            "usage_note": "These sources provide authoritative guidance for AI governance evaluation"
        }
    
    def get_citation_suggestions(self, evaluation_text, control_category):
        """Suggest relevant citations based on evaluation content"""
        relevant_sources = self.get_relevant_sources(control_category)
        suggestions = []
        
        evaluation_lower = evaluation_text.lower()
        
        for source in relevant_sources:
            # Check if evaluation mentions concepts related to this source
            for relevance_term in source['relevance']:
                if relevance_term in evaluation_lower:
                    suggestions.append({
                        "source": source['title'],
                        "url": source['url'],
                        "reason": f"Relevant for {relevance_term} guidance"
                    })
                    break
        
        return suggestions[:3]  # Top 3 suggestions

# Global instance
trusted_references = TrustedReferenceEngine()

def enhance_ai_prompt_with_references(control_info):
    """Enhance AI evaluation prompt with trusted reference context"""
    return trusted_references.get_enhanced_system_prompt(
        control_info.get('category', ''),
        control_info.get('name', '')
    )

def get_framework_citations(evaluation_text, control_category):
    """Get suggested framework citations for evaluation text"""
    return trusted_references.get_citation_suggestions(evaluation_text, control_category)

if __name__ == "__main__":
    # Test the reference engine
    print("🔗 ASIMOV-AI Trusted Reference Engine")
    print("=" * 50)
    
    # Test with security control
    test_control = {
        'category': 'Defensive Model Strengthening',
        'name': 'Anomaly Detection Techniques'
    }
    
    enhanced_prompt = trusted_references.get_enhanced_system_prompt(
        test_control['category'], 
        test_control['name']
    )
    
    print("Enhanced System Prompt for Security Control:")
    print("-" * 30)
    print(enhanced_prompt[:500] + "...")
    
    # Test citation suggestions
    test_evaluation = "This control implements comprehensive anomaly detection using machine learning algorithms following MITRE ATLAS guidance and NIST AI RMF principles."
    
    citations = trusted_references.get_citation_suggestions(test_evaluation, test_control['category'])
    
    print(f"\nSuggested Citations: {len(citations)} found")
    for citation in citations:
        print(f"• {citation['source']}: {citation['reason']}")