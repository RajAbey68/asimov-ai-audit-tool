"""
Test script for the Temporal Insight Variation system

This script demonstrates how insights change over time for the same control,
providing a more engaging and varied user experience.
"""

import sqlite3
import time
from temporal_insight_variation import initialize_variation_tracking, get_time_aware_insight

def get_db_connection():
    """Create a database connection with row factory"""
    conn = sqlite3.connect('audit_controls.db')
    conn.row_factory = sqlite3.Row
    return conn

def test_temporal_variation():
    """Test the temporal variation of insights for the same control"""
    print("\n" + "=" * 70)
    print("🧪 TESTING TEMPORAL INSIGHT VARIATION SYSTEM")
    print("=" * 70)
    
    # Initialize the tracking system
    initialize_variation_tracking()
    
    # Get a control for testing
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, control_name, category FROM controls LIMIT 1")
    control = cursor.fetchone()
    conn.close()
    
    if not control:
        print("❌ No controls found in the database. Please run the data loader first.")
        return
    
    control_id = control['id']
    control_name = control['control_name']
    category = control['category']
    
    print(f"📊 Testing with control: {control_name} (ID: {control_id})")
    print(f"📊 Category: {category}")
    print("\n" + "-" * 70)
    
    # Test variation 1 - initial insight
    print("🔄 Generating first variation")
    insight1 = get_time_aware_insight(
        control_name=control_name,
        control_id=control_id,
        category=category,
        sector="Financial Services",
        region="EU"
    )
    print("-" * 70)
    print(f"✅ VARIATION 1: {insight1}")
    print("-" * 70)
    
    # Test variation 2 - force new variation by updating the tracking data
    print("\n🔄 Forcing rotation to second variation...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE insight_variations SET view_count = ? WHERE control_id = ?",
        (10, control_id)  # Force rotation by setting view count high
    )
    conn.commit()
    conn.close()
    
    # Get the second variation
    insight2 = get_time_aware_insight(
        control_name=control_name,
        control_id=control_id,
        category=category,
        sector="Healthcare",
        region="US"
    )
    print("-" * 70)
    print(f"✅ VARIATION 2: {insight2}")
    print("-" * 70)
    
    # Test variation 3 - force new variation again
    print("\n🔄 Forcing rotation to third variation...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE insight_variations SET view_count = ? WHERE control_id = ?",
        (10, control_id)  # Force rotation by setting view count high
    )
    conn.commit()
    conn.close()
    
    # Get the third variation
    insight3 = get_time_aware_insight(
        control_name=control_name,
        control_id=control_id,
        category=category,
        sector="Manufacturing",
        region="APAC"
    )
    print("-" * 70)
    print(f"✅ VARIATION 3: {insight3}")
    print("-" * 70)
    
    # Check if variations are different
    variations_differ = (
        insight1 != insight2 and
        insight2 != insight3 and
        insight1 != insight3
    )
    
    # Report results
    print("\n" + "=" * 70)
    print("📊 TEMPORAL VARIATION TEST RESULTS")
    print("=" * 70)
    print(f"Control tested: {control_name}")
    print(f"Number of variations generated: 3")
    print(f"All variations are different: {'✅ YES' if variations_differ else '❌ NO'}")
    if not variations_differ:
        print("⚠️ Some variations were identical - check the variation logic.")
    print("=" * 70)

if __name__ == "__main__":
    test_temporal_variation()