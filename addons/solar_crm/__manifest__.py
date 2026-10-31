# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.
{
    'name': 'SolarFlow 360 — CRM Extensions',
    'version': '17.0.1.0.0',
    'category': 'Solar/CRM',
    'summary': 'Solar-specific CRM lead extensions for SolarFlow 360',
    'description': """
SolarFlow 360 — CRM Extensions
================================
Extends the standard Odoo CRM module with solar-specific fields and workflows:
- Lead source tracking (WhatsApp, phone, web form, referral, walk-in)
- Customer type and property classification on leads
- Estimated system capacity and type on opportunities
- Quick actions to create site surveys from leads
- Solar-specific pipeline stages
    """,
    'author': 'SunPower Solutions',
    'website': 'https://www.sunpowersolutions.example.com',
    'license': 'LGPL-3',
    'depends': [
        'solar_core',
        'solar_survey',
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
