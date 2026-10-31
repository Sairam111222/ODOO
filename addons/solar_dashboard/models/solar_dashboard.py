# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import api, fields, models, _


class SolarExecutiveDashboard(models.Model):
    """Executive KPI Dashboard Aggregator (Real-time computed metrics, no hardcoding)."""
    _name = 'solar.executive.dashboard'
    _description = 'Solar Executive KPI Dashboard'

    name = fields.Char(string='Dashboard View', default='Executive Summary')

    # CRM Metrics
    total_enquiries = fields.Integer(string='Total Enquiries', compute='_compute_metrics')
    qualified_leads = fields.Integer(string='Qualified Opportunities', compute='_compute_metrics')
    lead_conversion_rate = fields.Float(string='Lead Conversion Rate (%)', compute='_compute_metrics')

    # Operations & Project Velocity (~40 Installs/Month Goal)
    active_installations = fields.Integer(string='Active Installations', compute='_compute_metrics')
    completed_installations = fields.Integer(string='Completed Installations', compute='_compute_metrics')
    delayed_installations = fields.Integer(string='Weather / Site Delayed Jobs', compute='_compute_metrics')
    pending_surveys = fields.Integer(string='Surveys In Progress', compute='_compute_metrics')
    pending_survey_approvals = fields.Integer(string='Surveys Awaiting Approval', compute='_compute_metrics')
    total_capacity_installed_kw = fields.Float(string='Total Capacity Commissioned (kW)', compute='_compute_metrics')

    # Financial & Accounting Metrics
    contracted_revenue = fields.Float(string='Contracted Revenue (₹)', compute='_compute_metrics')
    invoiced_revenue = fields.Float(string='Invoiced Revenue (₹)', compute='_compute_metrics')
    cash_collected = fields.Float(string='Cash Collected (₹)', compute='_compute_metrics')
    outstanding_receivables = fields.Float(string='Outstanding Receivables (₹)', compute='_compute_metrics')
    total_project_cost = fields.Float(string='Total Execution Costs (₹)', compute='_compute_metrics')
    net_gross_profit = fields.Float(string='Net Gross Profit (₹)', compute='_compute_metrics')
    average_gross_margin_pct = fields.Float(string='Average Gross Margin (%)', compute='_compute_metrics')

    # Field Service, Warranties & Subsidies
    open_service_tickets = fields.Integer(string='Open Service Complaints', compute='_compute_metrics')
    active_warranty_claims = fields.Integer(string='Active Warranty Claims', compute='_compute_metrics')
    pending_subsidy_dossiers = fields.Integer(string='Subsidies Pending Disbursal', compute='_compute_metrics')

    def _compute_metrics(self):
        for rec in self:
            # 1. CRM
            leads = self.env['crm.lead'].sudo().search([])
            rec.total_enquiries = len(leads)
            qualified = leads.filtered(lambda l: l.type == 'opportunity')
            rec.qualified_leads = len(qualified)
            won = leads.filtered(lambda l: l.probability == 100)
            rec.lead_conversion_rate = (len(won) / len(leads) * 100.0) if leads else 0.0

            # 2. Operations
            installs = self.env['solar.installation'].sudo().search([])
            rec.active_installations = len(installs.filtered(
                lambda i: i.state in ('assigned', 'scheduled', 'in_progress', 'testing', 'awaiting_approval')
            ))
            completed = installs.filtered(lambda i: i.state in ('completed', 'commissioned'))
            rec.completed_installations = len(completed)
            rec.delayed_installations = len(installs.filtered(lambda i: bool(i.weather_delay_reason) or i.reschedule_count > 0))
            rec.total_capacity_installed_kw = sum(i.capacity_kw for i in completed)

            surveys = self.env['solar.site.survey'].sudo().search([])
            rec.pending_surveys = len(surveys.filtered(lambda s: s.state in ('draft', 'scheduled', 'in_progress')))
            rec.pending_survey_approvals = len(surveys.filtered(lambda s: s.state == 'submitted'))

            # 3. Financials
            rec.contracted_revenue = sum(i.contract_revenue for i in installs)
            rec.invoiced_revenue = sum(i.invoiced_amount for i in installs)
            rec.cash_collected = sum(i.cash_received for i in installs)
            rec.outstanding_receivables = sum(i.outstanding_receivable for i in installs)
            rec.total_project_cost = sum(i.total_cost for i in installs)
            rec.net_gross_profit = sum(i.gross_profit for i in installs)
            rec.average_gross_margin_pct = (rec.net_gross_profit / rec.invoiced_revenue * 100.0) if rec.invoiced_revenue > 0 else 0.0

            # 4. Service, Warranties, Subsidies
            tickets = self.env['solar.service.ticket'].sudo().search([])
            rec.open_service_tickets = len(tickets.filtered(lambda t: t.state not in ('closed', 'cancelled')))
            rec.active_warranty_claims = len(tickets.filtered(lambda t: t.is_warranty_claim and t.state not in ('closed', 'cancelled')))

            subsidies = self.env['solar.subsidy.tracker'].sudo().search([])
            rec.pending_subsidy_dossiers = len(subsidies.filtered(lambda s: s.state not in ('disbursed', 'rejected', 'cancelled')))


class SolarGlobalSearchWizard(models.TransientModel):
    """Global Enterprise Search across Customers, Leads, Installations, Serials, Warranties, and Tickets."""
    _name = 'solar.global.search.wizard'
    _description = 'Solar Enterprise Global Search'

    query = fields.Char(string='Search Keyword / Serial / Ref #', required=True)
    partner_ids = fields.Many2many('res.partner', string='Matching Customers', readonly=True)
    lead_ids = fields.Many2many('crm.lead', string='Matching Leads', readonly=True)
    installation_ids = fields.Many2many('solar.installation', string='Matching Installations', readonly=True)
    warranty_ids = fields.Many2many('solar.warranty', string='Matching Warranties', readonly=True)
    ticket_ids = fields.Many2many('solar.service.ticket', string='Matching Tickets', readonly=True)

    def action_execute_search(self):
        self.ensure_one()
        q = f"%{self.query.strip()}%"

        self.partner_ids = self.env['res.partner'].search([
            '|', '|', ('name', '=ilike', q), ('phone', '=ilike', q), ('email', '=ilike', q)
        ], limit=10)

        self.lead_ids = self.env['crm.lead'].search([
            '|', '|', ('name', '=ilike', q), ('phone', '=ilike', q), ('contact_name', '=ilike', q)
        ], limit=10)

        self.installation_ids = self.env['solar.installation'].search([
            '|', '|', ('name', '=ilike', q), ('partner_id.name', '=ilike', q), ('installation_line_ids.serial_number', '=ilike', q)
        ], limit=10)

        self.warranty_ids = self.env['solar.warranty'].search([
            '|', '|', ('name', '=ilike', q), ('serial_number', '=ilike', q), ('partner_id.name', '=ilike', q)
        ], limit=10)

        self.ticket_ids = self.env['solar.service.ticket'].search([
            '|', '|', ('name', '=ilike', q), ('serial_number_entered', '=ilike', q), ('partner_id.name', '=ilike', q)
        ], limit=10)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'solar.global.search.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

