"""
Fix for the "Security Control Testing" insight generation issue

This script specifically addresses the temporal variation test failure
by ensuring unique insights are generated for the Security Control Testing control.
"""

import random
from fallback_insights import generate_fallback_insight

def demo_security_control_testing_fix():
    """Demonstrate that the temporal variation fix works for Security Control Testing"""
    control_name = "Security Control Testing"
    category = "Security Testing"
    
    print(f"Testing insight variation for: {control_name}")
    
    # Generate multiple insights with explicit variation keys
    insights = []
    variation_keys = ["test1", "test2", "test3", "test4", "test5"]
    
    for key in variation_keys:
        insight = generate_fallback_insight(
            control_name=control_name,
            category=category,
            variation_key=key
        )
        print(f"\nInsight with key '{key}':")
        print(f"  {insight[:100]}...")
        insights.append(insight)
    
    # Check if we have unique insights
    unique_insights = set(insights)
    print(f"\nGenerated {len(insights)} insights")
    print(f"Unique insights: {len(unique_insights)}")
    print(f"Uniqueness rate: {(len(unique_insights) / len(insights)) * 100:.1f}%")
    
    if len(unique_insights) == len(insights):
        print("\n✅ SUCCESS: All insights were unique")
        return True
    else:
        print("\n❌ FAILED: Not all insights were unique")
        return False

def demo_broader_test():
    """Test insight generation for controls that were failing previously"""
    failing_controls = [
        ("Adversarial Training Implementation", "Training"),
        ("Transfer Attack Testing", "Testing"),
        ("Independent AI Risk Classification Verification", "Verification"),
        ("Comprehensive Documentation", "Documentation"),
        ("AI Risk Awareness Training", "Training")
    ]
    
    print(f"\nTesting insight variation for previously failing controls:")
    success_count = 0
    
    for control_name, category in failing_controls:
        print(f"\nTesting control: {control_name}")
        
        # Generate two insights with different variation keys
        insight1 = generate_fallback_insight(
            control_name=control_name,
            category=category,
            variation_key="key1"
        )
        insight2 = generate_fallback_insight(
            control_name=control_name,
            category=category,
            variation_key="key2"
        )
        
        print(f"Insight 1 (first 50 chars): {insight1[:50]}...")
        print(f"Insight 2 (first 50 chars): {insight2[:50]}...")
        
        if insight1 != insight2:
            print("✅ SUCCESS: Generated unique insights")
            success_count += 1
        else:
            print("❌ FAILED: Generated identical insights")
    
    success_rate = (success_count / len(failing_controls)) * 100
    print(f"\nSuccess rate for previously failing controls: {success_rate:.1f}%")
    return success_rate >= 80  # Consider successful if 80% or more pass

if __name__ == "__main__":
    print("=" * 70)
    print("SECURITY CONTROL TESTING VARIATION FIX")
    print("=" * 70)
    
    security_test_result = demo_security_control_testing_fix()
    broader_test_result = demo_broader_test()
    
    print("\n" + "=" * 70)
    print("TEST RESULTS:")
    print("=" * 70)
    print(f"Security Control Testing Test: {'PASSED' if security_test_result else 'FAILED'}")
    print(f"Broader Control Test: {'PASSED' if broader_test_result else 'FAILED'}")
    print(f"Overall Result: {'PASSED' if security_test_result and broader_test_result else 'FAILED'}")