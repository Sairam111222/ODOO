# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.
{
    'name': 'SolarFlow 360 — Service, Repairs & Tickets',
    'version': '17.0.1.0.0',
    'category': 'Solar/Service',
    'summary': 'Solar customer service ticketing, breakdown repairs, and maintenance technician dispatch',
    'description': """
SolarFlow 360 — Solar Service & Support
========================================
Addresses post-installation customer support:
- Service and breakdown ticket logging
- Linking customer, system installation, and active warranty
- Field technician assignment and repair logging
- Resolution tracking and customer satisfaction verification
    """,
    'author': 'SunPower Solutions',
    'website': 'https://www.sunpowersolutions.example.com',
    'license': 'LGPL-3',
    'depends': [
        'solar_core',
        'solar_installation',
        'solar_warranty',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/solar_service_record_rules.xml',
        'views/solar_service_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
