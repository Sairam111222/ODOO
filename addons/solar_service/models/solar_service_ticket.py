# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SolarServiceTicket(models.Model):
    """Solar Service & Complaint Ticket - Complete Maintenance & Breakdown Engine."""
    _name = 'solar.service.ticket'
    _description = 'Solar Service Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    name = fields.Char(
        string='Ticket Number',
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
        string='Affected Installation',
        tracking=True,
    )
    serial_number_entered = fields.Char(
        string='Equipment Serial Number',
        help="Inverter, battery, or component serial number reported by customer.",
    )
    warranty_id = fields.Many2one(
        comodel_name='solar.warranty',
        string='Matched Warranty Certificate',
        tracking=True,
        compute='_compute_warranty_link',
        store=True,
        readonly=False,
    )
    ticket_type = fields.Selection(
        selection=[
            ('breakdown', 'Inverter Failure / Complete Outage'),
            ('generation_low', 'Low Generation / Degradation / Shading'),
            ('cleaning', 'Routine Panel Cleaning & Wash'),
            ('earthing', 'Earthing / Inverter Error / Sparking'),
            ('net_meter', 'Net-Meter Discrepancy / Billing Dispute'),
            ('physical_damage', 'Physical Damage / Storm / Broken Glass'),
            ('general', 'General Maintenance & Inspection'),
        ],
        string='Issue Category',
        required=True,
        default='breakdown',
        tracking=True,
    )
    priority = fields.Selection(
        selection=[
            ('0', 'Low - Routine'),
            ('1', 'Normal - Maintenance'),
            ('2', 'High - Degradation / Urgent'),
            ('3', 'Critical - Zero Generation Outage'),
        ],
        string='Priority Level',
        default='1',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('new', 'New Request Logged'),
            ('assigned', 'Technician Dispatched'),
            ('diagnosis', 'Root Cause Diagnosis on Site'),
            ('awaiting_parts', 'Awaiting Spare Parts / Replacement'),
            ('in_progress', 'Repair / Replacement In Progress'),
            ('resolved', 'Testing Complete & Resolved'),
            ('customer_confirmation', 'Awaiting Customer Sign-off'),
            ('closed', 'Closed & Verified'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='new',
        required=True,
        tracking=True,
    )
    assigned_technician_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned Field Technician',
        tracking=True,
    )
    scheduled_visit_date = fields.Date(string='Scheduled Site Visit Date')
    description = fields.Text(string='Customer Problem Description', required=True)
    diagnosis_findings = fields.Text(string='Technician Diagnostic Findings')
    resolution_notes = fields.Html(string='Work Performed & Corrective Actions')

    # Warranty Classification (Free vs Chargeable)
    is_warranty_claim = fields.Boolean(
        string='Covered Under Active Warranty (Free of Charge)',
        compute='_compute_warranty_claim_status',
        store=True,
        readonly=False,
        help="Automated check: If the equipment has an active non-expired warranty.",
    )
    repair_classification = fields.Selection(
        selection=[
            ('free_warranty', 'Free Warranty Service / Replacement'),
            ('chargeable', 'Chargeable Non-Warranty Repair'),
            ('amc_covered', 'Covered Under Routine AMC'),
            ('goodwill', 'Commercial Goodwill / Free Courtesy'),
        ],
        string='Billing Classification',
        default='free_warranty',
        tracking=True,
    )

    # Repeat Complaints
    is_repeat_complaint = fields.Boolean(string='Is Repeat Complaint', default=False)
    previous_ticket_id = fields.Many2one(
        comodel_name='solar.service.ticket',
        string='Previous Linked Ticket',
    )

    # Parts Consumed & Financial Costing
    part_line_ids = fields.One2many(
        comodel_name='solar.service.part.line',
        inverse_name='ticket_id',
        string='Parts & Components Replaced',
    )
    spare_parts_cost = fields.Float(
        string='Parts Cost (₹)',
        compute='_compute_ticket_costs',
        store=True,
    )
    labour_hours = fields.Float(string='Technician Hours Spent', default=2.0)
    labour_cost = fields.Float(
        string='Labour Cost (₹)',
        compute='_compute_ticket_costs',
        store=True,
    )
    transport_cost = fields.Float(string='Transport / Travel Cost (₹)', default=500.0)
    total_service_cost = fields.Float(
        string='Total Service Cost (₹)',
        compute='_compute_ticket_costs',
        store=True,
    )
    customer_invoice_amount = fields.Float(
        string='Amount Billed to Customer (₹)',
        help="0 for free warranty; total billable amount if out-of-warranty.",
    )

    # Customer Sign-Off
    customer_confirmation_received = fields.Boolean(
        string='Customer Sign-off Confirmed',
        default=False,
    )
    customer_feedback = fields.Text(string='Customer Closure Feedback')

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    @api.depends('serial_number_entered', 'installation_id')
    def _compute_warranty_link(self):
        for rec in self:
            warranty = False
            if rec.serial_number_entered:
                warranty = self.env['solar.warranty'].search([
                    ('serial_number', '=', rec.serial_number_entered.strip()),
                    ('state', 'in', ('active', 'expiring_soon')),
                ], limit=1)
            if not warranty and rec.installation_id:
                warranty = self.env['solar.warranty'].search([
                    ('installation_id', '=', rec.installation_id.id),
                    ('state', 'in', ('active', 'expiring_soon')),
                ], limit=1)
            rec.warranty_id = warranty

    @api.depends('warranty_id', 'warranty_id.state')
    def _compute_warranty_claim_status(self):
        for rec in self:
            if rec.warranty_id and rec.warranty_id.state in ('active', 'expiring_soon'):
                rec.is_warranty_claim = True
                rec.repair_classification = 'free_warranty'
            else:
                rec.is_warranty_claim = False
                rec.repair_classification = 'chargeable'

    @api.depends('part_line_ids.subtotal', 'labour_hours', 'assigned_technician_id.hourly_rate', 'transport_cost')
    def _compute_ticket_costs(self):
        for rec in self:
            rec.spare_parts_cost = sum(p.subtotal for p in rec.part_line_ids)
            hourly = rec.assigned_technician_id.hourly_rate if rec.assigned_technician_id else 250.0
            rec.labour_cost = (rec.labour_hours or 0.0) * hourly
            rec.total_service_cost = rec.spare_parts_cost + rec.labour_cost + (rec.transport_cost or 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solar.service.ticket') or _('New')
        return super().create(vals_list)

    def action_assign(self):
        for rec in self:
            if not rec.assigned_technician_id:
                raise ValidationError(_("Please designate an Assigned Technician before dispatching."))
        self.write({'state': 'assigned'})

    def action_diagnose(self):
        self.write({'state': 'diagnosis'})

    def action_awaiting_parts(self):
        self.write({'state': 'awaiting_parts'})

    def action_start_repair(self):
        self.write({'state': 'in_progress'})

    def action_resolve(self):
        for rec in self:
            if not rec.resolution_notes:
                raise ValidationError(_("Resolution notes and technical actions must be documented before resolving ticket."))
        self.write({'state': 'resolved'})

    def action_request_customer_confirmation(self):
        self.write({'state': 'customer_confirmation'})

    def action_close(self):
        """Never close without customer confirmation or explicit sign-off."""
        for rec in self:
            if not rec.customer_confirmation_received:
                raise UserError(_(
                    "Compliance Enforcement: Service tickets cannot be closed without customer confirmation.\n"
                    "Please verify customer sign-off or record customer walkthrough feedback first."
                ))
        self.write({'state': 'closed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class SolarServicePartLine(models.Model):
    """Spare Parts and Consumables used during Solar Service."""
    _name = 'solar.service.part.line'
    _description = 'Solar Service Spare Part Line'

    ticket_id = fields.Many2one(
        comodel_name='solar.service.ticket',
        string='Service Ticket',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Replaced Component / Part',
        required=True,
    )
    description = fields.Char(string='Description / Model')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price (₹)', default=0.0)
    subtotal = fields.Float(
        string='Subtotal (₹)',
        compute='_compute_subtotal',
        store=True,
    )

    @api.depends('quantity', 'unit_price', 'product_id.standard_price')
    def _compute_subtotal(self):
        for line in self:
            price = line.unit_price or (line.product_id.standard_price if line.product_id else 0.0)
            line.subtotal = (line.quantity or 0.0) * price
