# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.
{
    'name': 'SolarFlow 360 — Customer Self-Service Portal',
    'version': '17.0.1.0.0',
    'category': 'Solar/Portal',
    'summary': 'Customer web portal to track installations, view warranties, submit tickets & enquiries',
    'description': """
SolarFlow 360 — Customer Self-Service Portal
============================================
Extends the Odoo customer portal with secure solar views:
- Track live solar installation progress
- View warranty certificates and guarantee validity
- Submit breakdown / maintenance tickets
- View permitted solar quotations
- Strictly isolated to the logged-in customer's partner ID
    """,
    'author': 'SunPower Solutions',
    'website': 'https://www.sunpowersolutions.example.com',
    'license': 'LGPL-3',
    'depends': [
        'portal',
        'solar_core',
        'solar_installation',
        'solar_warranty',
        'solar_service',
    ],
    'data': [
        'views/portal_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

