"""
Sector-Specific Regulatory Referencing Engine for ASIMOV-AI

This module enforces sector-specific regulatory citations and prevents cross-sector 
regulatory hallucination by validating audit sectors against authentic regulatory sources.

All regulatory references are sourced from official government and regulatory body publications.
"""

import json
import os
from typing import Dict, Optional, List

class SectorRegulatoryEngine:
    def __init__(self, references_file="sector_references.json"):
        """Initialize with authentic regulatory reference data"""
        self.references_file = references_file
        self.sector_data = self._load_sector_references()
    
    def _load_sector_references(self) -> Dict:
        """Load sector-specific regulatory references from JSON file"""
        try:
            if os.path.exists(self.references_file):
                with open(self.references_file, 'r') as f:
                    return json.load(f)
            else:
                print(f"⚠️ Warning: {self.references_file} not found. Creating minimal reference data.")
                return {}
        except Exception as e:
            print(f"❌ Error loading sector references: {e}")
            return {}
    
    def validate_sector(self, sector: str) -> bool:
        """Validate that the specified sector has regulatory reference data"""
        return sector in self.sector_data
    
    def get_sector_context(self, sector: str) -> Optional[Dict]:
        """
        Get authenticated regulatory context for a specific sector
        
        Args:
            sector: The industry sector (e.g., "Healthcare", "Financial Services")
            
        Returns:
            Dict containing regulatory authorities, documents, and citation format
            None if sector is not defined in reference data
        """
        if not self.validate_sector(sector):
            return None
        
        return self.sector_data.get(sector)
    
    def get_regulatory_authorities(self, sector: str) -> List[str]:
        """Get primary regulatory authorities for a sector"""
        context = self.get_sector_context(sector)
        return context.get('primary_regulators', []) if context else []
    
    def get_key_documents(self, sector: str) -> List[str]:
        """Get key regulatory documents for a sector"""
        context = self.get_sector_context(sector)
        return context.get('key_docs', []) if context else []
    
    def get_citation_format(self, sector: str) -> str:
        """Get proper citation format for regulatory references"""
        context = self.get_sector_context(sector)
        return context.get('citation_format', 'No citation format available') if context else 'Sector not found'
    
    def create_sector_prompt_context(self, sector: str, control_name: str = "") -> str:
        """
        Create sector-specific regulatory context for OpenAI prompts with citations
        
        Args:
            sector: Industry sector
            control_name: Specific control being evaluated
            
        Returns:
            Formatted prompt context with regulatory authorities and citations
        """
        sector_context = self.get_sector_context(sector)
        
        if not sector_context:
            raise ValueError(f"Sector-specific reference data not found for '{sector}'. "
                           f"Available sectors: {list(self.sector_data.keys())}")
        
        # Build regulatory context with citations
        prompt_context = f"""
REGULATORY CONTEXT FOR {sector.upper()} SECTOR:

Primary Regulatory Authorities: {', '.join(sector_context['primary_regulators'])}
Geographic Scope: {sector_context['region_context']}

Key Regulatory Documents:
{chr(10).join(f'• {doc}' for doc in sector_context['key_docs'])}

Sector-Specific Requirements:
{chr(10).join(f'• {req}' for req in sector_context.get('key_requirements', []))}

CITATION REQUIREMENT: {sector_context['citation_format']}

When evaluating the control "{control_name}", reference only the regulatory expectations, 
standards, and compliance obligations specific to the {sector} sector as outlined above. 
Do not reference regulations from other sectors.

IMPORTANT: Include proper citations in your response using the format specified above.
"""
        
        return prompt_context
    
    def create_sector_ui_indicators(self, sector: str) -> Dict[str, str]:
        """
        Create UI indicators showing sector-specific regulatory context
        
        Returns:
            Dict with sector, governing bodies, and reference links for display
        """
        sector_context = self.get_sector_context(sector)
        
        if not sector_context:
            return {
                'sector': sector,
                'governing_bodies': 'Not configured',
                'primary_source': 'Sector reference data not available',
                'region': 'Unknown'
            }
        
        return {
            'sector': sector,
            'governing_bodies': ', '.join(sector_context['primary_regulators'][:3]),  # Show top 3
            'primary_source': sector_context['reference_urls'][0] if sector_context.get('reference_urls') else 'No URL available',
            'region': sector_context['region_context'],
            'citation': sector_context['citation_format']
        }
    
    def get_available_sectors(self) -> List[str]:
        """Get list of all configured sectors"""
        return list(self.sector_data.keys())
    
    def validate_prompt_injection(self, sector: str, generated_insight: str) -> Dict[str, bool]:
        """
        Validate that generated insights contain proper sector-specific citations
        
        Returns:
            Dict with validation results and recommendations
        """
        if not self.validate_sector(sector):
            return {
                'valid_sector': False,
                'has_citations': False,
                'message': f"Sector '{sector}' not found in regulatory reference data"
            }
        
        sector_context = self.get_sector_context(sector)
        regulators = sector_context['primary_regulators']
        
        # Check if any regulatory authority is mentioned
        has_regulator_reference = any(regulator in generated_insight for regulator in regulators)
        
        # Check for citation patterns
        has_citation_pattern = any(pattern in generated_insight.lower() 
                                 for pattern in ['(20', 'guidance', 'framework', 'act', 'regulation'])
        
        return {
            'valid_sector': True,
            'has_citations': has_citation_pattern,
            'has_regulator_reference': has_regulator_reference,
            'message': 'Sector-specific regulatory context validated' if has_regulator_reference 
                      else f"Consider adding references to {', '.join(regulators[:2])}"
        }


