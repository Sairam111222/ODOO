# SolarFlow 360 — AI-Powered Solar ERP for SunPower Solutions

**SolarFlow 360** is an enterprise-grade Solar Installation Management ERP built natively on **Odoo 17 Community Edition (CE)**. It streamlines operational workflows for residential and small commercial rooftop solar projects (1 kW to 5 kW), coordinating ~40 installations per month across a 15-technician crew.

---

## 1. System Requirements & Architecture
- **OS**: Windows, Linux, or macOS
- **Container Runtime**: Docker Desktop (Engine 24+ / Compose v2+) **OR** Standalone Python 3.11 Enterprise Gateway
- **Ports**: `8069` (Odoo Web HTTP / SolarFlow UI), `5432` (PostgreSQL)
- **Architecture**: Modular Monolithic Odoo CE (10 Addons) + Modular AI Intelligence Layer (5 Engines)
- **UI Design System**: Apple-Caliber Dark Canvas (`#09090b`), Gold Accents (`#f59e0b`), Inter Typography, 12-Module Persistent Shell

---

## 2. Directory Structure Overview
```text
solarflow_360/
├── AGENTS.md               # Permanent engineering directives
├── README.md               # Quickstart, deployment & testing guide
├── PROJECT_STATUS.md       # Status, completed milestones & acceptance gates
├── ARCHITECTURE.md         # Full system architecture, sequence diagrams & ERD
├── DECISIONS.md            # Architecture Decision Records (ADRs 001 - 013)
├── SECURITY_CHECKLIST.md   # RBAC matrix, zero-trust rules & AI safety
├── TEST_REPORT.md          # Automated test execution report (28 pytest + 26 endpoint tests)
├── SOLARFLOW_360_TECHNICAL_DEFENSE.md # Comprehensive system audit & technical defense
│
├── addons/                 # Custom Odoo 17 CE addons (10 modules)
│   ├── solar_core/         # Base data, groups, rules, technician profiles, sequences
│   ├── solar_crm/          # WhatsApp/phone lead capture, duplicate detection & qualification
│   ├── solar_survey/       # Roof feasibility, shading, tilt, cable route & capacity sizing
│   ├── solar_package/      # 1kW-5kW standard packages & automated BOM sizing rules
│   ├── solar_installation/ # Crew dispatch, serial tracking, safety tests, job profitability
│   ├── solar_warranty/     # Configurable policies, 25-yr PV / 5-yr Inverter guarantee tracking
│   ├── solar_service/      # Breakdown repair ticketing, spare parts & SLA management
│   ├── solar_subsidy/      # PM Surya Ghar & state subsidy dossier tracking & 6-point checklist
│   ├── solar_portal/       # Customer self-service portal (installations, warranties, tickets)
│   └── solar_dashboard/    # Executive KPI graphs, pivot analytics & Enterprise Global Search
│
├── ai_services/            # Modular AI & Optimization Layer
│   ├── business_intelligence/  # Permission-aware BI agent (zero-hallucination tool calling)
│   ├── technician_optimizer/   # Constraint satisfaction & proximity routing optimizer
│   ├── inventory_forecasting/  # Run-rate baseline & procurement demand forecaster
│   ├── solar_intelligence/     # Photovoltaic yield, orientation derate & payback modeling
│   └── roof_assessment/        # Preliminary obstacle setback & usable area analysis
│
├── documentation/          # Enterprise Technical Documentation
│   ├── security/           # SECURITY_AUDIT.md (OWASP Top 10 Review)
│   ├── database/           # DATABASE_INTEGRITY.md (Relational & Concurrency Audit)
│   ├── architecture/       # PERFORMANCE_AUDIT.md (Scalability & ORM Review)
│   ├── workflows/          # DEMO_SCRIPT.md (Complete 31-Step Demonstration)
│   └── presentation/       # HACKATHON_PRESENTATION.md (Pitch Deck & Architecture Overview)
│
├── configuration/          # Production Odoo and DB configuration
│   └── odoo/odoo.conf
├── scripts/                # Production operations & disaster recovery
│   ├── backup_database.ps1 / .sh   # Automated PostgreSQL backup
│   └── restore_database.ps1 / .sh  # Automated PostgreSQL restoration
├── server.py               # Enterprise Application Server Gateway (Port 8069)
├── test_server_endpoints.py # Automated 26-step API and transaction test suite
├── start.bat               # One-click dual-mode launcher (Docker Compose or Python Gateway)
├── tests/                  # Automated integration & unit tests
│   └── integration/
├── docker-compose.yml      # Container orchestration
└── requirements.txt        # Python dependency manifest
```

---

## 3. Quickstart & Deployment Instructions

### One-Click Launch (Recommended)
Double-click `start.bat` or run:
```bat
start.bat
```
*Auto-detects Docker Desktop. If Docker is active, boots PostgreSQL 15 & Odoo 17 CE containers. If Docker is absent, transparently falls back to the high-performance Python 3.11 Gateway on port 8069 and opens your default browser.*

### Manual Docker Compose Deployment
```bash
cp .env.example .env
docker compose up -d
```
Access the web client at `http://localhost:8069`.

### Standalone Python Gateway Deployment
```bash
python server.py
```
Access the web client at `http://localhost:8069`.

---

## 4. Running Automated Tests

### 1. Pytest Integration Test Suite (28 Tests)
```bash
python -m pytest -v
```
Validates:
- Manifest syntax and dependency chains across all 10 modules
- XML view syntax and valid model bindings
- Cross-module ORM integrity and record rule self-containment
- Business logic: duplicate phone lead matching, electrical testing safety rule ($\le 5.0\,\Omega$), job profitability, serial collision prevention, warranty duration math, and survey mandatory measurements
- 5 AI services: prompt injection sanitization, RBAC boundaries, demand forecasting, obstacle setbacks, PV yield, and technician optimization

### 2. Runtime Endpoint & Transaction Suite (26 Tests)
```bash
python test_server_endpoints.py
```
Validates:
- 13 REST data endpoints (`overview`, `operations`, `dispatch`, `sizing`, `roof`, `surveys`, `packages`, `crm`, `inventory`, `installations`, `warranty`, `warranties`, `financials`)
- Global multi-entity search (`growatt`, `sharma`, `INS/2026`, `WRN`)
- All 9 required AI BI queries with grounded evidence citations
- AI RBAC permission security gate (Technician profit query blocked with HTTP 200 / `error_forbidden`)
- Inbound CRM lead creation with duplicate validation
- Site survey approval and quotation generation gating
- 15-technician dispatch constraint optimization and skill validation
- Mandatory electrical testing verification ($\text{DC} \approx 520\,\text{V}$, $\text{AC} \approx 415\,\text{V}$, Earthing resistance $\le 5.0\,\Omega$)
- Commissioning lifecycle transition and automated warranty certificate activation

---

## 5. Production Database Backup & Restore

### Backup Database
```bash
# Windows PowerShell
./scripts/backup_database.ps1

# Linux / macOS Bash
./scripts/backup_database.sh
```

### Restore Database
```bash
# Windows PowerShell
./scripts/restore_database.ps1 -DumpFile "./backups/solarflow_backup_XXXX.dump"

# Linux / macOS Bash
./scripts/restore_database.sh "./backups/solarflow_backup_XXXX.dump"
```
