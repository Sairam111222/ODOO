"""
SolarFlow 360 - Cross-Module Dependency & ORM Integrity Test Suite
Validates deep architectural rules, circular dependency prevention,
manifest declaration order, and runtime cross-module model safety.
"""

import ast
import csv
import glob
import os
import unittest
import xml.etree.ElementTree as ET

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ADDONS_DIR = os.path.join(BASE_DIR, "addons")


class TestSolarFlowDeepIntegrity(unittest.TestCase):

    def test_solar_survey_relativedelta_import(self):
        """Ensure solar_site_survey imports and uses relativedelta properly without crashing."""
        survey_py = os.path.join(ADDONS_DIR, "solar_survey", "models", "solar_site_survey.py")
        with open(survey_py, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("from dateutil.relativedelta import relativedelta", code)
        self.assertNotIn("fields.relativedelta", code)

    def test_solar_crm_manifest_depends_on_solar_survey(self):
        """Ensure solar_crm declares solar_survey in its manifest dependencies."""
        crm_manifest = os.path.join(ADDONS_DIR, "solar_crm", "__manifest__.py")
        with open(crm_manifest, "r", encoding="utf-8") as f:
            manifest = ast.literal_eval(f.read())
        self.assertIn("solar_survey", manifest.get("depends", []))

    def test_solar_survey_manifest_depends_on_solar_package(self):
        """Ensure solar_survey declares solar_package and sale_management in manifest."""
        survey_manifest = os.path.join(ADDONS_DIR, "solar_survey", "__manifest__.py")
        with open(survey_manifest, "r", encoding="utf-8") as f:
            manifest = ast.literal_eval(f.read())
        self.assertIn("solar_package", manifest.get("depends", []))
        self.assertIn("sale_management", manifest.get("depends", []))

    def test_solar_core_record_rules_self_containment(self):
        """Ensure solar_core record rules only reference models defined within solar_core."""
        core_rules_xml = os.path.join(ADDONS_DIR, "solar_core", "security", "solar_record_rules.xml")
        tree = ET.parse(core_rules_xml)
        root = tree.getroot()
        for record in root.findall(".//record"):
            model_field = record.find(".//field[@name='model_id']")
            if model_field is not None:
                model_ref = model_field.attrib.get("ref", "")
                # solar_core must not reference downstream models
                self.assertNotIn("model_solar_installation", model_ref)
                self.assertNotIn("model_solar_site_survey", model_ref)
                self.assertNotIn("model_solar_service_ticket", model_ref)
                self.assertNotIn("model_solar_warranty", model_ref)

    def test_solar_core_access_rights_covers_system_type(self):
        """Ensure solar_core/security/ir.model.access.csv grants access to solar.system.type."""
        core_acl = os.path.join(ADDONS_DIR, "solar_core", "security", "ir.model.access.csv")
        with open(core_acl, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            models_in_acl = [row["model_id:id"] for row in reader]
        self.assertIn("model_solar_system_type", models_in_acl)

    def test_solar_core_root_menu_permissions(self):
        """Ensure root menu is accessible to Support Agents, Accountants, and Technicians."""
        menu_xml = os.path.join(ADDONS_DIR, "solar_core", "views", "solar_menus.xml")
        tree = ET.parse(menu_xml)
        root = tree.getroot()
        root_menu = root.find(".//menuitem[@id='menu_solar_root']")
        self.assertIsNotNone(root_menu)
        groups = root_menu.attrib.get("groups", "")
        self.assertIn("group_solar_technician", groups)
        self.assertIn("group_solar_support_agent", groups)
        self.assertIn("group_solar_accountant", groups)

    def test_env_file_exists_and_matches_db_creds(self):
        """Verify .env exists and sets default matching postgres password."""
        env_path = os.path.join(BASE_DIR, ".env")
        self.assertTrue(os.path.exists(env_path))
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("POSTGRES_PASSWORD=", content)
        self.assertIn("ODOO_HTTP_PORT=8069", content)


if __name__ == "__main__":
    unittest.main()

