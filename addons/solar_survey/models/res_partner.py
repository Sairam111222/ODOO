# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    solar_survey_ids = fields.One2many(
        comodel_name='solar.site.survey',
        inverse_name='partner_id',
        string="Site Surveys",
    )

