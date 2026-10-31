# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SolarSiteSurvey(models.Model):
    """Solar Site Survey model capturing physical and electrical roof feasibility."""
    _name = 'solar.site.survey'
    _description = 'Solar Site Survey'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'survey_date desc, id desc'

    name = fields.Char(
        string='Survey Reference',
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
    surveyor_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned Surveyor',
        required=True,
        tracking=True,
        default=lambda self: self.env.user,
    )
    survey_date = fields.Date(
        string='Survey Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    scheduled_date = fields.Datetime(
        string='Scheduled Appointment',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('submitted', 'Submitted for Approval'),
            ('approved', 'Approved by Survey Manager'),
            ('rejected', 'Rejected / Re-survey Required'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    rejection_reason = fields.Text(
        string='Rejection Reason & Required Fixes',
        tracking=True,
    )
    revision_count = fields.Integer(
        string='Survey Revision',
        default=1,
        readonly=True,
    )
    original_survey_id = fields.Many2one(
        comodel_name='solar.site.survey',
        string='Original Survey (if Re-survey)',
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    # Property Assessment
    property_type = fields.Selection(
        selection=[
            ('independent_house', 'Independent House'),
            ('apartment', 'Apartment'),
            ('villa', 'Villa'),
            ('factory', 'Factory'),
            ('warehouse', 'Warehouse'),
            ('office', 'Office Building'),
            ('other', 'Other'),
        ],
        string='Property Type',
    )
    roof_type = fields.Selection(
        selection=[
            ('flat_rcc', 'Flat RCC'),
            ('sloped_tile', 'Sloped Tile'),
            ('sloped_metal', 'Sloped Metal Sheet'),
            ('tin_shed', 'Tin Shed'),
            ('other', 'Other'),
        ],
        string='Roof Type',
    )
    roof_area_sqft = fields.Float(string='Total Roof Area (sq ft)')
    available_area_sqft = fields.Float(string='Usable Solar Area (sq ft)')
    roof_tilt_degrees = fields.Float(
        string='Roof Tilt Angle (°)',
        default=15.0,
        help="Recommended 12° to 25° for optimal generation in India.",
    )
    roof_condition = fields.Selection(
        selection=[
            ('excellent', 'Excellent (Solid Concrete / New Structure)'),
            ('good', 'Good (Minor wear, safe for mounting)'),
            ('fair', 'Fair (Requires reinforcement)'),
            ('poor', 'Poor (Structurally unsafe for solar)'),
        ],
        string='Roof Structural Condition',
        default='good',
    )
    roof_orientation = fields.Selection(
        selection=[
            ('south', 'South (Optimal Generation)'),
            ('southeast', 'South-East'),
            ('southwest', 'South-West'),
            ('east', 'East'),
            ('west', 'West'),
            ('north', 'North (Not Recommended)'),
        ],
        string='Primary Roof Orientation',
        default='south',
    )
    shading_analysis = fields.Selection(
        selection=[
            ('no_shading', 'No Shading (Direct Sun > 6 hrs)'),
            ('minimal', 'Minimal (< 10% area)'),
            ('moderate', 'Moderate (10% - 30% area)'),
            ('heavy', 'Heavy (> 30% area, requires tree trimming/structure elevation)'),
        ],
        string='Shading Assessment',
        default='no_shading',
    )
    cable_distance_meters = fields.Float(
        string='Estimated DC/AC Cable Route (Meters)',
        default=25.0,
        help="Distance from solar panel array to inverter / main distribution board.",
    )

    # Electrical Details
    sanctioned_load_kw = fields.Float(string='Sanctioned Load (kW)')
    existing_load_kw = fields.Float(string='Connected Load (kW)')
    avg_monthly_bill = fields.Float(string='Avg Monthly Bill (₹)')
    avg_monthly_consumption_kwh = fields.Float(string='Avg Monthly Units (kWh)')
    electricity_provider = fields.Char(string='DISCOM / Utility Provider')
    consumer_number = fields.Char(string='Consumer Number')
    meter_type = fields.Selection(
        selection=[
            ('single_phase', 'Single Phase (Up to 3 kW typically)'),
            ('three_phase', 'Three Phase (Mandatory for > 5 kW)'),
        ],
        string='Grid Phase / Meter Type',
        default='single_phase',
    )
    grid_feasibility = fields.Selection(
        selection=[
            ('approved', 'Grid Feasible & Ready for Net-Meter'),
            ('upgrade_needed', 'Requires Phase / Load Enhancement at DISCOM'),
            ('offgrid_only', 'Unstable Grid / Frequent Outages -> Recommend Off-Grid'),
        ],
        string='Grid Interconnection Feasibility',
        default='approved',
    )

    # Technical Recommendations
    recommended_system_type_id = fields.Many2one(
        comodel_name='solar.system.type',
        string='Recommended System Type',
    )
    recommended_capacity_kw = fields.Float(string='Recommended Capacity (kW)')
    estimated_generation_kwh_month = fields.Float(
        string='Est. Generation (kWh/mo)',
        compute='_compute_estimates',
        store=True,
    )
    estimated_savings_monthly = fields.Float(
        string='Est. Monthly Savings (₹)',
        compute='_compute_estimates',
        store=True,
    )

    # Documentation & Notes
    survey_notes = fields.Html(string='Technical Observations & Obstacles')

    # Linked Sales Quotation
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Generated Quotation',
        readonly=True,
        tracking=True,
    )

    @api.depends('recommended_capacity_kw', 'avg_monthly_bill', 'avg_monthly_consumption_kwh')
    def _compute_estimates(self):
        for record in self:
            # 1 kW produces approx 120 kWh per month in standard Indian solar conditions (4 units/day * 30 days)
            gen = (record.recommended_capacity_kw or 0.0) * 120.0
            record.estimated_generation_kwh_month = gen
            # Estimated tariff approx ₹7.5 per unit
            record.estimated_savings_monthly = gen * 7.5

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solar.site.survey') or _('New')
        return super().create(vals_list)

    def action_schedule(self):
        self.write({'state': 'scheduled'})

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_submit_for_approval(self):
        """Mandatory validation before submission."""
        for record in self:
            missing_fields = []
            if not record.roof_area_sqft or record.roof_area_sqft <= 0:
                missing_fields.append("Total Roof Area (> 0 sq ft)")
            if not record.available_area_sqft or record.available_area_sqft <= 0:
                missing_fields.append("Usable Solar Area (> 0 sq ft)")
            if record.available_area_sqft > record.roof_area_sqft:
                raise ValidationError(_("Usable solar area cannot exceed total roof area."))
            if not record.cable_distance_meters or record.cable_distance_meters <= 0:
                missing_fields.append("Cable Distance (> 0 meters)")
            if not record.avg_monthly_bill or record.avg_monthly_bill <= 0:
                missing_fields.append("Average Monthly Electricity Bill (> ₹0)")
            if not record.recommended_capacity_kw or record.recommended_capacity_kw <= 0:
                missing_fields.append("Recommended System Capacity (> 0 kW)")
            if record.roof_condition == 'poor':
                raise ValidationError(_("Cannot submit survey with 'Poor' roof condition. Structural repairs or re-survey required."))

            if missing_fields:
                raise ValidationError(_(
                    "Mandatory measurements missing before submission:\n- %s",
                    "\n- ".join(missing_fields)
                ))

        self.write({'state': 'submitted'})
        self.message_post(body=_("Survey submitted for Managerial Review and Technical Approval."))

    def action_approve(self):
        self.write({'state': 'approved', 'rejection_reason': False})
        self.message_post(body=_("Survey approved. Ready for Quotation and Sizing generation."))

    def action_reject(self, reason="Survey measurements incomplete or inaccurate."):
        self.write({'state': 'rejected', 'rejection_reason': reason})
        self.message_post(body=_("Survey rejected by manager. Reason: %s", reason))

    def action_resurvey(self):
        """Creates a linked re-survey with incremented revision number."""
        self.ensure_one()
        new_survey = self.copy({
            'state': 'draft',
            'revision_count': self.revision_count + 1,
            'original_survey_id': self.id,
            'rejection_reason': False,
        })
        self.message_post(body=_("Re-survey %s initiated from this record.", new_survey.name))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Re-Survey Revision'),
            'res_model': 'solar.site.survey',
            'res_id': new_survey.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_generate_quotation(self):
        """Generates a quotation. SERVER-SIDE CHECK: Must be approved!"""
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_(
                "Compliance Violation: Quotations cannot be generated from unapproved surveys.\n"
                "Current survey state is '%s'. Please obtain Survey Manager approval first.",
                self.state.title()
            ))

        # Find matching package or standard template
        package = self.env['solar.package'].search([
            ('system_type_id', '=', self.recommended_system_type_id.id if self.recommended_system_type_id else False),
            ('capacity_kw', '=', self.recommended_capacity_kw),
            ('state', '=', 'active'),
        ], limit=1)

        # Create Quotation (Sale Order)
        order_vals = {
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'validity_date': fields.Date.context_today(self) + relativedelta(days=15),
            'note': _(
                "Solar Proposal for %s kW %s system based on approved Site Survey %s.\n"
                "Estimated Monthly Generation: %s kWh. Estimated Monthly Savings: ₹%s.",
                self.recommended_capacity_kw,
                self.recommended_system_type_id.name if self.recommended_system_type_id else "",
                self.name,
                self.estimated_generation_kwh_month,
                self.estimated_savings_monthly,
            ),
        }
        order = self.env['sale.order'].create(order_vals)
        self.sale_order_id = order

        self.message_post(body=_("Quotation %s generated from approved survey.", order.name))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Solar Quotation'),
            'res_model': 'sale.order',
            'res_id': order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
