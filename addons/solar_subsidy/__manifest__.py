# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.
{
    'name': 'SolarFlow 360 — Government Subsidy & DISCOM Documentation Tracker',
    'version': '17.0.1.0.0',
    'category': 'Solar/Subsidy',
    'summary': 'Track government solar subsidy dossiers (PM Surya Ghar / National Portal), DISCOM approvals & inspection paperwork',
    'description': """
SolarFlow 360 — Government Subsidy Tracking
============================================
Tracks state and central solar subsidies and net-metering dossiers:
- Customer & Installation mapping
- Required documents checklist (Aadhaar, Electricity Bill, Bank Passbook, Roof Photograph)
- National Portal / DISCOM Application Reference Number
- Dossier status: Draft -> Submitted -> Inspection Scheduled -> Approved -> Disbursed -> Rejected
- Segregated from customer receivables and company revenue
    """,
    'author': 'SunPower Solutions',
    'website': 'https://www.sunpowersolutions.example.com',
    'license': 'LGPL-3',
    'depends': [
        'solar_core',
        'solar_installation',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/solar_subsidy_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

