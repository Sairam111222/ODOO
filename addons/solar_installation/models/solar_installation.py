# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SolarInstallation(models.Model):
    """Solar Installation Project Model - Complete End-to-End Orchestration."""
    _name = 'solar.installation'
    _description = 'Solar Installation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc, id desc'

    name = fields.Char(
        string='Installation Reference',
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
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Originating Sales Order',
        tracking=True,
    )
    survey_id = fields.Many2one(
        comodel_name='solar.site.survey',
        string='Site Survey Reference',
        tracking=True,
    )
    package_id = fields.Many2one(
        comodel_name='solar.package',
        string='Installed Package',
        tracking=True,
    )
    system_type_id = fields.Many2one(
        comodel_name='solar.system.type',
        string='System Type',
        required=True,
    )
    capacity_kw = fields.Float(
        string='System Capacity (kW)',
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    # State Workflow
    state = fields.Selection(
        selection=[
            ('draft', 'Draft (Material Planning)'),
            ('assigned', 'Technician Crew Assigned'),
            ('scheduled', 'Deployment Scheduled'),
            ('in_progress', 'Mounting & Wiring In Progress'),
            ('testing', 'Electrical Safety & Grid Testing'),
            ('awaiting_approval', 'Awaiting Customer Sign-off & Inspection'),
            ('completed', 'Work Completed & Verified'),
            ('commissioned', 'Commissioned & Handed Over'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )

    # Technician Assignment (15 Technicians Pool)
    technician_id = fields.Many2one(
        comodel_name='res.users',
        string='Lead Technician',
        tracking=True,
    )
    helper_technician_ids = fields.Many2many(
        comodel_name='res.users',
        relation='solar_installation_helper_rel',
        column1='installation_id',
        column2='user_id',
        string='Assisted Technicians',
    )
    technician_hours_logged = fields.Float(
        string='Total Crew Hours Logged',
        default=16.0,
        help="Estimated or actual labor hours for technician costing.",
    )

    # Scheduling & Exceptions
    scheduled_date = fields.Date(string='Scheduled Date', tracking=True)
    actual_start_datetime = fields.Datetime(string='Actual Start Time')
    actual_completion_datetime = fields.Datetime(string='Actual Completion Time')
    commissioning_date = fields.Date(string='Commissioning Date', tracking=True)

    weather_delay_reason = fields.Text(string='Weather / Site Delay Remarks', tracking=True)
    reschedule_count = fields.Integer(string='Reschedule Count', default=0)

    # Quality, Testing & Grid Interconnection
    dc_voltage_measured = fields.Float(string='DC String Voltage (V)')
    ac_voltage_measured = fields.Float(string='AC Grid Voltage (V)')
    grid_frequency_hz = fields.Float(string='Grid Frequency (Hz)', default=50.0)
    earthing_resistance_ohms = fields.Float(string='Earthing Resistance (Ω)', default=2.5)
    net_meter_installed = fields.Boolean(string='Net Meter Connected', default=False)
    net_meter_number = fields.Char(string='Net Meter Serial Number')
    discom_inspection_passed = fields.Boolean(string='DISCOM Inspection Approved', default=False)
    testing_passed = fields.Boolean(string='Testing Verification Passed', default=False)

    # Customer Sign-Off & Verification
    customer_signoff_name = fields.Char(string='Sign-Off Signatory Name')
    customer_signoff_date = fields.Date(string='Customer Acceptance Date')
    customer_satisfaction_rating = fields.Selection(
        selection=[
            ('5', '5 Stars - Extremely Satisfied'),
            ('4', '4 Stars - Satisfied'),
            ('3', '3 Stars - Neutral'),
            ('2', '2 Stars - Dissatisfied'),
            ('1', '1 Star - Unacceptable'),
        ],
        string='Customer Handover Rating',
        default='5',
    )
    signoff_notes = fields.Text(string='Customer Walkthrough Feedback')

    # Installation Components / Equipment Serial Numbers
    installation_line_ids = fields.One2many(
        comodel_name='solar.installation.line',
        inverse_name='installation_id',
        string='Installed Components',
    )

    # Job-Level Financials & Profitability (Module 4)
    contract_revenue = fields.Float(
        string='Contract / Order Amount (₹)',
        compute='_compute_job_financials',
        store=True,
    )
    invoiced_amount = fields.Float(
        string='Invoiced Amount (₹)',
        compute='_compute_job_financials',
        store=True,
    )
    cash_received = fields.Float(
        string='Cash / Payments Received (₹)',
        compute='_compute_job_financials',
        store=True,
    )
    outstanding_receivable = fields.Float(
        string='Outstanding Receivable (₹)',
        compute='_compute_job_financials',
        store=True,
    )
    material_cost = fields.Float(
        string='Total Equipment Cost (₹)',
        compute='_compute_job_financials',
        store=True,
    )
    labour_cost = fields.Float(
        string='Labour Cost (₹)',
        compute='_compute_job_financials',
        store=True,
    )
    other_expenses = fields.Float(
        string='Other Direct Expenses (₹)',
        default=2500.0,
        help="Transport, scaffolding, safety gear, local authority permits.",
    )
    total_cost = fields.Float(
        string='Total Job Cost (₹)',
        compute='_compute_job_financials',
        store=True,
    )
    gross_profit = fields.Float(
        string='Gross Profit (₹)',
        compute='_compute_job_financials',
        store=True,
    )
    gross_margin_pct = fields.Float(
        string='Gross Margin (%)',
        compute='_compute_job_financials',
        store=True,
    )

    notes = fields.Html(string='Installation & Handover Remarks')

    @api.depends(
        'sale_order_id', 'sale_order_id.amount_total',
        'sale_order_id.invoice_ids.amount_total', 'sale_order_id.invoice_ids.payment_state',
        'installation_line_ids.cost_subtotal', 'technician_hours_logged',
        'technician_id.hourly_rate', 'other_expenses'
    )
    def _compute_job_financials(self):
        for rec in self:
            # 1. Revenue & Invoicing
            if rec.sale_order_id:
                rec.contract_revenue = rec.sale_order_id.amount_total
                invoices = rec.sale_order_id.invoice_ids.filtered(lambda i: i.state == 'posted')
                rec.invoiced_amount = sum(inv.amount_total for inv in invoices)
                paid_invs = invoices.filtered(lambda i: i.payment_state in ('paid', 'in_payment'))
                rec.cash_received = sum(inv.amount_total for inv in paid_invs)
                rec.outstanding_receivable = rec.invoiced_amount - rec.cash_received
            else:
                rec.contract_revenue = 0.0
                rec.invoiced_amount = 0.0
                rec.cash_received = 0.0
                rec.outstanding_receivable = 0.0

            # 2. Material Cost
            rec.material_cost = sum(line.cost_subtotal for line in rec.installation_line_ids)

            # 3. Labour Cost
            hourly = rec.technician_id.hourly_rate if rec.technician_id and rec.technician_id.hourly_rate else 250.0
            rec.labour_cost = (rec.technician_hours_logged or 0.0) * hourly

            # 4. Total Cost & Profitability
            rec.total_cost = rec.material_cost + rec.labour_cost + (rec.other_expenses or 0.0)
            rev = rec.contract_revenue or rec.invoiced_amount
            rec.gross_profit = rev - rec.total_cost
            rec.gross_margin_pct = (rec.gross_profit / rev * 100.0) if rev > 0 else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solar.installation') or _('New')
        return super().create(vals_list)

    def action_assign_crew(self):
        for rec in self:
            if not rec.technician_id:
                raise ValidationError(_("Please designate a Lead Technician before assigning the crew."))
        self.write({'state': 'assigned'})

    def action_schedule(self):
        for rec in self:
            if not rec.scheduled_date:
                raise ValidationError(_("Please specify a Scheduled Date before scheduling deployment."))
        self.write({'state': 'scheduled'})

    def action_log_weather_delay(self, reason):
        """Handle weather/delay exception."""
        self.write({
            'weather_delay_reason': reason,
            'reschedule_count': self.reschedule_count + 1,
            'state': 'scheduled',
        })
        self.message_post(body=_("Weather/Site delay recorded: %s (Reschedule count: %s)", reason, self.reschedule_count))

    def action_start_work(self):
        self.write({
            'state': 'in_progress',
            'actual_start_datetime': fields.Datetime.now(),
        })

    def action_start_testing(self):
        self.write({'state': 'testing'})

    def action_verify_testing(self):
        """Enforces electrical testing parameters."""
        for rec in self:
            if rec.dc_voltage_measured <= 0 or rec.ac_voltage_measured <= 0:
                raise ValidationError(_("Both DC String Voltage and AC Grid Voltage must be tested and recorded (> 0V)."))
            if rec.earthing_resistance_ohms <= 0 or rec.earthing_resistance_ohms > 5.0:
                raise ValidationError(_("Earthing resistance must be between 0.1 Ω and 5.0 Ω for electrical safety compliance."))
            rec.testing_passed = True
            rec.state = 'awaiting_approval'
            rec.message_post(body=_("Electrical safety and voltage testing verified. Awaiting customer sign-off."))

    def action_customer_signoff(self, signatory_name):
        """Submit customer acceptance sign-off."""
        self.write({
            'customer_signoff_name': signatory_name,
            'customer_signoff_date': fields.Date.context_today(self),
            'actual_completion_datetime': fields.Datetime.now(),
            'state': 'completed',
        })
        self.message_post(body=_("Customer digital sign-off completed by %s.", signatory_name))

    def action_commission(self):
        """Commission the installation and trigger warranty record creation."""
        for rec in self:
            if rec.state != 'completed':
                raise UserError(_("Cannot commission until installation is marked 'Completed' with customer sign-off."))
            if rec.system_type_id.code == 'ONGRID' and not rec.net_meter_installed:
                raise ValidationError(_("On-grid installations require Net Meter verification prior to commissioning."))

            # Verify that inverters and batteries have serial numbers recorded
            critical_lines = rec.installation_line_ids.filtered(lambda l: l.component_type in ('inverter', 'battery'))
            missing_serials = critical_lines.filtered(lambda l: not l.serial_number)
            if missing_serials:
                raise ValidationError(_(
                    "Mandatory Serial Numbers missing for equipment:\n%s\n"
                    "Serial numbers are strictly required for warranty activation.",
                    "\n".join([f"- {l.product_id.name}" for l in missing_serials])
                ))

            rec.write({
                'state': 'commissioned',
                'commissioning_date': fields.Date.context_today(self),
            })

            # Look up applicable warranty policy or defaults
            rec._activate_warranties()

    def _activate_warranties(self):
        """Automated Warranty Activation linking equipment and serial numbers."""
        self.ensure_one()
        if 'solar.warranty' not in self.env:
            return
        warranties_to_create = []

        # 1. Solar Panels (20-25 Years)
        panel_line = self.installation_line_ids.filtered(lambda l: l.component_type == 'panel')
        warranties_to_create.append({
            'partner_id': self.partner_id.id,
            'installation_id': self.id,
            'warranty_type': 'panel',
            'duration_years': 25,
            'start_date': fields.Date.context_today(self),
            'serial_number': panel_line[0].serial_number if panel_line else "BATCH-PANEL",
            'terms': _("25-Year 80% Performance Output Guarantee."),
        })

        # 2. Inverters (2-5 Years)
        inverter_lines = self.installation_line_ids.filtered(lambda l: l.component_type == 'inverter')
        for inv in inverter_lines:
            warranties_to_create.append({
                'partner_id': self.partner_id.id,
                'installation_id': self.id,
                'warranty_type': 'inverter',
                'duration_years': 5,
                'start_date': fields.Date.context_today(self),
                'serial_number': inv.serial_number or "INV-UNKNOWN",
                'terms': _("5-Year Manufacturer Warranty against component breakdown."),
            })

        # 3. Batteries (2-3 Years if applicable)
        battery_lines = self.installation_line_ids.filtered(lambda l: l.component_type == 'battery')
        for batt in battery_lines:
            warranties_to_create.append({
                'partner_id': self.partner_id.id,
                'installation_id': self.id,
                'warranty_type': 'battery',
                'duration_years': 3,
                'start_date': fields.Date.context_today(self),
                'serial_number': batt.serial_number or "BATT-UNKNOWN",
                'terms': _("3-Year Replacement Guarantee on cell capacity."),
            })

        # 4. Comprehensive Workmanship (1-5 Years)
        warranties_to_create.append({
            'partner_id': self.partner_id.id,
            'installation_id': self.id,
            'warranty_type': 'comprehensive',
            'duration_years': 1,
            'start_date': fields.Date.context_today(self),
            'serial_number': self.name,
            'terms': _("1-Year Comprehensive SunPower Workmanship Guarantee."),
        })

        self.env['solar.warranty'].sudo().create(warranties_to_create)
        self.message_post(body=_("Commissioning successful! Activated %s warranty certificates for customer.", len(warranties_to_create)))

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class SolarInstallationLine(models.Model):
    """Component Tracking Line for Installed Equipment (Serial Numbers & Costing)."""
    _name = 'solar.installation.line'
    _description = 'Solar Installation Component Line'

    installation_id = fields.Many2one(
        comodel_name='solar.installation',
        string='Installation',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Equipment Model',
        required=True,
    )
    component_type = fields.Selection(
        selection=[
            ('panel', 'PV Panel'),
            ('inverter', 'Inverter'),
            ('battery', 'Battery'),
            ('structure', 'Structure'),
            ('bos', 'Balance of System / Cables'),
        ],
        string='Component Class',
        required=True,
        default='panel',
    )
    quantity = fields.Float(string='Quantity', default=1.0)
    serial_number = fields.Char(string='Serial Number / Lot Number')
    unit_cost = fields.Float(string='Unit Cost (₹)', default=0.0)
    cost_subtotal = fields.Float(
        string='Cost Subtotal (₹)',
        compute='_compute_cost_subtotal',
        store=True,
    )
    status = fields.Selection(
        selection=[
            ('dispatched', 'Dispatched from Warehouse'),
            ('installed', 'Mounted & Connected'),
            ('verified', 'Tested & Verified'),
            ('defective', 'Defective / Replaced'),
        ],
        string='Installation Status',
        default='dispatched',
    )

    @api.depends('quantity', 'unit_cost', 'product_id.standard_price')
    def _compute_cost_subtotal(self):
        for line in self:
            price = line.unit_cost or (line.product_id.standard_price if line.product_id else 0.0)
            line.cost_subtotal = (line.quantity or 0.0) * price

    @api.constrains('serial_number', 'component_type')
    def _check_duplicate_serial_number(self):
        """Prevent duplicate serial numbers for inverters and batteries."""
        for line in self:
            if line.serial_number and line.component_type in ('inverter', 'battery'):
                duplicates = self.search([
                    ('id', '!=', line.id),
                    ('serial_number', '=', line.serial_number.strip()),
                    ('component_type', '=', line.component_type),
                    ('installation_id.state', 'not in', ('cancelled',)),
                ])
                if duplicates:
                    raise ValidationError(_(
                        "Serial Number Collision: Serial number '%s' is already registered on installation %s!\n"
                        "Each inverter and battery must have a unique serial number across installations.",
                        line.serial_number,
                        duplicates[0].installation_id.name
                    ))
