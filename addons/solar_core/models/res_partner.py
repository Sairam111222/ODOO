# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    """Extend res.partner with solar-specific fields.

    Adds fields for solar customer classification, property details,
    and links to solar records (surveys, installations, warranties).
    """
    _inherit = 'res.partner'

    # --- Solar Classification ---
    is_solar_customer = fields.Boolean(
        string="Solar Customer",
        default=False,
        tracking=True,
        help="Mark this contact as a solar customer.",
    )
    customer_type = fields.Selection(
        selection=[
            ('residential', 'Residential'),
            ('commercial', 'Small Factory / Commercial'),
        ],
        string="Customer Type",
        tracking=True,
    )

    # --- Property Details ---
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
        string="Property Type",
        tracking=True,
    )
    roof_type = fields.Selection(
        selection=[
            ('flat_rcc', 'Flat RCC'),
            ('sloped_tile', 'Sloped Tile'),
            ('sloped_metal', 'Sloped Metal Sheet'),
            ('tin_shed', 'Tin Shed'),
            ('other', 'Other'),
        ],
        string="Roof Type",
    )
    roof_area_sqft = fields.Float(
        string="Available Roof Area (sq ft)",
        digits=(10, 2),
    )
    monthly_electricity_bill = fields.Float(
        string="Monthly Electricity Bill (₹)",
        digits=(10, 2),
        help="Average monthly electricity bill in INR.",
    )
    electricity_provider = fields.Char(
        string="Electricity Provider / DISCOM",
    )
    consumer_number = fields.Char(
        string="Consumer Number",
    )
    sanctioned_load_kw = fields.Float(
        string="Sanctioned Load (kW)",
        digits=(6, 2),
    )

    # --- Geographical ---
    geo_latitude = fields.Float(
        string="Latitude",
        digits=(10, 7),
    )
    geo_longitude = fields.Float(
        string="Longitude",
        digits=(10, 7),
    )

    # --- Computed ---
    solar_installation_count = fields.Integer(
        string="Installation Count",
        compute='_compute_solar_installation_count',
    )

    def _compute_solar_installation_count(self):
        for partner in self:
            if 'solar.installation' in self.env:
                partner.solar_installation_count = self.env['solar.installation'].sudo().search_count([
                    ('partner_id', '=', partner.id)
                ])
            else:
                partner.solar_installation_count = 0

    # --- Constraints ---
    @api.constrains('roof_area_sqft')
    def _check_roof_area(self):
        for rec in self:
            if rec.roof_area_sqft and rec.roof_area_sqft < 0:
                raise ValidationError(_("Roof area cannot be negative."))

    @api.constrains('sanctioned_load_kw')
    def _check_sanctioned_load(self):
        for rec in self:
            if rec.sanctioned_load_kw and rec.sanctioned_load_kw < 0:
                raise ValidationError(_("Sanctioned load cannot be negative."))

