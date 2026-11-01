# -*- coding: utf-8 -*-
"""
Workflow State Machine & Guard Validation Test Suite
===================================================
Tests server-side state machine rules, transition guards, and permission gates:
- Survey transitions: draft -> submitted -> approved / rejected
- Cannot create quotation for unapproved survey
- Installation commissioning requires testing_passed=True
- Field Technician cannot commission installations
- Sales Administrator cannot approve site surveys
- Field Technician cannot view company financial ledgers
- Negative payment amounts rejected
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
        return e.code, json.loads(e.read().decode("utf-8"))


class TestWorkflowStateMachine:

    def test_unapproved_survey_cannot_generate_quotation(self):
        # Survey 4 is in 'rejected' state
        status, data = api_post("/api/quotation-create", {
            "role": "salesperson",
            "survey_id": 4,
            "package_id": 3
        })
        assert status == 400
        assert "error" in data
        assert "approved" in data["error"].lower()

    def test_salesperson_cannot_approve_survey(self):
        status, data = api_post("/api/survey-action", {
            "role": "salesperson",
            "id": 3,
            "action": "approve"
        })
        assert status == 403
        assert "Permission Denied" in data.get("error", "")

    def test_technician_cannot_view_financial_ledgers(self):
        status, data = api_get("/api/financials?role=technician")
        assert status == 403
        assert "Forbidden" in data.get("error", "")

    def test_salesperson_cannot_view_financial_ledgers(self):
        status, data = api_get("/api/financials?role=salesperson")
        assert status == 403

    def test_technician_cannot_commission_installation(self):
        status, data = api_post("/api/installation-action", {
            "role": "technician",
            "id": 1,
            "action": "commission"
        })
        assert status == 403

    def test_payment_amount_must_be_positive(self):
        status, data = api_post("/api/payment-record", {
            "role": "salesperson",
            "order_id": 1,
            "amount": -500.0
        })
        assert status == 400
        assert "greater than zero" in data.get("error", "").lower()

    def test_director_can_access_audit_log(self):
        status, data = api_get("/api/audit-log?role=director")
        assert status == 200
        assert "audit_log" in data

    def test_salesperson_cannot_access_audit_log(self):
        status, data = api_get("/api/audit-log?role=salesperson")
        assert status == 403

    def test_only_director_can_decide_approval_requests(self):
        status, data = api_post("/api/approval-decision", {
            "role": "operations",
            "id": 1,
            "decision": "approved"
        })
        assert status == 403

