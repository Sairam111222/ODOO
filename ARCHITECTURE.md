# ARCHITECTURE.md — SolarFlow 360 System Architecture

## 1. Executive Summary
SolarFlow 360 is an enterprise-grade solar installation ERP built natively on **Odoo 17 Community Edition (CE)**. It unifies the fragmented customer journey for **SunPower Solutions**—orchestrating lead acquisition (WhatsApp, calls, web forms), physical site surveys, standardized system packages (1kW to 5kW), multi-technician crew dispatch, quality testing, utility net-metering interconnection, government subsidy dossiers, long-term warranties, customer self-service portal, post-sales field service, and modular AI intelligence services.

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    actor Sales as Salesperson
    actor Surveyor as Field Surveyor
    actor Manager as Survey Manager
    actor Tech as Lead Technician (15-Crew Pool)
    actor Support as Support Agent
    actor AI as AI Services Layer

    Customer->>Sales: 1. Inbound Enquiry (WhatsApp / Web / Phone)
    Sales->>Sales: 2. Lead Qualification & Duplicate Check (solar_crm)
    Sales->>Surveyor: 3. Schedule Site Feasibility Survey (solar_survey)
    Surveyor->>AI: 4. Preliminary Roof Obstacle Assessment (roof_assessment)
    Surveyor->>Surveyor: 5. Inspect Roof, Tilt, Shading & Cable Route
    Surveyor->>Manager: 6. Submit Measurements (Mandatory Validations)
    Manager->>Manager: 7. Technical Review & Survey Approval
    Sales->>AI: 8. Sizing, PV Yield & Payback Calculation (solar_intelligence)
    Sales->>Sales: 9. Auto-Calculate Materials & Sizing (solar_package)
    Sales->>Customer: 10. Present Quotation (1kW-5kW Sized System)
    Customer->>Sales: 11. Acceptance & Advance Booking Payment
    Sales->>AI: 12. Run Intelligent Technician Optimization (technician_optimizer)
    AI-->>Manager: 13. Recommend Crew based on Proximity & Workload
    Manager->>Tech: 14. Approve Schedule & Dispatch Crew (solar_installation)
    Tech->>Tech: 15. Equipment Allocation & Serial Number Scanning
    Tech->>Tech: 16. Safety Verification (DC/AC Volts, Earthing <= 5 Ohm)
    Customer->>Tech: 17. Digital Handover Walkthrough & Sign-off
    Tech->>Manager: 18. Commission Installation & Net-Meter Sync
    Manager->>Customer: 19. Automated Warranties (25-Yr Panel, 5-Yr Inverter) (solar_warranty)
    Customer->>Support: 20. Log Breakdown Complaint via Portal (solar_portal)
    Support->>Tech: 21. Warranty Verification & Field Dispatch (solar_service)
    Manager->>AI: 22. Conversational Business Intelligence Review (solar_bi_agent)
```

---

## 2. Complete Module Dependency Matrix

```mermaid
graph TD
    base[Odoo base / mail / contacts] --> solar_core
    crm[crm] --> solar_crm
    solar_core --> solar_crm
    solar_core --> solar_survey
    solar_core --> solar_package
    product[product] --> solar_package
    solar_core --> solar_installation
    solar_survey --> solar_installation
    solar_package --> solar_installation
    stock[stock] --> solar_installation
    sale[sale_management] --> solar_installation
    solar_core --> solar_warranty
    solar_installation --> solar_warranty
    solar_core --> solar_service
    solar_installation --> solar_service
    solar_warranty --> solar_service
    solar_core --> solar_subsidy
    solar_installation --> solar_subsidy
    portal[portal] --> solar_portal
    solar_core --> solar_portal
    solar_installation --> solar_portal
    solar_warranty --> solar_portal
    solar_service --> solar_portal
    solar_core --> solar_dashboard
    solar_installation --> solar_dashboard
    solar_crm --> solar_dashboard
    solar_warranty --> solar_dashboard
    solar_service --> solar_dashboard
    solar_subsidy --> solar_dashboard

    subgraph AI_Intelligence_Layer["Modular AI Services Layer (ai_services/)"]
        AI_BI[solar_bi_agent]
        AI_TECH[technician_optimizer]
        AI_INV[inventory_forecasting]
        AI_SOL[solar_intelligence]
        AI_ROOF[roof_assessment]
    end

    solar_dashboard -.-> AI_BI
    solar_installation -.-> AI_TECH
    solar_package -.-> AI_INV
    solar_survey -.-> AI_SOL
    solar_survey -.-> AI_ROOF
