# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.
{
    'name': 'SolarFlow 360 — Installation Operations',
    'version': '17.0.1.0.0',
    'category': 'Solar/Installation',
    'summary': 'Solar installation lifecycle, technician assignment, equipment tracking, testing & commissioning',
    'description': """
SolarFlow 360 — Solar Installation Management
==============================================
Manages end-to-end execution of solar projects:
- Linking accepted quotation and site survey
- Technician crew dispatch (pool of 15 technicians)
- Equipment allocation and serial number tracking
- Electrical safety testing (DC/AC voltage, earthing, net-metering)
- Handover and automated warranty activation upon commissioning
    """,
    'author': 'SunPower Solutions',
    'website': 'https://www.sunpowersolutions.example.com',
    'license': 'LGPL-3',
    'depends': [
        'solar_core',
        'solar_survey',
        'solar_package',
        'sale_management',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/solar_installation_record_rules.xml',
        'views/solar_installation_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
