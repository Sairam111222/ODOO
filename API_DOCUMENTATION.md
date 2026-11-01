# SolarFlow 360 — Complete REST API & Integration Reference

**Base URL:** `http://localhost:8069`  
**Authentication:** Cookie-based session (`sf_session=<uuid>`) or JSON body `role=<role>`  
**Standard Response Headers:**  
- `Content-Type: application/json; charset=utf-8`  
- `X-Content-Type-Options: nosniff`  
- `X-Frame-Options: DENY`  
- `X-XSS-Protection: 1; mode=block`  

---

## 1. Authentication Endpoints

### `POST /api/login` (Alias: `/api/auth`)
Authenticates user credentials against the Odoo XML-RPC gateway (with graceful fallback to credential directory).

- **Allowed Roles:** All users
- **Request Body:**
  ```json
  {
    "email": "director@sunpower.com",
    "password": "Director@360"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "status": "success",
    "role": "director",
    "name": "Director (Executive)",
    "email": "director@sunpower.com",
    "token": "sf360_session_director_a3f89e21-..."
  }
  ```
- **Response Headers:** `Set-Cookie: sf_session=<token>; HttpOnly; SameSite=Strict; Path=/`
- **Error (401 Unauthorized):**
  ```json
  { "error": "Invalid email or password. Please verify the credentials." }
  ```

### `POST /api/logout`
Terminates user session and clears authentication cookies.

- **Response (200 OK):**
  ```json
  { "status": "logged_out" }
  ```

---

## 2. Core Operational Endpoints (GET)

| Endpoint | Allowed Roles | Description | Response Model |
|---|---|---|---|
| `GET /api/overview` | All roles (filtered by role) | Executive KPI summary, active projects, monthly target | `invoiced_revenue`, `gross_profit`, `monthly_installs` |
| `GET /api/operations` | Director, Operations | Daily dispatch schedules, crew status, technical queue | `active_projects`, `scheduled_today`, `technician_load` |
| `GET /api/crm` | Director, Sales, Operations | Leads, opportunities, customer accounts | `leads`, `customers`, `conversion_rate` |
| `GET /api/surveys` | Director, Operations, Sales | Site survey dossiers and measurement logs | `surveys` (array of `solar.site.survey`) |
| `GET /api/packages` | All roles | Pre-engineered BOM packages and pricing | `packages` (1kW to 5kW configurations) |
| `GET /api/installations` | All roles (row-level filtered) | Active and historical installation projects | Technicians only see assigned jobs; costs stripped |
| `GET /api/inventory` | Director, Operations, Sales | Warehouse stock levels and serial registries | `inventory` (on_hand, reserved, unit_cost) |
| `GET /api/financials` | Director only (403 for others) | Company ledgers, receivable schedules, gross margins | `cash_received`, `receivables`, `gross_margin_pct` |
| `GET /api/warranties` | Director, Operations, Sales, Tech | Registered warranties and service tickets | `warranties`, `tickets` |
| `GET /api/approvals` | Director, Operations | Maker-checker approval requests queue | `approvals`, `pending_count` |
| `GET /api/notifications`| All roles | In-app notification center | `notifications` (unread count, alert items) |
| `GET /api/audit-log` | Director only (403 for others) | Immutable audit log of operational and financial actions | `audit_log` (timestamp, user, action, result) |
| `GET /api/purchase-orders` | Director, Operations | Procurement orders and vendor deliveries | `purchase_orders` |
| `GET /api/odoo-status` | All roles | Odoo 17 CE connection and ORM bridge health check | `connected`, `url`, `db`, `mode` |

---

## 3. Workflow Transaction Endpoints (POST)

### `POST /api/create-lead`
Registers a new CRM opportunity.
- **Allowed Roles:** Director, Salesperson, Operations (Technician blocked with 403)
- **Request Body:**
  ```json
  {
    "role": "salesperson",
    "name": "Customer Name",
    "phone": "+91 98765 43210",
    "capacity_kw": 3.0
  }
  ```
