# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SolarSubsidyTracker(models.Model):
    """Government Rooftop Solar Subsidy & Paperwork Dossier Tracker."""
    _name = 'solar.subsidy.tracker'
    _description = 'Solar Subsidy Tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(
        string='Dossier Reference #',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Beneficiary Customer',
        required=True,
        tracking=True,
    )
    installation_id = fields.Many2one(
        comodel_name='solar.installation',
        string='Linked Solar Installation',
        required=True,
        tracking=True,
    )
    subsidy_scheme = fields.Char(
        string='Government Scheme Name',
        default='PM Surya Ghar: Muft Bijli Yojana / CFA Rooftop Scheme',
        required=True,
    )
    national_portal_app_number = fields.Char(
        string='National Portal / Application Ref #',
        tracking=True,
    )
    discom_application_number = fields.Char(
        string='DISCOM Net-Meter Application #',
        tracking=True,
    )
    responsible_employee_id = fields.Many2one(
        comodel_name='res.users',
        string='Liaison Officer / Responsible Employee',
        default=lambda self: self.env.user,
        tracking=True,
    )

    # Status Workflow
    state = fields.Selection(
        selection=[
            ('draft', 'Dossier Preparation'),
            ('documents_collected', 'Documents Verified'),
            ('submitted', 'Submitted to National Portal / DISCOM'),
            ('inspection_scheduled', 'DISCOM Site Inspection Scheduled'),
            ('approved', 'Subsidy Approved & Sanctioned'),
            ('disbursed', 'Subsidy Disbursed into Customer Account'),
            ('rejected', 'Rejected by Authority'),
            ('cancelled', 'Cancelled'),
        ],
        string='Dossier Status',
        default='draft',
        required=True,
        tracking=True,
    )

    # Document Checklist Verification
    has_electricity_bill = fields.Boolean(string='Latest Electricity Bill Attached', default=False)
    has_aadhaar_card = fields.Boolean(string='Customer Identity / Aadhaar Attached', default=False)
    has_bank_passbook = fields.Boolean(string='Cancelled Cheque / Bank Passbook Attached', default=False)
    has_roof_ownership_proof = fields.Boolean(string='Roof Ownership / Tax Receipt Attached', default=False)
    has_commissioning_certificate = fields.Boolean(string='Commissioning Certificate Attached', default=False)
    has_dcr_certificate = fields.Boolean(string='Domestic Content Requirement (DCR) Certificate', default=False)

    missing_documents = fields.Char(
        string='Missing Required Documents',
        compute='_compute_missing_documents',
        store=True,
    )

    # Financials (Purely informational - kept segregated from corporate revenue)
    estimated_subsidy_amount = fields.Float(
        string='Estimated Central Subsidy (₹)',
        help="Eligible subsidy credited directly by DBT to customer's account. NOT corporate revenue.",
    )
    approved_subsidy_amount = fields.Float(string='Actual Sanctioned Subsidy (₹)')

    submission_date = fields.Date(string='Official Portal Submission Date')
    approval_date = fields.Date(string='Sanction Date')
    disbursement_date = fields.Date(string='DBT Direct Credit Date')
    rejection_reason = fields.Text(string='Rejection / Disallowance Remarks')
    pending_actions = fields.Text(string='Next Pending Action')

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    @api.depends(
        'has_electricity_bill', 'has_aadhaar_card', 'has_bank_passbook',
        'has_roof_ownership_proof', 'has_commissioning_certificate', 'has_dcr_certificate'
    )
    def _compute_missing_documents(self):
        for rec in self:
            missing = []
            if not rec.has_electricity_bill:
                missing.append("Electricity Bill")
            if not rec.has_aadhaar_card:
                missing.append("Aadhaar Identity")
            if not rec.has_bank_passbook:
                missing.append("Bank Passbook / Cheque")
            if not rec.has_roof_ownership_proof:
                missing.append("Roof Ownership")
            if not rec.has_commissioning_certificate:
                missing.append("Commissioning Report")
            if not rec.has_dcr_certificate:
                missing.append("DCR Certificate")
            rec.missing_documents = ", ".join(missing) if missing else "All Required Documents Collected"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('solar.subsidy.tracker') or _('New')
        return super().create(vals_list)

    def action_verify_documents(self):
        for rec in self:
            if rec.missing_documents != "All Required Documents Collected":
                raise ValidationError(_("Cannot mark verified. Still missing: %s", rec.missing_documents))
        self.write({'state': 'documents_collected'})

    def action_submit_portal(self):
        for rec in self:
            if not rec.national_portal_app_number and not rec.discom_application_number:
                raise ValidationError(_("Please record either the National Portal or DISCOM Application Number."))
        self.write({
            'state': 'submitted',
            'submission_date': fields.Date.context_today(self),
        })

    def action_schedule_inspection(self):
        self.write({'state': 'inspection_scheduled'})

    def action_approve_subsidy(self):
        self.write({
            'state': 'approved',
            'approval_date': fields.Date.context_today(self),
        })

    def action_disburse_subsidy(self):
        self.write({
            'state': 'disbursed',
            'disbursement_date': fields.Date.context_today(self),
        })

    def action_reject_subsidy(self, reason):
        self.write({
            'state': 'rejected',
            'rejection_reason': reason,
        })