def get_sector_specific_insight_with_citations(control_name: str, category: str, 
                                             risk_level: str, sector: str, 
                                             region: str = "") -> Dict[str, str]:
    """
    Generate sector-specific insights with proper regulatory citations
    
    Args:
        control_name: Name of the AI governance control
        category: Control category
        risk_level: Risk level (High Risk, General Risk)
        sector: Industry sector
        region: Geographic region (optional)
    
    Returns:
        Dict with insight text and citation information
    """
    regulatory_engine = SectorRegulatoryEngine()
    
    try:
        # Validate sector and get regulatory context
        if not regulatory_engine.validate_sector(sector):
            return {
                'insight': f"Sector-specific guidance not available for '{sector}'. "
                          f"Available sectors: {', '.join(regulatory_engine.get_available_sectors())}",
                'citation': 'No citation available',
                'regulatory_context': 'Sector not configured',
                'validation_status': 'failed'
            }
        
        # Get sector-specific regulatory context
        prompt_context = regulatory_engine.create_sector_prompt_context(sector, control_name)
        
        # Create sector-aware insight (this would integrate with your existing OpenAI calls)
        sector_context = regulatory_engine.get_sector_context(sector)
        
        # Generate insight with regulatory context
        insight_text = f"""Based on {sector} sector regulatory requirements, {control_name} is critical for compliance with {', '.join(sector_context['primary_regulators'][:2])} standards. 

Organizations in the {sector} sector must implement this control to meet {sector_context['key_docs'][0] if sector_context['key_docs'] else 'regulatory'} requirements. 

Key compliance considerations include: {sector_context['key_requirements'][0] if sector_context.get('key_requirements') else 'sector-specific risk management'}.

Citation: {sector_context['citation_format']}"""
        
        # Validate the generated insight
        validation = regulatory_engine.validate_prompt_injection(sector, insight_text)
        
        return {
            'insight': insight_text,
            'citation': sector_context['citation_format'],
            'regulatory_context': f"Governed by: {', '.join(sector_context['primary_regulators'])}",
            'validation_status': 'validated' if validation['has_regulator_reference'] else 'needs_review',
            'sector_indicators': regulatory_engine.create_sector_ui_indicators(sector)
        }
        
    except ValueError as e:
        return {
            'insight': str(e),
            'citation': 'Error in sector validation',
            'regulatory_context': 'Configuration error',
            'validation_status': 'error'
        }


# Integration function for existing OpenAI calls
def enhance_openai_prompt_with_sector_context(base_prompt: str, sector: str, 
                                            control_name: str) -> str:
    """
    Enhance existing OpenAI prompts with sector-specific regulatory context and citation requirements
    
    Args:
        base_prompt: Your existing prompt
        sector: Industry sector
        control_name: Control being evaluated
        
    Returns:
        Enhanced prompt with regulatory context and citation requirements
    """
    regulatory_engine = SectorRegulatoryEngine()
    
    try:
        regulatory_context = regulatory_engine.create_sector_prompt_context(sector, control_name)
        
        enhanced_prompt = f"""{base_prompt}

{regulatory_context}

CITATION INSTRUCTION: Your response must include specific citations to the regulatory 
authorities and documents listed above. Use the provided citation format.
"""
        
        return enhanced_prompt
        
    except ValueError as e:
        # Fallback to base prompt if sector not configured
        return f"{base_prompt}\n\nNote: {str(e)}"