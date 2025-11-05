"""
Test Case for Life-Wise Insight Generation Uniqueness

This script verifies that:
1. Multiple calls to generate insights for the same control produce different results
2. Insights across different controls are unique and relevant to that specific control
3. The 'Generate New Insight' button actually produces new content

Usage:
    python test_insight_uniqueness.py
"""

import sqlite3
import json
import time
from fallback_insights import generate_fallback_insight

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def test_insight_uniqueness_for_control(control_name, category, count=5):
    """Test that multiple generations for the same control produce different insights"""
    print(f"\nTesting insight uniqueness for: {control_name}")
    
    # Generate multiple insights for the same control
    insights = []
    for i in range(count):
        # Use timestamp as variation key to ensure differences
        variation_key = str(time.time() + i)
        insight = generate_fallback_insight(
            control_name=control_name,
            category=category,
            variation_key=variation_key
        )
        insights.append(insight)
        
        # Brief delay to ensure timestamp changes
        time.sleep(0.01)
    
    # Check uniqueness by comparing each insight with others
    unique_insights = set(insights)
    uniqueness_percentage = (len(unique_insights) / len(insights)) * 100
    
    print(f"  Generated {count} insights")
    print(f"  Unique insights: {len(unique_insights)}")
    print(f"  Uniqueness rate: {uniqueness_percentage:.1f}%")
    
    # Fail if less than 90% are unique
    if uniqueness_percentage < 90:
        print("  ❌ FAILED: Too many duplicate insights")
        for i, insight in enumerate(insights):
            print(f"  Insight {i+1} (first 50 chars): {insight[:50]}...")
        return False
    else:
        print("  ✅ PASSED: Insights are sufficiently unique")
        return True

def test_control_specific_relevance(sample_size=10):
    """Test that insights are relevant to their specific controls"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get a sample of controls to test
    cursor.execute("SELECT * FROM controls ORDER BY RANDOM() LIMIT ?", (sample_size,))
    controls = cursor.fetchall()
    conn.close()
    
    print(f"\nTesting control-specific relevance across {sample_size} controls")
    
    results = []
    for control in controls:
        control_name = control['control_name']
        category = control['category']
        
        # Generate an insight for this control
        insight = generate_fallback_insight(control_name, category)
        
        # Check if the control name appears in the insight
        contains_control_name = control_name.lower() in insight.lower()
        
        # Basic check for relevance - the control name should be mentioned
        results.append({
            'control_id': control['id'],
            'control_name': control_name,
            'contains_control_name': contains_control_name,
            'first_50_chars': insight[:50] + '...'
        })
    
    # Print results
    success = True
    for result in results:
        if result['contains_control_name']:
            print(f"  ✅ Control {result['control_id']}: {result['control_name']} - Relevant")
        else:
            print(f"  ❌ Control {result['control_id']}: {result['control_name']} - Not clearly relevant")
            success = False
        print(f"     Insight starts with: {result['first_50_chars']}")
    
    return success

def test_insight_variation_over_time():
    """Test that repeated generation of insights shows variation over time"""
    control_name = "Security Control Testing"
    category = "Security Testing"
    
    print(f"\nTesting insight variation over time for: {control_name}")
    
    # Explicitly use different variation keys to ensure different outputs
    # First insight with timestamp as key
    first_insight = generate_fallback_insight(
        control_name=control_name, 
        category=category,
        variation_key="test_key_1"
    )
    print(f"  First insight: {first_insight[:100]}...")
    
    # Second insight with different variation key
    second_insight = generate_fallback_insight(
        control_name=control_name, 
        category=category,
        variation_key="test_key_2"
    )
    print(f"  Second insight: {second_insight[:100]}...")
    
    # Check if they're different
    if first_insight != second_insight:
        print("  ✅ PASSED: Insights vary with different variation keys")
        return True
    else:
        print("  ❌ FAILED: Insights did not change with different variation keys")
        return False

def run_all_tests():
    """Run all insight uniqueness and relevance tests"""
    print("=" * 80)
    print("RUNNING LIFE-WISE INSIGHT UNIQUENESS TESTS")
    print("=" * 80)
    
    # Test 1: Multiple generations for a single hardcoded control
    test1 = test_insight_uniqueness_for_control("AI Security Controls", "Security Controls", count=5)
    
    # Test 2: Multiple generations for a different control
    test2 = test_insight_uniqueness_for_control("Model Risk Assessment", "Risk Management", count=5)
    
    # Test 3: Check that insights are relevant to their controls
    test3 = test_control_specific_relevance(sample_size=10)
    
    # Test 4: Verify insights change over time
    test4 = test_insight_variation_over_time()
    
    # Overall results
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Test 1 - Single Control Uniqueness: {'PASSED' if test1 else 'FAILED'}")
    print(f"Test 2 - Different Control Uniqueness: {'PASSED' if test2 else 'FAILED'}")
    print(f"Test 3 - Control-Specific Relevance: {'PASSED' if test3 else 'FAILED'}")
    print(f"Test 4 - Temporal Variation: {'PASSED' if test4 else 'FAILED'}")
    
    all_passed = test1 and test2 and test3 and test4
    print("\nOVERALL RESULT: " + ("PASSED ✅" if all_passed else "FAILED ❌"))
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()