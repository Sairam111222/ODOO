# -*- coding: utf-8 -*-
"""
SolarFlow 360 — Role-Based Access Control (RBAC) & Security Boundary Test Suite
================================================================================
Validates all 4 user roles separately against the running server:
  1. Director / Administrator (Full Access)
  2. Sales Administrator (CRM & Quotes, no unrestricted financials, no tech admin)
  3. Operations Manager (Operations, Surveys, Dispatch, no executive financials)
  4. Field Technician (Assigned Jobs Only, no financials, no tech admin, no CRM)
"""

import json
import urllib.request
import urllib.error
import pytest

BASE_URL = "http://localhost:8069"


def make_request(path, method="GET", payload=None, role=None):
    url = f"{BASE_URL}{path}"
    if role and "?" not in url:
        url += f"?role={role}"
    elif role:
        url += f"&role={role}"

    data = json.dumps(payload).encode("utf-8") if payload else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8")) if e.fp else {}
        return e.code, body


class TestRoleSecurityBoundaries:

    # =========================================================================
    # ROLE 1: DIRECTOR / ADMINISTRATOR
    # =========================================================================
    def test_director_full_financial_access(self):
        status, data = make_request("/api/financials", role="director")
        assert status == 200
        assert "invoiced_total" in data
        assert "profit_total" in data
        assert data["profit_total"] > 0

    def test_director_survey_approval_allowed(self):
        status, data = make_request("/api/survey-action", method="POST", payload={"id": 1, "action": "approve", "role": "director"})
        assert status == 200
        assert data["status"] == "success"

    def test_director_technician_dispatch_allowed(self):
        status, data = make_request("/api/dispatch", role="director")
        assert status == 200
        assert "technicians" in data
        assert len(data["technicians"]) == 15

    # =========================================================================
    # ROLE 2: SALES ADMINISTRATOR
    # =========================================================================
    def test_salesperson_financials_denied_403(self):
        status, data = make_request("/api/financials", role="salesperson")
        assert status == 403
        assert "forbidden" in data.get("error", "").lower()

    def test_salesperson_survey_approval_denied_403(self):
        status, data = make_request("/api/survey-action", method="POST", payload={"id": 1, "action": "approve", "role": "salesperson"})
        assert status == 403
        assert "permission denied" in data.get("error", "").lower()

    def test_salesperson_inventory_reservation_denied_403(self):
        status, data = make_request("/api/reserve-stock", method="POST", payload={"installation_id": 1, "item_key": "panels_550w", "qty": 2, "role": "salesperson"})
        assert status == 403
        assert "permission denied" in data.get("error", "").lower()

    def test_salesperson_assign_technician_denied_403(self):
        status, data = make_request("/api/assign-technician", method="POST", payload={"installation_id": 1, "technician_id": 2, "role": "salesperson"})
        assert status == 403
        assert "permission denied" in data.get("error", "").lower()

    def test_salesperson_installations_margins_stripped(self):
        status, data = make_request("/api/installations", role="salesperson")
        assert status == 200
        for inst in data.get("installations", []):
            assert "material_cost" not in inst
            assert "gross_profit" not in inst
            assert "gross_margin_pct" not in inst

    def test_salesperson_crm_and_quotes_allowed(self):
        status, data = make_request("/api/crm", role="salesperson")
        assert status == 200
        assert "leads" in data
        assert len(data["leads"]) > 0

    # =========================================================================
    # ROLE 3: OPERATIONS MANAGER
    # =========================================================================
    def test_operations_executive_financials_denied_403(self):
        status, data = make_request("/api/financials", role="operations")
        assert status == 403
        assert "forbidden" in data.get("error", "").lower()

    def test_operations_survey_approval_allowed(self):
        status, data = make_request("/api/survey-action", method="POST", payload={"id": 2, "action": "approve", "role": "operations"})
        assert status == 200
        assert data["status"] == "success"

    def test_operations_assign_technician_allowed(self):
        status, data = make_request("/api/assign-technician", method="POST", payload={"installation_id": 1, "technician_id": 1, "role": "operations"})
        assert status == 200
        assert data["status"] == "success"

    def test_operations_inventory_access_and_reservation_allowed(self):
        status, data = make_request("/api/inventory", role="operations")
        assert status == 200
        assert "inventory" in data

    # =========================================================================
    # ROLE 4: FIELD TECHNICIAN
    # =========================================================================
    def test_technician_financials_denied_403(self):
        status, data = make_request("/api/financials", role="technician")
        assert status == 403
        assert "forbidden" in data.get("error", "").lower()

    def test_technician_crm_leads_denied_403(self):
        status, data = make_request("/api/crm", role="technician")
        assert status == 403
        assert "forbidden" in data.get("error", "").lower()

    def test_technician_dispatch_admin_denied_403(self):
        status, data = make_request("/api/dispatch", role="technician")
        assert status == 403
        assert "forbidden" in data.get("error", "").lower()

    def test_technician_inventory_admin_denied_403(self):
        status, data = make_request("/api/inventory", role="technician")
        assert status == 403
        assert "forbidden" in data.get("error", "").lower()

    def test_technician_survey_approval_denied_403(self):
        status, data = make_request("/api/survey-action", method="POST", payload={"id": 1, "action": "approve", "role": "technician"})
        assert status == 403
        assert "permission denied" in data.get("error", "").lower()

    def test_technician_create_lead_denied_403(self):
        status, data = make_request("/api/create-lead", method="POST", payload={"name": "Hacker Lead", "phone": "+919999999999", "capacity_kw": 3.0, "role": "technician"})
        assert status == 403
        assert "permission denied" in data.get("error", "").lower()

    def test_technician_row_level_isolation_own_jobs_only(self):
        status, data = make_request("/api/installations", role="technician")
        assert status == 200
        installs = data.get("installations", [])
        # Technician 2 (Suresh Patel) must only see jobs assigned to technician_id == 2
        for inst in installs:
            assert inst.get("technician_id") == 2
            assert "material_cost" not in inst
            assert "gross_profit" not in inst

    def test_technician_search_isolation(self):
        status, data = make_request("/api/search?q=sharma", role="technician")
        assert status == 200
        # No CRM Leads or Sales Orders returned for technician
        types = [r["type"] for r in data.get("results", [])]
        assert "Sales Order" not in types
        assert "CRM Lead" not in types

    def test_technician_commission_restricted_403(self):
        status, data = make_request("/api/installation-action", method="POST", payload={"id": 1, "action": "commission", "role": "technician"})
        assert status == 403
        assert "permission denied" in data.get("error", "").lower()

    def test_technician_record_testing_allowed(self):
        status, data = make_request("/api/installation-action", method="POST", payload={
            "id": 1, "action": "record_testing", "dc_v": 385.0, "ac_v": 232.0, "earthing": 2.1, "signatory": "Rajesh Sharma", "role": "technician"
        })
        assert status == 200
        assert data["status"] == "success"

