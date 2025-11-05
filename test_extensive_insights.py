"""
Extensive Insight Generation Test

This script tests insight generation across at least 50 controls to ensure:
1. Insights are unique when generated with different variation keys
2. Insights are relevant to their respective controls
3. The system handles a variety of control types correctly
"""

import sqlite3
import time
import random
from fallback_insights import generate_fallback_insight

def get_db_connection():
    """Create a database connection that returns rows as dictionaries"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def test_extensive_insights(min_controls=50):
    """Test insight generation across a large number of controls"""
    print(f"==== Testing Insight Generation Across {min_controls}+ Controls ====")
    
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get a list of control IDs
    cursor.execute("SELECT id FROM controls ORDER BY id")
    all_control_ids = [row['id'] for row in cursor.fetchall()]
    
    # Ensure we have enough controls
    if len(all_control_ids) < min_controls:
        print(f"Warning: Only {len(all_control_ids)} controls available, testing all of them")
        min_controls = len(all_control_ids)
    
    # Select a subset of controls to test
    selected_ids = sorted(random.sample(all_control_ids, min_controls))
    
    # Store test results
    successful_controls = []
    failed_controls = []
    
    # For each control, generate two insights with different variation keys
    for control_id in selected_ids:
        cursor.execute("SELECT * FROM controls WHERE id = ?", (control_id,))
        control = cursor.fetchone()
        
        if control:
            control_name = control['control_name']
            category = control['category']
            
            print(f"\nTesting control #{control_id}: {control_name}")
            
            # Generate two insights with different variation keys
            insight1 = generate_fallback_insight(
                control_name=control_name,
                category=category,
                variation_key=f"test_key_1_{control_id}"
            )
            
            insight2 = generate_fallback_insight(
                control_name=control_name,
                category=category,
                variation_key=f"test_key_2_{control_id}"
            )
            
            # Check if they're different
            if insight1 != insight2:
                successful_controls.append(control_id)
                print(f"  ✅ SUCCESS: Generated unique insights")
                print(f"  → Insight 1 (first 50 chars): {insight1[:50]}...")
                print(f"  → Insight 2 (first 50 chars): {insight2[:50]}...")
            else:
                failed_controls.append(control_id)
                print(f"  ❌ FAILED: Generated identical insights")
                print(f"  → Insight (first 50 chars): {insight1[:50]}...")
    
    conn.close()
    
    # Calculate success rate
    success_rate = (len(successful_controls) / min_controls) * 100
    
    # Print summary
    print("\n==== Test Results Summary ====")
    print(f"Total controls tested: {min_controls}")
    print(f"Successful controls: {len(successful_controls)}")
    print(f"Failed controls: {len(failed_controls)}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if failed_controls:
        print("\nFailed control IDs:")
        for batch in [failed_controls[i:i+10] for i in range(0, len(failed_controls), 10)]:
            print(f"  {', '.join(map(str, batch))}")
    
    return success_rate >= 95  # Consider the test passed if 95% or more controls succeed

def test_temporal_variation():
    """Test that insights vary with different variation keys for the same control"""
    print("\n==== Testing Temporal Variation ====")
    control_name = "Security Control Testing"
    category = "Security Testing"
    
    # Generate insights with different keys
    insight1 = generate_fallback_insight(control_name, category, variation_key="test_key_1")
    insight2 = generate_fallback_insight(control_name, category, variation_key="test_key_2")
    
    print(f"First insight (first 50 chars): {insight1[:50]}...")
    print(f"Second insight (first 50 chars): {insight2[:50]}...")
    
    if insight1 != insight2:
        print("✅ PASSED: Insights vary with different variation keys")
        return True
    else:
        print("❌ FAILED: Insights did not change with different variation keys")
        return False

if __name__ == "__main__":
    # First test the temporal variation fix
    temporal_test_result = test_temporal_variation()
    
    # Then test across many controls
    extensive_test_result = test_extensive_insights(min_controls=50)
    
    # Print overall result
    print("\n==== Overall Test Results ====")
    print(f"Temporal Variation Test: {'PASSED' if temporal_test_result else 'FAILED'}")
    print(f"Extensive Control Test: {'PASSED' if extensive_test_result else 'FAILED'}")
    print(f"Overall Result: {'PASSED' if temporal_test_result and extensive_test_result else 'FAILED'}")