```

---

## 3. Modular Architecture Overview (10 Addons + 5 AI Engines)

| Component | Primary Role | Key Models / Engines | Security & Governance Rules |
|---|---|---|---|
| **`solar_core`** | Foundation & Security | `res.partner`, `res.users`, `solar.system.type` | 9 RBAC roles, technician profiles, master sequences. |
| **`solar_crm`** | Lead Qualification | `crm.lead` | Inbound channel tracking, duplicate detection, 48h automated follow-up call activity. |
| **`solar_survey`** | Engineering Feasibility | `solar.site.survey` | Mandatory measurement validations, approval workflow, resurvey revisions, unapproved survey quotation block. |
| **`solar_package`** | System Sizing & BOM | `solar.package`, `solar.package.line` | 1kW-5kW configurations, auto BOM sizing rules (panels, structures, cables), quotation line generation. |
| **`solar_installation`** | Operations & Job Costing | `solar.installation`, `solar.installation.line` | 8-stage lifecycle, 15-technician pool, serial collision prevention, safety testing, job-level gross margin %. |
| **`solar_warranty`** | Guarantee Certificates | `solar.warranty`, `solar.warranty.policy` | Configurable policies (25-yr PV, 5-yr Inverter), serial mapping, 60-day expiry state transition. |
| **`solar_service`** | Breakdowns & Maintenance | `solar.service.ticket`, `solar.service.part.line` | 8-stage repair lifecycle, serial lookup, warranty claim classification (free vs chargeable), spare parts costing. |
| **`solar_subsidy`** | Government Paperwork | `solar.subsidy.tracker` | Central/state rooftop schemes, 6-point checklist, national portal application tracking (segregated from revenue). |
| **`solar_portal`** | Customer Self-Service | Controllers extending `CustomerPortal` | Secure customer tracking for installations, warranties, ticket logging. Isolated by `partner_id`. |
| **`solar_dashboard`**| Executive Control Center | `solar.executive.dashboard`, `solar.global.search.wizard` | Real-time computed KPIs (velocity vs 40 installs/mo, financials), multi-model global search. |
| **`solar_bi_agent`** | AI Business Intelligence | `SolarBIAgent` | Allowlisted tool execution, zero hallucination, RBAC permission gate on financial data. |
| **`technician_optimizer`** | Intelligent Dispatch | `TechnicianOptimizer` | Constraint satisfaction (skills, workload, proximity). Requires manager approval before commit. |
| **`inventory_forecasting`**| Predictive Procurement | `InventoryDemandForecaster` | Blended run-rate forecast based on 40 installs/month target. Suggests procurement with uncertainty bounds. |
| **`solar_intelligence`** | PV Yield & Financials | `SolarGenerationIntelligence` | Physics-grounded solar yield modeling with explicit estimation disclaimers. |
| **`roof_assessment`** | Feasibility Assistant | `RoofAssessmentAssistant` | Geometric obstacle setback deduction. Physical survey verification mandatory. |

---

## 4. Entity Relationship Model (ERD)

```mermaid
erDiagram
    RES_PARTNER ||--o{ CRM_LEAD : acquires
    RES_PARTNER ||--o{ SOLAR_SITE_SURVEY : requests
    RES_PARTNER ||--o{ SOLAR_INSTALLATION : contracts
    RES_PARTNER ||--o{ SOLAR_WARRANTY : holds
    RES_PARTNER ||--o{ SOLAR_SERVICE_TICKET : logs
    RES_PARTNER ||--o{ SOLAR_SUBSIDY_TRACKER : claims

    SOLAR_SYSTEM_TYPE ||--o{ SOLAR_PACKAGE : standardizes
    SOLAR_SYSTEM_TYPE ||--o{ SOLAR_SITE_SURVEY : recommends
    SOLAR_SYSTEM_TYPE ||--o{ SOLAR_INSTALLATION : deploys

    SOLAR_PACKAGE ||--o{ SOLAR_PACKAGE_LINE : decomposes
    SOLAR_PACKAGE ||--o{ SOLAR_INSTALLATION : provisions

    SOLAR_SITE_SURVEY ||--o| SALE_ORDER : feeds_approved_data
    SALE_ORDER ||--o| SOLAR_INSTALLATION : initiates

    SOLAR_INSTALLATION ||--o{ SOLAR_INSTALLATION_LINE : tracks_equipment_serials
    SOLAR_INSTALLATION ||--o{ SOLAR_WARRANTY : activates_on_commissioning
    SOLAR_INSTALLATION ||--o{ SOLAR_SERVICE_TICKET : services
    SOLAR_INSTALLATION ||--o| SOLAR_SUBSIDY_TRACKER : documents

    SOLAR_WARRANTY ||--o{ SOLAR_SERVICE_TICKET : verifies_warranty_coverage
```
