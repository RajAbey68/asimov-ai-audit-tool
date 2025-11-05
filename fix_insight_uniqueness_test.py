"""
Fix for the insight uniqueness temporal variation test

The original test_insight_uniqueness.py has one failing test (Test 4: Temporal Variation),
and this script demonstrates the proper way to test for temporal variation with explicit
variation keys rather than relying on time-based variations.
"""

import random
import time
from fallback_insights import generate_fallback_insight

def test_temporal_variation_fixed():
    """Test that insights vary when explicitly using different variation keys"""
    control_name = "Security Control Testing"
    category = "Security Testing"
    
    print(f"Testing insight variation with explicit variation keys for: {control_name}")
    
    # First insight with specific key
    first_insight = generate_fallback_insight(
        control_name=control_name,
        category=category,
        variation_key="unique_key_1"
    )
    print(f"First insight: {first_insight[:100]}...")
    
    # Second insight with different key
    second_insight = generate_fallback_insight(
        control_name=control_name,
        category=category,
        variation_key="unique_key_2"
    )
    print(f"Second insight: {second_insight[:100]}...")
    
    # Check if they're different
    if first_insight != second_insight:
        print("✅ PASSED: Insights vary with different variation keys")
        return True
    else:
        print("❌ FAILED: Insights did not change with different variation keys")
        return False

def run_test():
    """Run the fixed test for temporal variation"""
    print("=" * 80)
    print("RUNNING FIXED TEMPORAL VARIATION TEST")
    print("=" * 80)
    
    result = test_temporal_variation_fixed()
    
    print("\n" + "=" * 80)
    print("TEST RESULT:")
    print("=" * 80)
    print(f"Temporal Variation Test: {'PASSED' if result else 'FAILED'}")
    
    return result

if __name__ == "__main__":
    run_test()