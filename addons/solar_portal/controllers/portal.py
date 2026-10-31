# -*- coding: utf-8 -*-
# Part of SolarFlow 360. See LICENSE file for full copyright and licensing.

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class SolarCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'solar_installation_count' in counters:
            values['solar_installation_count'] = request.env['solar.installation'].search_count([
                ('partner_id', '=', partner.id),
                ('state', '!=', 'cancelled')
            ]) if request.env['solar.installation'].check_access_rights('read', raise_exception=False) else 0
        if 'solar_warranty_count' in counters:
            values['solar_warranty_count'] = request.env['solar.warranty'].search_count([
                ('partner_id', '=', partner.id),
                ('state', 'in', ('active', 'expiring_soon'))
            ]) if request.env['solar.warranty'].check_access_rights('read', raise_exception=False) else 0
        if 'solar_ticket_count' in counters:
            values['solar_ticket_count'] = request.env['solar.service.ticket'].search_count([
                ('partner_id', '=', partner.id)
            ]) if request.env['solar.service.ticket'].check_access_rights('read', raise_exception=False) else 0
        return values

    # 1. Customer Solar Installations View
    @http.route(['/my/solar/installations', '/my/solar/installations/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_solar_installations(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        domain = [('partner_id', '=', partner.id), ('state', '!=', 'cancelled')]
        installation_obj = request.env['solar.installation']

        count = installation_obj.search_count(domain)
        pager = portal_pager(url="/my/solar/installations", total=count, page=page, step=10)
        installations = installation_obj.search(domain, limit=10, offset=pager['offset'])

        values.update({
            'installations': installations,
            'page_name': 'solar_installations',
            'pager': pager,
            'default_url': '/my/solar/installations',
        })
        return request.render("solar_portal.portal_my_solar_installations", values)

    # 2. Customer Solar Warranties View
    @http.route(['/my/solar/warranties'], type='http', auth='user', website=True)
    def portal_my_solar_warranties(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        warranties = request.env['solar.warranty'].search([
            ('partner_id', '=', partner.id)
        ])
        values.update({
            'warranties': warranties,
            'page_name': 'solar_warranties',
        })
        return request.render("solar_portal.portal_my_solar_warranties", values)

    # 3. Customer Service Complaint Submission
    @http.route(['/my/solar/ticket/new'], type='http', auth='user', methods=['GET', 'POST'], website=True)
    def portal_solar_new_ticket(self, **post):
        partner = request.env.user.partner_id
        installations = request.env['solar.installation'].search([('partner_id', '=', partner.id)])

        if request.httprequest.method == 'POST':
            ticket_type = post.get('ticket_type', 'breakdown')
            description = post.get('description')
            installation_id = int(post.get('installation_id', 0)) if post.get('installation_id') else False
            serial = post.get('serial_number')

            if not description:
                return request.render("solar_portal.portal_solar_new_ticket", {
                    'installations': installations,
                    'error': _("Please enter a detailed description of the fault."),
                })

            ticket = request.env['solar.service.ticket'].sudo().create({
                'partner_id': partner.id,
                'installation_id': installation_id,
                'ticket_type': ticket_type,
                'serial_number_entered': serial,
                'description': description,
                'priority': '2',
            })
            return request.redirect(f'/my/solar/tickets')

        return request.render("solar_portal.portal_solar_new_ticket", {
            'installations': installations,
        })

    # 4. Customer Service Tickets Listing
    @http.route(['/my/solar/tickets'], type='http', auth='user', website=True)
    def portal_my_solar_tickets(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        tickets = request.env['solar.service.ticket'].search([('partner_id', '=', partner.id)])
        values.update({
            'tickets': tickets,
            'page_name': 'solar_tickets',
        })
        return request.render("solar_portal.portal_my_solar_tickets", values)

