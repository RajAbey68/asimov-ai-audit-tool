# ASIMOV AI Governance Audit Tool
## Technical Design Document

**Version:** 1.0  
**Document Date:** November 5, 2025  
**Status:** Production Ready

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Database Schema](#database-schema)
4. [Application Components](#application-components)
5. [AI Integration Architecture](#ai-integration-architecture)
6. [Security & Performance](#security--performance)
7. [Deployment Architecture](#deployment-architecture)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Audit UI     │ Dashboard    │ Admin Interface          │ │
│  │ (Bootstrap 5)│ (Charts.js)  │ (DB Management)          │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER (Flask)                  │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Main App     │ Roadmap Mgmt │ Evidence Evaluation      │ │
│  │ (app.py)     │ (Blueprint)  │ (Blueprint)              │ │
│  ├──────────────┼──────────────┼──────────────────────────┤ │
│  │ Report       │ DB Admin     │ Demo Mode                │ │
│  │ Dashboard    │ (Blueprint)  │ (Blueprint)              │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ Audit Engine │ Evidence     │ Insight Generation       │ │
│  │              │ Handler      │ (OpenAI Integration)     │ │
│  ├──────────────┼──────────────┼──────────────────────────┤ │
│  │ Sector Filter│ Reference    │ Temporal Variation       │ │
│  │              │ Engine       │ Engine                   │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ SQLite DB    │ Evidence     │ Sector References        │ │
│  │ (18 Tables)  │ Files        │ (JSON)                   │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  EXTERNAL INTEGRATIONS                       │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ OpenAI GPT-4 │ Regulatory   │ Export Services          │ │
│  │ API          │ References   │ (CSV, JSON, PDF)         │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns

- **MVC Pattern**: Separation of routes (controllers), business logic (models), and templates (views)
- **Blueprint Architecture**: Modular Flask blueprints for roadmap management, database admin, evidence evaluation
- **Repository Pattern**: Database connection abstraction via `get_db_connection()`
- **Strategy Pattern**: Multiple insight generation strategies (AI-powered, fallback, demo mode)
- **Decorator Pattern**: Route protection and session management

---

## Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web Framework | Flask | 2.3+ | Core HTTP routing and request handling |
| Programming Language | Python | 3.11 | Application logic and business rules |
| Database | SQLite | 3 | Data persistence and query engine |
| AI Engine | OpenAI GPT-4 | gpt-4o | Insight generation and evidence evaluation |
| ORM | Raw SQL | N/A | Direct database access for performance |

### Frontend Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| CSS Framework | Bootstrap | 5.x | Responsive UI components |
| JavaScript | Vanilla JS | Client-side interactivity |
| Templating | Jinja2 | Server-side HTML rendering |
| Icons | Font Awesome | UI iconography |

### Python Dependencies

```python
# Core Web Framework
flask==2.3.x
werkzeug==2.3.x

# AI Integration
openai==1.x.x

# Data Processing
pandas==2.x.x
openpyxl==3.x.x

# Document Processing
python-docx==0.8.x
pypdf2==3.x.x
beautifulsoup4==4.x.x

# PDF Generation
weasyprint==59.x

# Testing
pytest==7.x.x

# Utilities
python-dateutil==2.x.x
python-dotenv==1.x.x
requests==2.x.x
```

### System Dependencies

```
- Python 3.11
- SQLite 3
- wkhtmltopdf (for PDF generation)
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  frameworks │      │   controls   │      │  documents  │
│─────────────│      │──────────────│      │─────────────│
│ id (PK)     │      │ id (PK)      │      │ id (PK)     │
│ name        │      │ control_name │      │ name        │
│ description │      │ category     │      │ url         │
└─────────────┘      │ framework    │      │ description │
                     │ risk_level   │      └─────────────┘
                     │ description  │
                     └──────────────┘
                            │
                            │ 1:N
                            ↓
                  ┌──────────────────┐
                  │ audit_sessions   │
                  │──────────────────│
                  │ session_id (PK)  │
                  │ session_name     │
                  │ framework_filter │
                  │ category_filter  │
                  │ risk_level_filter│
                  │ sector_filter    │
                  │ region_filter    │
                  │ session_date     │
                  └──────────────────┘
                            │
                            │ 1:N
                            ↓
                  ┌──────────────────┐
                  │ audit_responses  │
                  │──────────────────│
                  │ id (PK)          │
                  │ session_id (FK)  │
                  │ control_id (FK)  │
                  │ response         │
                  │ response_score   │
                  │ evidence         │
                  │ evidence_notes   │
                  │ evidence_date    │
                  │ confidence       │
                  │ evaluation_text  │
                  │ evaluation_status│
                  │ created_at       │
                  └──────────────────┘
                      │           │
              ┌───────┘           └───────┐
              │ 1:N                   1:N │
              ↓                           ↓
    ┌─────────────────┐       ┌─────────────────┐
    │ evidence_urls   │       │ evidence_files  │
    │─────────────────│       │─────────────────│
    │ id (PK)         │       │ id (PK)         │
    │ response_id (FK)│       │ response_id (FK)│
    │ url             │       │ filename        │
    └─────────────────┘       │ file_path       │
                              │ upload_date     │
                              └─────────────────┘

┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│  roadmaps   │      │   sprints    │      │backlog_items │
│─────────────│      │──────────────│      │──────────────│
│ id (PK)     │──────│ id (PK)      │──────│ id (PK)      │
│ name        │ 1:N  │ roadmap_id FK│ 1:N  │ roadmap_id FK│
│ description │      │ name         │      │ sprint_id FK │
│ owner       │      │ start_date   │      │ control_id FK│
│ status      │      │ end_date     │      │ title        │
│ created_date│      │ status       │      │ priority     │
└─────────────┘      └──────────────┘      │ status       │
                                            │ assigned_to  │
                                            │ effort_est   │
                                            └──────────────┘

┌─────────────┐      ┌──────────────┐
│  sectors    │      │   regions    │
│─────────────│      │──────────────│
│ id (PK)     │      │ id (PK)      │
│ name        │      │ name         │
│ description │      │ description  │
│ region_id FK│──────│ is_standard  │
│ is_standard │      └──────────────┘
└─────────────┘
```

### Core Tables Specification

#### 1. **controls** (251 rows)
Primary table containing AI governance controls.

```sql
CREATE TABLE controls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    control_name TEXT,           -- Control title (e.g., "AI Risk Assessment Process")
    category TEXT,               -- Category (Security, Data, Monitoring, etc.)
    framework TEXT,              -- Source framework (EU AI Law, NIST, ISO, etc.)
    explainability TEXT,         -- Explainability requirement level
    description TEXT,            -- Detailed control description
    evidence TEXT,               -- Suggested evidence types
    risk_level TEXT              -- Risk classification (High Risk, General Risk)
);
```

**Sample Data:**
- 251 controls across 5 frameworks
- Categories: Security, Data Protection, Monitoring, Transparency, Oversight, Testing
- Risk Levels: High Risk (AI systems with significant impact), General Risk (standard AI systems)

#### 2. **frameworks** (5 rows)
Reference table for regulatory frameworks.

```sql
CREATE TABLE frameworks (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,            -- Framework name
    description TEXT             -- Framework description
);
```

**Supported Frameworks:**
1. EU AI Act (2023)
2. NIST AI Risk Management Framework
3. ISO/IEC 42001 AI Management System
4. GDPR Article 22 (Automated Decision-Making)
5. Secure Controls Framework (SCF)

#### 3. **audit_sessions**
Tracks individual audit sessions with filtering criteria.

```sql
CREATE TABLE audit_sessions (
    session_id TEXT PRIMARY KEY,
    session_name TEXT,
    framework_filter TEXT,       -- Selected framework
    framework_pattern TEXT,      -- SQL LIKE pattern for filtering
    category_filter TEXT,        -- Selected category
    risk_level_filter TEXT,      -- Selected risk level
    sector_filter TEXT,          -- Industry sector (Healthcare, Finance, etc.)
    region_filter TEXT,          -- Geographic region (UK, EU, US, etc.)
    session_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. **audit_responses**
Stores responses for each control within an audit session.

```sql
CREATE TABLE audit_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    control_id INTEGER,
    response TEXT,               -- Compliance status
    response_score INTEGER,      -- 1-5 compliance score
    evidence TEXT,               -- Primary evidence description
    evidence_notes TEXT,         -- Detailed evidence notes
    evidence_date TEXT,          -- Evidence collection/validation date
    confidence INTEGER,          -- Confidence level (1-5)
    evaluation_text TEXT,        -- AI evaluation summary
    evaluation_status TEXT,      -- AI evaluation status
    confidence_level TEXT,       -- AI confidence assessment
    evaluation_date TEXT,        -- AI evaluation timestamp
    created_at TEXT,
    FOREIGN KEY (session_id) REFERENCES audit_sessions(session_id),
    FOREIGN KEY (control_id) REFERENCES controls(id)
);
```

#### 5. **evidence_urls**
Stores URL references for evidence.

```sql
CREATE TABLE evidence_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER,
    url TEXT NOT NULL,
    FOREIGN KEY (response_id) REFERENCES audit_responses(id)
);
```

#### 6. **evidence_files**
Tracks uploaded evidence files.

```sql
CREATE TABLE evidence_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER,
    filename TEXT NOT NULL,      -- Original filename
    file_path TEXT NOT NULL,     -- Server storage path
    upload_date TEXT NOT NULL,
    FOREIGN KEY (response_id) REFERENCES audit_responses(id)
);
```

**File Storage Structure:**
```
evidence_files/
  └── response_{response_id}/
      ├── {uuid}.pdf
      ├── {uuid}.docx
      └── {uuid}.jpg
```

#### 7. **roadmaps**
Implementation roadmaps for governance controls.

```sql
CREATE TABLE roadmaps (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    owner TEXT,
    status TEXT DEFAULT 'Active',
    created_date TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 8. **sprints**
Sprint planning for roadmap implementation.

```sql
CREATE TABLE sprints (
    id TEXT PRIMARY KEY,
    roadmap_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    start_date TEXT,
    end_date TEXT,
    status TEXT DEFAULT 'Planned',
    FOREIGN KEY (roadmap_id) REFERENCES roadmaps(id)
);
```

#### 9. **backlog_items**
Backlog tracking for control implementation.

```sql
CREATE TABLE backlog_items (
    id TEXT PRIMARY KEY,
    roadmap_id TEXT NOT NULL,
    sprint_id TEXT,
    control_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'Backlog',
    priority TEXT DEFAULT 'Medium',
    assigned_to TEXT,
    effort_estimate INTEGER,
    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (roadmap_id) REFERENCES roadmaps(id),
    FOREIGN KEY (sprint_id) REFERENCES sprints(id),
    FOREIGN KEY (control_id) REFERENCES controls(id)
);
```

#### 10. **sectors**
Industry sector definitions.

```sql
CREATE TABLE sectors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    region_id INTEGER,
    is_standard BOOLEAN DEFAULT 0,
    FOREIGN KEY (region_id) REFERENCES regions(id)
);
```

**Standard Sectors:**
- Healthcare
- Financial Services
- Government & Public Sector
- Technology & Software
- Education
- Manufacturing & Industrial
- Retail & E-commerce

#### 11. **regions**
Geographic region definitions for regulatory compliance.

```sql
CREATE TABLE regions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_standard BOOLEAN DEFAULT 0
);
```

**Standard Regions:**
- United Kingdom (UK)
- European Union (EU)
- United States (US)
- Asia-Pacific (APAC)
- Global

#### 12. **reference_documents**
Regulatory reference document library.

```sql
CREATE TABLE reference_documents (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    year TEXT,
    url TEXT,
    sector TEXT,
    description TEXT,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 13. **insight_variations**
Tracks temporal variation of insights to prevent repetition.

```sql
CREATE TABLE insight_variations (
    control_id INTEGER PRIMARY KEY,
    last_generated_at TEXT,
    view_count INTEGER DEFAULT 0,
    rotation_index INTEGER DEFAULT 0,
    variation_history TEXT,      -- JSON array of previous insights
    FOREIGN KEY (control_id) REFERENCES controls(id)
);
```

#### 14. **framework_mapping**
Maps user-facing framework names to database search patterns.

```sql
CREATE TABLE framework_mapping (
    framework_name TEXT PRIMARY KEY,
    search_pattern TEXT
);
```

**Example Mappings:**
```
EU AI Act (2023) → %EU AI%
NIST AI RMF → %NIST%
ISO/IEC 42001 → %ISO%
```

---

## Application Components

### Component Architecture

```
asimov_audit_tool/
├── app.py                          # Main Flask application
├── bulletproof_startup.py          # Production startup with validation
├── config.py                       # Configuration management
│
├── Core Modules/
│   ├── db_admin.py                 # Database administration blueprint
│   ├── roadmap_management.py       # Roadmap & sprint management blueprint
│   ├── asimov_report_dashboard.py  # Analytics & reporting blueprint
│   ├── evidence_evaluation_engine.py # AI evidence evaluation
│   ├── evidence_handler.py         # Evidence file/URL management
│   ├── sector_filter.py            # Sector-specific filtering
│   └── demo_mode.py                # Professional demo mode
│
├── AI Integration/
│   ├── generate_enhanced_insights.py      # OpenAI GPT-4 integration
│   ├── authentic_sector_insights.py       # Sector-specific insights
│   ├── trusted_reference_engine.py        # Regulatory reference system
│   ├── temporal_insight_variation.py      # Insight rotation logic
│   └── fallback_insights.py               # Non-AI fallback system
│
├── Database/
│   ├── db_operations.py            # Core database operations
│   ├── init_db.py                  # Database initialization
│   └── audit_controls.db           # SQLite database file
│
├── Templates/
│   ├── index.html                  # Homepage & audit creation
│   ├── question.html               # Audit question interface
│   ├── summary.html                # Audit summary page
│   ├── roadmap/                    # Roadmap management templates
│   ├── report/                     # Report dashboard templates
│   └── db_admin/                   # Database admin templates
│
├── Static Assets/
│   ├── evidence_files/             # Uploaded evidence storage
│   └── sector_references.json      # Sector regulatory references
│
└── Testing/
    ├── comprehensive_test_suite.py  # Full integration tests
    ├── pre_release_test_suite.py    # Pre-deployment validation
    └── test_*.py                    # Component-specific tests
```

### Core Application Modules

#### 1. **app.py** - Main Flask Application

**Responsibilities:**
- Flask application initialization and configuration
- Route registration and request handling
- Blueprint integration
- Session management
- Database connection pooling

**Key Functions:**
```python
def get_db_connection()              # Database connection factory
def get_available_frameworks()       # Framework enumeration
def get_sector_specific_insight()    # AI insight generation
def start_audit()                    # Create new audit session
def question()                       # Display audit question
def submit()                         # Process audit response
def summary()                        # Generate audit summary
```

#### 2. **bulletproof_startup.py** - Production Startup

**Responsibilities:**
- Database integrity validation
- Port conflict detection and resolution
- Health check endpoint registration
- Graceful error handling
- Logging configuration

**Features:**
- Automatic port selection (5000, 5001, 5002, etc.)
- Database schema validation
- Control count verification (ensures 251 controls present)
- Framework count verification (ensures 5 frameworks present)

#### 3. **evidence_evaluation_engine.py** - AI Evidence Assessment

**Class:** `EvidenceEvaluationEngine`

**Responsibilities:**
- AI-powered evidence quality assessment
- Document text extraction (PDF, DOCX, TXT)
- URL content analysis
- Evidence recency validation
- Confidence scoring
- Regulatory sufficiency evaluation

**Key Methods:**
```python
def extract_text_from_file(file_content, file_type)
def extract_text_from_url(url)
def check_evidence_recency(evidence_date, control_category)
def generate_ai_evaluation(control_info, evidence_data)
def evaluate_evidence(control_id, session_id, evidence_data)
```

**AI Evaluation Process:**
1. Extract text from evidence (files, URLs, notes)
2. Construct evaluation prompt with control context
3. Call OpenAI GPT-4 with trusted reference enhancement
4. Parse AI response for quality score and recommendations
5. Store evaluation results in database
6. Return structured evaluation to frontend

#### 4. **asimov_report_dashboard.py** - Analytics Engine

**Responsibilities:**
- Compliance analytics calculation
- Heatmap generation
- Framework coverage analysis
- ASIMOV Pillars performance tracking
- CSV/JSON export generation

**Key Functions:**
```python
def analyze_audit_coverage()         # Overall audit statistics
def get_session_detailed_report()    # Session-specific analytics
def generate_heatmap_data()          # Risk heatmap matrix
def export_session_csv()             # CSV export
def calculate_asimov_pillars()       # ASIMOV framework analysis
```

**ASIMOV Pillars Mapping:**
- **A**ccountability: Data, Privacy, Information controls
- **S**ecurity: Security, Defense, Attack controls
- **I**nterpretability: Transparency, Explainability controls
- **M**onitoring: Monitor, Detect, Audit controls
- **O**versight: Oversight, Governance, Management controls
- **V**erification: Validation, Test, Verification controls

#### 5. **roadmap_management.py** - Implementation Planning

**Blueprint:** `roadmap_bp`

**Responsibilities:**
- Roadmap creation and management
- Sprint planning and tracking
- Backlog item management
- Control-to-roadmap mapping
- Team assignment and effort estimation

**Routes:**
```python
/roadmap/list                        # List all roadmaps
/roadmap/create                      # Create new roadmap
/roadmap/<id>                        # View roadmap details
/roadmap/<id>/create-sprint          # Create sprint
/roadmap/<id>/add-to-backlog         # Add backlog item
/roadmap/<id>/update-sprint/<sid>    # Update sprint
/roadmap/add-from-control/<cid>      # Add control to roadmap
```

#### 6. **db_admin.py** - Database Administration

**Blueprint:** `db_admin`

**Responsibilities:**
- Database table inspection
- Custom SQL query execution
- Data export functionality
- Database optimization
- Audit session analysis

**Routes:**
```python
/db_admin/                           # Admin dashboard
/db_admin/tables/<table_name>        # View table contents
/db_admin/query                      # Execute SQL query
/db_admin/export                     # Export data
/db_admin/optimize                   # Database optimization
/db_admin/audit_analysis/<session_id> # Audit analysis
```

---

## AI Integration Architecture

### OpenAI GPT-4 Integration

#### 1. **Life-Wise Insights Generation**

**Purpose:** Generate sector-specific, contextual compliance insights for each control.

**Process Flow:**
```
User selects control
       ↓
Extract context:
  - Control name
  - Category
  - Risk level
  - Sector (Healthcare, Finance, etc.)
  - Region (UK, EU, US, etc.)
       ↓
Build sector-specific prompt with:
  - Regulatory authorities (MHRA, FCA, NIST, etc.)
  - Authentic guidance documents
  - Framework references
       ↓
Call OpenAI GPT-4 (gpt-4o)
       ↓
Parse and sanitize response
       ↓
Display insight in audit UI
```

**Prompt Engineering:**

```python
system_prompt = f"""
You are a senior AI governance advisor. Your job is to evaluate AI audit controls 
using real-world references and sector-specific context.

Generate a short, audit-quality Life-Wise Insight for the following control:

- Control: {control_name}
- Risk Level: {risk_level}
- Sector: {sector}
- Region: {region}
- Frameworks: {', '.join(frameworks)}

Rules:
- Limit to under 200 words
- Reference public reports, real regulatory actions, or best practices
- Avoid fabricated events or statistics
- Prioritize insights useful to legal, audit, and governance stakeholders
- Draw from guidance by NIST, ISO, EU AI Act, FCA, ICO, MITRE, OWASP, CDEI, or NHS AI Lab
- Do not reference fictional companies or private case studies
- Highlight governance impact (e.g., audit exposure, policy adaptation, retraining)

Respond with only the rewritten Life-Wise Insight.
"""
```

**Sector-Specific Regulatory Context:**

| Sector | Authorities | Key Guidance Documents |
|--------|-------------|------------------------|
| Healthcare | MHRA, NHS AI Lab, FDA, Health Canada | MHRA AIaMD Guidance (2023), NHS AI Ethics Framework (2022), FDA AI/ML Action Plan (2021) |
| Financial Services | FCA, EBA, SEC, OCC | FCA AI Governance Overview (2022), EBA ICT Risk Guidelines (2020), SEC Robo-Adviser Guidance (2017) |
| Government | NIST, OMB, Cabinet Office | NIST AI RMF (2023), OMB M-24-10 (2024), UK AI White Paper (2023) |
| Technology | FTC, ICO, CNIL | FTC AI Guidance (2021), GDPR Article 22 (2018), ICO AI Guidance (2023) |

#### 2. **Evidence Evaluation**

**Purpose:** Assess quality and sufficiency of submitted evidence using AI.

**Evaluation Criteria:**
- Completeness: Does evidence address all control requirements?
- Recency: Is evidence current based on control category?
- Quality: Is evidence from authoritative sources?
- Sufficiency: Is evidence adequate for regulatory submission?
- Gaps: What additional evidence is needed?

**AI Evaluation Flow:**
```
User submits evidence (text, URLs, files)
       ↓
Extract text content from all sources
       ↓
Check evidence recency against control requirements
       ↓
Build evaluation prompt:
  - Control requirements
  - Evidence content
  - Sector/region context
  - Framework expectations
       ↓
Call OpenAI GPT-4
       ↓
Parse evaluation:
  - Quality score (1-5)
  - Confidence level (High/Medium/Low)
  - Gap identification
  - Recommendations
       ↓
Store evaluation in database
       ↓
Display results with visual indicators
```

**Evidence Recency Requirements:**

| Control Category | Maximum Age | Rationale |
|------------------|-------------|-----------|
| Security | 90 days | Rapid threat landscape changes |
| Monitoring | 30 days | Real-time operational requirements |
| Data Governance | 180 days | Semi-annual policy review cycles |
| Documentation | 365 days | Annual update standards |
| Default | 180 days | Standard regulatory review cycle |

#### 3. **Trusted Reference Engine**

**Module:** `trusted_reference_engine.py`

**Purpose:** Enhance AI prompts with authentic regulatory references.

**Reference Sources:**

```python
reference_sources = {
    "governance_frameworks": [
        {
            "title": "NIST AI Risk Management Framework",
            "url": "https://www.nist.gov/itl/ai-risk-management-framework",
            "scope": "Comprehensive AI risk management guidance",
            "relevance": ["risk assessment", "governance", "management"]
        },
        {
            "title": "ISO/IEC 42001 AI Management Systems",
            "url": "https://www.iso.org/standard/81228.html",
            "scope": "International standard for AI management",
            "relevance": ["management systems", "controls", "auditing"]
        },
        {
            "title": "EU AI Act",
            "url": "https://artificialintelligenceact.eu/",
            "scope": "EU regulatory framework for AI systems",
            "relevance": ["regulation", "compliance", "risk classification"]
        }
    ],
    "sector_specific": {
        "Healthcare": [
            {
                "authority": "MHRA",
                "url": "https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency",
                "guidance": "AIaMD Guidance (2023)"
            },
            {
                "authority": "FDA",
                "url": "https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-and-machine-learning-aiml-enabled-medical-devices",
                "guidance": "AI/ML Action Plan (2021)"
            }
        ],
        "Financial Services": [
            {
                "authority": "FCA",
                "url": "https://www.fca.org.uk/publications/multi-firm-reviews/artificial-intelligence-machine-learning",
                "guidance": "AI Governance Overview (2022)"
            },
            {
                "authority": "EBA",
                "url": "https://www.eba.europa.eu/",
                "guidance": "ICT Risk Guidelines (2020)"
            }
        ]
    }
}
```

#### 4. **Temporal Insight Variation**

**Module:** `temporal_insight_variation.py`

**Purpose:** Prevent repetitive insights by rotating AI-generated content.

**Strategy:**
- Track view count per control
- Rotate between 3-5 insight variations
- Regenerate insights after 10 views
- Store variation history in database

**Benefits:**
- Fresh perspectives on each audit
- Reduced AI generation costs
- Improved user experience
- Maintained insight quality

### Fallback System

**When AI is Unavailable:**
- Use pre-generated static insights from database
- Load fallback insights from `fallback_insights.py`
- Display sector-specific templates
- Maintain full audit functionality

---

## Security & Performance

### Security Features

#### 1. **Data Protection**
- SQLite database with file-level permissions
- Evidence files stored in session-specific directories
- No direct SQL injection vectors (parameterized queries)
- Environment variable management for API keys
- No secrets in source code

#### 2. **Session Management**
- UUID-based session identifiers
- Server-side session storage
- No client-side sensitive data storage
- Session timeout handling

#### 3. **Input Validation**
- Form field sanitization
- File type validation (PDF, DOCX, JPG, PNG only)
- URL validation for evidence references
- SQL injection prevention via parameterized queries

#### 4. **API Key Management**
- Environment variable storage (`OPENAI_API_KEY`)
- No API keys in logs or error messages
- Graceful fallback when API unavailable
- Rate limiting awareness

### Performance Optimizations

#### 1. **Database Optimization**
- Indexed foreign keys
- Row factory for efficient data access
- Connection pooling
- Query optimization with selective column retrieval

#### 2. **Caching Strategy**
- Static insight caching
- Framework/category enumeration caching
- Sector reference JSON caching
- Template fragment caching

#### 3. **File Handling**
- Chunked file uploads
- Secure filename generation (UUID)
- Organized directory structure
- Supported file types: PDF, DOCX, JPG, PNG (max size configurable)

#### 4. **AI Call Optimization**
- Insight rotation to reduce API calls
- Fallback system for offline operation
- Token limit management (300 tokens per insight)
- Temperature control (0.5 for consistency)

---

## Deployment Architecture

### Production Configuration

#### Port Management
```python
# Priority port selection
PRIORITY_PORTS = [5000, 5001, 5002, 5003, 8000, 8080]

# Automatic port conflict resolution
def find_available_port():
    for port in PRIORITY_PORTS:
        if is_port_available(port):
            return port
    raise RuntimeError("No available ports")
```

#### Startup Sequence
```
1. Load environment variables
2. Validate database existence
3. Check database schema
4. Verify control count (251 expected)
5. Verify framework count (5 expected)
6. Initialize roadmap tables
7. Find available port
8. Register health check endpoint
9. Start Flask application
10. Log startup success
```

#### Health Check Endpoints

```python
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "database": "connected",
        "controls": 251,
        "frameworks": 5,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    return jsonify({
        "version": "1.0",
        "ai_enabled": bool(OPENAI_API_KEY),
        "demo_mode": is_demo_mode()
    })
```

### Environment Variables

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

### Database Initialization

```python
# Initial database setup
def initialize_database():
    conn = sqlite3.connect('audit_controls.db')
    cursor = conn.cursor()
    
    # Create all tables
    create_controls_table(cursor)
    create_frameworks_table(cursor)
    create_audit_sessions_table(cursor)
    create_audit_responses_table(cursor)
    create_evidence_tables(cursor)
    create_roadmap_tables(cursor)
    create_sector_region_tables(cursor)
    
    # Load initial data
    load_controls_from_csv(cursor)
    load_frameworks(cursor)
    
    conn.commit()
    conn.close()
```

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('asimov_audit.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('asimov_audit')
```

---

## API Endpoints Summary

See `ASIMOV_API_REFERENCE.md` for complete API documentation.

**Key Endpoint Categories:**
- Audit Management: 8 endpoints
- Evidence Management: 4 endpoints
- Reporting & Analytics: 5 endpoints
- Roadmap Management: 12 endpoints
- Database Administration: 6 endpoints
- System Health: 2 endpoints

---

## Conclusion

The ASIMOV AI Governance Audit Tool represents a sophisticated, production-ready platform built on modern Python web technologies with advanced AI integration. The architecture emphasizes:

- **Modularity**: Blueprint-based component separation
- **Scalability**: Efficient database design and caching strategies
- **Reliability**: Bulletproof startup and health monitoring
- **Intelligence**: OpenAI GPT-4 integration with fallback systems
- **Security**: Input validation, session management, and API key protection
- **Maintainability**: Clean code structure with comprehensive documentation

This technical design enables rapid deployment, easy maintenance, and seamless integration into enterprise compliance workflows.
