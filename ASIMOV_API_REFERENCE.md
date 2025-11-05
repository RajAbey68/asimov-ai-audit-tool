# ASIMOV AI Governance Audit Tool
## API Reference & Functional Specification

**Version:** 1.0  
**Document Date:** November 5, 2025  
**Base URL:** `http://localhost:5000` (development) / `https://your-domain.com` (production)

---

## Table of Contents
1. [API Overview](#api-overview)
2. [Audit Management APIs](#audit-management-apis)
3. [Evidence Management APIs](#evidence-management-apis)
4. [Reporting & Analytics APIs](#reporting--analytics-apis)
5. [Roadmap Management APIs](#roadmap-management-apis)
6. [Database Administration APIs](#database-administration-apis)
7. [System Health APIs](#system-health-apis)
8. [Data Models](#data-models)
9. [Error Handling](#error-handling)
10. [Integration Examples](#integration-examples)

---

## API Overview

### Authentication
Current version uses session-based authentication. API key authentication can be implemented for production deployments.

### Response Formats
All API endpoints return responses in one of the following formats:
- **HTML**: Template-rendered pages for web UI
- **JSON**: Structured data for API consumers
- **CSV**: Tabular data exports
- **PDF**: Report documents (future enhancement)

### HTTP Methods
- `GET`: Retrieve resources
- `POST`: Create resources or submit data
- `PUT/PATCH`: Update resources (roadmap endpoints)
- `DELETE`: Remove resources (roadmap endpoints)

### Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Audit Management APIs

### 1. Home Page & Audit Configuration

#### `GET /`
Display home page with audit configuration form.

**Response:** HTML template
**Template:** `index.html`

**Functionality:**
- Display framework selection dropdown
- Display category filter options
- Display risk level filter options
- Display sector selection
- Display region selection
- Render audit creation form

**Example Response Data:**
```json
{
  "frameworks": [
    "EU AI Law",
    "GDPR",
    "NIST AI RMF",
    "ISO/IEC 42001",
    "SCF"
  ],
  "categories": [
    "Security",
    "Data Protection",
    "Monitoring",
    "Transparency",
    "Governance"
  ],
  "risk_levels": [
    "High Risk",
    "General Risk"
  ],
  "sectors": [
    {"id": 1, "name": "Healthcare"},
    {"id": 2, "name": "Financial Services"},
    {"id": 3, "name": "Government"},
    {"id": 4, "name": "Technology"}
  ],
  "regions": [
    {"id": 1, "name": "United Kingdom"},
    {"id": 2, "name": "European Union"},
    {"id": 3, "name": "United States"}
  ]
}
```

---

### 2. Start New Audit

#### `POST /start-audit`
Create a new audit session with specified filters.

**Request Parameters:**
```json
{
  "session_name": "Healthcare AI Audit Q4 2025",
  "framework_filter": "EU AI Act (2023)",
  "category_filter": "Security",
  "risk_level_filter": "High Risk",
  "sector_filter": "Healthcare",
  "region_filter": "United Kingdom"
}
```

**Response:** Redirect to `/audit/{session_id}/question/0`

**Database Operations:**
1. Create new UUID for session
2. Map framework name to search pattern via `framework_mapping` table
3. Insert audit session into `audit_sessions` table
4. Return session ID

**Example Session Record:**
```json
{
  "session_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "session_name": "Healthcare AI Audit Q4 2025",
  "framework_filter": "EU AI Act (2023)",
  "framework_pattern": "%EU AI%",
  "category_filter": "Security",
  "risk_level_filter": "High Risk",
  "sector_filter": "Healthcare",
  "region_filter": "United Kingdom",
  "session_date": "2025-11-05T10:30:00"
}
```

---

### 3. Display Audit Question

#### `GET /audit/{session_id}/question/{question_index}`
Display a specific audit question with control details.

**Path Parameters:**
- `session_id` (string): UUID of audit session
- `question_index` (integer): Zero-based question index

**Response:** HTML template
**Template:** `question.html`

**Functionality:**
1. Retrieve audit session filters
2. Query controls based on filters
3. Display control at specified index
4. Generate Life-Wise Insight using OpenAI GPT-4
5. Retrieve existing response if available
6. Display evidence collection form
7. Show progress indicator

**Response Data Structure:**
```json
{
  "session_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "question_index": 5,
  "progress": {
    "current": 6,
    "total": 42,
    "percentage": 14
  },
  "control": {
    "id": 123,
    "control_name": "AI System Risk Assessment Documentation",
    "category": "Risk Management",
    "framework": "EU AI Law",
    "risk_level": "High Risk",
    "description": "Document comprehensive risk assessment for AI systems...",
    "evidence": "Risk assessment reports, impact analysis, mitigation plans"
  },
  "insight": "The EU AI Act requires high-risk AI systems to undergo thorough conformity assessments. According to Article 9, providers must establish a risk management system throughout the AI system's lifecycle. The MHRA AIaMD Guidance (2023) emphasizes that healthcare AI devices require clinical evaluation reports demonstrating safety and performance. Recent FCA guidance highlights that financial institutions must document model risk management frameworks. Best practice includes maintaining version-controlled risk registers, conducting quarterly reviews, and engaging independent third-party audits.",
  "response": {
    "id": 456,
    "response": "Fully Implemented",
    "response_score": 5,
    "evidence": "We maintain comprehensive risk assessment documentation updated quarterly.",
    "evidence_notes": "Risk register includes 23 identified risks with mitigation strategies.",
    "evidence_date": "2025-10-15",
    "evidence_urls": [
      "https://internal-docs.example.com/risk-assessment-2025-q4",
      "https://compliance.example.com/ai-risk-register"
    ],
    "evidence_files": [
      {
        "id": 789,
        "filename": "AI_Risk_Assessment_Report_Q4_2025.pdf",
        "file_path": "evidence_files/response_456/a1b2c3d4.pdf",
        "upload_date": "2025-11-01T14:30:00"
      }
    ]
  },
  "has_prev": true,
  "has_next": true,
  "sector": "Healthcare",
  "region": "United Kingdom"
}
```

---

### 4. Submit Audit Response

#### `POST /audit/{session_id}/question/{question_index}/submit`
Submit an answer for an audit question.

**Path Parameters:**
- `session_id` (string): UUID of audit session
- `question_index` (integer): Zero-based question index

**Request Parameters:**
```json
{
  "response": "Fully Implemented",
  "response_score": 5,
  "reference_text": "We maintain comprehensive risk assessment documentation.",
  "evidence_notes": "Risk register includes 23 identified risks with mitigation strategies.",
  "evidence_date": "2025-10-15",
  "evidence_urls[]": [
    "https://internal-docs.example.com/risk-assessment",
    "https://compliance.example.com/ai-risk-register"
  ],
  "evidence_files[]": [
    "File upload (multipart/form-data)"
  ]
}
```

**Response:** Redirect to next question or summary page

**Database Operations:**
1. Check if response exists for this control/session
2. If exists: Update existing response
3. If not: Insert new response into `audit_responses`
4. Save evidence notes, date
5. Save evidence URLs to `evidence_urls` table
6. Save uploaded files to `evidence_files` table and filesystem
7. Redirect to next question

**Evidence File Storage:**
```
evidence_files/
  └── response_{response_id}/
      ├── {uuid1}.pdf
      ├── {uuid2}.docx
      └── {uuid3}.jpg
```

---

### 5. Audit Summary

#### `GET /audit/{session_id}/summary`
Display audit summary with all responses.

**Path Parameters:**
- `session_id` (string): UUID of audit session

**Response:** HTML template
**Template:** `summary.html`

**Functionality:**
- Display audit session details
- List all controls and responses
- Show completion percentage
- Provide export options
- Link to detailed report dashboard

**Response Data Structure:**
```json
{
  "session": {
    "session_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "session_name": "Healthcare AI Audit Q4 2025",
    "framework_filter": "EU AI Act (2023)",
    "sector_filter": "Healthcare",
    "region_filter": "United Kingdom",
    "session_date": "2025-11-05T10:30:00"
  },
  "summary_stats": {
    "total_controls": 42,
    "answered_controls": 38,
    "completion_percentage": 90,
    "avg_score": 4.2,
    "high_risk_controls": 15,
    "evidence_items": 76
  },
  "responses": [
    {
      "control_name": "AI System Risk Assessment Documentation",
      "category": "Risk Management",
      "response": "Fully Implemented",
      "response_score": 5,
      "evidence_count": 3
    }
  ]
}
```

---

## Evidence Management APIs

### 6. Evaluate Evidence (AI-Powered)

#### `POST /evaluate_evidence/{control_id}/{session_id}`
Trigger AI evaluation of submitted evidence.

**Path Parameters:**
- `control_id` (integer): Control ID
- `session_id` (string): Audit session UUID

**Request Body:**
```json
{
  "evidence_text": "Comprehensive risk assessment documentation...",
  "evidence_urls": ["https://example.com/doc1", "https://example.com/doc2"],
  "evidence_files": ["file1.pdf", "file2.docx"],
  "evidence_date": "2025-10-15"
}
```

**Response:** JSON
```json
{
  "success": true,
  "evaluation": {
    "quality_score": 4,
    "confidence_level": "High",
    "evaluation_text": "Evidence demonstrates comprehensive risk management framework. Documentation includes quarterly risk reviews, mitigation strategies, and third-party validation. Minor gap: Could enhance with more recent external audit findings. Overall assessment: Strong regulatory sufficiency for EU AI Act Article 9 compliance.",
    "recency_status": "current",
    "recency_message": "Evidence is 21 days old (within 90 day requirement)",
    "recommendations": [
      "Include most recent external audit report",
      "Add evidence of board-level risk oversight",
      "Document AI system change management process"
    ]
  }
}
```

**AI Evaluation Process:**
1. Extract text from all evidence sources (files, URLs, notes)
2. Check evidence recency against control category requirements
3. Construct evaluation prompt with control context and sector/region
4. Call OpenAI GPT-4 with trusted regulatory references
5. Parse AI response for quality score and recommendations
6. Store evaluation in `audit_responses` table
7. Return structured evaluation response

---

### 7. Evidence Status Check

#### `GET /api/evidence_status/{session_id}`
Retrieve evidence evaluation status for all controls in session.

**Path Parameters:**
- `session_id` (string): Audit session UUID

**Response:** JSON
```json
{
  "session_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "evidence_summary": {
    "total_controls": 42,
    "evaluated_controls": 35,
    "high_quality": 28,
    "medium_quality": 5,
    "low_quality": 2,
    "pending_evaluation": 7
  },
  "control_evaluations": [
    {
      "control_id": 123,
      "control_name": "AI System Risk Assessment Documentation",
      "evaluation_status": "evaluated",
      "quality_score": 4,
      "confidence_level": "High",
      "evaluation_date": "2025-11-05T15:45:00"
    }
  ]
}
```

---

### 8. Generate AI Insight

#### `POST /generate-insight`
Generate or regenerate Life-Wise Insight for a control.

**Request Body:**
```json
{
  "control_name": "AI System Risk Assessment Documentation",
  "category": "Risk Management",
  "risk_level": "High Risk",
  "sector": "Healthcare",
  "region": "United Kingdom"
}
```

**Response:** JSON
```json
{
  "success": true,
  "insight": "The EU AI Act requires high-risk AI systems to undergo thorough conformity assessments. According to Article 9, providers must establish a risk management system throughout the AI system's lifecycle. The MHRA AIaMD Guidance (2023) emphasizes that healthcare AI devices require clinical evaluation reports demonstrating safety and performance. Recent FCA guidance highlights that financial institutions must document model risk management frameworks. Best practice includes maintaining version-controlled risk registers, conducting quarterly reviews, and engaging independent third-party audits.",
  "sector": "Healthcare",
  "region": "United Kingdom",
  "frameworks_referenced": [
    "EU AI Act",
    "MHRA AIaMD Guidance",
    "ISO/IEC 42001"
  ]
}
```

---

## Reporting & Analytics APIs

### 9. Report Dashboard

#### `GET /report` or `GET /reports`
Display comprehensive analytics dashboard.

**Response:** HTML template
**Template:** `report/dashboard.html`

**Functionality:**
- Display overall compliance analytics
- Show framework coverage charts
- Render ASIMOV Pillars performance
- Display risk heatmaps
- List recent audit sessions
- Provide session comparison tools

**Data Included:**
```json
{
  "overall_stats": {
    "total_audits": 24,
    "total_responses": 856,
    "avg_compliance_score": 4.1,
    "frameworks_covered": 5,
    "sectors_audited": 7
  },
  "framework_coverage": [
    {
      "framework_name": "EU AI Act",
      "total_controls": 127,
      "responses": 98,
      "coverage_percentage": 77,
      "avg_score": 4.3
    }
  ],
  "asimov_pillars": [
    {
      "pillar": "A - Accountability",
      "responses": 156,
      "avg_score": 4.2,
      "coverage": 82
    },
    {
      "pillar": "S - Security",
      "responses": 143,
      "avg_score": 4.5,
      "coverage": 89
    }
  ],
  "risk_heatmap": [
    {
      "category": "Security",
      "high_risk": 15,
      "general_risk": 8,
      "avg_score": 4.3
    }
  ]
}
```

---

### 10. Session Detailed Report

#### `GET /report/{session_id}`
Display detailed report for specific audit session.

**Path Parameters:**
- `session_id` (string): Audit session UUID

**Response:** HTML template
**Template:** `report/session_detail.html`

**Functionality:**
- Session overview and metadata
- Control-by-control response summary
- Evidence quality analysis
- Compliance gap identification
- ASIMOV Pillars breakdown
- Export options (CSV, JSON)

---

### 11. Export Session CSV

#### `GET /report/{session_id}/export/csv`
Export audit session data as CSV file.

**Path Parameters:**
- `session_id` (string): Audit session UUID

**Response:** CSV file
**Content-Type:** `text/csv`
**Filename:** `audit_report_{session_id}_{timestamp}.csv`

**CSV Structure:**
```csv
Control ID,Control Name,Category,Framework,Risk Level,Response,Score,Evidence,Notes,Date
123,"AI System Risk Assessment","Risk Management","EU AI Law","High Risk","Fully Implemented",5,"Risk assessment reports...","Risk register includes...","2025-10-15"
```

---

### 12. Analytics API

#### `GET /api/report/analytics`
Retrieve analytics data in JSON format.

**Query Parameters:**
- `session_id` (optional): Filter by session
- `framework` (optional): Filter by framework
- `sector` (optional): Filter by sector
- `start_date` (optional): Filter by date range
- `end_date` (optional): Filter by date range

**Response:** JSON
```json
{
  "analytics": {
    "response_distribution": [
      {"response": "Fully Implemented", "count": 145},
      {"response": "Partially Implemented", "count": 67},
      {"response": "Not Implemented", "count": 12}
    ],
    "framework_coverage": [...],
    "pillar_analysis": [...]
  }
}
```

---

### 13. Heatmap Data API

#### `GET /api/report/heatmap`
Retrieve risk heatmap data.

**Query Parameters:**
- `session_id` (optional): Filter by session
- `framework` (optional): Filter by framework

**Response:** JSON
```json
{
  "heatmap_data": [
    {
      "category": "Security",
      "risk_level": "High Risk",
      "count": 15,
      "avg_score": 4.3,
      "color_code": "#28a745"
    },
    {
      "category": "Security",
      "risk_level": "General Risk",
      "count": 8,
      "avg_score": 4.7,
      "color_code": "#20c997"
    }
  ],
  "legend": {
    "excellent": {"min": 4.5, "max": 5.0, "color": "#20c997"},
    "good": {"min": 3.5, "max": 4.49, "color": "#28a745"},
    "fair": {"min": 2.5, "max": 3.49, "color": "#ffc107"},
    "poor": {"min": 0, "max": 2.49, "color": "#dc3545"}
  }
}
```

---

## Roadmap Management APIs

### 14. List Roadmaps

#### `GET /roadmap/list`
Display all implementation roadmaps.

**Response:** HTML template
**Template:** `roadmap/list.html`

**Data Structure:**
```json
{
  "roadmaps": [
    {
      "id": "roadmap-uuid-1",
      "name": "Q4 2025 AI Compliance Implementation",
      "description": "Implementation plan for EU AI Act compliance gaps",
      "owner": "Compliance Team",
      "status": "Active",
      "created_date": "2025-11-01T10:00:00",
      "sprint_count": 3,
      "backlog_count": 15
    }
  ]
}
```

---

### 15. Create Roadmap

#### `POST /roadmap/create`
Create a new implementation roadmap.

**Request Parameters:**
```json
{
  "name": "Q4 2025 AI Compliance Implementation",
  "description": "Implementation plan for EU AI Act compliance gaps",
  "owner": "Compliance Team"
}
```

**Response:** Redirect to `/roadmap/{roadmap_id}`

**Database Operations:**
1. Generate UUID for roadmap
2. Insert into `roadmaps` table
3. Set status to 'Active'
4. Set created_date to current timestamp
5. Return roadmap ID

---

### 16. View Roadmap

#### `GET /roadmap/{roadmap_id}`
Display roadmap details with sprints and backlog.

**Path Parameters:**
- `roadmap_id` (string): Roadmap UUID

**Response:** HTML template
**Template:** `roadmap/view.html`

**Data Structure:**
```json
{
  "roadmap": {
    "id": "roadmap-uuid-1",
    "name": "Q4 2025 AI Compliance Implementation",
    "description": "Implementation plan for EU AI Act compliance gaps",
    "owner": "Compliance Team",
    "status": "Active"
  },
  "sprints": [
    {
      "id": "sprint-uuid-1",
      "name": "Sprint 1: Security Controls",
      "description": "Implement high-priority security controls",
      "start_date": "2025-11-15",
      "end_date": "2025-11-29",
      "status": "In Progress",
      "item_count": 8
    }
  ],
  "backlog_items": [
    {
      "id": "item-uuid-1",
      "title": "Implement AI System Risk Assessment Process",
      "description": "Establish comprehensive risk assessment framework per EU AI Act Article 9",
      "control_id": 123,
      "control_name": "AI System Risk Assessment Documentation",
      "priority": "High",
      "status": "Backlog",
      "assigned_to": "Risk Team",
      "effort_estimate": 13
    }
  ]
}
```

---

### 17. Create Sprint

#### `POST /roadmap/{roadmap_id}/create-sprint`
Create a new sprint for a roadmap.

**Path Parameters:**
- `roadmap_id` (string): Roadmap UUID

**Request Parameters:**
```json
{
  "name": "Sprint 2: Data Protection Controls",
  "description": "Implement GDPR-aligned data protection controls",
  "start_date": "2025-12-01",
  "end_date": "2025-12-15"
}
```

**Response:** Redirect to `/roadmap/{roadmap_id}`

---

### 18. Add to Backlog

#### `POST /roadmap/{roadmap_id}/add-to-backlog`
Add an item to the roadmap backlog.

**Path Parameters:**
- `roadmap_id` (string): Roadmap UUID

**Request Parameters:**
```json
{
  "title": "Implement Continuous Monitoring System",
  "description": "Deploy automated monitoring for AI model performance",
  "control_id": 156,
  "priority": "High",
  "assigned_to": "DevOps Team",
  "effort_estimate": 8
}
```

**Response:** Redirect to `/roadmap/{roadmap_id}`

---

### 19. Add Control to Roadmap

#### `POST /roadmap/add-from-control/{control_id}`
Add a control directly to a roadmap from audit.

**Path Parameters:**
- `control_id` (integer): Control ID

**Request Parameters:**
```json
{
  "roadmap_id": "roadmap-uuid-1",
  "priority": "High",
  "notes": "Identified as gap during Healthcare AI audit"
}
```

**Response:** JSON
```json
{
  "success": true,
  "message": "Control added to roadmap",
  "backlog_item_id": "item-uuid-5"
}
```

---

### 20. Update Sprint

#### `POST /roadmap/{roadmap_id}/update-sprint/{sprint_id}`
Update sprint details or status.

**Path Parameters:**
- `roadmap_id` (string): Roadmap UUID
- `sprint_id` (string): Sprint UUID

**Request Parameters:**
```json
{
  "name": "Sprint 2: Data Protection Controls (Updated)",
  "status": "Completed",
  "end_date": "2025-12-20"
}
```

**Response:** Redirect to `/roadmap/{roadmap_id}`

---

### 21. Delete Backlog Item

#### `POST /roadmap/{roadmap_id}/delete/{item_id}`
Remove an item from the backlog.

**Path Parameters:**
- `roadmap_id` (string): Roadmap UUID
- `item_id` (string): Backlog item UUID

**Response:** Redirect to `/roadmap/{roadmap_id}`

---

### 22. Move Backlog Item API

#### `POST /api/roadmaps/{roadmap_id}/backlog/move`
Move backlog item between sprints or back to backlog.

**Path Parameters:**
- `roadmap_id` (string): Roadmap UUID

**Request Body:**
```json
{
  "item_id": "item-uuid-3",
  "target_sprint_id": "sprint-uuid-2"  // or null for backlog
}
```

**Response:** JSON
```json
{
  "success": true,
  "message": "Item moved successfully"
}
```

---

## Database Administration APIs

### 23. Database Admin Dashboard

#### `GET /db_admin/`
Display database administration interface.

**Response:** HTML template
**Template:** `db_admin/index.html`

**Functionality:**
- List all database tables with row counts
- Show database size and statistics
- Provide table inspection tools
- Enable custom SQL query execution
- Offer data export options

---

### 24. View Table Contents

#### `GET /db_admin/tables/{table_name}`
Display contents of a specific table.

**Path Parameters:**
- `table_name` (string): Name of database table

**Query Parameters:**
- `limit` (integer, default: 100): Number of rows to display
- `offset` (integer, default: 0): Starting row

**Response:** HTML template
**Template:** `db_admin/table_view.html`

---

### 25. Execute SQL Query

#### `POST /db_admin/query`
Execute custom SQL query (SELECT only for safety).

**Request Parameters:**
```json
{
  "sql_query": "SELECT * FROM controls WHERE risk_level = 'High Risk' LIMIT 10"
}
```

**Response:** HTML template with query results
**Template:** `db_admin/query_results.html`

**Safety Restrictions:**
- Only SELECT queries allowed
- No DELETE, UPDATE, DROP operations
- Query timeout: 30 seconds
- Maximum result rows: 1000

---

### 26. Export Database

#### `POST /db_admin/export`
Export database tables to CSV or JSON.

**Request Parameters:**
```json
{
  "format": "csv",  // or "json"
  "tables": ["controls", "audit_responses", "evidence_files"]
}
```

**Response:** ZIP file containing exported data

---

### 27. Database Optimization

#### `POST /db_admin/optimize`
Run database optimization (VACUUM).

**Response:** JSON
```json
{
  "success": true,
  "message": "Database optimized successfully",
  "size_before": "52.3 MB",
  "size_after": "48.1 MB",
  "space_saved": "4.2 MB"
}
```

---

### 28. Audit Analysis

#### `GET /db_admin/audit_analysis/{session_id}`
Display detailed database-level analysis of audit session.

**Path Parameters:**
- `session_id` (string): Audit session UUID

**Response:** HTML template
**Template:** `db_admin/audit_analysis.html`

**Analysis Includes:**
- Query performance statistics
- Evidence storage analysis
- Response pattern analysis
- Database query optimization suggestions

---

## System Health APIs

### 29. Health Check

#### `GET /health`
System health check endpoint for monitoring.

**Response:** JSON
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T16:45:00Z",
  "database": "connected",
  "controls_count": 251,
  "frameworks_count": 5,
  "version": "1.0",
  "uptime_seconds": 3600
}
```

**Status Codes:**
- `200`: System healthy
- `503`: System unhealthy (database error, etc.)

---

### 30. API Status

#### `GET /api/status`
Detailed API status and configuration.

**Response:** JSON
```json
{
  "version": "1.0",
  "environment": "production",
  "ai_integration": {
    "enabled": true,
    "provider": "OpenAI",
    "model": "gpt-4o"
  },
  "demo_mode": {
    "enabled": false
  },
  "features": {
    "evidence_evaluation": true,
    "roadmap_management": true,
    "report_dashboard": true,
    "database_admin": true
  },
  "database": {
    "type": "SQLite",
    "path": "audit_controls.db",
    "size_mb": 48.1,
    "tables": 18
  }
}
```

---

## Data Models

### Audit Session Model

```typescript
interface AuditSession {
  session_id: string;           // UUID
  session_name: string;          // e.g., "Healthcare AI Audit Q4 2025"
  framework_filter: string;      // e.g., "EU AI Act (2023)"
  framework_pattern: string;     // SQL LIKE pattern
  category_filter: string;       // e.g., "Security"
  risk_level_filter: string;     // e.g., "High Risk"
  sector_filter: string;         // e.g., "Healthcare"
  region_filter: string;         // e.g., "United Kingdom"
  session_date: string;          // ISO 8601 timestamp
}
```

### Control Model

```typescript
interface Control {
  id: number;
  control_name: string;
  category: string;
  framework: string;
  explainability: string;
  description: string;
  evidence: string;              // Suggested evidence types
  risk_level: string;            // "High Risk" | "General Risk"
}
```

### Audit Response Model

```typescript
interface AuditResponse {
  id: number;
  session_id: string;
  control_id: number;
  response: string;              // e.g., "Fully Implemented"
  response_score: number;        // 1-5
  evidence: string;              // Primary evidence text
  evidence_notes: string;        // Detailed notes
  evidence_date: string;         // ISO 8601 date
  confidence: number;            // 1-5
  evaluation_text: string;       // AI evaluation summary
  evaluation_status: string;     // "evaluated" | "pending"
  confidence_level: string;      // "High" | "Medium" | "Low"
  evaluation_date: string;       // ISO 8601 timestamp
  created_at: string;            // ISO 8601 timestamp
}
```

### Evidence URL Model

```typescript
interface EvidenceURL {
  id: number;
  response_id: number;
  url: string;
}
```

### Evidence File Model

```typescript
interface EvidenceFile {
  id: number;
  response_id: number;
  filename: string;              // Original filename
  file_path: string;             // Server storage path
  upload_date: string;           // ISO 8601 timestamp
}
```

### Roadmap Model

```typescript
interface Roadmap {
  id: string;                    // UUID
  name: string;
  description: string;
  owner: string;
  status: string;                // "Active" | "Completed" | "Archived"
  created_date: string;          // ISO 8601 timestamp
}
```

### Sprint Model

```typescript
interface Sprint {
  id: string;                    // UUID
  roadmap_id: string;
  name: string;
  description: string;
  start_date: string;            // ISO 8601 date
  end_date: string;              // ISO 8601 date
  status: string;                // "Planned" | "In Progress" | "Completed"
}
```

### Backlog Item Model

```typescript
interface BacklogItem {
  id: string;                    // UUID
  roadmap_id: string;
  sprint_id: string | null;      // null if in backlog
  control_id: number | null;
  title: string;
  description: string;
  status: string;                // "Backlog" | "In Progress" | "Completed"
  priority: string;              // "High" | "Medium" | "Low"
  assigned_to: string;
  effort_estimate: number;       // Story points
  created_date: string;          // ISO 8601 timestamp
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": true,
  "message": "Resource not found",
  "code": "RESOURCE_NOT_FOUND",
  "details": {
    "resource_type": "audit_session",
    "resource_id": "invalid-uuid"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_SESSION` | 404 | Audit session not found |
| `INVALID_CONTROL` | 404 | Control ID not found |
| `MISSING_PARAMETER` | 400 | Required parameter missing |
| `INVALID_FORMAT` | 400 | Invalid data format |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `AI_SERVICE_ERROR` | 503 | OpenAI API unavailable |
| `FILE_UPLOAD_ERROR` | 400 | File upload failed |
| `UNAUTHORIZED` | 401 | Authentication required |

---

## Integration Examples

### Example 1: Create Audit and Submit Responses (Python)

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Start new audit
response = requests.post(f"{BASE_URL}/start-audit", data={
    "session_name": "Healthcare AI Compliance Audit",
    "framework_filter": "EU AI Act (2023)",
    "sector_filter": "Healthcare",
    "region_filter": "United Kingdom",
    "risk_level_filter": "High Risk"
})

# Extract session ID from redirect
session_id = response.url.split("/")[4]

# Submit response for first control
response = requests.post(
    f"{BASE_URL}/audit/{session_id}/question/0/submit",
    data={
        "response": "Fully Implemented",
        "response_score": 5,
        "reference_text": "Comprehensive risk assessment framework in place",
        "evidence_notes": "Quarterly risk reviews conducted",
        "evidence_date": "2025-10-15"
    }
)

print(f"Audit session created: {session_id}")
```

### Example 2: Retrieve Analytics Data (JavaScript)

```javascript
const BASE_URL = 'http://localhost:5000';

async function getAnalytics(sessionId) {
  const response = await fetch(`${BASE_URL}/api/report/analytics?session_id=${sessionId}`);
  const data = await response.json();
  
  console.log('Response Distribution:', data.analytics.response_distribution);
  console.log('Framework Coverage:', data.analytics.framework_coverage);
  console.log('Pillar Analysis:', data.analytics.pillar_analysis);
  
  return data;
}

// Usage
getAnalytics('a1b2c3d4-5678-90ab-cdef-1234567890ab');
```

### Example 3: Evaluate Evidence with AI (cURL)

```bash
curl -X POST http://localhost:5000/evaluate_evidence/123/a1b2c3d4-5678-90ab \
  -H "Content-Type: application/json" \
  -d '{
    "evidence_text": "Risk assessment documentation with quarterly reviews",
    "evidence_urls": ["https://docs.example.com/risk-assessment"],
    "evidence_date": "2025-10-15"
  }'
```

### Example 4: Export Audit Report (Python)

```python
import requests

BASE_URL = "http://localhost:5000"
session_id = "a1b2c3d4-5678-90ab-cdef-1234567890ab"

# Export to CSV
response = requests.get(f"{BASE_URL}/report/{session_id}/export/csv")

with open(f"audit_report_{session_id}.csv", "wb") as f:
    f.write(response.content)

print("Report exported successfully")
```

### Example 5: Create Implementation Roadmap (JavaScript)

```javascript
const BASE_URL = 'http://localhost:5000';

async function createRoadmapFromAudit(sessionId) {
  // Create roadmap
  const roadmapResponse = await fetch(`${BASE_URL}/roadmap/create`, {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: new URLSearchParams({
      name: 'Q4 2025 Compliance Implementation',
      description: 'Implementation plan for audit gaps',
      owner: 'Compliance Team'
    })
  });
  
  const roadmapUrl = roadmapResponse.url;
  const roadmapId = roadmapUrl.split('/').pop();
  
  // Add controls from audit to roadmap
  const controls = [123, 145, 167]; // Control IDs with gaps
  
  for (const controlId of controls) {
    await fetch(`${BASE_URL}/roadmap/add-from-control/${controlId}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        roadmap_id: roadmapId,
        priority: 'High',
        notes: `Gap identified in audit ${sessionId}`
      })
    });
  }
  
  return roadmapId;
}

// Usage
createRoadmapFromAudit('a1b2c3d4-5678-90ab-cdef-1234567890ab');
```

---

## Rate Limits & Quotas

### OpenAI API Limits
- Insight generation: Limited by OpenAI API quota
- Evidence evaluation: Limited by OpenAI API quota
- Recommended: Monitor usage and implement caching

### File Upload Limits
- Maximum file size: 10 MB per file
- Allowed formats: PDF, DOCX, JPG, PNG
- Maximum files per response: 10 files

### Database Limits
- Maximum concurrent sessions: Unlimited (SQLite limited by disk I/O)
- Maximum audit sessions: Unlimited
- Database size: Limited by available disk space

---

## Conclusion

The ASIMOV AI Governance Audit Tool provides a comprehensive REST API for conducting AI governance audits, managing evidence, generating reports, and planning implementations. The API is designed for:

- **Ease of Integration**: RESTful design with predictable endpoints
- **Rich Functionality**: 30+ endpoints covering all audit workflows
- **Flexible Data Export**: CSV, JSON, and HTML formats
- **AI-Powered Intelligence**: OpenAI GPT-4 integration for insights and evaluation
- **Enterprise Scalability**: Session-based architecture supporting concurrent users

For support, feature requests, or integration assistance, contact the development team or consult the technical design documentation.
