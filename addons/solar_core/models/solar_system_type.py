# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SolarSystemType(models.Model):
    """Solar system type reference data (On-Grid, Off-Grid, Hybrid).

    Read-only master data used across surveys, packages, and installations.
    """
    _name = 'solar.system.type'
    _description = 'Solar System Type'
    _order = 'name'

    name = fields.Char(string="Name", required=True, translate=True)
    code = fields.Char(string="Code", required=True)
    description = fields.Text(string="Description", translate=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'System type code must be unique.'),
    ]

