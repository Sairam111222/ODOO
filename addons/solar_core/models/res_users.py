# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    """Extend res.users to maintain Technician profiles, skills, and workload."""
    _inherit = 'res.users'

    is_solar_technician = fields.Boolean(
        string="Is Solar Technician",
        default=False,
        help="Check if this user is a field technician for solar installations.",
    )
    is_solar_surveyor = fields.Boolean(
        string="Is Solar Surveyor",
        default=False,
        help="Check if this user performs site surveys.",
    )
    technician_grade = fields.Selection(
        selection=[
            ('junior', 'Junior Technician'),
            ('senior', 'Senior Technician'),
            ('lead', 'Master / Lead Technician'),
        ],
        string="Technician Grade",
        default='junior',
    )
    certifications = fields.Char(
        string="Certifications / Licenses",
        help="e.g. MNRE Certified, Govt Electrical License Grade A, Working at Heights",
    )
    hourly_rate = fields.Float(
        string="Internal Labour Rate / Hour (₹)",
        default=250.0,
        help="Internal standard cost rate for technician labour costing.",
    )
    active_installations_count = fields.Integer(
        string="Active Installations Assigned",
        compute='_compute_technician_workload',
    )
    completed_installations_count = fields.Integer(
        string="Completed Installations",
        compute='_compute_technician_workload',
    )

    def _compute_technician_workload(self):
        for user in self:
            if 'solar.installation' in self.env:
                installations = self.env['solar.installation'].sudo().search([
                    '|',
                    ('technician_id', '=', user.id),
                    ('helper_technician_ids', 'in', [user.id]),
                ])
                user.active_installations_count = len(installations.filtered(
                    lambda i: i.state in ('assigned', 'scheduled', 'in_progress', 'testing', 'awaiting_approval')
                ))
                user.completed_installations_count = len(installations.filtered(
                    lambda i: i.state in ('completed', 'commissioned')
                ))
            else:
                user.active_installations_count = 0
                user.completed_installations_count = 0

