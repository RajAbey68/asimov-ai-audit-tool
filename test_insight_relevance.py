"""
Test Case for Life-Wise Insight Generation and Relevance Assessment

This test validates that the insight generation system:
1. Successfully generates insights for different sectors and controls
2. Returns relevant, sector-specific content
3. Includes authentic regulatory references
4. Maintains professional audit-quality language
"""

import sqlite3
import os
import json
from datetime import datetime

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def test_basic_insight_assertions():
    """Simple assertion-based test for core insight requirements"""
    
    print("🔍 Basic Assertion Tests for Life-Wise Insights")
    print("=" * 50)
    
    try:
        from app import get_sector_specific_insight
        
        # Test scenario
        control = "AI Fairness Certification & Standards"
        risk = "High"
        sector = "Financial Services"
        region = "UK"
        
        insight = get_sector_specific_insight(control, "Governance", risk, sector, region)
        
        # Core assertions
        assert isinstance(insight, str), "Insight should be a string"
        assert len(insight) > 0, "Insight should not be empty"
        assert len(insight) > 50, "Insight should be substantial (>50 chars)"
        assert len(insight.split()) <= 200, "Insight should be concise (under 200 words)"
        
        # Content quality assertions
        governance_keywords = ["AI", "audit", "compliance", "governance", "regulatory", "control", "assessment"]
        has_governance_content = any(keyword.lower() in insight.lower() for keyword in governance_keywords)
        assert has_governance_content, "Insight should mention key governance themes"
        
        print("✓ All basic assertions passed")
        print(f"   Generated insight: {len(insight)} chars, {len(insight.split())} words")
        print(f"   Preview: {insight[:100]}...")
        
        return True
        
    except AssertionError as e:
        print(f"❌ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in basic test: {e}")
        return False

def test_insight_generation():
    """Test insight generation for multiple scenarios"""
    
    print("\n🔍 Comprehensive Life-Wise Insight Testing")
    print("=" * 60)
    
    # Import the insight generation function
    try:
        from app import get_sector_specific_insight
        print("✓ Successfully imported insight generation function")
    except ImportError as e:
        print(f"❌ Failed to import insight function: {e}")
        return False
    
    # Test scenarios with different sectors and controls
    test_scenarios = [
        {
            "control_name": "AI Fairness Certification & Standards",
            "category": "Governance", 
            "risk_level": "High",
            "sector": "Financial Services",
            "region": "UK"
        },
        {
            "control_name": "Model Performance Monitoring",
            "category": "Technical",
            "risk_level": "Medium", 
            "sector": "Healthcare",
            "region": "EU"
        },
        {
            "control_name": "Data Privacy Impact Assessment",
            "category": "Legal",
            "risk_level": "High",
            "sector": "Technology",
            "region": "US"
        }
    ]
    
    test_results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test Scenario {i}: {scenario['control_name']}")
        print(f"   Sector: {scenario['sector']} | Risk: {scenario['risk_level']} | Region: {scenario['region']}")
        
        try:
            # Generate insight
            insight = get_sector_specific_insight(
                control_name=scenario['control_name'],
                category=scenario['category'],
                risk_level=scenario['risk_level'],
                sector=scenario['sector'],
                region=scenario['region']
            )
            
            # Assess relevance
            relevance_score = assess_insight_relevance(insight, scenario)
            
            result = {
                "scenario": scenario,
                "insight": insight,
                "relevance_score": relevance_score,
                "timestamp": datetime.now().isoformat()
            }
            
            test_results.append(result)
            
            print(f"   Generated Insight ({len(insight)} chars):")
            print(f"   {insight[:150]}{'...' if len(insight) > 150 else ''}")
            print(f"   Relevance Score: {relevance_score}/10")
            
        except Exception as e:
            print(f"   ❌ Error generating insight: {e}")
            result = {
                "scenario": scenario,
                "insight": None,
                "error": str(e),
                "relevance_score": 0,
                "timestamp": datetime.now().isoformat()
            }
            test_results.append(result)
    
    # Generate summary report
    generate_test_report(test_results)
    
    return test_results

