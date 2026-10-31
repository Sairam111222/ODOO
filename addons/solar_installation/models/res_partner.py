# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    solar_installation_ids = fields.One2many(
        comodel_name='solar.installation',
        inverse_name='partner_id',
        string="Installations",
    )

