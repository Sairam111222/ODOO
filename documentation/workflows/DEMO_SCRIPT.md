# DEMO_SCRIPT.md — Complete 31-Step SolarFlow 360 Demonstration Scenario

This live demonstration script walks through the complete end-to-end customer journey for **SunPower Solutions** using actual Odoo records without manual database hacking or mock placeholders.

---

## Act 1: Customer Acquisition & Lead Qualification (Steps 1–3)
- **Step 1: Inbound Lead Intake**: Customer *Sharma Textiles / Rajesh Sharma* submits an enquiry via WhatsApp / Web Form requesting a 3kW On-Grid rooftop solar system.
- **Step 2: Duplicate Check**: Salesperson inspects `crm.lead`. System runs `_compute_duplicate_lead()` against phone `+919876543210` to confirm uniqueness.
- **Step 3: Lead Qualification**: Salesperson tags customer as *Small Commercial*, records monthly electricity bill (₹4,500), and schedules an automated 48-hour follow-up activity.

---

## Act 2: Engineering Feasibility Survey (Steps 4–6)
- **Step 4: Survey Request**: Salesperson clicks **Create Site Survey**. System auto-creates `solar.site.survey` (Ref: `SRV/2026/0001`).
- **Step 5: On-Site Roof Inspection**: Field surveyor records roof measurements: 500 sq ft RCC roof, 15° tilt, South orientation, No shading, 25m cable distance to distribution board.
- **Step 6: Technical Review & Approval**: Surveyor submits survey. Survey Manager reviews parameters, confirms grid feasibility, and clicks **Approve Survey**.

---

## Act 3: Package Sizing & Quotation (Steps 7–10)
- **Step 7: Sizing & BOM Engine**: Sizing engine calculates exact materials: 6 panels (550 Wp Mono-PERC), 3 mounting structure pairs, 60m DC cable, 30m AC cable, DCDB/ACDB, 2 earthing pits.
- **Step 8: Quotation Generation**: Salesperson clicks **Generate Quotation** from the approved survey. Sale Order `SO-2026-0001` is created with itemized pricing (₹185,000 total).
- **Step 9: Customer Acceptance**: Customer reviews proposal via Customer Portal and accepts the terms.
- **Step 10: Advance Payment**: Accountant logs 20% advance booking payment (₹37,000) against `SO-2026-0001`.

---

## Act 4: Warehouse Allocation & Equipment Dispatch (Steps 11–15)
- **Step 11: Inventory Verification**: Warehouse Manager inspects stock availability for 550W panels and 3kW inverters.
- **Step 12: Stock Reservation**: Materials are allocated to project.
- **Step 13: Mandatory Serial Scanning**: Inverter serial `INV-GROWATT-9921` is scanned and recorded on the project line.
- **Step 14: Collision Prevention Verification**: System confirms `INV-GROWATT-9921` is not registered on any other active project.
- **Step 15: Material Dispatch**: Warehouse confirms dispatch to installation site.

---

## Act 5: Intelligent Technician Dispatch & Installation (Steps 16–22)
- **Step 16: Project Generation**: System creates installation project `INS/2026/0001`.
- **Step 17: AI Technician Optimization**: Dispatcher runs **Technician Optimizer**. AI recommends *Suresh Patel (Senior Technician)* based on proximity, 0 active workload, and 3kW qualifications.
- **Step 18: Schedule Approval**: Dispatcher confirms schedule for tomorrow 09:00 AM.
- **Step 19: Work In Progress**: Technician crew arrives on site, mounts elevated structure, and fixes 6 PV panels.
- **Step 20: Photographic Evidence**: Technician uploads before, during, and after photos to Odoo chatter.
- **Step 21: Electrical Safety Testing**: Technician records DC Voltage (380V), AC Voltage (230V), and Earthing Resistance (2.1 Ω). System validates safety thresholds.
- **Step 22: Customer Sign-off**: Customer conducts walkthrough with lead technician and signs off with a 5-star rating.

---

## Act 6: Commissioning & Automated Warranties (Step 23)
- **Step 23: Commissioning & Handover**: Manager clicks **Commission & Activate Warranties**. System verifies net-meter installation, updates project status, and auto-generates:
  - 25-Year Performance Warranty for Solar Panels (`WRN/2026/0001`)
  - 5-Year Hardware Warranty for Inverter (`WRN/2026/0002`)
  - 1-Year Comprehensive Workmanship Guarantee (`WRN/2026/0003`)

---

## Act 7: Post-Sales Service & Breakdown Management (Steps 24–29)
- **Step 24: Customer Complaint**: Customer notices an inverter error code after a thunderstorm and logs a complaint via Customer Portal.
- **Step 25: Ticket Generation**: Service Ticket `SVC/2026/0001` is logged.
- **Step 26: Serial Lookup & Warranty Check**: System auto-matches serial `INV-GROWATT-9921` to active warranty `WRN/2026/0002` and classifies job as **Free Warranty Service**.
- **Step 27: Technician Dispatch & Diagnosis**: Technician diagnoses a blown DC surge protection device (SPD) and replaces it.
- **Step 28: Customer Confirmation**: Customer confirms generation is restored.
- **Step 29: Ticket Closure**: Ticket is closed with zero billable customer charge.

---

## Act 8: Financial Job Profitability & AI Executive Review (Steps 30–31)
- **Step 30: Project Profitability**:
  - Revenue Invoiced: ₹185,000
  - Equipment Cost: ₹115,000
  - Technician Labour: ₹4,000 (16 hrs @ ₹250/hr)
  - Transport & Permits: ₹3,500
  - **Gross Profit: ₹62,500 (Gross Margin: 33.8%)**
- **Step 31: AI Business Assistant Summary**: Director asks: *"What was our gross profit and margin on the Sharma Textiles project?"*
  - AI Assistant immediately replies with exact grounded figures (₹62,500 / 33.8%) citing `INS/2026/0001`.

