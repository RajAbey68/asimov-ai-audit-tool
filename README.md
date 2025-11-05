# ASIMOV AI Governance Audit Tool

**Version:** 1.0  
**Status:** Production Ready  
**Test Coverage:** 75% (6/8 comprehensive tests passing)

---

## Overview

The **ASIMOV AI Governance Audit Tool** is an enterprise-grade platform for conducting AI governance and compliance audits against international regulatory frameworks. It enables organizations to systematically evaluate their AI systems against **251 governance controls** across 5 major frameworks.

### Key Features

✅ **Intelligent Compliance Auditing** - 251 AI governance controls across EU AI Act, NIST AI RMF, ISO/IEC, GDPR, and SCF  
✅ **AI-Powered Insights** - Sector-specific guidance using OpenAI GPT-4 with authentic regulatory references  
✅ **Advanced Evidence Management** - Multi-format evidence collection with AI quality assessment  
✅ **Analytics & Reporting** - Visual dashboards, risk heatmaps, and ASIMOV Pillars tracking  
✅ **Implementation Roadmaps** - Sprint planning and backlog management for governance controls  
✅ **Enterprise-Ready** - RESTful APIs, multi-user support, and production deployment

---

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key (for AI-powered features)
- SQLite 3

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/asimov-ai-audit-tool.git
cd asimov-ai-audit-tool

# Install dependencies
pip install flask openai pandas python-docx pypdf2 weasyprint python-dateutil python-dotenv requests beautifulsoup4 openpyxl pytest werkzeug

# Set up environment variables
export OPENAI_API_KEY="your-openai-api-key"

# Initialize database (if needed)
python init_db.py

# Start the application
python bulletproof_startup.py
```

The application will be available at `http://localhost:5000`

---

## Documentation

📋 **[Executive Summary](ASIMOV_EXECUTIVE_SUMMARY.md)** - What this application does  
🏗️ **[Technical Design](ASIMOV_TECHNICAL_DESIGN.md)** - Complete architecture and database schema  
🔌 **[API Reference](ASIMOV_API_REFERENCE.md)** - Full API documentation with examples  

---

## Features

### 1. Intelligent Audit Management
- 251 AI governance controls covering all major regulatory frameworks
- Multi-framework support: EU AI Act, NIST AI RMF, ISO/IEC, GDPR, SCF
- Risk-based categorization (High Risk, General Risk)
- Industry-specific filtering (Healthcare, Financial Services, Government, Technology)
- Geographic region compliance (UK, EU, US, APAC)

### 2. AI-Powered Intelligence
- **Life-Wise Insights**: Sector-specific compliance guidance using OpenAI GPT-4
- Real-world regulatory references from MHRA, FCA, NIST, FDA, EBA, SEC, ICO
- Contextual recommendations based on sector and region
- Evidence evaluation with quality scoring and gap identification

### 3. Evidence Management
- Multi-format evidence collection (PDF, Word, URLs, notes)
- AI-powered evidence quality assessment
- File upload system with organized storage
- Evidence recency validation
- Comprehensive audit trail with timestamps

### 4. Analytics & Reporting
- **ASIMOV Report Dashboard** with visual compliance analytics
- Framework coverage analysis with gap identification
- Risk heatmaps showing priority areas
- ASIMOV Pillars performance tracking (Accountability, Security, Interpretability, Monitoring, Oversight, Verification)
- CSV/JSON data export

### 5. Implementation Roadmap Management
- Sprint planning and tracking
- Backlog management for controls requiring remediation
- Priority-based work item organization
- Effort estimation and team assignment

---

## Technology Stack

- **Backend**: Python 3.11 with Flask
- **Database**: SQLite (18 tables, 251 controls)
- **AI Integration**: OpenAI GPT-4 (gpt-4o)
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Testing**: pytest with comprehensive test suite

---

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...              # OpenAI API key for AI features

# Optional
FLASK_ENV=production               # production|development
DATABASE_URL=audit_controls.db     # SQLite database path
PORT=5000                          # Preferred port
HOST=0.0.0.0                       # Bind address
DEBUG=False                        # Debug mode (development only)
```

---

## Use Cases

### Healthcare AI Compliance Audit
A healthcare provider audits their AI-powered diagnostic system for MHRA compliance with sector-specific insights and CE marking documentation tracking.

### Financial Services AI Risk Assessment
A bank assesses their AI lending model against FCA and EBA guidelines with fairness testing reports and model documentation.

### Government AI Transparency Initiative
A government agency audits AI systems for NIST AI RMF compliance with impact assessments and transparency measures.

---

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest comprehensive_test_suite.py -v

# Run pre-release validation
pytest pre_release_test_suite.py -v

# Current test results: 75% pass rate (6/8 tests)
```

---

## Security

- Input validation and SQL injection prevention
- Environment-based API key management
- Session-based authentication
- Evidence file type validation
- Secure file upload handling
- No secrets in source code

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is proprietary software. All rights reserved.

---

## Support

For support, feature requests, or integration assistance:
- Create an issue in the GitHub repository
- Consult the [Technical Design](ASIMOV_TECHNICAL_DESIGN.md) documentation
- Review the [API Reference](ASIMOV_API_REFERENCE.md) for integration details

---

## Acknowledgments

- **Regulatory Frameworks**: EU AI Act, NIST AI RMF, ISO/IEC 42001, GDPR, SCF
- **AI Integration**: OpenAI GPT-4
- **Trusted References**: MHRA, FCA, NIST, FDA, EBA, SEC, ICO, NHS AI Lab

---

**Built with ❤️ for AI Governance Excellence**

