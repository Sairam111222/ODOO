# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.
{
    'name': 'SolarFlow 360 — Executive Operations & Profitability Dashboard',
    'version': '17.0.1.0.0',
    'category': 'Solar/Dashboard',
    'summary': 'Executive view of 40 installations/month target, capacity (kW), technician workload, and gross margin',
    'description': """
SolarFlow 360 — Solar Analytics & Dashboard
============================================
Real-time KPI visualization for SunPower Solutions management:
- Monthly installation run-rate vs 40 installations/month target
- Total generation capacity commissioned (kW)
- Active technician workload across 15 field crew members
- Lead conversion from WhatsApp / phone to completed installation
- Cross-Model Global Enterprise Search
    """,
    'author': 'SunPower Solutions',
    'website': 'https://www.sunpowersolutions.example.com',
    'license': 'LGPL-3',
    'depends': [
        'solar_core',
        'solar_installation',
        'solar_crm',
        'solar_warranty',
        'solar_service',
        'solar_subsidy',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/solar_dashboard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
