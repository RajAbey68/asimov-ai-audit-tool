"""
Regulatory Timeline Awareness System

This module enhances Life-Wise Insights with regulatory timeline information,
highlighting upcoming compliance deadlines and enforcement dates for AI regulations.

Key features:
- Maps controls to specific regulatory frameworks and their deadlines
- Highlights when controls become mandatory in different regions
- Adds urgency indicators for approaching compliance dates
"""

import datetime
from dateutil.relativedelta import relativedelta

class RegulatoryTimeline:
    """Class for managing regulatory timeline information"""
    
    def __init__(self):
        """Initialize the regulatory timeline system"""
        # Current date for timeline calculations
        self.current_date = datetime.datetime.now().date()
        
        # Major AI regulatory frameworks and their implementation dates
        self.framework_timelines = {
            "EU AI Act": {
                "general_application": datetime.date(2026, 8, 2),  # 24 months after entry into force
                "high_risk_systems": datetime.date(2025, 8, 2),    # 12 months after entry into force
                "prohibited_systems": datetime.date(2025, 2, 2),   # 6 months after entry into force
                "entry_into_force": datetime.date(2024, 8, 2),     # 20 days after publication
                "foundation_models": datetime.date(2025, 2, 2),    # 6 months after entry into force
            },
            "NIST AI RMF": {
                "v1_0_release": datetime.date(2023, 1, 26),
                "v1_0_implementation": datetime.date(2023, 7, 1),  # Approximate date organizations began implementation
                "v2_0_expected": datetime.date(2025, 6, 1),        # Expected future update
            },
            "ISO 42001": {
                "published": datetime.date(2023, 6, 15),
                "expected_adoption": datetime.date(2025, 6, 15),   # Approximate industry adoption timeframe
            }
        }
        
        # Risk level urgency mapping (earlier dates for higher risks)
        self.risk_urgency_adjustments = {
            "High": relativedelta(months=-6),    # High-risk requires earlier compliance
            "Medium": relativedelta(months=-3),  # Medium risk needs moderate lead time
            "Low": relativedelta(months=0)       # Low risk can follow standard timeline
        }
        
        # Control category to framework mapping
        self.category_framework_map = {
            "Defensive Model Strengthening": ["EU AI Act", "NIST AI RMF"],
            "Prompt Engineering Defense": ["EU AI Act", "NIST AI RMF"],
            "Audit and Logging": ["EU AI Act", "NIST AI RMF", "ISO 42001"],
            "Model Governance": ["EU AI Act", "ISO 42001"],
            "Security Testing": ["NIST AI RMF", "ISO 42001"],
            "Model Documentation": ["EU AI Act", "ISO 42001"],
            "Data Quality": ["EU AI Act", "NIST AI RMF", "ISO 42001"],
            "Human Oversight": ["EU AI Act"],
            "Explainability": ["EU AI Act", "NIST AI RMF"],
            "Risk Assessment": ["EU AI Act", "NIST AI RMF", "ISO 42001"],
        }
        
    def get_regulatory_deadline(self, control_name, category, risk_level="Medium"):
        """
        Get the regulatory deadline information for a control.
        
        Args:
            control_name (str): The name of the control
            category (str): The category of the control
            risk_level (str): The risk level of the control (High, Medium, Low)
            
        Returns:
            dict: Regulatory deadline information
        """
        # Find applicable frameworks for this control category
        applicable_frameworks = self.category_framework_map.get(category, [])
        if not applicable_frameworks:
            # Default to all frameworks if category not found
            applicable_frameworks = list(self.framework_timelines.keys())
        
        # Default risk level if not provided or invalid
        if risk_level not in self.risk_urgency_adjustments:
            risk_level = "Medium"
        
        # Get deadline information for each applicable framework
        deadlines = {}
        for framework in applicable_frameworks:
            timeline = self.framework_timelines.get(framework, {})
            
            # Select the appropriate date based on framework and risk level
            if framework == "EU AI Act":
                if "high risk" in control_name.lower() or risk_level == "High":
                    key_date = "high_risk_systems"
                elif "prohibited" in control_name.lower():
                    key_date = "prohibited_systems"
                elif "foundation model" in control_name.lower() or "general purpose" in control_name.lower():
                    key_date = "foundation_models"
                else:
                    key_date = "general_application"
                
                deadline_date = timeline.get(key_date)
            elif framework == "NIST AI RMF":
                deadline_date = timeline.get("v1_0_implementation")
            elif framework == "ISO 42001":
                deadline_date = timeline.get("expected_adoption")
            else:
                continue
                
            if deadline_date:
                # Apply risk-based adjustment
                adjusted_date = deadline_date + self.risk_urgency_adjustments.get(risk_level, relativedelta(months=0))
                
                # Calculate time remaining
                if adjusted_date > self.current_date:
                    days_remaining = (adjusted_date - self.current_date).days
                    months_remaining = days_remaining // 30
                    
                    deadlines[framework] = {
                        "date": adjusted_date.strftime("%B %d, %Y"),
                        "days_remaining": days_remaining,
                        "months_remaining": months_remaining,
                        "passed": False
                    }
                else:
                    # Deadline has passed
                    deadlines[framework] = {
                        "date": adjusted_date.strftime("%B %d, %Y"),
                        "days_remaining": 0,
                        "months_remaining": 0,
                        "passed": True
                    }
        
        return deadlines
    
    def get_timeline_message(self, control_name, category, risk_level="Medium"):
        """
        Generate a human-readable message about regulatory timelines for a control.
        
        Args:
            control_name (str): The name of the control
            category (str): The category of the control
            risk_level (str): The risk level of the control (High, Medium, Low)
            
        Returns:
            str: A message about regulatory timelines
        """
        deadlines = self.get_regulatory_deadline(control_name, category, risk_level)
        
        if not deadlines:
            return ""
        
        # Find the earliest upcoming deadline
        earliest_framework = None
        earliest_date = None
        earliest_days = float('inf')
        
        for framework, info in deadlines.items():
            if not info["passed"] and info["days_remaining"] < earliest_days:
                earliest_framework = framework
                earliest_date = info["date"]
                earliest_days = info["days_remaining"]
        
        # Generate message based on timeline
        if earliest_framework and earliest_days < float('inf'):
            if earliest_days <= 90:
                urgency = "URGENT: "
            else:
                urgency = ""
                
            if earliest_days <= 30:
                timeframe = f"this month"
            elif earliest_days <= 90:
                months_remaining = earliest_days // 30
                timeframe = f"within {months_remaining} months"
            else:
                timeframe = f"by {earliest_date}"
                
            message = f"{urgency}This control becomes mandatory under {earliest_framework} {timeframe}."
            
            # Add extra context for specific frameworks
            if earliest_framework == "EU AI Act" and earliest_days <= 180:
                message += " Non-compliance may result in fines up to 7% of global annual turnover."
            
            return message
        
        # All deadlines have passed
        passed_frameworks = [f for f in deadlines.keys() if deadlines[f]["passed"]]
        if passed_frameworks:
            return f"This control is currently mandatory under {', '.join(passed_frameworks)}."
            
        return ""

