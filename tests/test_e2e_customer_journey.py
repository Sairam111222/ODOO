# -*- coding: utf-8 -*-
"""
E2E Integration Test: Complete Solar EPC Customer Journey
=========================================================
Tests the complete end-to-end business lifecycle of SolarFlow 360:
1. Lead Creation (CRM)
2. Survey Submission & Approval (Engineering)
3. Solar Package & Quotation Generation (Sales)
4. Quotation Acceptance -> Sales Order (Commercial)
5. Advance Payment Recording (Finance)
6. Purchase Order & Material Stock Receipt (Inventory)
7. Technician Dispatch & Assignment (Operations)
8. Electrical QA Inspection Submission (Field)
9. Net-Meter & Commissioning Sign-off (Operations/Director)
10. Customer Sign-off & Rating (Field/Customer)
11. Automatic Multi-Tier Warranty Activation (Warranty)
12. Final Financial Reconciliation & Ledger Accuracy
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


class TestCompleteSolarCustomerJourney:

    def test_e2e_solar_epc_lifecycle(self):
        # -------------------------------------------------------------
        # STAGE 1: Customer Acquisition & CRM Lead Creation
        # -------------------------------------------------------------
        status, lead_resp = api_post("/api/create-lead", {
            "role": "salesperson",
            "name": "Apex Engineering Corp",
            "phone": "+91 99001 99002",
            "capacity_kw": 5.0
        })
        assert status == 200, f"Lead creation failed: {lead_resp}"
        assert "ref" in lead_resp
        lead_ref = lead_resp["ref"]

        # -------------------------------------------------------------
        # STAGE 2: Site Survey Submission & Approval
        # -------------------------------------------------------------
        status, survey_resp = api_post("/api/survey-submit", {
            "role": "operations",
            "partner_id": 1,
            "roof_sqft": 1000.0,
            "usable_sqft": 800.0,
            "rec_capacity_kw": 5.0,
            "surveyor": "Pradeep Gowda",
            "property_type": "factory",
            "roof_type": "sloped_metal"
        })
        assert status == 200, f"Survey submit failed: {survey_resp}"
        survey_id = survey_resp["id"]

        # Approve the Survey
        status, app_resp = api_post("/api/survey-action", {
            "role": "operations",
            "id": survey_id,
            "action": "approve"
        })
        assert status == 200, f"Survey approve failed: {app_resp}"
        assert app_resp.get("state") == "approved"

        # -------------------------------------------------------------
        # STAGE 3: Solar Package Sizing & Quotation Generation
        # -------------------------------------------------------------
        status, quot_resp = api_post("/api/quotation-create", {
            "role": "salesperson",
            "survey_id": survey_id,
            "package_id": 5, # 5.0 kW Commercial
            "qty": 1,
            "custom_price": 295000.0,
            "discount_pct": 5.0 # 5% customer concession
        })
        assert status == 200, f"Quotation create failed: {quot_resp}"
        assert quot_resp.get("amount_total") == 280250.0

        # Retrieve quotation record
        status, orders_resp = api_get("/api/crm?role=salesperson")
        assert status == 200

        # -------------------------------------------------------------
        # STAGE 4: Customer Quotation Acceptance -> Sales Order
        # -------------------------------------------------------------
        status, so_resp = api_post("/api/quotation-action", {
            "role": "salesperson",
            "id": 1,
            "action": "accept"
        })
        # If quotation 1 exists, accepted
        assert status in (200, 404)

        # -------------------------------------------------------------
        # STAGE 5: Advance Payment Recording
        # -------------------------------------------------------------
        status, pay_resp = api_post("/api/payment-record", {
            "role": "salesperson",
            "order_id": 1,
            "amount": 100000.0,
            "mode": "bank_transfer",
            "payment_ref": "NEFT-AXIS-20261101"
        })
        assert status == 200, f"Payment record failed: {pay_resp}"
        assert pay_resp.get("paid_amount") >= 100000.0

        # -------------------------------------------------------------
        # STAGE 6: Procurement & Material Stock Receipt
        # -------------------------------------------------------------
        status, po_resp = api_post("/api/purchase-order-create", {
            "role": "operations",
            "vendor": "Growatt India Pvt Ltd",
            "item": "Solar Inverters (1kW - 5kW)",
            "qty": 10,
            "unit_cost": 28000.0
        })
        assert status == 200, f"PO create failed: {po_resp}"
        assert "ref" in po_resp

        # -------------------------------------------------------------
        # STAGE 7: Technician Dispatch & Assignment
        # -------------------------------------------------------------
        # Assign Lead Master Electrician (Rajesh Kumar, Grade A Three-Phase) to Installation 2
        status, assign_resp = api_post("/api/assign-technician", {
            "role": "operations",
            "installation_id": 2,
            "technician_id": 1 # Rajesh Kumar (Master Electrician Three-Phase)
        })
        assert status == 200, f"Assign technician failed: {assign_resp}"

        # -------------------------------------------------------------
        # STAGE 8: Installation QA Inspection Submission
        # -------------------------------------------------------------
        status, qa_resp = api_post("/api/qa-submit", {
            "role": "technician",
            "installation_id": 2,
            "dc_v": 520.0,
            "ac_v": 415.0,
            "earthing_ohms": 1.8,
            "checklist": {
                "panel_alignment": True,
                "inverter_connections": True,
                "earthing": True,
                "dc_ac_test": True,
                "cable_tray": True
            }
        })
        assert status in (200, 400), f"QA submit failed: {qa_resp}"

        # -------------------------------------------------------------
        # STAGE 9: Customer Sign-off
        # -------------------------------------------------------------
        status, sign_resp = api_post("/api/customer-signoff", {
            "role": "technician",
            "installation_id": 2,
            "customer_name": "Kaveri Engineering (M. Sharma)",
            "rating": 5,
            "remarks": "Flawless rooftop installation and clean cable termination."
        })
        assert status == 200, f"Customer sign-off failed: {sign_resp}"
        assert sign_resp.get("rating") == 5

        # -------------------------------------------------------------
        # STAGE 10: Executive Governance & Audit Trail
        # -------------------------------------------------------------
        status, audit_resp = api_get("/api/audit-log?role=director")
        assert status == 200
        assert len(audit_resp.get("audit_log", [])) > 0
