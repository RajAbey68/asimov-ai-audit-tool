"""
ASIMOV-AI Evidence Evaluation Engine
Intelligent assessment of governance evidence using OpenAI GPT-4
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from flask import jsonify
import requests
from urllib.parse import urlparse
import PyPDF2
import docx
import io
import base64
from trusted_reference_engine import enhance_ai_prompt_with_references, get_framework_citations

# Check for OpenAI API key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
USE_AI_EVALUATION = bool(OPENAI_API_KEY)

class EvidenceEvaluationEngine:
    def __init__(self):
        self.confidence_thresholds = {
            'high': ['comprehensive', 'complete', 'thoroughly', 'excellent', 'robust'],
            'medium': ['adequate', 'sufficient', 'reasonable', 'acceptable'],
            'low': ['limited', 'insufficient', 'incomplete', 'partial', 'minimal']
        }
    
    def get_db_connection(self):
        """Create database connection with row factory"""
        conn = sqlite3.connect('audit_controls.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def extract_text_from_file(self, file_content, file_type):
        """Extract text from uploaded files"""
        try:
            if file_type.lower() == 'pdf':
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            
            elif file_type.lower() in ['docx', 'doc']:
                doc = docx.Document(io.BytesIO(file_content))
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            
            elif file_type.lower() == 'txt':
                return file_content.decode('utf-8')
            
            else:
                return "Unsupported file type for text extraction"
                
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def extract_text_from_url(self, url):
        """Extract text content from URL references"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Basic HTML stripping for text extraction
                text = response.text
                # Remove HTML tags
                import re
                text = re.sub(r'<[^>]+>', ' ', text)
                # Clean up whitespace
                text = ' '.join(text.split())
                return text[:2000]  # Limit to first 2000 characters
            else:
                return f"Could not access URL (Status: {response.status_code})"
        except Exception as e:
            return f"Error accessing URL: {str(e)}"
    
    def check_evidence_recency(self, evidence_date, control_category):
        """Check if evidence is recent enough based on control type"""
        if not evidence_date:
            return "No date provided", "unknown"
        
        try:
            evidence_dt = datetime.strptime(evidence_date, '%Y-%m-%d')
            days_old = (datetime.now() - evidence_dt).days
            
            # Define recency requirements by control category
            recency_requirements = {
                'security': 90,      # Security controls: 90 days
                'monitoring': 30,    # Monitoring controls: 30 days
                'data': 180,         # Data governance: 180 days
                'documentation': 365, # Documentation: 1 year
                'default': 180       # Default: 180 days
            }
            
            category_lower = control_category.lower()
            required_days = recency_requirements.get('default', 180)
            
            for key, days in recency_requirements.items():
                if key in category_lower:
                    required_days = days
                    break
            
            if days_old <= required_days:
                return f"Evidence is {days_old} days old (within {required_days} day requirement)", "current"
            else:
                return f"Evidence is {days_old} days old (exceeds {required_days} day requirement)", "stale"
                
        except ValueError:
            return "Invalid date format", "unknown"
    
    def generate_ai_evaluation(self, control_info, evidence_data):
        """Generate AI evaluation using OpenAI GPT-4"""
        if not USE_AI_EVALUATION:
            return self.generate_fallback_evaluation(control_info, evidence_data)
        
        try:
            # Get enhanced system prompt with trusted references
            enhanced_system_prompt = enhance_ai_prompt_with_references(control_info)
            
            # Construct evaluation prompt with framework context
            prompt = f"""
CONTROL INFORMATION:
- Name: {control_info['name']}
- Category: {control_info['category']}
- Risk Level: {control_info['risk_level']}
- Framework: {control_info['framework']}
- Description: {control_info['control_question']}

SUBMITTED EVIDENCE:
- Notes: {evidence_data.get('notes', 'None provided')}
- File Content: {evidence_data.get('file_text', 'No files uploaded')}
- URL Content: {evidence_data.get('url_text', 'No URLs provided')}
- Evidence Date: {evidence_data.get('evidence_date', 'No date provided')}
- Recency Assessment: {evidence_data.get('recency_check', 'Unknown')}

EVALUATION REQUIREMENTS:
Assess whether this evidence is "fit for governance purpose" by evaluating:
1. Completeness: Does evidence address the control requirements?
2. Quality: Is the evidence detailed and specific?
3. Relevance: Does evidence directly relate to the control?
4. Recency: Is evidence current enough for the control type?
5. Framework Alignment: Does evidence meet standards from referenced frameworks?

Provide a response in exactly this JSON format:
{{
    "evaluation_summary": "Brief assessment referencing specific frameworks when applicable",
    "governance_alignment": "Fit for Purpose" | "Partial / Incomplete" | "Not Sufficient",
    "confidence_level": "High" | "Medium" | "Low",
    "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "framework_references": ["Framework 1", "Framework 2"]
}}

Keep evaluation_summary under 250 words and include specific framework references where relevant.
"""

            # Make OpenAI API call
            headers = {
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4o',  # Using latest OpenAI model
                'messages': [
                    {'role': 'system', 'content': enhanced_system_prompt},
                    {'role': 'user', 'content': prompt}
                ],
                'response_format': {'type': 'json_object'},
                'max_tokens': 1000,
                'temperature': 0.3
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                evaluation_json = json.loads(result['choices'][0]['message']['content'])
                
                # Add framework citations if not present
                if 'framework_references' not in evaluation_json:
                    evaluation_json['framework_references'] = []
                
                # Get suggested citations based on evaluation content
                citations = get_framework_citations(
                    evaluation_json.get('evaluation_summary', ''),
                    control_info.get('category', '')
                )
                
                # Add citation suggestions to the evaluation
                evaluation_json['suggested_citations'] = citations
                
                return evaluation_json
            else:
                return self.generate_fallback_evaluation(control_info, evidence_data)
                
        except Exception as e:
            print(f"AI evaluation error: {e}")
            return self.generate_fallback_evaluation(control_info, evidence_data)
    
    def generate_fallback_evaluation(self, control_info, evidence_data):
        """Generate structured evaluation without AI"""
        # Analyze evidence completeness
        has_notes = bool(evidence_data.get('notes', '').strip())
        has_files = bool(evidence_data.get('file_text', '').strip())
        has_urls = bool(evidence_data.get('url_text', '').strip())
        has_date = bool(evidence_data.get('evidence_date'))
        
        evidence_count = sum([has_notes, has_files, has_urls, has_date])
        
        # Determine governance alignment
        if evidence_count >= 3:
            alignment = "Fit for Purpose"
            confidence = "High"
        elif evidence_count == 2:
            alignment = "Partial / Incomplete"
            confidence = "Medium"
        else:
            alignment = "Not Sufficient"
            confidence = "Low"
        
        # Generate summary
        evidence_types = []
        if has_notes: evidence_types.append("detailed notes")
        if has_files: evidence_types.append("supporting documents")
        if has_urls: evidence_types.append("reference materials")
        if has_date: evidence_types.append("evidence date")
        
        if evidence_types:
            summary = f"Evidence includes {', '.join(evidence_types)}. "
        else:
            summary = "Limited evidence provided. "
        
        summary += f"Assessment shows {alignment.lower()} level of documentation for {control_info['category']} control."
        
        return {
            "evaluation_summary": summary,
            "governance_alignment": alignment,
            "confidence_level": confidence,
            "key_findings": [
                f"Evidence completeness: {evidence_count}/4 components provided",
                f"Control category: {control_info['category']} ({control_info['risk_level']})",
                f"Recency status: {evidence_data.get('recency_status', 'Unknown')}"
            ],
            "recommendations": [
                "Ensure evidence directly addresses control requirements",
                "Maintain regular evidence updates based on control criticality",
                "Document implementation details and testing results"
            ]
        }
    
    def evaluate_control_evidence(self, control_id, session_id, evidence_data=None):
        """Main evaluation function for control evidence"""
        conn = self.get_db_connection()
        
        try:
            # Get control information
            control = conn.execute("""
                SELECT name, category, risk_level, framework, control_question
                FROM controls 
                WHERE id = ?
            """, (control_id,)).fetchone()
            
            if not control:
                return {"error": "Control not found"}
            
            # Get existing evidence if not provided
            if not evidence_data:
                evidence = conn.execute("""
                    SELECT evidence_notes, evidence_date, comments
                    FROM audit_responses 
                    WHERE session_id = ? AND control_id = ?
                """, (session_id, control_id)).fetchone()
                
                if evidence:
                    evidence_data = {
                        'notes': evidence['evidence_notes'] or '',
                        'evidence_date': evidence['evidence_date'] or '',
                        'comments': evidence['comments'] or ''
                    }
                else:
                    evidence_data = {}
            
            # Check evidence recency
            recency_message, recency_status = self.check_evidence_recency(
                evidence_data.get('evidence_date'), 
                control['category']
            )
            evidence_data['recency_check'] = recency_message
            evidence_data['recency_status'] = recency_status
            
            # Generate AI evaluation
            evaluation = self.generate_ai_evaluation(dict(control), evidence_data)
            
            # Save evaluation to database
            evaluation_json = json.dumps(evaluation)
            conn.execute("""
                UPDATE audit_responses 
                SET evaluation_text = ?, evaluation_status = ?, confidence_level = ?, evaluation_date = ?
                WHERE session_id = ? AND control_id = ?
            """, (
                evaluation_json,
                evaluation['governance_alignment'],
                evaluation['confidence_level'],
                datetime.now().isoformat(),
                session_id,
                control_id
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "evaluation": evaluation,
                "control_name": control['name'],
                "recency_status": recency_status
            }
            
        except Exception as e:
            conn.close()
            return {"error": f"Evaluation failed: {str(e)}"}

# Global instance
evaluation_engine = EvidenceEvaluationEngine()

def create_evaluation_routes(app):
    """Add evidence evaluation routes to Flask app"""
    
    @app.route('/evaluate_evidence/<int:control_id>/<session_id>', methods=['POST'])
    def evaluate_evidence(control_id, session_id):
        """Evaluate evidence for a specific control"""
        try:
            # Get evidence data from request
            from flask import request
            evidence_data = request.get_json() or {}
            
            # Perform evaluation
            result = evaluation_engine.evaluate_control_evidence(
                control_id, session_id, evidence_data
            )
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({"error": f"Evaluation failed: {str(e)}"}), 500
    
    @app.route('/api/evidence_status/<session_id>')
    def get_evidence_status(session_id):
        """Get evidence evaluation status for all controls in session"""
        try:
            conn = evaluation_engine.get_db_connection()
            
            evaluations = conn.execute("""
                SELECT 
                    ar.control_id,
                    c.name as control_name,
                    ar.evaluation_status,
                    ar.confidence_level,
                    ar.evaluation_date
                FROM audit_responses ar
                JOIN controls c ON ar.control_id = c.id
                WHERE ar.session_id = ? AND ar.evaluation_text IS NOT NULL
                ORDER BY ar.control_id
            """, (session_id,)).fetchall()
            
            conn.close()
            
            return jsonify([dict(row) for row in evaluations])
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Test the evaluation engine
    print("🧠 ASIMOV-AI Evidence Evaluation Engine")
    print(f"OpenAI Integration: {'✅ Available' if USE_AI_EVALUATION else '⚠️ Using Fallback'}")
    
    # Test fallback evaluation
    test_control = {
        'name': 'Anomaly Detection Techniques',
        'category': 'Defensive Model Strengthening',
        'risk_level': 'High Risk',
        'framework': 'EU AI Law',
        'control_question': 'Develop and implement anomaly detection techniques'
    }
    
    test_evidence = {
        'notes': 'Implemented comprehensive anomaly detection using ML algorithms',
        'evidence_date': '2025-05-20',
        'file_text': 'Technical documentation shows 95% accuracy rate',
        'url_text': 'Reference to industry best practices'
    }
    
    engine = EvidenceEvaluationEngine()
    result = engine.generate_fallback_evaluation(test_control, test_evidence)
    print(f"Test Evaluation: {result['governance_alignment']} ({result['confidence_level']})")