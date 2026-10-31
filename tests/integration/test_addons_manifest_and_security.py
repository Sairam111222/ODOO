"""
SolarFlow 360 - Architectural & Addon Validation Test Suite
Validates manifest configurations, Python module loading, XML view integrity,
and RBAC security permissions across all 10 modules.
"""

import ast
import csv
import glob
import os
import unittest
import xml.etree.ElementTree as ET

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ADDONS_DIR = os.path.join(BASE_DIR, "addons")


class TestSolarFlowAddonsIntegrity(unittest.TestCase):

    def setUp(self):
        self.addons = [
            "solar_core",
            "solar_crm",
            "solar_survey",
            "solar_package",
            "solar_installation",
            "solar_warranty",
            "solar_service",
            "solar_subsidy",
            "solar_portal",
            "solar_dashboard",
        ]

    def test_addons_manifest_existence_and_syntax(self):
        """Verify each addon has a syntactically valid __manifest__.py dictionary."""
        for addon in self.addons:
            manifest_path = os.path.join(ADDONS_DIR, addon, "__manifest__.py")
            self.assertTrue(
                os.path.exists(manifest_path),
                f"Missing manifest in {addon}",
            )
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()
            manifest_dict = ast.literal_eval(content)
            self.assertIsInstance(manifest_dict, dict)
            self.assertIn("name", manifest_dict)
            self.assertIn("version", manifest_dict)
            self.assertIn("depends", manifest_dict)
            self.assertTrue(manifest_dict.get("installable", False))

    def test_addons_init_existence(self):
        """Verify __init__.py exists in each addon root and subdirectories."""
        for addon in self.addons:
            init_path = os.path.join(ADDONS_DIR, addon, "__init__.py")
            self.assertTrue(
                os.path.exists(init_path),
                f"Missing __init__.py in {addon}",
            )
            models_dir = os.path.join(ADDONS_DIR, addon, "models")
            if os.path.exists(models_dir):
                models_init = os.path.join(models_dir, "__init__.py")
                self.assertTrue(
                    os.path.exists(models_init),
                    f"Missing models/__init__.py in {addon}",
                )

    def test_python_syntax_across_all_modules(self):
        """Ensure all python files parse without syntax errors."""
        py_files = glob.glob(os.path.join(ADDONS_DIR, "**", "*.py"), recursive=True)
        self.assertGreater(len(py_files), 15)
        for py_path in py_files:
            with open(py_path, "r", encoding="utf-8") as f:
                code = f.read()
            try:
                ast.parse(code, filename=py_path)
            except SyntaxError as e:
                self.fail(f"Syntax error in {py_path}: {e}")

    def test_xml_views_validity(self):
        """Ensure all Odoo XML data and view files are valid well-formed XML."""
        xml_files = glob.glob(os.path.join(ADDONS_DIR, "**", "*.xml"), recursive=True)
        self.assertGreater(len(xml_files), 8)
        for xml_path in xml_files:
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                self.assertEqual(root.tag, "odoo")
            except Exception as e:
                self.fail(f"XML parse error in {xml_path}: {e}")

    def test_ir_model_access_csv_validity(self):
        """Ensure ir.model.access.csv files conform to standard Odoo security schema."""
        csv_files = glob.glob(os.path.join(ADDONS_DIR, "**", "ir.model.access.csv"), recursive=True)
        self.assertGreaterEqual(len(csv_files), 7)
        expected_headers = [
            "id",
            "name",
            "model_id:id",
            "group_id:id",
            "perm_read",
            "perm_write",
            "perm_create",
            "perm_unlink",
        ]
        for csv_path in csv_files:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                self.assertEqual(header, expected_headers, f"Malformed headers in {csv_path}")
                for row in reader:
                    if not row:
                        continue
                    self.assertEqual(
                        len(row),
                        8,
                        f"Row does not have 8 columns in {csv_path}: {row}",
                    )
                    for perm in row[4:8]:
                        self.assertIn(perm, ["0", "1"])


if __name__ == "__main__":
    unittest.main()
