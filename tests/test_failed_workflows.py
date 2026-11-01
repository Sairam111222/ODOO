# -*- coding: utf-8 -*-
"""
Negative & Failure Scenario Test Suite: 15 Critical Edge Cases
==============================================================
Validates that invalid inputs, permission violations, and corrupt workflow
transitions are safely caught, rejected with appropriate HTTP status codes,
and leave database records untainted.
"""

import json
import urllib.request
import urllib.error
import pytest

BASE = "http://127.0.0.1:8069"

def api_post(path, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def api_get(path):
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=5) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"error": "Non-JSON response"}


class TestFailureScenarios:

    def test_case_01_technician_cannot_create_leads(self):
        status, data = api_post("/api/create-lead", {
            "role": "technician",
            "name": "Intruder Corp",
            "phone": "+91 91234 56789"
        })
        assert status == 403
        assert "Permission Denied" in data.get("error", "")

    def test_case_02_technician_cannot_configure_package_pricing(self):
        status, data = api_post("/api/package-configure", {
            "role": "technician",
            "capacity_kw": 3.0
        })
        assert status == 403

    def test_case_03_junior_tech_assigned_to_5kw_three_phase_rejected(self):
        # Vikram Singh is junior (id=3), lacking 'Three-Phase Certified'
        status, data = api_post("/api/assign-technician", {
            "role": "operations",
            "installation_id": 2, # 5.0 kW three-phase installation
            "technician_id": 3    # Vikram Singh (Junior)
        })
        assert status == 400
        assert "Three-Phase Certified" in data.get("error", "")

    def test_case_04_salesperson_cannot_approve_subsidy(self):
        status, data = api_post("/api/subsidy-action", {
            "role": "salesperson",
            "id": 1,
            "action": "approve"
        })
        assert status == 403

    def test_case_05_technician_cannot_manage_subsidy(self):
        status, data = api_post("/api/subsidy-action", {
            "role": "technician",
            "id": 1,
            "action": "submit"
        })
        assert status == 403

    def test_case_06_nonexistent_order_payment_returns_404(self):
        status, data = api_post("/api/payment-record", {
            "role": "salesperson",
            "order_id": 999999,
            "amount": 5000.0
        })
        assert status == 404

    def test_case_07_customer_signoff_missing_customer_name_returns_400(self):
        status, data = api_post("/api/customer-signoff", {
            "role": "technician",
            "installation_id": 1,
            "customer_name": "   ", # empty
            "rating": 5
        })
        assert status == 400
        assert "customer_name is required" in data.get("error", "")

    def test_case_08_customer_signoff_nonexistent_installation_returns_404(self):
        status, data = api_post("/api/customer-signoff", {
            "role": "technician",
            "installation_id": 999999,
            "customer_name": "Valid Name",
            "rating": 5
        })
        assert status == 404

    def test_case_09_invalid_approval_decision_rejected(self):
        status, data = api_post("/api/approval-decision", {
            "role": "director",
            "id": 1,
            "decision": "invalid_choice"
        })
        assert status == 400

    def test_case_10_po_negative_quantity_rejected(self):
        status, data = api_post("/api/purchase-order-create", {
            "role": "operations",
            "vendor": "Test Vendor",
            "item": "Test Panels",
            "qty": -5,
            "unit_cost": 1000.0
        })
        assert status == 400

    def test_case_11_po_zero_unit_cost_rejected(self):
        status, data = api_post("/api/purchase-order-create", {
            "role": "operations",
            "vendor": "Test Vendor",
            "item": "Test Panels",
            "qty": 5,
            "unit_cost": 0.0
        })
        assert status == 400

    def test_case_12_nonexistent_survey_quotation_rejected(self):
        status, data = api_post("/api/quotation-create", {
            "role": "salesperson",
            "survey_id": 999999,
            "package_id": 3
        })
        assert status == 404

    def test_case_13_nonexistent_approval_request_returns_404(self):
        status, data = api_post("/api/approval-decision", {
            "role": "director",
            "id": 999999,
            "decision": "approved"
        })
        assert status == 404

    def test_case_14_nonexistent_po_stock_receive_returns_404(self):
        status, data = api_post("/api/stock-receive", {
            "role": "operations",
            "po_id": 999999,
            "qty_received": 10
        })
        assert status == 404

    def test_case_15_nonexistent_route_returns_404(self):
        status, data = api_get("/api/unknown-nonexistent-endpoint")
        assert status == 404
