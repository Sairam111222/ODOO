# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

import math
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SolarPackage(models.Model):
    """Solar Package Master (1kW to 5kW standardized & custom solar systems)."""
    _name = 'solar.package'
    _description = 'Solar Package'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'capacity_kw asc, name asc'

    name = fields.Char(string='Package Name', required=True, tracking=True)
    code = fields.Char(string='Package Code', required=True, copy=False)
    system_type_id = fields.Many2one(
        comodel_name='solar.system.type',
        string='System Type',
        required=True,
        tracking=True,
    )
    capacity_kw = fields.Float(
        string='Rated Capacity (kW)',
        required=True,
        tracking=True,
        help="Capacity rating from 1 kW to 5 kW",
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('discontinued', 'Discontinued'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    # Component Specifications
    panel_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Solar Panel Model',
    )
    panel_wattage = fields.Float(string='Panel Wattage (Wp)', default=550.0)
    panel_quantity = fields.Integer(string='Panel Quantity', default=6)
    total_panel_capacity_kw = fields.Float(
        string='Calculated PV Capacity (kW)',
        compute='_compute_panel_capacity',
        store=True,
    )

    inverter_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Solar Inverter Model',
    )
    inverter_capacity_kw = fields.Float(string='Inverter Capacity (kW)')

    battery_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Battery Model (Off-Grid/Hybrid)',
    )
    battery_capacity_ah = fields.Float(string='Battery Capacity (Ah)', default=150.0)
    battery_quantity = fields.Integer(string='Battery Count', default=0)

    # Standard Pricing & Cost Breakdown
    base_equipment_price = fields.Float(
        string='Base Equipment Price (₹)',
        compute='_compute_bom_cost',
        store=True,
        readonly=False,
        tracking=True,
    )
    installation_charge = fields.Float(
        string='Installation & Labour Charge (₹)',
        default=15000.0,
        tracking=True,
    )
    transport_charge = fields.Float(
        string='Transport & Logistics (₹)',
        default=3000.0,
    )
    discom_paperwork_charge = fields.Float(
        string='DISCOM Net-Metering Liaison (₹)',
        default=5000.0,
    )
    total_price = fields.Float(
        string='Total Standard Price (₹)',
        compute='_compute_total_price',
        store=True,
    )

    # Warranties
    panel_warranty_years = fields.Integer(string='Panel Performance Warranty (Yrs)', default=25)
    inverter_warranty_years = fields.Integer(string='Inverter Warranty (Yrs)', default=5)
    workmanship_warranty_years = fields.Integer(string='Workmanship Warranty (Yrs)', default=5)

    # Package Lines / Detailed BOM
    package_line_ids = fields.One2many(
        comodel_name='solar.package.line',
        inverse_name='package_id',
        string='Package Components & Materials',
    )

    @api.depends('panel_wattage', 'panel_quantity')
    def _compute_panel_capacity(self):
        for rec in self:
            rec.total_panel_capacity_kw = (rec.panel_wattage * rec.panel_quantity) / 1000.0

    @api.depends('package_line_ids.subtotal')
    def _compute_bom_cost(self):
        for rec in self:
            bom_sum = sum(line.subtotal for line in rec.package_line_ids)
            if bom_sum > 0:
                rec.base_equipment_price = bom_sum

    @api.depends('base_equipment_price', 'installation_charge', 'transport_charge', 'discom_paperwork_charge')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = (
                (rec.base_equipment_price or 0.0) +
                (rec.installation_charge or 0.0) +
                (rec.transport_charge or 0.0) +
                (rec.discom_paperwork_charge or 0.0)
            )

    @api.constrains('capacity_kw')
    def _check_capacity(self):
        for rec in self:
            if rec.capacity_kw <= 0:
                raise ValidationError(_("Package capacity must be strictly greater than 0 kW."))

    def action_auto_calculate_materials(self, cable_distance=25.0):
        """Engineering Sizing Rules:
        - Panel Count = ceil((Capacity in kW * 1000) / Panel Wattage)
        - Mounting Structure Kits = ceil(Panel Count / 2)
        - DC Cable 4 sq mm = (Cable Distance * 2) + 10 meters safety loop
        - AC Cable 4/6 sq mm = Cable Distance + 5 meters
        - Earthing Kit = 2 Sets (1 for Solar Array/LA, 1 for Inverter)
        - Lightning Arrester = 1 Set
        - Distribution Boxes = 1 DCDB + 1 ACDB
        """
        self.ensure_one()
        p_watt = self.panel_wattage or 550.0
        p_count = math.ceil((self.capacity_kw * 1000.0) / p_watt)
        self.panel_quantity = p_count

        # Clear existing auto lines and re-populate
        self.package_line_ids.unlink()

        lines_to_create = []

        # 1. Panels
        if self.panel_product_id:
            lines_to_create.append({
                'package_id': self.id,
                'product_id': self.panel_product_id.id,
                'component_type': 'panel',
                'description': _("High Efficiency Mono-PERC Solar PV Panels (%s Wp)", p_watt),
                'quantity': p_count,
                'unit_price': self.panel_product_id.lst_price or 14000.0,
            })

        # 2. Inverter
        if self.inverter_product_id:
            lines_to_create.append({
                'package_id': self.id,
                'product_id': self.inverter_product_id.id,
                'component_type': 'inverter',
                'description': _("Solar Grid-Tie / Hybrid Inverter (%s kW)", self.capacity_kw),
                'quantity': 1.0,
                'unit_price': self.inverter_product_id.lst_price or 35000.0,
            })

        # 3. Mounting Structures
        structure_count = math.ceil(p_count / 2.0)
        prod_structure = self.env['product.product'].search([('name', 'ilike', 'Structure')], limit=1)
        if not prod_structure and self.panel_product_id:
            prod_structure = self.panel_product_id
        if prod_structure:
            lines_to_create.append({
                'package_id': self.id,
                'product_id': prod_structure.id,
                'component_type': 'structure',
                'description': _("Elevated HDGI / Aluminum Mounting Structure (Pairs)"),
                'quantity': structure_count,
                'unit_price': 3500.0,
            })

        # 4. DC & AC Cables
        dc_len = (cable_distance * 2.0) + 10.0
        ac_len = cable_distance + 5.0
        prod_cable = self.env['product.product'].search([('name', 'ilike', 'Cable')], limit=1)
        if not prod_cable and self.panel_product_id:
            prod_cable = self.panel_product_id
        if prod_cable:
            lines_to_create.append({
                'package_id': self.id,
                'product_id': prod_cable.id,
                'component_type': 'cable',
                'description': _("4 sq mm Solar DC Cable (UV Protected)"),
                'quantity': dc_len,
                'unit_price': 85.0,
            })
            lines_to_create.append({
                'package_id': self.id,
                'product_id': prod_cable.id,
                'component_type': 'cable',
                'description': _("4/6 sq mm AC Armoured Cable"),
                'quantity': ac_len,
                'unit_price': 110.0,
            })

        # 5. Protection & Earthing
        prod_protect = self.env['product.product'].search([('name', 'ilike', 'Earthing')], limit=1)
        if not prod_protect and self.panel_product_id:
            prod_protect = self.panel_product_id
        if prod_protect:
            lines_to_create.append({
                'package_id': self.id,
                'product_id': prod_protect.id,
                'component_type': 'protection',
                'description': _("Pre-wired DCDB + ACDB with SPD & MCB Protection"),
                'quantity': 1.0,
                'unit_price': 6500.0,
            })
            lines_to_create.append({
                'package_id': self.id,
                'product_id': prod_protect.id,
                'component_type': 'earthing',
                'description': _("Chemical Earthing Electrode (2 Pits) + Lightning Arrester"),
                'quantity': 2.0,
                'unit_price': 4500.0,
            })

        # 6. Batteries (if off-grid or hybrid)
        if self.system_type_id.code in ('OFFGRID', 'HYBRID') and self.battery_product_id:
            batt_qty = self.battery_quantity or 2
            lines_to_create.append({
                'package_id': self.id,
                'product_id': self.battery_product_id.id,
                'component_type': 'battery',
                'description': _("Solar Tubular / Lithium Battery Bank (%s Ah)", self.battery_capacity_ah),
                'quantity': batt_qty,
                'unit_price': self.battery_product_id.lst_price or 18000.0,
            })

        self.env['solar.package.line'].create(lines_to_create)
        self.message_post(body=_(
            "Automated Bill of Materials calculated: %s panels (%s Wp), %s structure kits, %sm DC cable, %sm AC cable.",
            p_count, p_watt, structure_count, dc_len, ac_len
        ))

    def action_activate(self):
        self.write({'state': 'active'})

    def action_discontinue(self):
        self.write({'state': 'discontinued'})

    def action_draft(self):
        self.write({'state': 'draft'})


class SolarPackageLine(models.Model):
    """Detailed Component Line for Solar Package (BOM)."""
    _name = 'solar.package.line'
    _description = 'Solar Package Line'

    package_id = fields.Many2one(
        comodel_name='solar.package',
        string='Package',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Component Product',
        required=True,
    )
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    unit_price = fields.Float(string='Unit Cost (₹)', default=0.0)
    subtotal = fields.Float(
        string='Subtotal (₹)',
        compute='_compute_subtotal',
        store=True,
    )
    component_type = fields.Selection(
        selection=[
            ('panel', 'Solar PV Panel'),
            ('inverter', 'Inverter'),
            ('battery', 'Battery Storage'),
            ('structure', 'Mounting Structure'),
            ('cable', 'DC/AC Cabling'),
            ('protection', 'Distribution Box / Protection'),
            ('earthing', 'Earthing Kit & Lightning Arrester'),
            ('other', 'Other Accessories'),
        ],
        string='Component Type',
        default='other',
        required=True,
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (line.quantity or 0.0) * (line.unit_price or 0.0)