# Example usage
if __name__ == "__main__":
    timeline = RegulatoryTimeline()
    
    # Test with different controls
    test_controls = [
        {"name": "Anomaly Detection Techniques", "category": "Defensive Model Strengthening", "risk": "Medium"},
        {"name": "High-Risk AI System Documentation", "category": "Model Documentation", "risk": "High"},
        {"name": "Foundation Model Registration", "category": "Model Governance", "risk": "High"},
        {"name": "Prohibited AI Use Prevention", "category": "Risk Assessment", "risk": "High"}
    ]
    
    print("\n" + "=" * 70)
    print("🧪 REGULATORY TIMELINE AWARENESS SYSTEM")
    print("=" * 70)
    
    for control in test_controls:
        print(f"\n📊 Control: {control['name']}")
        print(f"📊 Category: {control['category']}")
        print(f"📊 Risk Level: {control['risk']}")
        print("-" * 70)
        
        message = timeline.get_timeline_message(control['name'], control['category'], control['risk'])
        print(f"✅ Timeline Message: {message}")
        print("-" * 70)
        
        deadlines = timeline.get_regulatory_deadline(control['name'], control['category'], control['risk'])
        print("✅ Detailed Deadlines:")
        for framework, info in deadlines.items():
            status = "Passed" if info["passed"] else f"{info['days_remaining']} days remaining"
            print(f"  - {framework}: {info['date']} ({status})")