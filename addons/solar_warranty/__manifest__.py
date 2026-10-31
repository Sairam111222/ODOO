# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.
{
    'name': 'SolarFlow 360 — Warranties & AMC',
    'version': '17.0.1.0.0',
    'category': 'Solar/Warranty',
    'summary': 'Solar warranty tracking, component guarantee terms, and claims lifecycle',
    'description': """
SolarFlow 360 — Solar Warranty Management
=========================================
Tracks component and system warranties:
- 25-Year PV Panel Performance Warranty
- 5-Year Inverter Guarantee
- 1-5 Year System Workmanship Warranty
- Automated expiry tracking and notifications
- Seamless warranty claim linking to service tickets
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
        'security/solar_warranty_record_rules.xml',
        'views/solar_warranty_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
