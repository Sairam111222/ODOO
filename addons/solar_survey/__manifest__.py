# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.
{
    'name': 'SolarFlow 360 — Site Surveys',
    'version': '17.0.1.0.0',
    'category': 'Solar/Survey',
    'summary': 'Site feasibility surveys and engineering evaluations for solar installations',
    'description': """
SolarFlow 360 — Site Survey Module
===================================
Manages the site survey process for rooftop solar installations:
- Physical roof inspection, azimuth/tilt, condition, and shading analysis
- Electrical meter, sanction load, and DISCOM consumer verification
- Capacity estimation and generation forecasting
- Direct workflow from scheduling to engineering approval
- Seamless handover to Quotation and Installation
    """,
    'author': 'SunPower Solutions',
    'website': 'https://www.sunpowersolutions.example.com',
    'license': 'LGPL-3',
    'depends': [
        'solar_core',
        'solar_package',
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/solar_survey_record_rules.xml',
        'views/solar_survey_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
