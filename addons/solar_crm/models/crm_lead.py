# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class CrmLead(models.Model):
    """Extend crm.lead with solar-specific fields, duplicate detection,
    and customer journey orchestration.
    """
    _inherit = 'crm.lead'

    # --- Lead Source & Multi-Channel Origin ---
    solar_lead_source = fields.Selection(
        selection=[
            ('whatsapp', 'WhatsApp Inquiry'),
            ('phone', 'Phone Call'),
            ('webform', 'Website Online Form'),
            ('walkin', 'Walk-In / Showroom'),
            ('referral', 'Customer Referral'),
            ('social_media', 'Social Media Campaign'),
            ('exhibition', 'Exhibition / Expo'),
            ('other', 'Other'),
        ],
        string="Lead Channel Source",
        default='webform',
        tracking=True,
        help="Inbound acquisition channel for the solar enquiry.",
    )

    # --- Customer Classification & Requirements ---
    customer_type = fields.Selection(
        selection=[
            ('residential', 'Residential (Individual / Villa / Apartment)'),
            ('commercial', 'Small Commercial / Factory / Workshop'),
        ],
        string="Customer Segment",
        default='residential',
        tracking=True,
    )
    property_type = fields.Selection(
        selection=[
            ('independent_house', 'Independent House'),
            ('apartment', 'Apartment / Society'),
            ('villa', 'Gated Villa'),
            ('factory', 'Small Industrial Unit / Factory'),
            ('warehouse', 'Warehouse / Godown'),
            ('office', 'Commercial Office'),
            ('other', 'Other'),
        ],
        string="Property Type",
        default='independent_house',
    )
    customer_requirements = fields.Text(
        string="Specific Customer Requirements / Notes",
        help="Customer remarks on power cuts, load requirements, battery backup hours, etc.",
    )

    # --- Solar Sizing & Preference ---
    grid_preference = fields.Selection(
        selection=[
            ('ongrid', 'On-Grid (Net Metering, No Battery)'),
            ('offgrid', 'Off-Grid (Full Battery Storage)'),
            ('hybrid', 'Hybrid (Net Metering + Battery Backup)'),
        ],
        string="Grid Connection Preference",
        default='ongrid',
        tracking=True,
    )
    estimated_system_type_id = fields.Many2one(
        comodel_name='solar.system.type',
        string="Estimated System Type",
    )
    estimated_capacity_kw = fields.Float(
        string="Desired Capacity (kW)",
        digits=(6, 2),
        default=3.0,
        help="System capacity preference (1.0 to 5.0 kW)",
    )
    monthly_electricity_bill = fields.Float(
        string="Monthly Electricity Bill (₹)",
        digits=(10, 2),
    )
    roof_area_sqft = fields.Float(
        string="Estimated Roof Area (sq ft)",
        digits=(10, 2),
    )
    installation_street = fields.Char(string="Installation Street Address")
    installation_city = fields.Char(string="Installation City")
    installation_zip = fields.Char(string="Installation Pincode")

    # --- Duplicate Lead Management ---
    is_duplicate_lead = fields.Boolean(
        string="Potential Duplicate",
        compute='_compute_duplicate_lead',
        store=True,
    )
    duplicate_lead_ids = fields.Many2many(
        comodel_name='crm.lead',
        relation='solar_crm_duplicate_lead_rel',
        column1='lead_id',
        column2='duplicate_id',
        string="Matching Duplicate Leads",
        compute='_compute_duplicate_lead',
    )

    # --- Cancellation & Loss Reason Tracking ---
    solar_lost_reason = fields.Selection(
        selection=[
            ('high_price', 'High Upfront Cost / Budget Issue'),
            ('discom_delay', 'DISCOM / Net-Metering Concerns'),
            ('roof_unfit', 'Roof Structurally Unsuitable / Shaded'),
            ('competitor', 'Chosen Competitor Provider'),
            ('changed_mind', 'Customer Postponed / Not Interested'),
            ('unreachable', 'Contact Invalid / Unresponsive'),
            ('other', 'Other Reason'),
        ],
        string="Solar Loss / Cancellation Reason",
        tracking=True,
    )
    solar_lost_notes = fields.Text(string="Loss Details & Feedback")

    # --- Site Survey Handover ---
    survey_id = fields.Many2one(
        comodel_name='solar.site.survey',
        string="Linked Site Survey",
        tracking=True,
    )
    survey_state = fields.Selection(
        related='survey_id.state',
        string="Survey Status",
        readonly=True,
    )

    @api.depends('phone', 'mobile', 'email_from', 'partner_id')
    def _compute_duplicate_lead(self):
        for lead in self:
            domain = [('id', '!=', lead.id if isinstance(lead.id, int) else 0)]
            conditions = []
            if lead.phone:
                conditions.append(('phone', '=', lead.phone))
            if lead.mobile:
                conditions.append(('mobile', '=', lead.mobile))
            if lead.email_from:
                conditions.append(('email_from', '=', lead.email_from))
            if lead.partner_id:
                conditions.append(('partner_id', '=', lead.partner_id.id))

            if conditions:
                from odoo.osv import expression
                matching_domain = expression.AND([domain, expression.OR([[c] for c in conditions])])
                duplicates = self.env['crm.lead'].search(matching_domain, limit=5)
                lead.duplicate_lead_ids = duplicates
                lead.is_duplicate_lead = bool(duplicates)
            else:
                lead.duplicate_lead_ids = False
                lead.is_duplicate_lead = False

    @api.constrains('estimated_capacity_kw')
    def _check_capacity_range(self):
        for lead in self:
            if lead.estimated_capacity_kw and (lead.estimated_capacity_kw < 0.5 or lead.estimated_capacity_kw > 100.0):
                raise ValidationError(_("Requested capacity must be between 0.5 kW and 100.0 kW."))

    def action_schedule_solar_followup(self):
        """Schedule an automated follow-up activity for the lead owner."""
        self.ensure_one()
        activity_type = self.env.ref('mail.mail_activity_data_call', raise_if_not_found=False)
        if not activity_type:
            activity_type = self.env['mail.activity.type'].search([('category', '=', 'default')], limit=1)

        self.env['mail.activity'].create({
            'activity_type_id': activity_type.id if activity_type else False,
            'summary': _("Follow-up on Solar Inquiry (%s kW)", self.estimated_capacity_kw),
            'note': _("Customer inquiry regarding %s system. Check electricity bill and schedule site survey.", self.grid_preference),
            'date_deadline': fields.Date.context_today(self) + relativedelta(days=2),
            'user_id': self.user_id.id or self.env.user.id,
            'res_id': self.id,
            'res_model_id': self.env['ir.model']._get('crm.lead').id,
        })
        self.message_post(body=_("Automated 48-hour follow-up call activity scheduled for %s.", self.user_id.name or 'sales team'))

    def action_reassign_lead(self, new_user_id):
        """Audit-logged lead reassignment."""
        self.ensure_one()
        old_user = self.user_id
        self.user_id = new_user_id
        self.message_post(body=_(
            "Lead reassigned from %s to %s.",
            old_user.name if old_user else "Unassigned",
            self.user_id.name
        ))

    def action_create_survey(self):
        """Create a site survey from this lead/opportunity."""
        self.ensure_one()
        if not self.partner_id:
            # Auto-create customer partner if missing
            partner = self.env['res.partner'].create({
                'name': self.contact_name or self.partner_name or self.name,
                'phone': self.phone or self.mobile,
                'email': self.email_from,
                'street': self.installation_street or self.street,
                'city': self.installation_city or self.city,
                'zip': self.installation_zip or self.zip,
                'is_solar_customer': True,
                'customer_type': self.customer_type,
                'property_type': self.property_type,
            })
            self.partner_id = partner

        survey = self.env['solar.site.survey'].create({
            'partner_id': self.partner_id.id,
            'property_type': self.property_type,
            'roof_area_sqft': self.roof_area_sqft,
            'avg_monthly_bill': self.monthly_electricity_bill,
            'recommended_capacity_kw': self.estimated_capacity_kw,
            'recommended_system_type_id': self.estimated_system_type_id.id if self.estimated_system_type_id else False,
        })
        self.survey_id = survey

        self.message_post(body=_("Site Survey %s generated from this inquiry.", survey.name))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Site Survey'),
            'res_model': 'solar.site.survey',
            'res_id': survey.id,
            'view_mode': 'form',
            'target': 'current',
        }
