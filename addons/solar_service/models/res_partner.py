# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    solar_service_ticket_ids = fields.One2many(
        comodel_name='solar.service.ticket',
        inverse_name='partner_id',
        string="Service Tickets",
    )