- **Response (200 OK):** `{"status": "success", "ref": "LEAD-2026-0046"}`

### `POST /api/survey-submit`
Submits site measurements and shading assessments.
- **Allowed Roles:** Director, Operations, Salesperson
- **Request Body:**
  ```json
  {
    "role": "operations",
    "partner_id": 1,
    "lead_id": 1,
    "roof_sqft": 600.0,
    "usable_sqft": 450.0,
    "rec_capacity_kw": 3.0,
    "surveyor": "Pradeep Gowda",
    "roof_type": "flat_rcc",
    "tilt": 15.0,
    "orientation": "south"
  }
  ```
- **Response (200 OK):** `{"status": "success", "ref": "SRV/2026/0005", "id": 5}`

### `POST /api/survey-action`
Executes approval or rejection transitions on site surveys.
- **Allowed Roles:** Director, Operations (Sales/Tech blocked with 403)
- **Actions:** `approve`, `reject`, `submit`
- **Response (200 OK):** `{"status": "success", "state": "approved"}`

### `POST /api/quotation-create`
Generates a commercial quotation from an approved site survey.
- **Allowed Roles:** Sales Administrator, Operations, Director
- **Guard:** Survey must be in `approved` state (HTTP 400 otherwise)
- **Request Body:**
  ```json
  {
    "role": "salesperson",
    "survey_id": 1,
    "package_id": 3,
    "qty": 1,
    "custom_price": 185000.0,
    "discount_pct": 5.0
  }
  ```
- **Response (200 OK):** `{"status": "success", "ref": "QT-2026-0001", "amount_total": 175750.0}`

### `POST /api/payment-record`
Records customer advance or milestone payments against sales orders.
- **Allowed Roles:** Sales Administrator, Operations, Director
- **Guard:** Amount must be > 0. Automatically recalculates order `paid_amount` and `payment_state`.
- **Response (200 OK):** `{"status": "success", "paid_amount": 185000.0, "payment_state": "paid", "remaining": 0.0}`

### `POST /api/assign-technician`
Dispatches certified field technicians to installation jobs.
- **Allowed Roles:** Operations Manager, Director
- **Guards:** Skill-matching (e.g. 5kW+ requires Three-Phase certification) and workload ceiling (`max_jobs`).
- **Response (200 OK):** `{"status": "success", "assigned_tech": "Rajesh Kumar", "active_jobs": 2}`

### `POST /api/qa-submit`
Records electrical safety and quality verification results.
- **Allowed Roles:** Field Technician, Operations Manager, Director
- **Request Body:**
  ```json
  {
    "role": "technician",
    "installation_id": 2,
    "dc_v": 520.0,
    "ac_v": 415.0,
    "earthing_ohms": 1.8,
    "checklist": {
      "panel_alignment": true,
      "inverter_connections": true,
      "earthing": true,
      "dc_ac_test": true,
      "cable_tray": true
    }
  }
  ```
- **Response (200 OK):** `{"status": "success", "qa_result": "PASSED", "testing_passed": true}`

### `POST /api/commissioning`
Final commissioning sign-off and multi-tier warranty activation.
- **Allowed Roles:** Director, Operations Manager (Technician/Sales blocked with 403)
- **Guard:** Requires `testing_passed = true`.
- **Response (200 OK):** `{"status": "success", "commissioned_date": "2026-11-01", "warranties_activated": 3}`

### `POST /api/customer-signoff`
Captures customer acceptance, signature acknowledgement, and rating.
- **Allowed Roles:** Field Technician, Operations, Director
- **Response (200 OK):** `{"status": "success", "customer_signoff": "Customer Name", "rating": 5}`

### `POST /api/approval-request` & `POST /api/approval-decision`
Maker-checker governance framework for financial and operational exceptions.
- **Request:** Raised by Sales or Operations (`status: pending`)
- **Decision:** Authorized strictly by Director (`status: approved` or `rejected`)

