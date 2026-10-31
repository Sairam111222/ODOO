# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.
{
    'name': 'SolarFlow 360 — Core',
    'version': '17.0.1.0.0',
    'category': 'Solar/Core',
    'summary': 'Core models, security groups, and shared utilities for SolarFlow 360 Solar ERP',
    'description': """
SolarFlow 360 — Core Module
============================
Foundation module for the SolarFlow 360 Solar Installation Management ERP.

Provides:
- Solar-specific security groups (Director, Surveyor, Technician, etc.)
- Base mixins and abstract models
- Shared constants, enumerations, and utility functions
- System-wide configuration settings
- Company-level solar defaults

This module must be installed before any other solar_* module.
    """,
    'author': 'SunPower Solutions',
    'website': 'https://www.sunpowersolutions.example.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'contacts',
        'crm',
        'sale_management',
        'stock',
        'purchase',
        'account',
        'project',
    ],
    'data': [
        # Security — loaded first
        'security/solar_security_groups.xml',
        'security/ir.model.access.csv',
        'security/solar_record_rules.xml',
        # Data
        'data/solar_system_type_data.xml',
        'data/solar_sequence_data.xml',
        # Views
        'views/res_partner_views.xml',
        'views/solar_menus.xml',
    ],
    'demo': [],
    'assets': {},
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}

