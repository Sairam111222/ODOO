# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SolarWarrantyPolicy(models.Model):
    """Configurable Warranty Policy Master (Product Category / Component Guarantees)."""
    _name = 'solar.warranty.policy'
    _description = 'Solar Warranty Policy Master'
    _order = 'name'

    name = fields.Char(string='Policy Name', required=True)
    component_type = fields.Selection(
        selection=[
            ('panel', 'PV Panels'),
            ('inverter', 'Solar Inverter'),
            ('battery', 'Battery Storage'),
            ('structure', 'Mounting Structure'),
            ('comprehensive', 'System Workmanship & AMC'),
        ],
        string='Component Class',
        required=True,
    )
    standard_duration_years = fields.Integer(
        string='Default Duration (Years)',
        required=True,
        default=5,
        help="Configurable guarantee duration (e.g. 20-25 yrs for panels, 2-5 yrs for inverters)",
    )
    coverage_scope = fields.Text(
        string='Coverage Scope',
        default="Covers manufacturing defects, internal component breakdown, and rated power output degradation.",
    )
    exclusions = fields.Text(
        string='Exclusions',
        default="Grid surge over-voltage without SPD, unauthorized third-party tampering, physical structural damage, force majeure.",
    )
    active = fields.Boolean(default=True)


class SolarWarranty(models.Model):
    """Solar Warranty Certificate / Record with Serial Tracking."""
    _name = 'solar.warranty'
    _description = 'Solar Warranty Certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'end_date desc, id desc'

    name = fields.Char(
        string='Warranty Certificate #',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True,
        tracking=True,
    )
    installation_id = fields.Many2one(
        comodel_name='solar.installation',
        string='Solar Installation Project',
        required=True,
        tracking=True,
    )
    policy_id = fields.Many2one(
        comodel_name='solar.warranty.policy',
        string='Underlying Warranty Policy',
    )
    warranty_type = fields.Selection(
        selection=[
            ('panel', 'PV Panel Performance Guarantee (20-25 Years)'),
            ('inverter', 'Inverter Hardware Guarantee (2-5 Years)'),
            ('battery', 'Battery Capacity Guarantee (2-3 Years)'),
            ('comprehensive', 'System Workmanship & AMC (1-5 Years)'),
        ],
        string='Warranty Category',
        required=True,
        tracking=True,
    )
    serial_number = fields.Char(
        string='Covered Equipment Serial #',
        tracking=True,
        help="Serial number of specific inverter, battery, or panel batch.",
    )
    state = fields.Selection(
        selection=[
            ('active', 'Active & Covered'),
            ('expiring_soon', 'Expiring Within 60 Days'),
            ('expired', 'Expired'),
            ('claimed', 'Claim Logged / Active Dispute'),
            ('void', 'Void / Breached / Tampered'),
        ],
        string='Coverage Status',
        default='active',
        compute='_compute_warranty_state',
        store=True,
        tracking=True,
    )
    start_date = fields.Date(
        string='Commencement Date',
        required=True,
        default=fields.Date.context_today,
    )
    duration_years = fields.Integer(string='Duration (Years)', default=5, required=True)
    end_date = fields.Date(
        string='Expiry Date',
        compute='_compute_end_date',
        store=True,
        readonly=False,
    )
    terms = fields.Text(string='Terms & Exclusions')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    # Claim & Replacement History
    claim_count = fields.Integer(
        string='Claims Registered',
        compute='_compute_claims',
    )
    replacement_notes = fields.Text(string='Replacement / RMA History')

    def _compute_claims(self):
        for rec in self:
            if 'solar.service.ticket' in self.env:
                tickets = self.env['solar.service.ticket'].sudo().search([
                    ('warranty_id', '=', rec.id),
                    ('is_warranty_claim', '=', True),
                ])
                rec.claim_count = len(tickets)
            else:
                rec.claim_count = 0

    @api.depends('start_date', 'duration_years')
    def _compute_end_date(self):
        for rec in self:
            if rec.start_date and rec.duration_years:
                rec.end_date = rec.start_date + relativedelta(years=rec.duration_years)
            else:
                rec.end_date = rec.start_date

    @api.depends('end_date')
    def _compute_warranty_state(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if not rec.end_date:
                rec.state = 'active'
            elif rec.end_date < today:
                rec.state = 'expired'
            elif (rec.end_date - today).days <= 60:
                rec.state = 'expiring_soon'
            else:
                rec.state = 'active'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solar.warranty') or _('New')
        return super().create(vals_list)

    def action_void(self):
        self.write({'state': 'void'})

    def action_log_claim(self):
        self.write({'state': 'claimed'})
