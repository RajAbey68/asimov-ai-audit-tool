"""
Bulletproof Demo Integration for ASIMOV AI Governance Audit Tool
This script safely integrates demo mode into the existing application
"""

import re

def integrate_demo_mode():
    """Integrate demo mode into the existing app.py safely"""
    
    # Read current app.py
    with open("app.py", "r") as f:
        content = f.read()
    
    # Add demo mode to insights generation
    if "def get_lifewise_insights():" in content:
        # Replace the insights generation with demo-safe version
        insights_pattern = r"(def get_lifewise_insights\(\):.*?return insights)"
        
        demo_insights_replacement = '''def get_lifewise_insights():
    """Generate sector-aware contextual insights for all controls"""
    if is_demo_mode():
        # Use bulletproof demo insights for stable presentations
        return demo_manager.get_demo_insights()
    
    # Production insight generation code (existing functionality)
    insights = []
    
    try:
        conn = get_db_connection()
        
        # Get all controls
        controls = conn.execute("""
            SELECT id, name, category, risk_level, control_question, framework
            FROM controls 
            ORDER BY id
        """).fetchall()
        
        for control in controls:
            try:
                # Generate safe insight
                insight = get_safe_insight(control['name'], control['category'])
                
                insights.append({
                    'control_id': control['id'],
                    'control_name': control['name'],
                    'category': control['category'],
                    'insight': insight,
                    'generated_date': datetime.datetime.now().isoformat()
                })
                
            except Exception as e:
                # Fallback insight for reliability
                insights.append({
                    'control_id': control['id'],
                    'control_name': control['name'],
                    'category': control['category'],
                    'insight': f"This {control['category']} control is essential for AI governance compliance and risk management.",
                    'generated_date': datetime.datetime.now().isoformat(),
                    'note': 'Generated using fallback method for demo stability'
                })
        
        conn.close()
        
    except Exception as e:
        print(f"Insights generation error: {e}")
        # Return empty list rather than failing
        insights = []
        
    return insights'''
        
        content = re.sub(insights_pattern, demo_insights_replacement, content, flags=re.DOTALL)
    
    # Add demo mode to PDF export
    if "def export_pdf" in content and "pdfkit" in content:
        # Add demo mode check for PDF export
        pdf_demo_check = '''
    # Demo mode safety check
    if is_demo_mode():
        demo_response = demo_manager.safe_pdf_export_message()
        flash(demo_response['message'], 'info')
        return redirect(url_for('question', session_id=session_id, question_index=question_index))
'''
        
        # Insert demo check at beginning of export_pdf function
        content = content.replace(
            'def export_pdf(session_id, question_index):\n    """Export the current audit question to PDF"""',
            'def export_pdf(session_id, question_index):\n    """Export the current audit question to PDF"""' + pdf_demo_check
        )
    
    # Add demo session creation route
    demo_route = '''
@app.route('/demo/create-session')
def create_demo_session():
    """Create a pre-populated demo session for presentations"""
    if is_demo_mode():
        session_id = demo_manager.create_demo_session()
        if session_id:
            flash('Demo session created successfully! Ready for presentation.', 'success')
            return redirect(url_for('question', session_id=session_id, question_index=0))
        else:
            flash('Demo session already exists or could not be created.', 'info')
            return redirect(url_for('index'))
    else:
        flash('Demo session creation is only available in demo mode.', 'warning')
        return redirect(url_for('index'))

@app.route('/demo/status')
def demo_status():
    """Get demo mode status"""
    return jsonify(demo_manager.get_demo_status_message())
'''
    
    # Add demo routes before the main block
    if 'if __name__ == \'__main__\':' in content:
        content = content.replace('if __name__ == \'__main__\':', demo_route + '\n\nif __name__ == \'__main__\':')
    
    # Write updated content
    with open("app.py", "w") as f:
        f.write(content)
    
    print("✅ Demo mode integrated successfully!")

def add_demo_ui_elements():
    """Add demo mode UI elements to templates"""
    
    # Add demo banner to index.html if it exists
    try:
        with open("templates/index.html", "r") as f:
            index_content = f.read()
        
        # Add demo mode banner
        demo_banner = '''
        {% if demo_status and demo_status.status == 'demo' %}
        <div class="alert alert-info mt-3" role="alert">
            <strong>{{ demo_status.message }}</strong>
            <div class="mt-2">
                <a href="/demo/create-session" class="btn btn-sm btn-outline-primary">Launch Demo Session</a>
                <small class="text-muted ms-2">Pre-populated with sample responses for smooth presentations</small>
            </div>
        </div>
        {% endif %}
        '''
        
        # Insert after the main heading
        if '<h1' in index_content and 'ASIMOV' in index_content:
            # Find the first closing div after the h1
            h1_pos = index_content.find('<h1')
            if h1_pos != -1:
                # Find the next </div> after the h1
                div_pos = index_content.find('</div>', h1_pos)
                if div_pos != -1:
                    index_content = index_content[:div_pos] + demo_banner + index_content[div_pos:]
        
        with open("templates/index.html", "w") as f:
            f.write(index_content)
            
        print("✅ Demo UI elements added to index.html")
        
    except FileNotFoundError:
        print("⚠️  index.html not found - demo banner will be added when template is created")

def run_bulletproof_integration():
    """Run the complete bulletproof demo integration"""
    print("🎯 Integrating Bulletproof Demo Mode...")
    print("-" * 50)
    
    print("1. Integrating demo mode into app.py...")
    integrate_demo_mode()
    
    print("2. Adding demo UI elements...")
    add_demo_ui_elements()
    
    print("3. Creating demo session...")
    from demo_mode import demo_manager
    demo_session = demo_manager.create_demo_session()
    if demo_session:
        print(f"   ✅ Demo session created: {demo_session}")
    
    print("\n🎉 Bulletproof Demo Mode Integration Complete!")
    print("\nDemo Features Available:")
    print("• Stable, pre-loaded insights that never fail")
    print("• Pre-populated demo session with sample responses")
    print("• Safe handling of PDF export and file uploads")
    print("• Demo mode banner for presentations")
    print("• /demo/create-session endpoint for quick setup")
    print("\nYour presentations will now be completely reliable!")

if __name__ == "__main__":
    run_bulletproof_integration()