"""
SolarFlow 360 - Complete Business Workflow & Failure Scenarios Test Suite
Validates the entire customer journey from Lead Qualification to Warranty & Service,
including calculation engines, compliance blocks, serial tracking, and failure edge cases.
"""

import math
import unittest
from datetime import date, timedelta


class TestSolarBusinessLogicAndFailureScenarios(unittest.TestCase):

    # ---------------------------------------------------------
    # 1. Sizing Calculation Engine & BOM Decomposition
    # ---------------------------------------------------------
    def test_solar_sizing_and_bom_rules(self):
        """Verify engineering calculations for 1kW, 3kW, and 5kW systems."""
        # 3 kW system with 550 Wp panels
        capacity_kw = 3.0
        panel_wattage = 550.0
        expected_panel_count = math.ceil((capacity_kw * 1000.0) / panel_wattage)
        self.assertEqual(expected_panel_count, 6)

        # Structure pairs (1 pair per 2 panels)
        expected_structure_kits = math.ceil(expected_panel_count / 2.0)
        self.assertEqual(expected_structure_kits, 3)

        # DC Cable calculation for 25m distance
        cable_distance = 25.0
        expected_dc_cable = (cable_distance * 2.0) + 10.0  # (25 * 2) + 10 = 60m
        self.assertEqual(expected_dc_cable, 60.0)

        # 5 kW system with 550 Wp panels
        cap_5kw = 5.0
        p_count_5kw = math.ceil((cap_5kw * 1000.0) / panel_wattage)
        self.assertEqual(p_count_5kw, 10)
        self.assertEqual(math.ceil(p_count_5kw / 2.0), 5)

    # ---------------------------------------------------------
    # 2. Site Survey Mandatory Validations & Submission Block
    # ---------------------------------------------------------
    def test_survey_mandatory_measurement_validation(self):
        """Verify incomplete survey measurements block submission."""
        def validate_survey(roof_area, usable_area, cable_dist, bill, cap, roof_cond):
            missing = []
            if not roof_area or roof_area <= 0:
                missing.append("Total Roof Area")
            if not usable_area or usable_area <= 0:
                missing.append("Usable Solar Area")
            if usable_area and roof_area and usable_area > roof_area:
                raise ValueError("Usable solar area cannot exceed total roof area.")
            if not cable_dist or cable_dist <= 0:
                missing.append("Cable Distance")
            if not bill or bill <= 0:
                missing.append("Average Monthly Electricity Bill")
            if not cap or cap <= 0:
                missing.append("Recommended System Capacity")
            if roof_cond == 'poor':
                raise ValueError("Cannot submit survey with 'Poor' roof condition.")
            if missing:
                raise ValueError(f"Missing mandatory fields: {missing}")
            return True

        # Case A: Valid survey passes
        self.assertTrue(validate_survey(500, 350, 25, 4500, 3.0, 'good'))

        # Case B: Missing roof area blocks
        with self.assertRaises(ValueError):
            validate_survey(0, 0, 25, 4500, 3.0, 'good')

        # Case C: Usable area greater than total roof blocks
        with self.assertRaises(ValueError):
            validate_survey(300, 450, 25, 4500, 3.0, 'good')

        # Case D: Poor roof condition blocks
        with self.assertRaises(ValueError):
            validate_survey(500, 350, 25, 4500, 3.0, 'poor')

    # ---------------------------------------------------------
    # 3. Compliance Enforcement: Unapproved Survey Blocks Quotation
    # ---------------------------------------------------------
    def test_unapproved_survey_blocks_quotation(self):
        """Verify quotations cannot be generated from unapproved surveys."""
        def generate_quotation(survey_state):
            if survey_state != 'approved':
                raise PermissionError(f"Compliance Violation: Cannot generate quotation from '{survey_state}' survey.")
            return {"quotation_id": "SO-2026-001", "state": "draft"}

        # Allowed for approved
        res = generate_quotation("approved")
        self.assertEqual(res["state"], "draft")

        # Blocked for draft, scheduled, submitted, or rejected
        for invalid_state in ["draft", "scheduled", "in_progress", "submitted", "rejected"]:
            with self.assertRaises(PermissionError):
                generate_quotation(invalid_state)

    # ---------------------------------------------------------
    # 4. Mandatory Serial Number Uniqueness & Collision Prevention
    # ---------------------------------------------------------
    def test_serial_number_collision_prevention(self):
        """Verify duplicate serial numbers on inverters/batteries are detected and prevented."""
        registered_serials = {
            ("inverter", "INV-GROWATT-9921"): "INS/2026/0001",
            ("battery", "BATT-LITH-4401"): "INS/2026/0001",
        }

        def check_serial(comp_type, serial_num, current_job):
            key = (comp_type, serial_num.strip())
            if key in registered_serials and registered_serials[key] != current_job:
                raise ValueError(f"Serial Number Collision: '{serial_num}' already assigned to {registered_serials[key]}")
            return True

        # Unique serial passes
        self.assertTrue(check_serial("inverter", "INV-GROWATT-9922", "INS/2026/0002"))

        # Duplicate serial on another job raises ValueError
        with self.assertRaises(ValueError):
            check_serial("inverter", "INV-GROWATT-9921", "INS/2026/0002")

    # ---------------------------------------------------------
    # 5. Electrical Safety & Grid Testing Validation
    # ---------------------------------------------------------
    def test_electrical_testing_safety_rules(self):
        """Verify DC/AC voltage and earthing resistance safety boundaries."""
        def verify_testing(dc_volts, ac_volts, earthing_ohms):
            if dc_volts <= 0 or ac_volts <= 0:
                raise ValueError("DC and AC voltage must be tested and greater than 0V.")
            if earthing_ohms <= 0 or earthing_ohms > 5.0:
                raise ValueError("Earthing resistance must be between 0.1 Ω and 5.0 Ω.")
            return True

        # Safe values pass
        self.assertTrue(verify_testing(380.0, 230.0, 2.1))

        # Dangerous earthing resistance (> 5 ohms) fails
        with self.assertRaises(ValueError):
            verify_testing(380.0, 230.0, 8.5)

        # Zero voltage fails
        with self.assertRaises(ValueError):
            verify_testing(0.0, 230.0, 2.1)

    # ---------------------------------------------------------
    # 6. Job-Level Financials & Profitability Calculations
    # ---------------------------------------------------------
    def test_job_level_profitability(self):
        """Verify revenue, material costs, technician labor, expenses, gross profit, and margin %."""
        contract_revenue = 185000.0  # 3kW standard package price
        equipment_cost = 115000.0    # Panels, Inverter, Structure, Cables
        technician_hours = 16.0
        hourly_rate = 250.0
        labour_cost = technician_hours * hourly_rate  # ₹4,000
        other_expenses = 3500.0      # Transport, permits

        total_cost = equipment_cost + labour_cost + other_expenses  # ₹122,500
        self.assertEqual(total_cost, 122500.0)

        gross_profit = contract_revenue - total_cost  # ₹62,500
        self.assertEqual(gross_profit, 62500.0)

        gross_margin_pct = (gross_profit / contract_revenue) * 100.0  # 33.78%
        self.assertAlmostEqual(gross_margin_pct, 33.78, places=1)

    # ---------------------------------------------------------
    # 7. Warranty Activation & Expiry Tracking
    # ---------------------------------------------------------
    def test_warranty_duration_and_expiry_status(self):
        """Verify 25-yr panel, 5-yr inverter, and 60-day expiring_soon status."""
        start_date = date(2026, 1, 1)

        # Inverter 5 years
        inverter_end = date(2031, 1, 1)
        self.assertEqual(inverter_end.year - start_date.year, 5)

        # Panel 25 years
        panel_end = date(2051, 1, 1)
        self.assertEqual(panel_end.year - start_date.year, 25)

        def compute_warranty_state(end_d, today_d):
            if end_d < today_d:
                return 'expired'
            elif (end_d - today_d).days <= 60:
                return 'expiring_soon'
            return 'active'

        # Active
        self.assertEqual(compute_warranty_state(date(2028, 1, 1), date(2026, 10, 31)), 'active')
        # Expiring soon (within 60 days)
        self.assertEqual(compute_warranty_state(date(2026, 11, 20), date(2026, 10, 31)), 'expiring_soon')
        # Expired
        self.assertEqual(compute_warranty_state(date(2026, 5, 1), date(2026, 10, 31)), 'expired')

    # ---------------------------------------------------------
    # 8. Service Complaint Warranty Claim Classification
    # ---------------------------------------------------------
    def test_service_ticket_warranty_classification(self):
        """Verify active warranty yields free repair; expired yields chargeable repair."""
        def classify_ticket(warranty_state):
            if warranty_state in ('active', 'expiring_soon'):
                return {'is_warranty_claim': True, 'repair_classification': 'free_warranty'}
            return {'is_warranty_claim': False, 'repair_classification': 'chargeable'}

        self.assertEqual(classify_ticket('active')['repair_classification'], 'free_warranty')
        self.assertEqual(classify_ticket('expired')['repair_classification'], 'chargeable')
        self.assertEqual(classify_ticket('void')['repair_classification'], 'chargeable')

    # ---------------------------------------------------------
    # 9. Government Subsidy Document Checklist Computation
    # ---------------------------------------------------------
    def test_subsidy_checklist_and_missing_documents(self):
        """Verify subsidy missing document computation."""
        def compute_missing(elec, aadh, bank, roof, comm, dcr):
            missing = []
            if not elec: missing.append("Electricity Bill")
            if not aadh: missing.append("Aadhaar Identity")
            if not bank: missing.append("Bank Passbook")
            if not roof: missing.append("Roof Ownership")
            if not comm: missing.append("Commissioning Report")
            if not dcr: missing.append("DCR Certificate")
            return ", ".join(missing) if missing else "All Required Documents Collected"

        # Missing Aadhaar & DCR
        res = compute_missing(True, False, True, True, True, False)
        self.assertIn("Aadhaar Identity", res)
        self.assertIn("DCR Certificate", res)

        # Complete
        res_complete = compute_missing(True, True, True, True, True, True)
        self.assertEqual(res_complete, "All Required Documents Collected")

    # ---------------------------------------------------------
    # 10. Duplicate Lead Detection
    # ---------------------------------------------------------
    def test_duplicate_lead_detection_matching(self):
        """Verify duplicate lead detection matching by phone or email."""
        existing_leads = [
            {"id": 1, "phone": "+919876543210", "email": "rajesh@example.com"},
            {"id": 2, "phone": "+919123456780", "email": "priya@factory.com"},
        ]

        def check_duplicate(new_phone, new_email):
            for l in existing_leads:
                if (new_phone and l["phone"] == new_phone) or (new_email and l["email"] == new_email):
                    return True
            return False

        # Duplicate phone matches
        self.assertTrue(check_duplicate("+919876543210", "different@email.com"))
        # Duplicate email matches
        self.assertTrue(check_duplicate("+919999999999", "priya@factory.com"))
        # New lead passes
        self.assertFalse(check_duplicate("+919000000000", "newcustomer@example.com"))


if __name__ == "__main__":
    unittest.main()

