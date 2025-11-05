
from flask import Flask
from lifewise_insight_engine import generate_lifewise_insight

app = Flask(__name__)

@app.route('/')
def index():
    return "ASIMOV-AI Life-Wise Insight Test Server is running."

@app.route('/test')
def test_insight():
    try:
        insight = generate_lifewise_insight(
            "AI Fairness Certification & Standards",
            "High",
            "Financial Services", 
            "UK",
            ["EU AI Act", "ISO 42001"]
        )
        return f"<h2>Life-Wise Insight Test</h2><pre>{insight}</pre>"
    except Exception as e:
        return f"<h2>Error</h2><p>Failed to generate insight: {str(e)}</p><p>Make sure your OPENAI_API_KEY is set in Replit Secrets.</p>"

@app.route('/test-multiple')
def test_multiple_insights():
    """Test multiple different controls"""
    controls = [
        ("AI Fairness Certification & Standards", "High", "Financial Services", "UK"),
        ("Model Performance Monitoring", "Medium", "Healthcare", "EU"),
        ("Data Privacy Impact Assessment", "High", "Technology", "US")
    ]
    
    results = []
    for control, risk, sector, region in controls:
        try:
            insight = generate_lifewise_insight(control, risk, sector, region, ["EU AI Act", "ISO 42001"])
            results.append(f"<h3>{control}</h3><p><strong>Sector:</strong> {sector} | <strong>Risk:</strong> {risk} | <strong>Region:</strong> {region}</p><pre>{insight}</pre><hr>")
        except Exception as e:
            results.append(f"<h3>{control}</h3><p>Error: {str(e)}</p><hr>")
    
    return f"<h2>Multiple Life-Wise Insights Test</h2>{''.join(results)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
