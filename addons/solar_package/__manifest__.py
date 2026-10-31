# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.
{
    'name': 'SolarFlow 360 — Packages & Bundles',
    'version': '17.0.1.0.0',
    'category': 'Solar/Package',
    'summary': 'Standardized solar equipment packages (1kW to 5kW On-Grid/Off-Grid)',
    'description': """
SolarFlow 360 — Solar Package Module
====================================
Configurable standard solar packages bundling solar panels, inverters, structures, and wiring:
- 1kW to 5kW residential and small commercial pre-engineered packages
- On-Grid, Off-Grid, and Hybrid options
- Bill of Materials (BOM) decomposition for quick inventory picking and costing
- Standardized pricing, installation fees, and warranty definitions
    """,
    'author': 'SunPower Solutions',
    'website': 'https://www.sunpowersolutions.example.com',
    'license': 'LGPL-3',
    'depends': [
        'solar_core',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/solar_package_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}

