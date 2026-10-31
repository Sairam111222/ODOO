# SECURITY_CHECKLIST.md — Security Architecture & Verification

## 1. Role-Based Access Control (RBAC) Matrix

| Role | Odoo Security Group | Model Permissions | Record Scope | Financial Access? |
|---|---|---|---|---|
| **Technician** | `group_solar_technician` | Read & Write on `solar.installation`, `solar.service.ticket` | **Own Assigned Records Only** (enforced by `ir.rule`) | ❌ NO |
| **Surveyor** | `group_solar_surveyor` | Full CRUD on `solar.site.survey` | **Own Surveys Only** (enforced by `ir.rule`) | ❌ NO |
| **Salesperson** | `group_solar_salesperson` | Full on CRM & Leads, Read-Only on Packages, Create on Surveys & Subsidies | Company-wide sales pipeline | ⚠️ Quotations Only |
| **Survey Manager** | `group_solar_survey_manager` | Full on Surveys (Approve/Reject) | Company-wide surveys | ❌ NO |
| **Warehouse Manager** | `group_solar_warehouse_manager` | Full on `stock` & Serial Numbers | All inventory & picking | ❌ NO |
| **Accountant** | `group_solar_accountant` | Full on `account.move`, `account.payment`, Subsidies | Company-wide financials & job margins | ✅ Full Financials |
| **Support Agent** | `group_solar_support_agent` | Full on `solar.service.ticket`, Read on Warranties | Company-wide service tickets (No Delete) | ❌ NO |
| **Director** | `group_solar_director` | Full CRUD on all Solar models & Executive Dashboard | All records across company | ✅ Executive Views |
| **Administrator** | `group_solar_admin` | Unrestricted System Access | Global | ✅ Full Admin |

---

## 2. Server-Side Security Enforcement Rules

- [x] **No Security-Through-Obscurity**:
  - Hiding a button via XML `invisible="..."` or `groups="..."` is treated strictly as a UI convenience.
  - Every critical state transition:
    - `action_submit_for_approval` in `solar.site.survey`: validates mandatory measurements (roof area > 0, usable area <= roof area, cable distance > 0, bill > 0).
    - `action_generate_quotation` in `solar.site.survey`: server-side check strictly blocks unapproved surveys.
    - `action_verify_testing` in `solar.installation`: verifies earthing resistance between 0.1 and 5.0 Ω.
    - `action_commission` in `solar.installation`: enforces customer sign-off and serial numbers on inverters/batteries.
    - `action_close` in `solar.service.ticket`: enforces customer confirmation before closure.
- [x] **Row-Level Isolation (`ir.rule`)**:
  - Technicians cannot query or inspect installations assigned to other technicians (`[('technician_id', '=', user.id)]`).
  - Surveyors are constrained to surveys they originated or were explicitly assigned to (`['|', ('surveyor_id', '=', user.id), ('create_uid', '=', user.id)]`).
- [x] **Customer Portal Data Isolation**:
  - Authenticated portal customers are restricted strictly to `[('partner_id', '=', request.env.user.partner_id.id)]`.
  - Portal templates never render internal equipment cost, technician labor rates, or internal gross margins.
- [x] **Financial Segregation of Duties**:
  - Field Technicians and Support Agents have no read or write permissions to `account.move`, `sale.order.line` margins, or customer payment journals.
  - Warehouse managers can update serial numbers and stock moves but cannot alter invoice totals or payment statuses.

---

## 3. AI Safety & Cybersecurity Governance

| Threat / Vulnerability | Mitigation Mechanism in SolarFlow 360 | Status |
|---|---|---|
| **Prompt Injection** | Rigorous sanitization layer (`_sanitize_input`) strips system override prompts. | ✅ Verified |
| **Financial Hallucination**| Controlled tool-calling: LLM selects allowlisted tools; backend ORM returns grounded figures. | ✅ Verified |
| **Unauthorized Data Leakage**| RBAC permission verification gate on BI queries: technicians/support blocked from financial endpoints. | ✅ Verified |
| **Autonomous Action Hazard** | All AI recommendations (technician dispatch, procurement orders) require human managerial approval. | ✅ Verified |
| **SQL Injection** | Exclusively use Odoo ORM methods (`search`, `read`, `write`, `create`). No unescaped raw SQL. | ✅ Verified |
| **Cross-Site Scripting (XSS)** | All user-supplied text rendered through standard QWeb and Odoo XML field widgets with automatic HTML escaping. | ✅ Verified |
| **CSRF Attacks** | Odoo native session token validation enforced on all HTTP controller routes and web client RPCs. | ✅ Verified |
| **Serial Collision** | Server-side constraint prevents registering the same serial number across different installations. | ✅ Verified |
| **AI Service Failure Resilience**| Graceful local fallbacks: normal ERP operations continue unimpeded if an external AI service is offline. | ✅ Verified |
