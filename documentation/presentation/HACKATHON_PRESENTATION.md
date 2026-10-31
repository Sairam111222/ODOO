# HACKATHON_PRESENTATION.md — SolarFlow 360 Pitch Deck & Presentation Guide

## 1. Executive Problem Statement
- **The Customer**: SunPower Solutions (Residential & Small Commercial Rooftop Solar EPC).
- **Scale**: ~40 installations/month across a 15-technician crew.
- **The Pain Point**: Disconnected operations using WhatsApp, paper notes, disconnected Excel sheets, and phone calls.
  - Sizing errors caused frequent site shortages.
  - Lost serial numbers invalidated manufacturer warranties.
  - No real-time visibility into whether installations were making or losing money.
  - Customer complaints were lost in WhatsApp group chats.

---

## 2. The Solution: SolarFlow 360
A unified, end-to-end Solar ERP built natively on **Odoo 17 Community Edition** powered by 5 modular AI engines:
1. **Zero-Fragmentation Workflow**: Enquiry $\rightarrow$ Survey $\rightarrow$ Package $\rightarrow$ Quotation $\rightarrow$ Payment $\rightarrow$ Serials $\rightarrow$ Dispatch $\rightarrow$ Installation $\rightarrow$ Testing $\rightarrow$ Sign-off $\rightarrow$ Warranty $\rightarrow$ Service.
2. **Deterministic Engineering Sizing Engine**: Converts roof measurements and cable distances directly into exact component lists.
3. **Mandatory Equipment Serial Traceability**: Tracks individual inverters and batteries from warehouse receipt to 25-year warranty enforcement.
4. **Job-Level True Profitability**: Tracks exact revenue vs material, labour, and transport expenses per project.

---

## 3. Five Signature Architectural Innovations

### Innovation 1: End-to-End Serial Traceability
- Prevents serial number collisions.
- Automatically generates 25-yr PV / 5-yr Inverter warranty certificates on verified commissioning.
- Service tickets immediately identify warranty eligibility by scanning the inverter serial number.

### Innovation 2: Intelligent Technician Optimization Engine
- Solves the multi-objective scheduling problem across the 15-technician field crew.
- Matches technician certifications (e.g. 5kW Three-Phase systems require Senior/Lead grade).
- Balances daily workloads and minimizes travel distance via GPS proximity modeling.
- Requires managerial confirmation before committing schedules.

### Innovation 3: Conversational Business Intelligence Agent
- Grounded strictly in authorized Odoo database records.
- Zero hallucination of financial or customer figures.
- Role-based security gates: Field technicians cannot query executive profit margins; Directors see full financial breakdowns.

### Innovation 4: Transparent PV Yield & Sizing Engine
- Calculates expected generation, seasonal derates, and simple payback period.
- Clearly separates statistical estimates from guaranteed outputs with explicit uncertainty intervals.

### Innovation 5: Zero-Trust Customer Self-Service Portal
- Responsive web portal allowing customers to track installation status, review active warranty certificates, and log breakdown complaints without exposing internal company costing.

---

## 4. Live Demonstration Flow (6 Minutes)
1. **0:00 - 1:00**: Show inbound WhatsApp lead and automated duplicate detection in `solar_crm`.
2. **1:00 - 2:00**: Open Site Survey `SRV/2026/0001` showing mandatory measurement validation and manager approval.
3. **2:00 - 3:00**: Demonstrate Sizing & BOM engine auto-calculating 6 panels, structure kits, and 60m cable.
4. **3:00 - 4:00**: Dispatch 15-technician pool using the **Technician Optimizer**; demonstrate serial scanning and electrical safety verification.
5. **4:00 - 5:00**: Commission project $\rightarrow$ show automated 25-year warranty activation $\rightarrow$ log breakdown ticket via Customer Portal with serial lookup.
6. **5:00 - 6:00**: Show real-time **Executive Dashboard** and ask the **AI Business Intelligence Agent** for actual job profit (₹62,500 / 33.8% margin).

---

## 5. Technology Stack & Architectural Elegance
- **Backend ERP**: Odoo 17 Community Edition (Python 3.11, PostgreSQL 15, XML QWeb, OWL).
- **Deployment**: Zero-dependency Docker Compose orchestration with persistent named volumes.
- **AI / Optimization**: Modular Python constraint satisfaction, heuristic routing, and statistical forecasting engines.
- **Code Quality**: 100% PEP 8 compliant, 21 passing automated integration tests in 0.108s.