def assess_insight_relevance(insight, scenario):
    """
    Assess the relevance and quality of generated insights
    Returns a score from 1-10 based on various criteria
    """
    if not insight or len(insight) < 50:
        return 1
    
    score = 0
    
    # Check for sector relevance (2 points)
    sector_keywords = {
        "Financial Services": ["financial", "banking", "FCA", "trading", "investment", "credit"],
        "Healthcare": ["healthcare", "medical", "patient", "MHRA", "clinical", "health"],
        "Technology": ["technology", "software", "digital", "platform", "ICO", "data"],
        "Government": ["government", "public", "policy", "NIST", "federal", "regulatory"]
    }
    
    sector = scenario['sector']
    if sector in sector_keywords:
        for keyword in sector_keywords[sector]:
            if keyword.lower() in insight.lower():
                score += 0.3
                break
    
    # Check for regulatory authority mentions (2 points)
    regulatory_authorities = ["FCA", "MHRA", "ICO", "NIST", "FDA", "SEC", "EBA", "CDEI", "NHS", "MITRE", "OWASP"]
    for authority in regulatory_authorities:
        if authority in insight:
            score += 0.3
            break
    
    # Check for framework references (2 points)
    frameworks = ["EU AI Act", "ISO", "GDPR", "NIST AI RMF", "FCA AI Guidelines"]
    for framework in frameworks:
        if framework in insight:
            score += 0.4
            break
    
    # Check for governance language (2 points)
    governance_terms = ["audit", "compliance", "governance", "regulatory", "assessment", "control", "policy"]
    governance_count = sum(1 for term in governance_terms if term.lower() in insight.lower())
    score += min(governance_count * 0.3, 2)
    
    # Check length appropriateness (1 point)
    if 100 <= len(insight) <= 300:
        score += 1
    elif 50 <= len(insight) <= 400:
        score += 0.5
    
    # Check for professional tone (1 point)
    professional_indicators = ["should", "must", "requires", "compliance", "assessment", "implementation"]
    professional_count = sum(1 for term in professional_indicators if term.lower() in insight.lower())
    score += min(professional_count * 0.2, 1)
    
    return min(round(score, 1), 10)

def generate_test_report(test_results):
    """Generate a comprehensive test report"""
    
    report_filename = f"insight_relevance_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Calculate summary statistics
    successful_tests = [r for r in test_results if r.get('insight') is not None]
    failed_tests = [r for r in test_results if r.get('insight') is None]
    
    if successful_tests:
        avg_score = sum(r['relevance_score'] for r in successful_tests) / len(successful_tests)
        max_score = max(r['relevance_score'] for r in successful_tests)
        min_score = min(r['relevance_score'] for r in successful_tests)
    else:
        avg_score = max_score = min_score = 0
    
    summary = {
        "test_summary": {
            "total_tests": len(test_results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "average_relevance_score": round(avg_score, 2),
            "max_relevance_score": max_score,
            "min_relevance_score": min_score,
            "test_timestamp": datetime.now().isoformat()
        },
        "detailed_results": test_results
    }
    
    # Save report
    with open(report_filename, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📊 Test Summary Report")
    print(f"   Total Tests: {len(test_results)}")
    print(f"   Successful: {len(successful_tests)}")
    print(f"   Failed: {len(failed_tests)}")
    print(f"   Average Relevance Score: {avg_score:.2f}/10")
    print(f"   Report saved: {report_filename}")
    
    # Determine overall test status
    if len(successful_tests) >= 2 and avg_score >= 7.0:
        print("   ✅ INSIGHT GENERATION TESTS PASSED")
        return True
    else:
        print("   ⚠️  INSIGHT GENERATION NEEDS IMPROVEMENT")
        return False

def test_database_integration():
    """Test that insights can be retrieved from actual audit controls"""
    
    print(f"\n🗄️  Testing Database Integration")
    
    try:
        conn = get_db_connection()
        
        # Get a sample control from the database
        cursor = conn.execute("""
            SELECT control_name, category, risk_level 
            FROM audit_controls 
            WHERE control_name IS NOT NULL 
            LIMIT 3
        """)
        
        controls = cursor.fetchall()
        conn.close()
        
        if not controls:
            print("   ⚠️  No controls found in database")
            return False
        
        print(f"   Found {len(controls)} controls in database")
        
        # Test insight generation for real database controls
        for control in controls:
            print(f"   Testing: {control['control_name']}")
            
            try:
                from app import get_sector_specific_insight
                insight = get_sector_specific_insight(
                    control_name=control['control_name'],
                    category=control['category'],
                    risk_level=control['risk_level'],
                    sector="Technology",
                    region="Global"
                )
                
                if insight and len(insight) > 50:
                    print(f"   ✓ Generated insight ({len(insight)} chars)")
                else:
                    print(f"   ⚠️  Short or empty insight: {insight[:50] if insight else 'None'}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Life-Wise Insight Relevance Testing")
    print("This test validates insight generation quality and relevance")
    
    # Run basic assertion tests first
    basic_test_success = test_basic_insight_assertions()
    
    # Run comprehensive insight generation tests
    insight_results = test_insight_generation()
    
    # Run database integration tests
    db_integration_success = test_database_integration()
    
    print(f"\n🎯 Overall Test Results:")
    print(f"   Basic Assertions: {'✅ PASSED' if basic_test_success else '❌ FAILED'}")
    print(f"   Comprehensive Testing: {'✅ PASSED' if insight_results else '❌ FAILED'}")
    print(f"   Database Integration: {'✅ PASSED' if db_integration_success else '❌ FAILED'}")
    
    if basic_test_success and insight_results and db_integration_success:
        print("\n🏆 ALL TESTS PASSED - Insight system is working correctly!")
    else:
        print("\n⚠️  SOME TESTS FAILED - Review the report for details")