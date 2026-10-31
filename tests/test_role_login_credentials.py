# -*- coding: utf-8 -*-
"""
Automated Test Suite for SolarFlow 360 Role Authentication & Distinct Credentials.
Validates:
- 4 distinct role accounts (Director, Sales Administrator, Operations Manager, Field Technician).
- Correct password verification per role.
- Bad password rejection (401 Unauthorized).
- Unknown user rejection.
- Role token payload generation.
"""

import json
import urllib.error
import urllib.request
import pytest

BASE_URL = "http://localhost:8069"

ROLE_CREDENTIAL_MATRIX = [
    {
        "role": "director",
        "email": "director@sunpower.com",
        "password": "Director@360",
        "name": "Director (Executive)"
    },
    {
        "role": "salesperson",
        "email": "sales@sunpower.com",
        "password": "Sales@360",
        "name": "Sales Administrator"
    },
    {
        "role": "operations",
        "email": "ops@sunpower.com",
        "password": "Ops@360",
        "name": "Operations Manager"
    },
    {
        "role": "technician",
        "email": "tech@sunpower.com",
        "password": "Tech@360",
        "name": "Field Technician"
    }
]

def make_login_request(email, password):
    req = urllib.request.Request(
        f"{BASE_URL}/api/login",
        data=json.dumps({"email": email, "password": password}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


class TestRoleLoginAuthentication:

    @pytest.mark.parametrize("cred", ROLE_CREDENTIAL_MATRIX)
    def test_distinct_role_credentials_authenticate_successfully(self, cred):
        status, data = make_login_request(cred["email"], cred["password"])
        assert status == 200
        assert data["status"] == "success"
        assert data["role"] == cred["role"]
        assert cred["name"] in data["name"]
        assert "sf360_session_" in data["token"]

    @pytest.mark.parametrize("cred", ROLE_CREDENTIAL_MATRIX)
    def test_incorrect_password_rejected_with_401(self, cred):
        status, data = make_login_request(cred["email"], "InvalidPassword!999")
        assert status == 401
        assert "error" in data
        assert "invalid email or password" in data["error"].lower()

    def test_unregistered_email_rejected_with_401(self):
        status, data = make_login_request("intruder@unknown.com", "Password@123")
        assert status == 401
        assert "error" in data
