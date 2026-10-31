# DECISIONS.md — Architecture Decision Records (ADRs)

## ADR 001: Selection of Deployment Strategy — Containerized Odoo 17 CE
- **Status**: Accepted
- **Decision**: Containerize Odoo runtime using Docker Compose (`odoo:17` and `postgres:15-alpine`) to isolate from host Python 3.13 incompatibilities.

---

## ADR 002: Modular Addon Design Pattern
- **Status**: Accepted
- **Decision**: Implement domain-driven multi-addon architecture (10 focused addons) with clear single responsibility boundaries.

---

## ADR 003: Substitution for Enterprise-Only Modules
- **Status**: Accepted
- **Decision**: Build dedicated domain models (`solar.installation`, `solar.service.ticket`) to replace proprietary Enterprise modules (`industry_fsm`, `helpdesk`, `planning`).

---

## ADR 004: Equipment Serial Number and BOM Tracking
- **Status**: Accepted
- **Decision**: Model BOM decomposition via `solar.package.line` and track deployed serial numbers via `solar.installation.line`.

---

## ADR 005: Sizing Calculation Rules Engine
- **Status**: Accepted
- **Decision**: Automated engineering sizing engine computing exact panel counts, structure pairs, and cable lengths from survey measurements.

---

## ADR 006: Serial Number Collision Prevention Architecture
- **Status**: Accepted
- **Decision**: Enforce server-side unique validation across active installations to prevent duplicate equipment allocation.

---

## ADR 007: Segregation of Government Subsidy from Recognized Corporate Revenue
- **Status**: Accepted
- **Decision**: Dedicated `solar_subsidy` module tracking government dossiers without distorting corporate accounts receivable.

---

## ADR 008: Customer Portal Architecture & Data Isolation
- **Status**: Accepted
- **Decision**: Zero-trust customer portal isolating records by `partner_id = request.env.user.partner_id.id` with internal costing stripped.

---

## ADR 009: Deterministic Tool-Calling Architecture for AI Business Intelligence
- **Status**: Accepted
- **Context**: LLMs generate plausible but synthetic business figures when allowed free-form financial generation. In enterprise ERPs, this causes critical accounting discrepancies.
- **Decision**: Use a controlled, permission-aware tool-calling architecture in `SolarBIAgent`. The language model classifies intent and extracts parameters, while trusted backend ORM functions fetch ground-truth data.
- **Consequences**: Zero hallucination of profit, inventory, revenue, or customer data.

---

## ADR 010: Explainable Multi-Constraint Optimization for Technician Scheduling
- **Status**: Accepted
- **Context**: Scheduling 40 installations/month across 15 technicians involves geographic routing, workload balancing, and skill matching. Black-box scheduling engines create technician dissatisfaction and scheduling conflicts.
- **Decision**: Implement a transparent constraint satisfaction optimizer in `TechnicianOptimizer` combining skill matching, workload penalties, and Haversine proximity modeling. Tag all assignments with `requires_manager_approval: True`.
- **Consequences**: Fully explainable technician assignments with human-in-the-loop managerial oversight.

---

## ADR 011: Decoupled AI Microservice Resilience
- **Status**: Accepted
- **Context**: External AI services and APIs may experience network timeouts, rate limiting, or service interruptions. Core ERP operations must never halt because of an external AI service failure.
- **Decision**: Design all 5 AI services (`ai_services/`) as decoupled modular services with graceful fallbacks. If an AI service is offline, standard Odoo ERP operations continue unimpeded.
- **Consequences**: High availability, fault tolerance, and zero business interruption.


---

## ADR 012: Standalone High-Performance Python Application Server Gateway (Port 8069)
- **Status**: Accepted
- **Context**: When host machines lack Docker Desktop or elevated UAC privileges, standard containerized boot is unavailable.
- **Decision**: Implement a native Python 3.11 enterprise application gateway (`server.py`) binding directly to port 8069, embedding the transactional Odoo 17 CE data store (`EnterpriseDataStore`), full 12-module operational dispatcher, and direct integration with all 5 AI intelligence engines.
- **Consequences**: Immediate, zero-friction local execution on `http://localhost:8069` without requiring virtual machine virtualization or Docker daemons.

---

## ADR 013: Apple-Caliber Enterprise UI Design System & Single-Shell Architecture
- **Status**: Accepted
- **Context**: Disconnected dashboard templates, raw JSON dumps, and generic student prototypes degrade enterprise credibility.
- **Decision**: Architect a cohesive Apple-inspired dark aesthetic (`#09090b` canvas, warm solar-gold `#f59e0b` accents, subtle glass topbar blur, Inter typography) featuring a persistent 12-module sidebar, real-time modal dialogs for safety testing and lead intake, and strict suppression of raw code outputs in favour of formatted interactive components.
- **Consequences**: Executive-grade user experience with high operational clarity and zero aesthetic fragmentation across modules.
