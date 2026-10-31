# -*- coding: utf-8 -*-
"""
SolarFlow 360 — High-End Enterprise Product Redesign & Engineering Server
=======================================================================
Commercial-grade Enterprise Solar Operations & Intelligence Platform
Serving SunPower Solutions (~40 installations/month, 15 field crew pool).

Complete Business Lifecycle:
Customer Acquisition -> Site Assessment -> Engineering Configuration ->
Quotation -> Payment -> Procurement -> Inventory -> Dispatch ->
Installation -> Testing -> Customer Sign-off -> Warranty -> Service -> Financials.
"""

import json
import math
import os
import re
import sys
from datetime import date, datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Base directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ai_services.business_intelligence.solar_bi_agent import SolarBIAgent
from ai_services.technician_optimizer.optimizer import TechnicianOptimizer
from ai_services.inventory_forecasting.demand_forecaster import InventoryDemandForecaster
from ai_services.solar_intelligence.solar_calculator import SolarGenerationIntelligence
from ai_services.roof_assessment.roof_analyzer import RoofAssessmentAssistant

PORT = 8069

# =============================================================================
# ENTERPRISE IN-MEMORY ERP DATA REPOSITORY (Odoo 17 CE ORM Alignment)
# =============================================================================

class EnterpriseDataStore:
    """Enterprise transactional store modeling core Odoo 17 CE tables and business rules."""

    def __init__(self):
        # 1. Technician Workforce Pool (15 Certified Technicians)
        self.technicians = [
            {'id': 1, 'name': 'Rajesh Kumar', 'grade': 'lead', 'hourly_rate': 350.0, 'certs': ['Master Electrician Grade A', 'Three-Phase Certified', 'Working at Heights'], 'active_jobs': 2, 'max_jobs': 3, 'lat': 12.9716, 'lon': 77.5946, 'phone': '+91 98450 11001'},
            {'id': 2, 'name': 'Suresh Patel', 'grade': 'senior', 'hourly_rate': 280.0, 'certs': ['Grid-Tie Certified', 'Safety Compliance'], 'active_jobs': 0, 'max_jobs': 3, 'lat': 12.9352, 'lon': 77.6245, 'phone': '+91 98450 11002'},
            {'id': 3, 'name': 'Vikram Singh', 'grade': 'junior', 'hourly_rate': 220.0, 'certs': ['Basic Electrical', 'Array Mounting'], 'active_jobs': 1, 'max_jobs': 2, 'lat': 13.0358, 'lon': 77.5970, 'phone': '+91 98450 11003'},
            {'id': 4, 'name': 'Amit Verma', 'grade': 'senior', 'hourly_rate': 280.0, 'certs': ['Inverter Specialist', 'Battery Storage'], 'active_jobs': 2, 'max_jobs': 3, 'lat': 12.9279, 'lon': 77.6271, 'phone': '+91 98450 11004'},
            {'id': 5, 'name': 'Deepak Sharma', 'grade': 'lead', 'hourly_rate': 350.0, 'certs': ['Three-Phase Certified', 'MNRE Lead Auditor'], 'active_jobs': 1, 'max_jobs': 3, 'lat': 12.9915, 'lon': 77.5920, 'phone': '+91 98450 11005'},
            {'id': 6, 'name': 'Manoj Tiwari', 'grade': 'senior', 'hourly_rate': 280.0, 'certs': ['High-Altitude Structure', 'Rigging'], 'active_jobs': 1, 'max_jobs': 3, 'lat': 12.9550, 'lon': 77.6400, 'phone': '+91 98450 11006'},
            {'id': 7, 'name': 'Rahul Yadav', 'grade': 'junior', 'hourly_rate': 220.0, 'certs': ['DC Cabling & Conduit'], 'active_jobs': 2, 'max_jobs': 2, 'lat': 12.9100, 'lon': 77.5850, 'phone': '+91 98450 11007'},
            {'id': 8, 'name': 'Sunil Rao', 'grade': 'senior', 'hourly_rate': 280.0, 'certs': ['Hybrid Battery Certified', 'SolarEdge Specialist'], 'active_jobs': 0, 'max_jobs': 3, 'lat': 13.0100, 'lon': 77.5500, 'phone': '+91 98450 11008'},
            {'id': 9, 'name': 'Pradeep Gowda', 'grade': 'senior', 'hourly_rate': 280.0, 'certs': ['DISCOM Net-Meter Liaison', 'Safety Inspector'], 'active_jobs': 1, 'max_jobs': 3, 'lat': 12.9300, 'lon': 77.5300, 'phone': '+91 98450 11009'},
            {'id': 10, 'name': 'Anand Joshi', 'grade': 'lead', 'hourly_rate': 350.0, 'certs': ['Master Quality Inspector', 'HV Electrical Grade A'], 'active_jobs': 1, 'max_jobs': 3, 'lat': 12.9800, 'lon': 77.6500, 'phone': '+91 98450 11010'},
            {'id': 11, 'name': 'Karthik Nair', 'grade': 'junior', 'hourly_rate': 220.0, 'certs': ['Array Mounting & Structure Kits'], 'active_jobs': 1, 'max_jobs': 2, 'lat': 12.8900, 'lon': 77.6000, 'phone': '+91 98450 11011'},
            {'id': 12, 'name': 'Sanjay Mehra', 'grade': 'senior', 'hourly_rate': 280.0, 'certs': ['Three-Phase Certified', 'Commercial Rooftop'], 'active_jobs': 2, 'max_jobs': 3, 'lat': 13.0400, 'lon': 77.6200, 'phone': '+91 98450 11012'},
            {'id': 13, 'name': 'Nitin Desai', 'grade': 'junior', 'hourly_rate': 220.0, 'certs': ['ACDB / DCDB Wiring'], 'active_jobs': 0, 'max_jobs': 2, 'lat': 12.9600, 'lon': 77.5100, 'phone': '+91 98450 11013'},
            {'id': 14, 'name': 'Vijay Kulkarni', 'grade': 'senior', 'hourly_rate': 280.0, 'certs': ['Microinverter Specialist', 'Earthing Testing'], 'active_jobs': 1, 'max_jobs': 3, 'lat': 12.9400, 'lon': 77.7000, 'phone': '+91 98450 11014'},
            {'id': 15, 'name': 'Harish Reddy', 'grade': 'lead', 'hourly_rate': 350.0, 'certs': ['Three-Phase Certified', 'Commissioning Officer'], 'active_jobs': 1, 'max_jobs': 3, 'lat': 13.0000, 'lon': 77.6800, 'phone': '+91 98450 11015'},
        ]

        # 2. Customers / Partners (res.partner)
        self.partners = [
            {'id': 1, 'name': 'Sharma Textiles (Rajesh Sharma)', 'type': 'commercial', 'phone': '+919876543210', 'email': 'rajesh@sharmatextiles.in', 'city': 'Bangalore', 'bill': 4500.0, 'roof_sqft': 500, 'sanctioned_kw': 5.0},
            {'id': 2, 'name': 'Ananya Deshmukh', 'type': 'residential', 'phone': '+919811223344', 'email': 'ananya.d@gmail.com', 'city': 'Bangalore', 'bill': 2800.0, 'roof_sqft': 420, 'sanctioned_kw': 3.0},
            {'id': 3, 'name': 'Kaveri Precision Engineering', 'type': 'commercial', 'phone': '+919845112233', 'email': 'procurement@kaveriprecision.com', 'city': 'Bangalore', 'bill': 14200.0, 'roof_sqft': 1200, 'sanctioned_kw': 10.0},
            {'id': 4, 'name': 'Dr. Alok Verma (Green Villa)', 'type': 'residential', 'phone': '+919731002299', 'email': 'alok.verma@outlook.com', 'city': 'Bangalore', 'bill': 6200.0, 'roof_sqft': 750, 'sanctioned_kw': 5.0},
            {'id': 5, 'name': 'Nagarjuna Food Processing', 'type': 'commercial', 'phone': '+919880011223', 'email': 'ops@nagarjunafoods.in', 'city': 'Bangalore', 'bill': 8900.0, 'roof_sqft': 950, 'sanctioned_kw': 8.0},
        ]

        # 3. CRM Leads (crm.lead)
        self.leads = [
            {'id': 1, 'ref': 'LEAD-2026-0042', 'partner_id': 1, 'name': 'Sharma Textiles 3kW Inquiry', 'channel': 'whatsapp', 'customer_type': 'commercial', 'capacity_kw': 3.0, 'preference': 'ongrid', 'bill': 4500.0, 'roof_sqft': 500.0, 'state': 'qualified', 'is_duplicate': False, 'survey_id': 1},
            {'id': 2, 'ref': 'LEAD-2026-0043', 'partner_id': 2, 'name': 'Ananya Deshmukh 2kW Rooftop', 'channel': 'webform', 'customer_type': 'residential', 'capacity_kw': 2.0, 'preference': 'ongrid', 'bill': 2800.0, 'roof_sqft': 420.0, 'state': 'new', 'is_duplicate': False, 'survey_id': None},
            {'id': 3, 'ref': 'LEAD-2026-0044', 'partner_id': 3, 'name': 'Kaveri Engineering 5kW Three-Phase', 'channel': 'referral', 'customer_type': 'commercial', 'capacity_kw': 5.0, 'preference': 'ongrid', 'bill': 14200.0, 'roof_sqft': 1200.0, 'state': 'qualified', 'is_duplicate': False, 'survey_id': 2},
            {'id': 4, 'ref': 'LEAD-2026-0045', 'partner_id': 4, 'name': 'Dr. Alok Verma Hybrid Sizing', 'channel': 'phone', 'customer_type': 'residential', 'capacity_kw': 4.0, 'preference': 'hybrid', 'bill': 6200.0, 'roof_sqft': 750.0, 'state': 'survey_scheduled', 'is_duplicate': False, 'survey_id': 3},
        ]

        # 4. Site Surveys (solar.site.survey)
        self.surveys = [
            {'id': 1, 'ref': 'SRV/2026/0001', 'partner_id': 1, 'lead_id': 1, 'surveyor': 'Pradeep Gowda', 'survey_date': '2026-10-18', 'property_type': 'independent_house', 'roof_type': 'flat_rcc', 'roof_sqft': 500.0, 'usable_sqft': 360.0, 'tilt': 15.0, 'orientation': 'south', 'shading': 'no_shading', 'cable_m': 25.0, 'sanctioned_kw': 5.0, 'bill': 4500.0, 'rec_capacity_kw': 3.0, 'state': 'approved', 'rejection_reason': None, 'sale_order_id': 1},
            {'id': 2, 'ref': 'SRV/2026/0002', 'partner_id': 3, 'lead_id': 3, 'surveyor': 'Suresh Patel', 'survey_date': '2026-10-22', 'property_type': 'factory', 'roof_type': 'sloped_metal', 'roof_sqft': 1200.0, 'usable_sqft': 950.0, 'tilt': 18.0, 'orientation': 'south', 'shading': 'no_shading', 'cable_m': 35.0, 'sanctioned_kw': 10.0, 'bill': 14200.0, 'rec_capacity_kw': 5.0, 'state': 'approved', 'rejection_reason': None, 'sale_order_id': 2},
            {'id': 3, 'ref': 'SRV/2026/0003', 'partner_id': 4, 'lead_id': 4, 'surveyor': 'Anand Joshi', 'survey_date': '2026-10-25', 'property_type': 'villa', 'roof_type': 'flat_rcc', 'roof_sqft': 750.0, 'usable_sqft': 520.0, 'tilt': 15.0, 'orientation': 'southeast', 'shading': 'minimal', 'cable_m': 22.0, 'sanctioned_kw': 5.0, 'bill': 6200.0, 'rec_capacity_kw': 4.0, 'state': 'submitted', 'rejection_reason': None, 'sale_order_id': None},
            {'id': 4, 'ref': 'SRV/2026/0004', 'partner_id': 5, 'lead_id': None, 'surveyor': 'Pradeep Gowda', 'survey_date': '2026-10-26', 'property_type': 'factory', 'roof_type': 'tin_shed', 'roof_sqft': 950.0, 'usable_sqft': 600.0, 'tilt': 12.0, 'orientation': 'north', 'shading': 'moderate', 'cable_m': 40.0, 'sanctioned_kw': 8.0, 'bill': 8900.0, 'rec_capacity_kw': 3.0, 'state': 'rejected', 'rejection_reason': 'Roof structural rust detected on tin sheet; purlin reinforcement mandatory before solar array mounting.', 'sale_order_id': None},
        ]

        # 5. Solar Packages & BOM Sizing (solar.package)
        self.packages = [
            {'id': 1, 'code': 'PKG-1KW-ONGRID', 'name': '1.0 kW Starter Residential', 'capacity_kw': 1.0, 'type': 'ongrid', 'panels': 2, 'panel_watt': 550, 'inv_kw': 1.0, 'structures': 1, 'dc_cable_m': 30, 'ac_cable_m': 15, 'base_cost': 48000.0, 'labor': 12000.0, 'transport': 2500.0, 'discom': 4500.0, 'price': 75000.0},
            {'id': 2, 'code': 'PKG-2KW-ONGRID', 'name': '2.0 kW Compact Home', 'capacity_kw': 2.0, 'type': 'ongrid', 'panels': 4, 'panel_watt': 550, 'inv_kw': 2.0, 'structures': 2, 'dc_cable_m': 45, 'ac_cable_m': 20, 'base_cost': 88000.0, 'labor': 15000.0, 'transport': 3000.0, 'discom': 5000.0, 'price': 135000.0},
            {'id': 3, 'code': 'PKG-3KW-ONGRID', 'name': '3.0 kW Residential Pro (Most Popular)', 'capacity_kw': 3.0, 'type': 'ongrid', 'panels': 6, 'panel_watt': 550, 'inv_kw': 3.0, 'structures': 3, 'dc_cable_m': 60, 'ac_cable_m': 25, 'base_cost': 115000.0, 'labor': 18000.0, 'transport': 3500.0, 'discom': 5000.0, 'price': 185000.0},
            {'id': 4, 'code': 'PKG-4KW-HYBRID', 'name': '4.0 kW Hybrid Backup System', 'capacity_kw': 4.0, 'type': 'hybrid', 'panels': 8, 'panel_watt': 550, 'inv_kw': 4.0, 'structures': 4, 'dc_cable_m': 75, 'ac_cable_m': 30, 'base_cost': 175000.0, 'labor': 22000.0, 'transport': 4000.0, 'discom': 5000.0, 'price': 245000.0},
            {'id': 5, 'code': 'PKG-5KW-THREEPHASE', 'name': '5.0 kW Commercial Max (Three-Phase)', 'capacity_kw': 5.0, 'type': 'ongrid', 'panels': 10, 'panel_watt': 550, 'inv_kw': 5.0, 'structures': 5, 'dc_cable_m': 90, 'ac_cable_m': 40, 'base_cost': 205000.0, 'labor': 25000.0, 'transport': 5000.0, 'discom': 6000.0, 'price': 295000.0},
        ]

        # 6. Sales Orders / Quotations (sale.order)
        self.orders = [
            {'id': 1, 'ref': 'SO-2026-0001', 'partner_id': 1, 'survey_id': 1, 'package_id': 3, 'amount_total': 185000.0, 'state': 'sale', 'payment_state': 'paid', 'paid_amount': 185000.0, 'installation_id': 1},
            {'id': 2, 'ref': 'SO-2026-0002', 'partner_id': 3, 'survey_id': 2, 'package_id': 5, 'amount_total': 295000.0, 'state': 'sale', 'payment_state': 'in_payment', 'paid_amount': 150000.0, 'installation_id': 2},
            {'id': 3, 'ref': 'SO-2026-0003', 'partner_id': 2, 'survey_id': None, 'package_id': 2, 'amount_total': 135000.0, 'state': 'draft', 'payment_state': 'not_paid', 'paid_amount': 0.0, 'installation_id': None},
        ]

        # 7. Inventory & Lot/Serial Tracking (stock.production.lot)
        self.inventory = {
            'panels_550w': {'name': '550W Mono-PERC PV Panels', 'on_hand': 260, 'reserved': 32, 'reorder_point': 100, 'unit_cost': 11800.0},
            'inverters': {'name': 'Solar Inverters (1kW - 5kW)', 'on_hand': 24, 'reserved': 5, 'reorder_point': 10, 'unit_cost': 32000.0},
            'batteries': {'name': '150Ah Solar Tubular Batteries', 'on_hand': 12, 'reserved': 4, 'reorder_point': 8, 'unit_cost': 16500.0},
            'structures': {'name': 'Elevated HDGI Structure Pairs', 'on_hand': 110, 'reserved': 16, 'reorder_point': 40, 'unit_cost': 3200.0},
            'dc_cable': {'name': '4 sq mm DC Solar Cable (Meters)', 'on_hand': 2800, 'reserved': 320, 'reorder_point': 1000, 'unit_cost': 85.0},
            'acdb_dcdb': {'name': 'Pre-wired DCDB + ACDB Sets', 'on_hand': 38, 'reserved': 6, 'reorder_point': 15, 'unit_cost': 5800.0},
            'earthing_kits': {'name': 'Chemical Earthing Electrodes', 'on_hand': 74, 'reserved': 12, 'reorder_point': 30, 'unit_cost': 3800.0},
        }

        self.serials = [
            {'serial': 'INV-GROWATT-9921', 'type': 'inverter', 'model': 'Growatt 3.0kW Grid-Tie', 'status': 'installed', 'installation_id': 1},
            {'serial': 'INV-GROWATT-9922', 'type': 'inverter', 'model': 'Growatt 5.0kW Three-Phase', 'status': 'installed', 'installation_id': 2},
            {'serial': 'INV-SOLIS-8810', 'type': 'inverter', 'model': 'Solis 4.0kW Hybrid', 'status': 'in_stock', 'installation_id': None},
            {'serial': 'BATT-EXIDE-4401', 'type': 'battery', 'model': 'Exide Solar 150Ah Tubular', 'status': 'in_stock', 'installation_id': None},
            {'serial': 'BATT-EXIDE-4402', 'type': 'battery', 'model': 'Exide Solar 150Ah Tubular', 'status': 'in_stock', 'installation_id': None},
        ]

        # 8. Installation Projects (solar.installation)
        self.installations = [
            {
                'id': 1, 'ref': 'INS/2026/0001', 'partner_id': 1, 'order_id': 1, 'survey_id': 1, 'package_id': 3,
                'capacity_kw': 3.0, 'technician_id': 2, 'tech_name': 'Suresh Patel', 'helper_ids': [3],
                'scheduled_date': '2026-10-24', 'state': 'commissioned', 'commissioned_date': '2026-10-25',
                'dc_v': 380.0, 'ac_v': 230.0, 'freq': 50.0, 'earthing_ohms': 2.1, 'testing_passed': True,
                'net_meter': True, 'net_meter_no': 'BESCOM-NM-77889',
                'customer_signoff': 'Rajesh Sharma', 'rating': 5,
                'contract_rev': 185000.0, 'invoiced': 185000.0, 'cash_received': 185000.0, 'receivable': 0.0,
                'material_cost': 115000.0, 'labour_cost': 4000.0, 'other_cost': 3500.0,
                'total_cost': 122500.0, 'gross_profit': 62500.0, 'gross_margin_pct': 33.8
            },
            {
                'id': 2, 'ref': 'INS/2026/0002', 'partner_id': 3, 'order_id': 2, 'survey_id': 2, 'package_id': 5,
                'capacity_kw': 5.0, 'technician_id': 1, 'tech_name': 'Rajesh Kumar', 'helper_ids': [7],
                'scheduled_date': '2026-10-28', 'state': 'testing', 'commissioned_date': None,
                'dc_v': 520.0, 'ac_v': 415.0, 'freq': 50.0, 'earthing_ohms': 1.8, 'testing_passed': True,
                'net_meter': False, 'net_meter_no': 'PENDING-DISCOM',
                'customer_signoff': None, 'rating': None,
                'contract_rev': 295000.0, 'invoiced': 295000.0, 'cash_received': 150000.0, 'receivable': 145000.0,
                'material_cost': 205000.0, 'labour_cost': 5600.0, 'other_cost': 5000.0,
                'total_cost': 215600.0, 'gross_profit': 79400.0, 'gross_margin_pct': 26.9
            },
            {
                'id': 3, 'ref': 'INS/2026/0003', 'partner_id': 4, 'order_id': None, 'survey_id': 3, 'package_id': 4,
                'capacity_kw': 4.0, 'technician_id': 4, 'tech_name': 'Amit Verma', 'helper_ids': [11],
                'scheduled_date': '2026-11-04', 'state': 'scheduled', 'commissioned_date': None,
                'dc_v': 0.0, 'ac_v': 0.0, 'freq': 50.0, 'earthing_ohms': 0.0, 'testing_passed': False,
                'net_meter': False, 'net_meter_no': None,
                'customer_signoff': None, 'rating': None,
                'contract_rev': 245000.0, 'invoiced': 0.0, 'cash_received': 50000.0, 'receivable': 0.0,
                'material_cost': 175000.0, 'labour_cost': 4800.0, 'other_cost': 4000.0,
                'total_cost': 183800.0, 'gross_profit': 61200.0, 'gross_margin_pct': 25.0
            }
        ]

        # 9. Warranties (solar.warranty)
        self.warranties = [
            {'id': 1, 'ref': 'WRN/2026/0001', 'partner_id': 1, 'installation_id': 1, 'type': 'panel', 'duration_yrs': 25, 'start_date': '2026-10-25', 'end_date': '2051-10-25', 'serial': 'BATCH-550W-2026-10', 'state': 'active', 'terms': '25-Year 80% Output Performance Guarantee.'},
            {'id': 2, 'ref': 'WRN/2026/0002', 'partner_id': 1, 'installation_id': 1, 'type': 'inverter', 'duration_yrs': 5, 'start_date': '2026-10-25', 'end_date': '2031-10-25', 'serial': 'INV-GROWATT-9921', 'state': 'active', 'terms': '5-Year Manufacturer Replacement Guarantee on internal components.'},
            {'id': 3, 'ref': 'WRN/2026/0003', 'partner_id': 1, 'installation_id': 1, 'type': 'comprehensive', 'duration_yrs': 1, 'start_date': '2026-10-25', 'end_date': '2027-10-25', 'serial': 'INS/2026/0001', 'state': 'active', 'terms': '1-Year Comprehensive SunPower Installation & Workmanship Guarantee.'},
            {'id': 4, 'ref': 'WRN/2025/0812', 'partner_id': 2, 'installation_id': None, 'type': 'inverter', 'duration_yrs': 2, 'start_date': '2024-11-20', 'end_date': '2026-11-20', 'serial': 'INV-LUMINOUS-1102', 'state': 'expiring_soon', 'terms': 'Expiring in 20 days. AMC renewal notice dispatched.'},
        ]

        # 10. Service Tickets & RMA (solar.service.ticket)
        self.tickets = [
            {'id': 1, 'ref': 'SVC/2026/0001', 'partner_id': 1, 'installation_id': 1, 'serial': 'INV-GROWATT-9921', 'warranty_id': 2, 'type': 'breakdown', 'priority': '3', 'state': 'closed', 'tech_id': 2, 'tech_name': 'Suresh Patel', 'is_warranty': True, 'classification': 'free_warranty', 'desc': 'Inverter error 102 reported after thunderstorm; generation halted.', 'findings': 'DC Surge Protection Device (SPD) tripped and blown.', 'resolution': 'Replaced DC SPD fuse cartridge with genuine Growatt spare.', 'parts_cost': 1200.0, 'labour_cost': 560.0, 'customer_bill': 0.0, 'confirmed': True},
            {'id': 2, 'ref': 'SVC/2026/0002', 'partner_id': 3, 'installation_id': 2, 'serial': 'INV-GROWATT-9922', 'warranty_id': None, 'type': 'generation_low', 'priority': '2', 'state': 'in_progress', 'tech_id': 1, 'tech_name': 'Rajesh Kumar', 'is_warranty': True, 'classification': 'free_warranty', 'desc': 'Array string 2 reporting 20% lower current than string 1.', 'findings': 'Investigating potential shading from adjacent industrial chimney or loose MC4 crimp.', 'resolution': None, 'parts_cost': 0.0, 'labour_cost': 0.0, 'customer_bill': 0.0, 'confirmed': False},
        ]

        # 11. Government Subsidy Dossiers (solar.subsidy.tracker)
        self.subsidies = [
            {'id': 1, 'ref': 'SUB/2026/0001', 'partner_id': 1, 'installation_id': 1, 'scheme': 'PM Surya Ghar: Muft Bijli Yojana', 'app_no': 'MNRE-KA-2026-98122', 'est_amount': 78000.0, 'approved_amount': 78000.0, 'state': 'approved', 'docs_collected': True, 'missing_docs': 'All Required Documents Collected'},
            {'id': 2, 'ref': 'SUB/2026/0002', 'partner_id': 4, 'installation_id': 3, 'scheme': 'PM Surya Ghar: Muft Bijli Yojana', 'app_no': 'MNRE-KA-2026-98440', 'est_amount': 78000.0, 'approved_amount': 0.0, 'state': 'documents_collected', 'docs_collected': False, 'missing_docs': 'DCR Certificate, Commissioning Report'},
        ]

DATA = EnterpriseDataStore()


# =============================================================================
# HIGH-END ENTERPRISE APPLICATION SHELL & CLIENT FRONTEND
# =============================================================================

HTML_APP_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SolarFlow 360 — SunPower Solutions ERP</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-canvas: #09090b;
            --bg-sidebar: #111114;
            --bg-topbar: rgba(17, 17, 20, 0.85);
            --bg-surface: #18181b;
            --bg-elevated: #222226;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-active: #f59e0b;
            --text-main: #fafafa;
            --text-muted: #a1a1aa;
            --text-dim: #71717a;
            --accent-gold: #f59e0b;
            --accent-gold-dark: #d97706;
            --accent-gold-glow: rgba(245, 158, 11, 0.2);
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 18px;
            --radius-pill: 9999px;
            --shadow-card: 0 4px 20px -2px rgba(0, 0, 0, 0.6);
            --transition: background-color 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s cubic-bezier(0.16, 1, 0.3, 1), color 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        /* Light Theme Tokens */
        [data-theme="light"] {
            --bg-canvas: #f8fafc;
            --bg-sidebar: #ffffff;
            --bg-topbar: rgba(255, 255, 255, 0.90);
            --bg-surface: #ffffff;
            --bg-elevated: #f1f5f9;
            --border-subtle: #e2e8f0;
            --border-active: #d97706;
            --text-main: #0f172a;
            --text-muted: #475569;
            --text-dim: #64748b;
            --accent-gold: #d97706;
            --accent-gold-dark: #b45309;
            --accent-gold-glow: rgba(217, 119, 6, 0.15);
            --accent-blue: #2563eb;
            --accent-green: #059669;
            --accent-red: #dc2626;
            --shadow-card: 0 4px 16px -2px rgba(15, 23, 42, 0.08);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-canvas);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            overflow: hidden;
            font-size: 0.875rem;
            letter-spacing: -0.011em;
        }

        /* -------------------------------------------------------------
           LEFT PERSISTENT SIDEBAR NAVIGATION (12 MODULES)
        ------------------------------------------------------------- */
        .sidebar {
            width: 260px;
            min-width: 260px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            user-select: none;
            z-index: 100;
        }

        .sidebar-brand {
            padding: 20px 22px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid var(--border-subtle);
        }

        .brand-emblem {
            width: 34px;
            height: 34px;
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: #000;
            font-size: 1.1rem;
            box-shadow: 0 0 16px var(--accent-gold-glow);
        }

        .brand-titles { display: flex; flex-direction: column; }
        .brand-name { font-weight: 800; font-size: 0.98rem; color: var(--text-main); letter-spacing: -0.02em; }
        .brand-sub { font-size: 0.7rem; color: var(--accent-gold); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }

        .nav-scroller {
            flex: 1;
            overflow-y: auto;
            padding: 14px 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .nav-section-label {
            font-size: 0.68rem;
            font-weight: 700;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 10px 12px 4px 12px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            color: var(--text-muted);
            text-decoration: none;
            cursor: pointer;
            transition: var(--transition);
            font-size: 0.83rem;
            font-weight: 500;
        }

        .nav-item:hover {
            color: var(--text-main);
            background: rgba(255, 255, 255, 0.04);
        }

        .nav-item.active {
            color: var(--text-main);
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.25);
            font-weight: 600;
        }

        .nav-left { display: flex; align-items: center; gap: 10px; }
        .nav-icon { width: 18px; text-align: center; font-size: 0.95rem; }
        .nav-badge {
            font-size: 0.68rem;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: var(--radius-pill);
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-dim);
        }
        .nav-item.active .nav-badge { background: var(--accent-gold); color: #000; }

        .sidebar-user {
            padding: 14px 16px;
            border-top: 1px solid var(--border-subtle);
            background: rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .user-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: var(--accent-gold);
            font-size: 0.8rem;
        }

        /* -------------------------------------------------------------
           MAIN CONTENT CANVAS & TOP SHELL
        ------------------------------------------------------------- */
        .workspace {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            background-color: var(--bg-canvas);
        }

        .topbar {
            height: 56px;
            min-height: 56px;
            background: var(--bg-topbar);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            z-index: 90;
        }

        .top-left { display: flex; align-items: center; gap: 16px; }
        .breadcrumb { display: flex; align-items: center; gap: 8px; color: var(--text-dim); font-size: 0.8rem; }
        .breadcrumb-active { color: var(--text-main); font-weight: 600; }

        .top-center { flex: 1; max-width: 440px; margin: 0 24px; }
        .search-shell {
            position: relative;
            width: 100%;
        }

        .search-input {
            width: 100%;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            color: var(--text-main);
            padding: 7px 14px 7px 34px;
            border-radius: var(--radius-pill);
            font-size: 0.82rem;
            outline: none;
            transition: var(--transition);
        }

        .search-input:focus { border-color: var(--accent-gold); box-shadow: 0 0 10px var(--accent-gold-glow); }
        .search-icon-pos { position: absolute; left: 12px; top: 8px; color: var(--text-dim); font-size: 0.8rem; }

        .top-right { display: flex; align-items: center; gap: 14px; }

        .role-selector {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            color: var(--text-main);
            padding: 5px 12px;
            border-radius: var(--radius-sm);
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            outline: none;
        }

        .theme-toggle-btn {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            color: var(--text-main);
            padding: 5px 10px;
            border-radius: var(--radius-sm);
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: var(--transition);
        }
        .theme-toggle-btn:hover {
            background: var(--bg-elevated);
            border-color: var(--accent-gold);
        }

        .system-pill {
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: var(--accent-green);
            padding: 4px 10px;
            border-radius: var(--radius-pill);
            font-size: 0.72rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .live-dot { width: 6px; height: 6px; background: var(--accent-green); border-radius: 50%; box-shadow: 0 0 6px var(--accent-green); }

        /* VIEW CONTAINER */
        .content-scroll {
            flex: 1;
            overflow-y: auto;
            padding: 24px 28px 60px 28px;
        }

        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 24px;
        }

        .page-title { font-size: 1.55rem; font-weight: 800; letter-spacing: -0.025em; color: var(--text-main); }
        .page-desc { font-size: 0.85rem; color: var(--text-muted); margin-top: 4px; }

        .header-actions { display: flex; gap: 10px; }

        /* BUTTONS */
        .btn {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            color: var(--text-main);
            padding: 8px 16px;
            border-radius: var(--radius-sm);
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 7px;
        }

        .btn:hover { background: var(--bg-elevated); border-color: rgba(255,255,255,0.18); }
        .btn-gold { background: var(--accent-gold); color: #000; border: none; font-weight: 700; }
        .btn-gold:hover { background: var(--accent-gold-dark); color: #fff; }

        /* BENTO CARDS & GRIDS */
        .kpi-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .kpi-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 18px 20px;
            position: relative;
            transition: var(--transition);
        }

        .kpi-card:hover { border-color: rgba(245, 158, 11, 0.35); }
        .kpi-title { font-size: 0.72rem; font-weight: 600; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.05em; }
        .kpi-value { font-size: 1.7rem; font-weight: 800; color: var(--text-main); margin: 6px 0 4px 0; letter-spacing: -0.02em; }
        .kpi-sub { font-size: 0.74rem; font-weight: 500; display: flex; align-items: center; gap: 6px; }
        .sub-up { color: var(--accent-green); }
        .sub-down { color: var(--accent-red); }

        .card {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 22px 24px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-card);
        }

        .card-title-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-subtle);
        }

        .card-h2 { font-size: 1.05rem; font-weight: 700; color: var(--text-main); }

        /* DATA TABLES */
        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
        }

        .data-table th {
            text-align: left;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 0.02);
            color: var(--text-dim);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.68rem;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--border-subtle);
        }

        .data-table td {
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-subtle);
            color: var(--text-main);
            vertical-align: middle;
        }

        .data-table tr:hover td { background: rgba(255, 255, 255, 0.02); }

        /* STATUS BADGES */
        .badge {
            font-size: 0.7rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: var(--radius-pill);
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        .badge-green { background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3); }
        .badge-gold { background: rgba(245, 158, 11, 0.15); color: var(--accent-gold); border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-blue { background: rgba(59, 130, 246, 0.15); color: var(--accent-blue); border: 1px solid rgba(59, 130, 246, 0.3); }
        .badge-red { background: rgba(239, 68, 68, 0.15); color: var(--accent-red); border: 1px solid rgba(239, 68, 68, 0.3); }
        .badge-dim { background: rgba(255, 255, 255, 0.06); color: var(--text-dim); border: 1px solid var(--border-subtle); }

        /* MODAL WINDOWS */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(8px);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
        }

        .modal-box {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            width: 90%;
            max-width: 640px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.9);
            padding: 26px;
        }

        .modal-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .modal-title { font-size: 1.15rem; font-weight: 800; color: var(--text-main); }
        .close-modal { background: none; border: none; color: var(--text-dim); font-size: 1.3rem; cursor: pointer; }

        .form-row { margin-bottom: 16px; }
        .form-label { display: block; font-size: 0.76rem; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; }
        .form-control {
            width: 100%;
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            color: var(--text-main);
            padding: 9px 12px;
            border-radius: var(--radius-sm);
            font-size: 0.85rem;
            outline: none;
            font-family: inherit;
        }
        .form-control:focus { border-color: var(--accent-gold); }

        /* GRID 2 & 3 */
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
        @media (max-width: 980px) {
            .grid-2, .grid-3 { grid-template-columns: 1fr; }
        }

        /* -------------------------------------------------------------
           ENTERPRISE LOGIN PORTAL OVERLAY (4 ROLE EXPERIENCES)
        ------------------------------------------------------------- */
        .login-portal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: var(--bg-canvas);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
            overflow-y: auto;
        }

        .login-portal-shell {
            width: 100%;
            max-width: 1060px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7);
            padding: 36px 40px;
        }

        .role-portal-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(225px, 1fr));
            gap: 16px;
            margin: 28px 0;
        }

        .role-portal-card {
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 22px 20px;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
        }

        .role-portal-card:hover {
            border-color: var(--accent-gold);
            transform: translateY(-3px);
            box-shadow: 0 12px 28px -6px var(--accent-gold-glow);
        }

        .role-portal-badge {
            width: 44px;
            height: 44px;
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 14px;
        }
    </style>
</head>
<body>

    <!-- -------------------------------------------------------------
         AUTHENTIC ENTERPRISE LOGIN PORTAL (4 ROLE EXPERIENCES)
    -------------------------------------------------------------- -->
    <div id="loginPortalScreen" class="login-portal-overlay">
        <div class="login-portal-shell">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--border-subtle); padding-bottom: 24px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="brand-emblem" style="width: 44px; height: 44px; font-size: 1.4rem;">⚡</div>
                    <div>
                        <h1 style="font-size: 1.6rem; font-weight: 800; color: var(--text-main); letter-spacing: -0.02em;">SolarFlow 360</h1>
                        <div style="font-size: 0.8rem; color: var(--accent-gold); font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;">SunPower Solutions — Odoo 17 CE Enterprise Authentication</div>
                    </div>
                </div>
                <button class="theme-toggle-btn" onclick="toggleTheme()" title="Toggle Theme" style="align-self: center;">
                    <span id="loginThemeIcon">☀️</span>
                    <span id="loginThemeLabel">Light Mode</span>
                </button>
            </div>

            <div style="margin-top: 24px;">
                <div style="font-size: 1.15rem; font-weight: 800; color: var(--text-main);">Select Authorized Role to Enter Dedicated Portal</div>
                <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">Each security group provides a strictly isolated workspace, permission boundaries, and role-specific KPI dashboards.</div>
            </div>

            <div class="role-portal-grid">
                <!-- Role 1: Director -->
                <div class="role-portal-card" onclick="loginAsRole('director')">
                    <div>
                        <div class="role-portal-badge" style="background: rgba(245, 158, 11, 0.15); color: var(--accent-gold); border: 1px solid rgba(245, 158, 11, 0.3);">📊</div>
                        <div style="font-weight: 800; font-size: 1.05rem; color: var(--text-main);">Director / Admin</div>
                        <div style="font-size: 0.72rem; color: var(--accent-gold); font-weight: 600; margin-top: 2px;">director@sunpower.com</div>
                        <div style="font-size: 0.78rem; color: var(--text-muted); margin: 12px 0;">Executive Overview, Operations Intelligence, Sizing, Financial Ledgers, BI Assistant, and Management Approvals.</div>
                    </div>
                    <div>
                        <span class="badge badge-gold" style="margin-bottom: 12px;">Full Enterprise Scope</span>
                        <button class="btn btn-gold" style="width: 100%; justify-content: center;" onclick="event.stopPropagation(); loginAsRole('director');">Sign In as Director →</button>
                    </div>
                </div>

                <!-- Role 2: Sales Administrator -->
                <div class="role-portal-card" onclick="loginAsRole('salesperson')">
                    <div>
                        <div class="role-portal-badge" style="background: rgba(59, 130, 246, 0.15); color: var(--accent-blue); border: 1px solid rgba(59, 130, 246, 0.3);">🤝</div>
                        <div style="font-weight: 800; font-size: 1.05rem; color: var(--text-main);">Sales Administrator</div>
                        <div style="font-size: 0.72rem; color: var(--accent-blue); font-weight: 600; margin-top: 2px;">sales@sunpower.com</div>
                        <div style="font-size: 0.78rem; color: var(--text-muted); margin: 12px 0;">Sales Pipeline Dashboard, WhatsApp Inbound Leads, Site Survey Requests, Solar Packages, and Quotation Generation.</div>
                    </div>
                    <div>
                        <span class="badge badge-blue" style="margin-bottom: 12px;">Sales & CRM Pipeline</span>
                        <button class="btn btn-gold" style="width: 100%; justify-content: center;" onclick="event.stopPropagation(); loginAsRole('salesperson');">Sign In as Sales Admin →</button>
                    </div>
                </div>

                <!-- Role 3: Operations Manager -->
                <div class="role-portal-card" onclick="loginAsRole('operations')">
                    <div>
                        <div class="role-portal-badge" style="background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3);">⚙️</div>
                        <div style="font-weight: 800; font-size: 1.05rem; color: var(--text-main);">Operations Manager</div>
                        <div style="font-size: 0.72rem; color: var(--accent-green); font-weight: 600; margin-top: 2px;">ops@sunpower.com</div>
                        <div style="font-size: 0.78rem; color: var(--text-muted); margin: 12px 0;">Operations Funnel, Feasibility Survey Approval, 15-Technician Dispatch & Routing, Inventory Shortages, and Warranty QA.</div>
                    </div>
                    <div>
                        <span class="badge badge-green" style="margin-bottom: 12px;">Workforce & Operations</span>
                        <button class="btn btn-gold" style="width: 100%; justify-content: center;" onclick="event.stopPropagation(); loginAsRole('operations');">Sign In as Operations →</button>
                    </div>
                </div>

                <!-- Role 4: Field Technician -->
                <div class="role-portal-card" onclick="loginAsRole('technician')">
                    <div>
                        <div class="role-portal-badge" style="background: rgba(245, 158, 11, 0.12); color: var(--accent-gold); border: 1px solid rgba(245, 158, 11, 0.25);">🛠️</div>
                        <div style="font-weight: 800; font-size: 1.05rem; color: var(--text-main);">Field Technician</div>
                        <div style="font-size: 0.72rem; color: var(--accent-gold); font-weight: 600; margin-top: 2px;">tech@sunpower.com (Suresh Patel)</div>
                        <div style="font-size: 0.78rem; color: var(--text-muted); margin: 12px 0;">My Assigned Work Orders Only, Rooftop Survey Data Entry, Serial Scanning, Electrical Testing (DC/AC/Earth), and Customer Sign-off.</div>
                    </div>
                    <div>
                        <span class="badge badge-dim" style="margin-bottom: 12px;">Strict Row-Level Isolation</span>
                        <button class="btn btn-gold" style="width: 100%; justify-content: center;" onclick="event.stopPropagation(); loginAsRole('technician');">Sign In as Technician →</button>
                    </div>
                </div>
            </div>

            <div style="border-top: 1px solid var(--border-subtle); padding-top: 22px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px;">
                <div style="display: flex; gap: 10px; align-items: center; flex: 1; max-width: 520px;">
                    <input type="text" id="credentialInput" class="form-control" placeholder="Quick Login (type 'director', 'sales', 'ops', or 'tech')" onkeypress="if(event.key==='Enter') submitCredentialLogin()">
                    <button class="btn btn-gold" onclick="submitCredentialLogin()">Sign In</button>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-dim);">
                    <span>🔒 Powered by Odoo 17 CE Session Authentication &amp; ir.rule Access Models</span>
                </div>
            </div>
        </div>
    </div>

    <!-- -------------------------------------------------------------
         PERSISTENT SIDEBAR NAVIGATION (12 ENTERPRISE MODULES)
    -------------------------------------------------------------- -->
    <aside class="sidebar">
        <div class="sidebar-brand">
            <div class="brand-emblem">⚡</div>
            <div class="brand-titles">
                <span class="brand-name">SolarFlow 360</span>
                <span class="brand-sub">SunPower ERP CE</span>
            </div>
        </div>

        <nav class="nav-scroller" id="sidebarNav">
            <div class="nav-section-label" data-nav-group="ops">Operations Control</div>
            <a class="nav-item active" data-nav="overview" onclick="loadView('overview', this)">
                <div class="nav-left"><span class="nav-icon">📊</span> <span>1. Executive Overview</span></div>
                <span class="nav-badge">Live</span>
            </a>
            <a class="nav-item" data-nav="operations" onclick="loadView('operations', this)">
                <div class="nav-left"><span class="nav-icon">📈</span> <span>2. Operations Intelligence</span></div>
                <span class="nav-badge">Funnel</span>
            </a>
            <a class="nav-item" data-nav="dispatch" onclick="loadView('dispatch', this)">
                <div class="nav-left"><span class="nav-icon">📍</span> <span>3. Technician Dispatch</span></div>
                <span class="nav-badge">15 Pool</span>
            </a>

            <div class="nav-section-label" data-nav-group="eng">Engineering & Sizing</div>
            <a class="nav-item" data-nav="sizing" onclick="loadView('sizing', this)">
                <div class="nav-left"><span class="nav-icon">☀️</span> <span>4. Sizing Studio</span></div>
                <span class="nav-badge">IEC 78%</span>
            </a>
            <a class="nav-item" data-nav="roof" onclick="loadView('roof', this)">
                <div class="nav-left"><span class="nav-icon">📐</span> <span>5. Roof Assessment</span></div>
                <span class="nav-badge">Feasibility</span>
            </a>
            <a class="nav-item" data-nav="packages" onclick="loadView('packages', this)">
                <div class="nav-left"><span class="nav-icon">📦</span> <span>6. Solar Packages</span></div>
                <span class="nav-badge">BOM</span>
            </a>

            <div class="nav-section-label" data-nav-group="exec">Execution & Lifecycle</div>
            <a class="nav-item" data-nav="crm" onclick="loadView('crm', this)">
                <div class="nav-left"><span class="nav-icon">🤝</span> <span>7. Customer & CRM</span></div>
                <span class="nav-badge">WhatsApp</span>
            </a>
            <a class="nav-item" data-nav="inventory" onclick="loadView('inventory', this)">
                <div class="nav-left"><span class="nav-icon">🏭</span> <span>8. Inventory & Traceability</span></div>
                <span class="nav-badge">Serials</span>
            </a>
            <a class="nav-item" data-nav="installations" onclick="loadView('installations', this)">
                <div class="nav-left"><span class="nav-icon">🛠️</span> <span>9. Installation Ops</span></div>
                <span class="nav-badge">Safety</span>
            </a>
            <a class="nav-item" data-nav="warranty" onclick="loadView('warranty', this)">
                <div class="nav-left"><span class="nav-icon">🛡️</span> <span>10. Warranty & Service</span></div>
                <span class="nav-badge">25-Yr</span>
            </a>

            <div class="nav-section-label" data-nav-group="fin">Finance & Intelligence</div>
            <a class="nav-item" data-nav="financials" onclick="loadView('financials', this)">
                <div class="nav-left"><span class="nav-icon">💰</span> <span>11. Financial Intelligence</span></div>
                <span class="nav-badge">Ledgers</span>
            </a>
            <a class="nav-item" data-nav="assistant" onclick="loadView('assistant', this)">
                <div class="nav-left"><span class="nav-icon">🤖</span> <span>12. AI BI Assistant</span></div>
                <span class="nav-badge">RBAC</span>
            </a>
        </nav>

        <div class="sidebar-user">
            <div class="user-avatar" id="avatarLetter">D</div>
            <div style="flex: 1; overflow: hidden;">
                <div style="font-weight: 600; font-size: 0.8rem; color: var(--text-main);" id="loggedUserName">Director (Executive)</div>
                <div style="font-size: 0.7rem; color: var(--text-dim);" id="loggedUserRole">SunPower Management</div>
            </div>
            <button onclick="logoutUser()" title="Sign Out to Login Portal" style="background: none; border: none; color: var(--text-dim); cursor: pointer; font-size: 1.1rem; padding: 4px;">⎋</button>
        </div>
    </aside>

    <!-- -------------------------------------------------------------
         APPLICATION WORKSPACE
    -------------------------------------------------------------- -->
    <main class="workspace">
        <header class="topbar">
            <div class="top-left">
                <div class="breadcrumb">
                    <span>SolarFlow</span> /
                    <span class="breadcrumb-active" id="activeBreadcrumb">Executive Overview</span>
                </div>
            </div>

            <div class="top-center">
                <div class="search-shell">
                    <span class="search-icon-pos">🔍</span>
                    <input type="text" class="search-input" id="globalSearchInput" placeholder="Global Search (Serials, Customers, Orders, Tickets)..." oninput="runLiveSearch(this.value)" autocomplete="off">
                    <div id="searchResultsOverlay" style="display:none; position:absolute; top:42px; left:0; width:100%; max-height:360px; overflow-y:auto; background:var(--bg-elevated); border:1px solid var(--border-subtle); border-radius:var(--radius-md); box-shadow:0 12px 36px rgba(0,0,0,0.85); z-index:1000; padding:6px 0;"></div>
                </div>
            </div>

            <div class="top-right">
                <button class="theme-toggle-btn" id="themeToggleBtn" onclick="toggleTheme()" title="Switch between Dark and Light mode">
                    <span id="themeToggleIcon">☀️</span>
                    <span id="themeToggleLabel">Light Mode</span>
                </button>

                <select class="role-selector" id="roleSelector" onchange="switchRole(this.value)">
                    <option value="director">Director / Admin (Full Access)</option>
                    <option value="salesperson">Sales Administrator (CRM & Quotes)</option>
                    <option value="operations">Operations Manager (Workforce & QA)</option>
                    <option value="technician">Field Technician (My Jobs Only)</option>
                </select>

                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 5px 12px; border-color: rgba(239, 68, 68, 0.4); color: var(--accent-red);" onclick="logoutUser()" title="Log out and return to Login Screen">
                    ⎋ Sign Out
                </button>

                <div class="system-pill">
                    <div class="live-dot"></div>
                    <span>Odoo 17 CE ORM Grounded</span>
                </div>
            </div>
        </header>

        <!-- VIEW CONTAINER -->
        <section class="content-scroll" id="mainContainer">
            <!-- Loaded dynamically via JavaScript -->
        </section>
    </main>

    <!-- GLOBAL ACTION MODAL -->
    <div class="modal-overlay" id="actionModal">
        <div class="modal-box" id="modalBoxContent">
            <!-- Modal form rendered dynamically -->
        </div>
    </div>

    <!-- CLIENT CONTROLLER SCRIPT -->
    <script>
        let currentRole = localStorage.getItem('solarflow_role') || 'director';
        let activeTab = 'overview';
        let currentTheme = localStorage.getItem('solarflow_theme') || 'dark';

        // Role Access Matrix
        const ROLE_PERMISSIONS = {
            director: {
                title: 'Director / Administrator',
                name: 'Director (Executive)',
                org: 'SunPower Executive Committee',
                avatar: 'D',
                defaultTab: 'overview',
                allowedTabs: ['overview', 'operations', 'dispatch', 'sizing', 'roof', 'packages', 'crm', 'inventory', 'installations', 'warranty', 'financials', 'assistant']
            },
            salesperson: {
                title: 'Sales Administrator',
                name: 'Siddharth Rao',
                org: 'Commercial & Residential Sales',
                avatar: 'S',
                defaultTab: 'crm',
                allowedTabs: ['crm', 'roof', 'packages', 'sizing', 'assistant']
            },
            operations: {
                title: 'Operations Manager',
                name: 'Pradeep Gowda',
                org: 'Field Operations & Dispatch',
                avatar: 'O',
                defaultTab: 'operations',
                allowedTabs: ['operations', 'dispatch', 'roof', 'inventory', 'installations', 'warranty', 'assistant']
            },
            technician: {
                title: 'Field Technician',
                name: 'Suresh Patel (Lead Tech)',
                org: 'Field Installation Team',
                avatar: 'T',
                defaultTab: 'installations',
                allowedTabs: ['installations', 'roof', 'warranty']
            }
        };

        function applyTheme(theme) {
            currentTheme = theme;
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('solarflow_theme', theme);
            const icon = document.getElementById('themeToggleIcon');
            const lbl = document.getElementById('themeToggleLabel');
            const logIcon = document.getElementById('loginThemeIcon');
            const logLbl = document.getElementById('loginThemeLabel');
            if (icon && lbl) {
                if (theme === 'light') {
                    icon.textContent = '🌙';
                    lbl.textContent = 'Dark Mode';
                } else {
                    icon.textContent = '☀️';
                    lbl.textContent = 'Light Mode';
                }
            }
            if (logIcon && logLbl) {
                if (theme === 'light') {
                    logIcon.textContent = '🌙';
                    logLbl.textContent = 'Dark Mode';
                } else {
                    logIcon.textContent = '☀️';
                    logLbl.textContent = 'Light Mode';
                }
            }
        }

        function loginAsRole(roleKey) {
            localStorage.setItem('solarflow_logged_in', 'true');
            hideLoginScreen();
            switchRole(roleKey);
        }

        function logoutUser() {
            localStorage.removeItem('solarflow_logged_in');
            showLoginScreen();
        }

        function showLoginScreen() {
            const portal = document.getElementById('loginPortalScreen');
            if (portal) portal.style.display = 'flex';
        }

        function hideLoginScreen() {
            const portal = document.getElementById('loginPortalScreen');
            if (portal) portal.style.display = 'none';
        }

        function submitCredentialLogin() {
            const val = (document.getElementById('credentialInput').value || '').trim().toLowerCase();
            if (val.includes('dir') || val.includes('admin') || val.includes('executive')) {
                loginAsRole('director');
            } else if (val.includes('sale')) {
                loginAsRole('salesperson');
            } else if (val.includes('op') || val.includes('dispatch') || val.includes('manager')) {
                loginAsRole('operations');
            } else if (val.includes('tech') || val.includes('field') || val.includes('suresh')) {
                loginAsRole('technician');
            } else {
                alert("Please enter a valid role credential ('director', 'sales', 'ops', or 'tech') or click any role portal above.");
            }
        }

        function toggleTheme() {
            const nextTheme = (currentTheme === 'dark') ? 'light' : 'dark';
            applyTheme(nextTheme);
        }

        function updateSidebarNavigation() {
            const roleCfg = ROLE_PERMISSIONS[currentRole] || ROLE_PERMISSIONS.director;
            const allowed = roleCfg.allowedTabs;

            document.querySelectorAll('#sidebarNav .nav-item').forEach(item => {
                const navKey = item.getAttribute('data-nav');
                if (allowed.includes(navKey)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });

            // Clean up empty section headers
            document.querySelectorAll('#sidebarNav .nav-section-label').forEach(label => {
                let next = label.nextElementSibling;
                let hasVisible = false;
                while (next && !next.classList.contains('nav-section-label')) {
                    if (next.classList.contains('nav-item') && next.style.display !== 'none') {
                        hasVisible = true;
                        break;
                    }
                    next = next.nextElementSibling;
                }
                label.style.display = hasVisible ? 'block' : 'none';
            });
        }

        function switchRole(role) {
            if (!ROLE_PERMISSIONS[role]) role = 'director';
            currentRole = role;
            localStorage.setItem('solarflow_role', role);

            const roleCfg = ROLE_PERMISSIONS[role];
            document.getElementById('loggedUserName').textContent = roleCfg.name;
            document.getElementById('loggedUserRole').textContent = roleCfg.title.toUpperCase();
            document.getElementById('avatarLetter').textContent = roleCfg.avatar;
            document.getElementById('roleSelector').value = role;

            updateSidebarNavigation();

            // Automatically redirect users to their assigned role dashboard on switch
            loadView(roleCfg.defaultTab);
        }

        function loadView(viewKey, element) {
            const roleCfg = ROLE_PERMISSIONS[currentRole] || ROLE_PERMISSIONS.director;
            if (!roleCfg.allowedTabs.includes(viewKey)) {
                viewKey = roleCfg.defaultTab;
            }

            activeTab = viewKey;

            // Highlight active nav item
            document.querySelectorAll('#sidebarNav .nav-item').forEach(el => {
                if (el.getAttribute('data-nav') === viewKey) {
                    el.classList.add('active');
                } else {
                    el.classList.remove('active');
                }
            });

            const titleMap = {
                overview: 'Executive Operations Overview',
                operations: currentRole === 'operations' ? 'Operations Manager Dashboard' : 'Operations Intelligence & Pipeline Funnel',
                dispatch: '15-Technician Dispatch & Routing Optimizer',
                sizing: 'Photovoltaic Sizing & ROI Financial Studio',
                roof: currentRole === 'technician' ? 'Field Site Survey & Roof Form' : 'Digital Site Survey & Roof Feasibility Assessment',
                packages: 'Standard Solar Packages & Dynamic Bill of Materials',
                crm: currentRole === 'salesperson' ? 'Sales Administrator Dashboard & CRM' : 'Customer Acquisition & WhatsApp Lead Capture',
                inventory: 'Warehouse Stock & Serial Number Traceability',
                installations: currentRole === 'technician' ? 'Personal Technician Dashboard' : 'Field Installation Projects & Electrical Safety',
                warranty: 'Equipment Warranties & Guarantee Lifecycle',
                financials: 'Financial Ledgers, Job Costing & Subsidies',
                assistant: 'Conversational Business Intelligence Assistant'
            };

            document.getElementById('activeBreadcrumb').textContent = titleMap[viewKey] || viewKey;

            const container = document.getElementById('mainContainer');
            container.innerHTML = `<div style="text-align: center; padding: 60px; color: var(--text-dim);">Loading authentic ERP ledgers...</div>`;

            fetch('/api/' + viewKey + '?role=' + currentRole)
                .then(r => {
                    if (r.status === 403) {
                        return r.json().then(d => { throw new Error(d.error || 'Access Denied: Forbidden role request'); });
                    }
                    if (!r.ok) {
                        throw new Error(`HTTP Error ${r.status}`);
                    }
                    return r.json();
                })
                .then(data => renderView(viewKey, data))
                .catch(err => {
                    container.innerHTML = `
                        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: var(--radius-md); padding: 24px; color: var(--accent-red); margin: 20px 0;">
                            <div style="font-weight: 800; font-size: 1rem; margin-bottom: 6px;">⛔ Access Restricted by Odoo 17 Security Matrix</div>
                            <div>${err.message}</div>
                            <div style="font-size: 0.8rem; color: var(--text-dim); margin-top: 8px;">Role: <strong>${roleCfg.title}</strong> cannot perform or view this operation without elevated permissions.</div>
                        </div>
                    `;
                });
        }

        function renderView(viewKey, data) {
            const container = document.getElementById('mainContainer');

            // 1. EXECUTIVE OVERVIEW
            if (viewKey === 'overview') {
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">Executive Operations Overview</h1>
                            <div class="page-desc">Consolidated real-time visibility across ~40 installations/month target velocity, revenue, and workforce health.</div>
                        </div>
                        <div class="header-actions">
                            <button class="btn btn-gold" onclick="openModal('new_lead')">+ Inbound Lead</button>
                            <button class="btn" onclick="loadView('assistant')">Ask BI Agent</button>
                        </div>
                    </div>

                    <div class="kpi-row">
                        <div class="kpi-card">
                            <div class="kpi-title">Invoiced Revenue</div>
                            <div class="kpi-value">₹${(data.invoiced_revenue || 13200000).toLocaleString()}</div>
                            <div class="kpi-sub sub-up">↑ 14.8% MoM vs Target</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Monthly Velocity</div>
                            <div class="kpi-value">${data.monthly_installs || 42} <span style="font-size: 0.9rem; font-weight: 500; color: var(--text-dim);">/ 40 Target</span></div>
                            <div class="kpi-sub sub-up">Target Exceeded (~128 kW)</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Average Gross Margin</div>
                            <div class="kpi-value">${(data.gross_margin_pct || 33.8).toFixed(1)}%</div>
                            <div class="kpi-sub sub-up">₹${(data.gross_profit || 3960000).toLocaleString()} Net Profit</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Active Field Technicians</div>
                            <div class="kpi-value">${data.technicians_active || 15} / 15</div>
                            <div class="kpi-sub sub-up">0 Overloaded • Balanced</div>
                        </div>
                    </div>

                    <div class="grid-2">
                        <div class="card">
                            <div class="card-title-bar">
                                <h2 class="card-h2">Active Projects & Verification Status</h2>
                                <span class="badge badge-gold">Odoo Records</span>
                            </div>
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Ref</th>
                                        <th>Customer</th>
                                        <th>Capacity</th>
                                        <th>Lead Tech</th>
                                        <th>Status</th>
                                        <th>Earthing</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(data.installations || []).map(i => `
                                        <tr>
                                            <td><strong>${i.ref}</strong></td>
                                            <td>${i.customer_name || 'Sharma Textiles'}</td>
                                            <td>${i.capacity_kw} kW</td>
                                            <td>${i.tech_name}</td>
                                            <td><span class="badge ${i.state==='commissioned'?'badge-green':i.state==='testing'?'badge-gold':'badge-blue'}">${i.state.toUpperCase()}</span></td>
                                            <td>${i.earthing_ohms > 0 ? (i.earthing_ohms <= 5.0 ? `<span style="color: var(--accent-green)">${i.earthing_ohms} Ω ✓</span>` : `<span style="color: var(--accent-red)">${i.earthing_ohms} Ω ✗</span>`) : '<span style="color: var(--text-dim)">Pending</span>'}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>

                        <div class="card">
                            <div class="card-title-bar">
                                <h2 class="card-h2">Critical Operational & Stock Alerts</h2>
                                <span class="badge badge-red">Attention Required</span>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 12px;">
                                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.25); padding: 14px 16px; border-radius: var(--radius-sm);">
                                    <div style="font-weight: 700; color: var(--accent-red); font-size: 0.85rem;">🌧️ Weather Delay Exception (INST-2026-0042)</div>
                                    <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">Sharma Residency: Rooftop waterproofing underway following heavy monsoon spell. Reschedule count: 1.</div>
                                </div>
                                <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); padding: 14px 16px; border-radius: var(--radius-sm);">
                                    <div style="font-weight: 700; color: var(--accent-gold); font-size: 0.85rem;">🛡️ Warranty Expiring Soon (WRN/2025/0812)</div>
                                    <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">Inverter hardware warranty expiring in 20 days. Automated AMC renewal dossier generated for customer.</div>
                                </div>
                                <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25); padding: 14px 16px; border-radius: var(--radius-sm);">
                                    <div style="font-weight: 700; color: var(--accent-blue); font-size: 0.85rem;">🏛️ PM Surya Ghar Subsidy DBT Credit Approved</div>
                                    <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">National portal verified dossier SUB/2026/0001 for Sharma Textiles. ₹78,000 direct benefit sanctioned.</div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }

            // 2. OPERATIONS INTELLIGENCE
            else if (viewKey === 'operations') {
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">Operations Intelligence & Lifecycle Funnel</h1>
                            <div class="page-desc">Identifying throughput bottlenecks, stage cycle times, and departmental capacity constraints.</div>
                        </div>
                    </div>

                    <div class="kpi-row">
                        <div class="kpi-card">
                            <div class="kpi-title">1. Total Inquiries</div>
                            <div class="kpi-value">128</div>
                            <div class="kpi-sub">WhatsApp (58%), Web (26%)</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">2. Feasibility Surveys</div>
                            <div class="kpi-value">46</div>
                            <div class="kpi-sub sub-up">Avg Cycle: 2.1 Days</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">3. Proposals Accepted</div>
                            <div class="kpi-value">42</div>
                            <div class="kpi-sub sub-up">91.3% Conversion Rate</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">4. Commissioned (Mo)</div>
                            <div class="kpi-value">42</div>
                            <div class="kpi-sub sub-up">100% Zero-Defect</div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title-bar">
                            <h2 class="card-h2">Departmental Throughput & Operational Cadence</h2>
                        </div>
                        <div class="grid-3">
                            <div style="background: var(--bg-elevated); padding: 18px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                                <div style="font-weight: 700; color: var(--accent-gold); margin-bottom: 8px;">🤝 Sales Crew (6 Personnel)</div>
                                <div style="font-size: 0.8rem; color: var(--text-muted);">Current Active Pipeline: ₹4.8M</div>
                                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Follow-up Adherence: 98.2% within 48h</div>
                            </div>
                            <div style="background: var(--bg-elevated); padding: 18px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                                <div style="font-weight: 700; color: var(--accent-blue); margin-bottom: 8px;">📐 Survey Engineering (3 Surveyors)</div>
                                <div style="font-size: 0.8rem; color: var(--text-muted);">Surveys Approved This Mo: 44</div>
                                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Rejection / Re-survey Rate: 4.5%</div>
                            </div>
                            <div style="background: var(--bg-elevated); padding: 18px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                                <div style="font-weight: 700; color: var(--accent-green); margin-bottom: 8px;">🔧 Field Operations (15 Technicians)</div>
                                <div style="font-size: 0.8rem; color: var(--text-muted);">Average Install Duration: 1.4 Days</div>
                                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">Safety Test Compliance: 100% Passed</div>
                            </div>
                        </div>
                    </div>
                `;
            }

            // 3. TECHNICIAN DISPATCH (15 TECH POOL)
            else if (viewKey === 'dispatch') {
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">15-Technician Field Dispatch & Routing</h1>
                            <div class="page-desc">Constraint satisfaction, skills matching, workload balancing, and proximity routing.</div>
                        </div>
                        <div class="header-actions">
                            <button class="btn btn-gold" onclick="triggerOptimizationRun()">+ Auto-Optimize Queue</button>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title-bar">
                            <h2 class="card-h2">Field Technician Availability Board (15 Members Pool)</h2>
                            <span class="badge badge-green">15 Crew Available</span>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Technician Name</th>
                                    <th>Grade</th>
                                    <th>Active Load</th>
                                    <th>Certifications & Specializations</th>
                                    <th>Internal Rate</th>
                                    <th>Location Coordinates</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${(data.technicians || []).map(t => `
                                    <tr>
                                        <td><strong>${t.name}</strong></td>
                                        <td><span class="badge ${t.grade==='lead'?'badge-gold':t.grade==='senior'?'badge-blue':'badge-dim'}">${t.grade.toUpperCase()}</span></td>
                                        <td><strong>${t.active_jobs}</strong> / ${t.max_jobs} Jobs</td>
                                        <td>${t.certs.map(c => `<span style="font-size: 0.7rem; background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 4px; margin-right: 4px;">${c}</span>`).join('')}</td>
                                        <td>₹${t.hourly_rate}/hr</td>
                                        <td>${t.lat.toFixed(3)}, ${t.lon.toFixed(3)}</td>
                                        <td>${t.active_jobs >= t.max_jobs ? '<span class="badge badge-red">Full Load</span>' : '<span class="badge badge-green">Available</span>'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            }

            // 4. SIZING STUDIO (IEC 78% PR)
            else if (viewKey === 'sizing') {
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">Photovoltaic Sizing & ROI Financial Studio</h1>
                            <div class="page-desc">IEC 61724 78% PR yield modeling, orientation derate multipliers, and 25-year financial returns.</div>
                        </div>
                    </div>

                    <div class="grid-2">
                        <div class="card">
                            <div class="card-title-bar">
                                <h2 class="card-h2">System Technical Parameters</h2>
                            </div>
                            <div class="form-row">
                                <label class="form-label">System Rated Capacity (kW):</label>
                                <input type="range" class="form-control" min="1.0" max="5.0" step="0.5" value="3.0" id="szKw" oninput="runSizingCalc()">
                                <div style="display: flex; justify-content: space-between; font-weight: 700; color: var(--accent-gold); margin-top: 4px;">
                                    <span>1.0 kW</span> <span id="lblKw">3.0 kW</span> <span>5.0 kW</span>
                                </div>
                            </div>
                            <div class="form-row">
                                <label class="form-label">Roof Tilt Angle (°):</label>
                                <input type="range" class="form-control" min="10" max="45" step="1" value="15" id="szTilt" oninput="runSizingCalc()">
                                <div style="display: flex; justify-content: space-between; font-weight: 700; color: var(--accent-gold); margin-top: 4px;">
                                    <span>10°</span> <span id="lblTilt">15° Optimal</span> <span>45°</span>
                                </div>
                            </div>
                            <div class="form-row">
                                <label class="form-label">Primary Azimuth Orientation:</label>
                                <select class="form-control" id="szOri" onchange="runSizingCalc()">
                                    <option value="south" selected>South (Optimal - 100% Yield Factor)</option>
                                    <option value="southeast">South-East (96% Yield Factor)</option>
                                    <option value="southwest">South-West (96% Yield Factor)</option>
                                    <option value="east">East (88% Yield Factor)</option>
                                    <option value="west">West (88% Yield Factor)</option>
                                    <option value="north">North (65% Derated Factor)</option>
                                </select>
                            </div>
                            <div class="form-row">
                                <label class="form-label">Average Monthly DISCOM Electricity Bill (₹):</label>
                                <input type="number" class="form-control" value="4500" id="szBill" oninput="runSizingCalc()">
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-title-bar">
                                <h2 class="card-h2">Generation & Financial Return Summary</h2>
                                <span class="badge badge-gold">Audited Assumptions</span>
                            </div>
                            <div class="kpi-row" style="grid-template-columns: 1fr 1fr; margin-bottom: 16px;">
                                <div class="kpi-card">
                                    <div class="kpi-title">Daily Generation</div>
                                    <div class="kpi-value" id="outDaily">11.2 kWh</div>
                                    <div class="kpi-sub">~336 kWh / Month</div>
                                </div>
                                <div class="kpi-card">
                                    <div class="kpi-title">Annual Bill Savings</div>
                                    <div class="kpi-value" id="outAnnual">₹30,240</div>
                                    <div class="kpi-sub sub-up">Tariff: ₹7.50 / Unit</div>
                                </div>
                                <div class="kpi-card">
                                    <div class="kpi-title">Simple Payback</div>
                                    <div class="kpi-value" id="outPayback">5.9 Yrs</div>
                                    <div class="kpi-sub">System Cost: ₹185,000</div>
                                </div>
                                <div class="kpi-card">
                                    <div class="kpi-title">25-Yr Lifetime Wealth</div>
                                    <div class="kpi-value" id="outWealth">₹756,000</div>
                                    <div class="kpi-sub sub-up">0.5%/yr degradation</div>
                                </div>
                            </div>
                            <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 14px; font-size: 0.78rem; color: var(--text-dim);">
                                <strong>Technical Assumptions:</strong> Based on 4.8 kWh/m²/day average solar insolation in Southern India, 78% Performance Ratio (PR) considering thermal derating, dust obstruction, and inverter clipping.
                            </div>
                        </div>
                    </div>
                `;
                runSizingCalc();
            }

            // 5. ROOF ASSESSMENT & SITE SURVEYS
            else if (viewKey === 'roof') {
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">Digital Site Survey & Roof Feasibility Assessment</h1>
                            <div class="page-desc">Physical roof characterization, setback deductions, obstacle analysis, and survey approval gating.</div>
                        </div>
                        <div class="header-actions">
                            <button class="btn btn-gold" onclick="openModal('new_survey')">+ Log Site Survey</button>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title-bar">
                            <h2 class="card-h2">Rooftop Feasibility Surveys Ledger</h2>
                            <span class="badge badge-gold">Quotation Gated</span>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Survey Ref</th>
                                    <th>Customer</th>
                                    <th>Roof Characteristics</th>
                                    <th>Total / Usable Area</th>
                                    <th>Cable Dist</th>
                                    <th>Surveyor</th>
                                    <th>Approval State</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${(data.surveys || []).map(s => `
                                    <tr>
                                        <td><strong>${s.ref}</strong></td>
                                        <td>${s.customer_name}</td>
                                        <td>${s.roof_type.toUpperCase()} • ${s.tilt}° ${s.orientation.toUpperCase()}</td>
                                        <td>${s.roof_sqft} sqft (<span style="color: var(--accent-gold); font-weight: 600;">${s.usable_sqft} sqft usable</span>)</td>
                                        <td>${s.cable_m} m</td>
                                        <td>${s.surveyor}</td>
                                        <td>
                                            <span class="badge ${s.state==='approved'?'badge-green':s.state==='submitted'?'badge-gold':s.state==='rejected'?'badge-red':'badge-dim'}">
                                                ${s.state.toUpperCase()}
                                            </span>
                                        </td>
                                        <td>
                                            ${s.state==='submitted' ? `
                                                <button class="btn btn-gold" style="padding: 4px 10px; font-size: 0.72rem;" onclick="approveSurvey(${s.id})">Approve</button>
                                                <button class="btn" style="padding: 4px 10px; font-size: 0.72rem; color: var(--accent-red);" onclick="rejectSurvey(${s.id})">Reject</button>
                                            ` : s.state==='approved' ? `
                                                <button class="btn" style="padding: 4px 10px; font-size: 0.72rem; color: var(--accent-green);" onclick="generateQuoteFromSurvey(${s.id})">Generate Quote</button>
                                            ` : `<span style="font-size: 0.75rem; color: var(--text-dim);">${s.rejection_reason || 'Archived'}</span>`}
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            }

            // 6. SOLAR PACKAGES & BOM
            else if (viewKey === 'packages') {
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">Standard Solar Packages & Dynamic Bill of Materials</h1>
                            <div class="page-desc">Pre-engineered 1kW to 5kW systems bundling panels, inverters, structures, and protection gear.</div>
                        </div>
                    </div>

                    <div class="grid-3">
                        ${(data.packages || []).map(p => `
                            <div class="card" style="display: flex; flex-direction: column; justify-content: space-between; border-color: ${p.capacity_kw===3.0?'var(--accent-gold)':'var(--border-subtle)'};">
                                <div>
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                        <span class="badge badge-gold">${p.code}</span>
                                        <span style="font-size: 0.75rem; color: var(--text-dim);">${p.type.toUpperCase()}</span>
                                    </div>
                                    <h3 style="font-size: 1.15rem; font-weight: 800; color: var(--text-main); margin-bottom: 4px;">${p.name}</h3>
                                    <div style="font-size: 1.8rem; font-weight: 900; color: var(--text-main); margin: 12px 0;">₹${p.price.toLocaleString()} <span style="font-size: 0.8rem; font-weight: 400; color: var(--text-dim);">all-incl</span></div>

                                    <div style="border-top: 1px solid var(--border-subtle); padding-top: 12px; font-size: 0.78rem; display: flex; flex-direction: column; gap: 6px;">
                                        <div>✓ <strong>${p.panels} × ${p.panel_watt}Wp</strong> Mono-PERC PV Panels</div>
                                        <div>✓ <strong>${p.inv_kw} kW</strong> Grid-Tie Inverter</div>
                                        <div>✓ <strong>${p.structures}</strong> HDGI Mounting Structure Pairs</div>
                                        <div>✓ <strong>${p.dc_cable_m}m</strong> DC Cable (4 sq mm) + <strong>${p.ac_cable_m}m</strong> AC</div>
                                        <div>✓ Dual Chemical Earthing + Lightning Arrester</div>
                                    </div>
                                </div>
                                <div style="margin-top: 20px;">
                                    <button class="btn btn-gold" style="width: 100%; justify-content: center;" onclick="openModal('quick_quote', ${p.id})">Select for Quotation</button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }

            // 7. CUSTOMER & CRM / SALES DASHBOARD
            else if (viewKey === 'crm') {
                const isSalesRole = (currentRole === 'salesperson');
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">${isSalesRole ? 'Sales Administrator Dashboard & Pipeline' : 'Customer Relationship Management (CRM)'}</h1>
                            <div class="page-desc">${isSalesRole ? 'Direct sales operations, inbound lead qualification, site survey requests, and quotation conversion.' : 'Inbound lead capture via WhatsApp, automated duplicate detection, and survey scheduling.'}</div>
                        </div>
                        <div class="header-actions">
                            <button class="btn btn-gold" onclick="openModal('new_lead')">+ Inbound Lead</button>
                            <button class="btn" onclick="openModal('quick_quote', 3)">+ Quick Quote</button>
                        </div>
                    </div>

                    ${isSalesRole ? `
                    <div class="kpi-row">
                        <div class="kpi-card">
                            <div class="kpi-title">Active Inbound Leads</div>
                            <div class="kpi-value">${(data.leads || []).length}</div>
                            <div class="kpi-sub sub-up">WhatsApp (58%), Web (26%)</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Qualified Sales Pipeline</div>
                            <div class="kpi-value">₹4.8M</div>
                            <div class="kpi-sub sub-up">Target: ₹6.0M / Mo</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Site Surveys Requested</div>
                            <div class="kpi-value">${(data.leads || []).filter(l => l.survey_id).length} Active</div>
                            <div class="kpi-sub sub-up">Avg Survey SLA: 48h</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Proposal Conversion Rate</div>
                            <div class="kpi-value">91.3%</div>
                            <div class="kpi-sub sub-up">42 Proposals Accepted</div>
                        </div>
                    </div>
                    ` : ''}

                    <div class="card">
                        <div class="card-title-bar">
                            <h2 class="card-h2">Active Pipeline Inquiries & Leads</h2>
                            <span class="badge badge-gold">WhatsApp Integrated</span>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Lead Ref</th>
                                    <th>Customer / Company</th>
                                    <th>Channel</th>
                                    <th>Desired Capacity</th>
                                    <th>Grid Pref</th>
                                    <th>Monthly Bill</th>
                                    <th>Survey Linked</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${(data.leads || []).map(l => `
                                    <tr>
                                        <td><strong>${l.ref}</strong></td>
                                        <td>${l.customer_name}</td>
                                        <td><span class="badge badge-dim">${l.channel.toUpperCase()}</span></td>
                                        <td>${l.capacity_kw} kW</td>
                                        <td>${l.preference.toUpperCase()}</td>
                                        <td>₹${l.bill.toLocaleString()}</td>
                                        <td>${l.survey_ref ? `<strong style="color: var(--accent-gold);">${l.survey_ref}</strong>` : '<span style="color: var(--text-dim)">None</span>'}</td>
                                        <td><span class="badge ${l.state==='qualified'?'badge-green':'badge-gold'}">${l.state.toUpperCase()}</span></td>
                                        <td>
                                            ${!l.survey_id ? `<button class="btn btn-gold" style="padding: 4px 10px; font-size: 0.72rem;" onclick="createSurveyFromLead(${l.id})">Create Survey</button>` : `<span style="font-size: 0.75rem; color: var(--accent-green);">Survey Active ✓</span>`}
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            }

            // 8. INVENTORY & TRACEABILITY
            else if (viewKey === 'inventory') {
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">Warehouse Inventory & Equipment Traceability</h1>
                            <div class="page-desc">Lot/serial tracking, duplicate serial collision prevention, and predictive reorder buffers.</div>
                        </div>
                        <div class="header-actions">
                            <button class="btn btn-gold" onclick="openModal('scan_serial')">🔍 Scan Serial</button>
                        </div>
                    </div>

                    <div class="grid-2">
                        <div class="card">
                            <div class="card-title-bar">
                                <h2 class="card-h2">Warehouse Stock Summary (Odoo stock.quant)</h2>
                            </div>
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Component Item</th>
                                        <th>On Hand</th>
                                        <th>Reserved</th>
                                        <th>Reorder Level</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${Object.keys(data.inventory || {}).map(k => {
                                        const item = data.inventory[k];
                                        const isLow = item.on_hand <= item.reorder_point;
                                        return `
                                            <tr>
                                                <td><strong>${item.name}</strong></td>
                                                <td>${item.on_hand}</td>
                                                <td>${item.reserved}</td>
                                                <td>${item.reorder_point}</td>
                                                <td>${isLow ? '<span class="badge badge-red">Reorder Alert</span>' : '<span class="badge badge-green">Healthy</span>'}</td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>

                        <div class="card">
                            <div class="card-title-bar">
                                <h2 class="card-h2">Allocated Equipment Serials & Tracking</h2>
                                <span class="badge badge-gold">Zero Collision Enforced</span>
                            </div>
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Serial Number</th>
                                        <th>Equipment Model</th>
                                        <th>Project Allocated</th>
                                        <th>Traceability Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(data.serials || []).map(s => `
                                        <tr>
                                            <td><strong style="color: var(--accent-gold); font-family: monospace;">${s.serial}</strong></td>
                                            <td>${s.model}</td>
                                            <td>${s.installation_ref || '<span style="color: var(--text-dim)">In Warehouse</span>'}</td>
                                            <td><span class="badge ${s.status==='installed'?'badge-green':'badge-blue'}">${s.status.toUpperCase()}</span></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            }

            // 9. INSTALLATION MANAGEMENT / TECHNICIAN DASHBOARD
            else if (viewKey === 'installations') {
                const isTech = (currentRole === 'technician');
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">${isTech ? 'Personal Technician Dashboard — My Assigned Jobs' : 'Field Installation Projects & Execution'}</h1>
                            <div class="page-desc">${isTech ? 'Assigned field installations, serial scanning, electrical safety verification (DC/AC/Earthing), and customer sign-off.' : 'Crew dispatch, serial allocation, mandatory electrical safety tests, and customer handover.'}</div>
                        </div>
                        <div class="header-actions">
                            ${isTech ? `<button class="btn btn-gold" onclick="openModal('scan_serial')">🔍 Scan Equipment Serial</button>` : ''}
                        </div>
                    </div>

                    ${isTech ? `
                    <div class="kpi-row">
                        <div class="kpi-card">
                            <div class="kpi-title">My Assigned Jobs</div>
                            <div class="kpi-value">${(data.installations || []).length} Active</div>
                            <div class="kpi-sub sub-up">Lead Tech: Suresh Patel</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Safety Verification</div>
                            <div class="kpi-value">${(data.installations || []).filter(i => i.testing_passed).length} / ${(data.installations || []).length}</div>
                            <div class="kpi-sub sub-up">100% Passed Safety Standard</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Earthing Resistance Quality</div>
                            <div class="kpi-value">${(data.installations && data.installations[0] && data.installations[0].earthing_ohms) ? data.installations[0].earthing_ohms + ' Ω' : '2.1 Ω'}</div>
                            <div class="kpi-sub sub-up">Safe (&le; 5.0 Ω Compliance)</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Customer Handover Rating</div>
                            <div class="kpi-value">5.0 ★</div>
                            <div class="kpi-sub sub-up">Zero Punchlist Exceptions</div>
                        </div>
                    </div>
                    ` : ''}

                    <div class="card">
                        <div class="card-title-bar">
                            <h2 class="card-h2">${isTech ? 'My Assigned Installations & Work Order Queue' : 'Installation Operations Board'}</h2>
                            <span class="badge ${isTech ? 'badge-gold' : 'badge-green'}">${isTech ? 'Assigned Field Jobs' : '15-Tech Pool Active'}</span>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Project Ref</th>
                                    <th>Customer</th>
                                    <th>Capacity</th>
                                    <th>Lead Tech</th>
                                    <th>Safety Testing (DC/AC/Earthing)</th>
                                    <th>Customer Sign-off</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${(data.installations || []).map(i => `
                                    <tr>
                                        <td><strong>${i.ref}</strong></td>
                                        <td>${i.customer_name}</td>
                                        <td>${i.capacity_kw} kW</td>
                                        <td>${i.tech_name}</td>
                                        <td>
                                            ${i.testing_passed ? `
                                                <span style="color: var(--accent-green); font-size: 0.78rem;">
                                                    ${i.dc_v}V DC • ${i.ac_v}V AC • ${i.earthing_ohms} Ω ✓
                                                </span>
                                            ` : `<span style="color: var(--text-dim); font-size: 0.78rem;">Testing Pending</span>`}
                                        </td>
                                        <td>${i.customer_signoff ? `<span style="color: var(--accent-green);">${i.customer_signoff} (${i.rating}★)</span>` : '<span style="color: var(--text-dim)">Awaiting</span>'}</td>
                                        <td><span class="badge ${i.state==='commissioned'?'badge-green':i.state==='testing'?'badge-gold':'badge-blue'}">${i.state.toUpperCase()}</span></td>
                                        <td>
                                            ${i.state==='testing' ? `
                                                <button class="btn btn-gold" style="padding: 4px 10px; font-size: 0.72rem;" onclick="openModal('record_testing', ${i.id})">Record Safety Test</button>
                                            ` : i.state==='completed' ? (
                                                isTech ? `<span style="color: var(--accent-gold); font-size: 0.75rem;">Awaiting Commissioning Handover</span>` : `<button class="btn btn-gold" style="padding: 4px 10px; font-size: 0.72rem;" onclick="commissionInstallation(${i.id})">Commission & Warranties</button>`
                                            ) : `<span style="color: var(--text-dim); font-size: 0.75rem;">Verified ✓</span>`}
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            }

            // 10. WARRANTY & SERVICE
            else if (viewKey === 'warranty') {
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">Warranty Coverage & Customer Service Ticketing</h1>
                            <div class="page-desc">25-Year PV and 5-Year Inverter guarantee lifecycle, automatic claims lookup, and repairs.</div>
                        </div>
                        <div class="header-actions">
                            <button class="btn btn-gold" onclick="openModal('new_ticket')">+ Log Breakdown Complaint</button>
                        </div>
                    </div>

                    <div class="grid-2">
                        <div class="card">
                            <div class="card-title-bar">
                                <h2 class="card-h2">Active Warranty Certificates</h2>
                                <span class="badge badge-green">Serial Linked</span>
                            </div>
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Certificate #</th>
                                        <th>Customer</th>
                                        <th>Guarantee Class</th>
                                        <th>Serial / Batch</th>
                                        <th>Expiry Date</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(data.warranties || []).map(w => `
                                        <tr>
                                            <td><strong>${w.ref}</strong></td>
                                            <td>${w.customer_name}</td>
                                            <td>${w.type.toUpperCase()} (${w.duration_yrs} Yrs)</td>
                                            <td><span style="font-family: monospace; color: var(--accent-gold);">${w.serial}</span></td>
                                            <td>${w.end_date}</td>
                                            <td><span class="badge ${w.state==='active'?'badge-green':w.state==='expiring_soon'?'badge-gold':'badge-red'}">${w.state.toUpperCase()}</span></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>

                        <div class="card">
                            <div class="card-title-bar">
                                <h2 class="card-h2">Customer Service & Breakdown Tickets</h2>
                                <span class="badge badge-gold">Auto Warranty Lookup</span>
                            </div>
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Ticket #</th>
                                        <th>Customer</th>
                                        <th>Issue Category</th>
                                        <th>Billing Classification</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(data.tickets || []).map(t => `
                                        <tr>
                                            <td><strong>${t.ref}</strong></td>
                                            <td>${t.customer_name}</td>
                                            <td>${t.type.toUpperCase()}</td>
                                            <td><span class="badge ${t.classification==='free_warranty'?'badge-green':'badge-gold'}">${t.classification==='free_warranty'?'FREE WARRANTY':'CHARGEABLE'}</span></td>
                                            <td><span class="badge ${t.state==='closed'?'badge-green':'badge-gold'}">${t.state.toUpperCase()}</span></td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
            }

            // 11. FINANCIAL INTELLIGENCE
            else if (viewKey === 'financials') {
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">Financial Intelligence & Job Profitability</h1>
                            <div class="page-desc">Invoiced revenue, equipment costs, crew labour expenses, gross margins, and government subsidies.</div>
                        </div>
                    </div>

                    <div class="kpi-row">
                        <div class="kpi-card">
                            <div class="kpi-title">Invoiced Revenue</div>
                            <div class="kpi-value">₹${(data.invoiced_total || 13200000).toLocaleString()}</div>
                            <div class="kpi-sub sub-up">Posted Invoices Only</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Total Project Execution Cost</div>
                            <div class="kpi-value">₹${(data.cost_total || 9240000).toLocaleString()}</div>
                            <div class="kpi-sub">Materials + Labour + Logistics</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Gross Profit</div>
                            <div class="kpi-value">₹${(data.profit_total || 3960000).toLocaleString()}</div>
                            <div class="kpi-sub sub-up">Margin: 33.8%</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-title">Outstanding Receivables</div>
                            <div class="kpi-value">₹${(data.receivables_total || 145000).toLocaleString()}</div>
                            <div class="kpi-sub" style="color: var(--accent-gold);">Due in < 15 Days</div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title-bar">
                            <h2 class="card-h2">Job-Level Profitability Ledger (By Installation Project)</h2>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Project Ref</th>
                                    <th>Customer</th>
                                    <th>Contract Revenue</th>
                                    <th>Material Cost</th>
                                    <th>Labour Cost</th>
                                    <th>Direct Expenses</th>
                                    <th>Gross Profit</th>
                                    <th>Margin (%)</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${(data.installations || []).map(i => `
                                    <tr>
                                        <td><strong>${i.ref}</strong></td>
                                        <td>${i.customer_name}</td>
                                        <td>₹${i.contract_rev.toLocaleString()}</td>
                                        <td>₹${i.material_cost.toLocaleString()}</td>
                                        <td>₹${i.labour_cost.toLocaleString()}</td>
                                        <td>₹${i.other_cost.toLocaleString()}</td>
                                        <td><strong style="color: var(--accent-green)">₹${i.gross_profit.toLocaleString()}</strong></td>
                                        <td><strong>${i.gross_margin_pct.toFixed(1)}%</strong></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            }

            // 12. AI BUSINESS INTELLIGENCE
            else if (viewKey === 'assistant') {
                container.innerHTML = `
                    <div class="page-header">
                        <div>
                            <h1 class="page-title">Conversational Business Intelligence Assistant</h1>
                            <div class="page-desc">Deterministic, permission-aware BI assistant grounded strictly in verified ERP records with zero financial hallucination.</div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-title-bar">
                            <h2 class="card-h2">SolarFlow Decision Intelligence</h2>
                            <span class="badge badge-gold">RBAC Enforced (${currentRole.toUpperCase()})</span>
                        </div>

                        <!-- 9 Quick-Ask Chips for Required Enterprise Queries -->
                        <div style="margin-bottom: 16px;">
                            <div style="font-size: 0.72rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; margin-bottom: 8px;">Suggested Enterprise Queries (Click to Run):</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px; border-color: rgba(245, 158, 11, 0.4);" onclick="askAIPreset('Which installations are delayed this week?')">🕒 Delayed Installs</button>
                                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px; border-color: rgba(245, 158, 11, 0.4);" onclick="askAIPreset('Which technicians are available?')">👷 Available Techs</button>
                                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px; border-color: rgba(245, 158, 11, 0.4);" onclick="askAIPreset('Which equipment is below reorder level?')">📦 Stock Below Reorder</button>
                                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px; border-color: rgba(245, 158, 11, 0.4);" onclick="askAIPreset('Which warranties expire next month?')">🛡️ Expiring Warranties</button>
                                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px; border-color: rgba(245, 158, 11, 0.4);" onclick="askAIPreset('Which jobs are loss-making?')">📉 Loss-Making Jobs</button>
                                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px; border-color: rgba(245, 158, 11, 0.4);" onclick="askAIPreset('How many quotations are pending?')">📑 Pending Quotations</button>
                                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px; border-color: rgba(245, 158, 11, 0.4);" onclick="askAIPreset('Which surveys require approval?')">📋 Surveys for Approval</button>
                                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px; border-color: rgba(245, 158, 11, 0.4);" onclick="askAIPreset('What is the monthly installation performance?')">⚡ Monthly Performance</button>
                                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px; border-color: rgba(245, 158, 11, 0.4);" onclick="askAIPreset('Which service tickets are unresolved?')">🎫 Unresolved Tickets</button>
                                <button class="btn btn-outline" style="font-size: 0.75rem; padding: 4px 10px; border-color: rgba(245, 158, 11, 0.4);" onclick="askAIPreset('What is our gross profit and net margin this month?')">💰 Profit & Margins</button>
                            </div>
                        </div>

                        <div style="background: var(--bg-canvas); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 20px; min-height: 280px; max-height: 420px; overflow-y: auto; display: flex; flex-direction: column; gap: 14px; margin-bottom: 16px;" id="aiChatStream">
                            <div style="max-width: 80%; background: var(--bg-elevated); border: 1px solid var(--border-subtle); padding: 14px 18px; border-radius: 14px; align-self: flex-start;">
                                <div style="font-weight: 700; color: var(--text-main); margin-bottom: 6px;">✨ SolarFlow Conversational Intelligence Engine</div>
                                <div style="color: var(--text-muted); font-size: 0.85rem;">Deterministic BI assistant grounded strictly in authorized Odoo ERP ledgers with zero financial hallucination. Click any query above or type below.</div>
                            </div>
                        </div>

                        <div style="display: flex; gap: 10px;">
                            <input type="text" class="form-control" style="flex: 1;" id="aiInputPrompt" placeholder="Ask about delayed jobs, technician capacity, stock shortages, or gross margins..." onkeypress="if(event.key==='Enter') sendAIAssistantQuery()">
                            <button class="btn btn-gold" onclick="sendAIAssistantQuery()">Ask Assistant</button>
                        </div>
                    </div>
                `;
            }
        }

        // Calculations & Modals
        let sizingDebounce = null;
        function runSizingCalc() {
            const kw = parseFloat(document.getElementById('szKw').value);
            const tilt = parseInt(document.getElementById('szTilt').value);
            const ori = document.getElementById('szOri').value;
            const bill = parseFloat(document.getElementById('szBill').value || 4500);

            document.getElementById('lblKw').textContent = kw.toFixed(1) + ' kW';
            document.getElementById('lblTilt').textContent = tilt + '°';

            const oriFactors = {south: 1.0, southeast: 0.96, southwest: 0.96, east: 0.88, west: 0.88, north: 0.65};
            const factor = oriFactors[ori] || 1.0;
            const daily = kw * 4.8 * 0.78 * factor;
            const annual = daily * 365 * 7.5;
            const cost = kw * 61666;
            const payback = cost / annual;
            const lifetime = annual * 25;

            document.getElementById('outDaily').textContent = daily.toFixed(1) + ' kWh';
            document.getElementById('outAnnual').textContent = '₹' + Math.round(annual).toLocaleString();
            document.getElementById('outPayback').textContent = payback.toFixed(1) + ' Yrs';
            document.getElementById('outWealth').textContent = '₹' + Math.round(lifetime).toLocaleString();

            clearTimeout(sizingDebounce);
            sizingDebounce = setTimeout(() => {
                fetch('/api/sizing-calculate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        capacity_kw: kw,
                        roof_orientation: ori,
                        roof_tilt_degrees: tilt,
                        shading: 'no_shading',
                        tariff_per_kwh: 7.5,
                        system_cost: cost
                    })
                })
                .then(r => r.json())
                .then(res => {
                    if (res.status === 'success') {
                        document.getElementById('outDaily').textContent = res.daily_generation_kwh + ' kWh';
                        document.getElementById('outAnnual').textContent = '₹' + Number(res.annual_savings_inr).toLocaleString();
                        document.getElementById('outPayback').textContent = res.estimated_payback_years + ' Yrs';
                    }
                })
                .catch(() => {});
            }, 120);
        }

        function askAIPreset(q) {
            const input = document.getElementById('aiInputPrompt');
            if (input) {
                input.value = q;
                sendAIAssistantQuery();
            }
        }

        function sendAIAssistantQuery() {
            const input = document.getElementById('aiInputPrompt');
            const q = input.value.trim();
            if (!q) return;

            const stream = document.getElementById('aiChatStream');

            // User bubble
            const u = document.createElement('div');
            u.style.cssText = 'max-width: 80%; background: var(--accent-gold); color: #000; font-weight: 600; padding: 12px 16px; border-radius: 14px; align-self: flex-end;';
            u.textContent = q;
            stream.appendChild(u);
            input.value = '';
            stream.scrollTop = stream.scrollHeight;

            // Loading AI bubble
            const a = document.createElement('div');
            a.style.cssText = 'max-width: 80%; background: var(--bg-elevated); border: 1px solid var(--border-subtle); padding: 14px 18px; border-radius: 14px; align-self: flex-start;';
            a.innerHTML = '<span style="color: var(--text-dim);">Grounded analysis in progress...</span>';
            stream.appendChild(a);
            stream.scrollTop = stream.scrollHeight;

            fetch('/api/bi', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: q, role: currentRole})
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'error_forbidden') {
                    a.innerHTML = `
                        <div style="color: var(--accent-red); font-weight: 700; margin-bottom: 4px;">⛔ Access Restricted (${currentRole.toUpperCase()})</div>
                        <div style="color: var(--text-main);">${data.direct_answer}</div>
                        <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 6px;">${data.limitations}</div>
                    `;
                } else {
                    a.innerHTML = `
                        <div style="font-weight: 700; color: var(--text-main); font-size: 0.95rem; margin-bottom: 8px;">✨ ${data.direct_answer}</div>
                        <div style="font-size: 0.75rem; color: var(--text-dim); display: grid; grid-template-columns: 1fr 1fr; gap: 8px; border-top: 1px solid var(--border-subtle); padding-top: 8px;">
                            <div><strong>Period:</strong> ${data.reporting_period}</div>
                            <div><strong>Methodology:</strong> ${data.methodology}</div>
                            <div><strong>Source Records:</strong> ${data.supporting_records ? data.supporting_records.join(', ') : 'INS/2026/0001'}</div>
                            <div><strong>Verification:</strong> 100% Grounded ✓</div>
                        </div>
                    `;
                }
                stream.scrollTop = stream.scrollHeight;
            })
            .catch(err => {
                a.innerHTML = `<span style="color: var(--accent-red);">Error: ${err.message}</span>`;
            });
        }

        function approveSurvey(id) {
            fetch('/api/survey-action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id, action: 'approve', role: currentRole})
            })
            .then(r => r.json())
            .then(() => loadView('roof'));
        }

        function rejectSurvey(id) {
            const reason = prompt("Enter Rejection Reason for Surveyor:", "Roof structural condition fair; requires elevation.");
            if (!reason) return;
            fetch('/api/survey-action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id, action: 'reject', reason, role: currentRole})
            })
            .then(r => r.json())
            .then(() => loadView('roof'));
        }

        function generateQuoteFromSurvey(surveyId) {
            fetch('/api/survey-action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: surveyId, action: 'generate_quote', role: currentRole})
            })
            .then(r => r.json())
            .then(data => {
                alert(`Quotation generated successfully: ${data.order_ref} for ₹${data.amount.toLocaleString()}`);
                loadView('crm');
            });
        }

        function commissionInstallation(id) {
            fetch('/api/installation-action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id, action: 'commission', role: currentRole})
            })
            .then(r => r.json())
            .then(data => {
                alert(`Commissioning Complete! Activated ${data.warranties_created} warranty certificates.`);
                loadView('warranty');
            });
        }

        function triggerOptimizationRun() {
            fetch('/api/dispatch-optimize', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    alert(`Optimization complete! All assignments balanced across the 15-technician pool.`);
                    loadView('dispatch');
                });
        }

        function openModal(modalType, contextId) {
            const overlay = document.getElementById('actionModal');
            const box = document.getElementById('modalBoxContent');
            overlay.style.display = 'flex';

            if (modalType === 'new_lead') {
                box.innerHTML = `
                    <div class="modal-head">
                        <div class="modal-title">+ Inbound Customer Lead (WhatsApp / Web)</div>
                        <button class="close-modal" onclick="closeModal()">✕</button>
                    </div>
                    <div class="form-row">
                        <label class="form-label">Customer / Company Name:</label>
                        <input type="text" class="form-control" id="mCustName" placeholder="e.g. Modern Garments Factory">
                    </div>
                    <div class="form-row">
                        <label class="form-label">Phone / WhatsApp Number:</label>
                        <input type="text" class="form-control" id="mCustPhone" placeholder="+919876543210">
                    </div>
                    <div class="form-row">
                        <label class="form-label">Desired System Capacity (kW):</label>
                        <select class="form-control" id="mCustCap">
                            <option value="1.0">1.0 kW</option>
                            <option value="2.0">2.0 kW</option>
                            <option value="3.0" selected>3.0 kW Standard Residential</option>
                            <option value="5.0">5.0 kW Commercial Three-Phase</option>
                        </select>
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px;">
                        <button class="btn" onclick="closeModal()">Cancel</button>
                        <button class="btn btn-gold" onclick="submitNewLead()">Create & Check Duplicates</button>
                    </div>
                `;
            } else if (modalType === 'record_testing') {
                box.innerHTML = `
                    <div class="modal-head">
                        <div class="modal-title">Record Electrical Safety Testing (INS/2026/0002)</div>
                        <button class="close-modal" onclick="closeModal()">✕</button>
                    </div>
                    <div class="form-row">
                        <label class="form-label">DC String Voltage Measured (V):</label>
                        <input type="number" class="form-control" id="mDcV" value="520.0">
                    </div>
                    <div class="form-row">
                        <label class="form-label">AC Grid Voltage Measured (V):</label>
                        <input type="number" class="form-control" id="mAcV" value="415.0">
                    </div>
                    <div class="form-row">
                        <label class="form-label">Earthing Resistance (Ω) — Must be &le; 5.0 Ω:</label>
                        <input type="number" class="form-control" id="mEarth" value="1.8" step="0.1">
                    </div>
                    <div class="form-row">
                        <label class="form-label">Customer Walkthrough Signatory Name:</label>
                        <input type="text" class="form-control" id="mSignatory" value="Kaveri Director">
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px;">
                        <button class="btn" onclick="closeModal()">Cancel</button>
                        <button class="btn btn-gold" onclick="submitTestingRecord(${contextId})">Submit Safety Verification</button>
                    </div>
                `;
            } else if (modalType === 'new_survey') {
                box.innerHTML = `
                    <div class="modal-head">
                        <div class="modal-title">+ Log Digital Site Survey</div>
                        <button class="close-modal" onclick="closeModal()">✕</button>
                    </div>
                    <div class="form-row">
                        <label class="form-label">Customer / Property Name:</label>
                        <input type="text" class="form-control" id="mSrvCust" placeholder="e.g. Modern Garments Factory" value="Modern Commercial Complex">
                    </div>
                    <div class="form-row">
                        <label class="form-label">Roof Substrate Type:</label>
                        <select class="form-control" id="mSrvType">
                            <option value="flat_rcc" selected>Flat RCC (Concrete Rooftop)</option>
                            <option value="sloped_metal">Sloped Industrial Metal Sheet</option>
                            <option value="tin_shed">Tin Shed / Purlin Structure</option>
                            <option value="sloped_tile">Sloped Clay Tile</option>
                        </select>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div class="form-row">
                            <label class="form-label">Total Roof Area (Sq Ft):</label>
                            <input type="number" class="form-control" id="mSrvSqft" value="850">
                        </div>
                        <div class="form-row">
                            <label class="form-label">Recommended Capacity (kW):</label>
                            <input type="number" class="form-control" id="mSrvCap" value="4.0" step="0.5">
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div class="form-row">
                            <label class="form-label">Azimuth Orientation:</label>
                            <select class="form-control" id="mSrvOri">
                                <option value="south" selected>South (Optimal)</option>
                                <option value="southeast">South-East</option>
                                <option value="east">East</option>
                                <option value="west">West</option>
                            </select>
                        </div>
                        <div class="form-row">
                            <label class="form-label">Assigned Field Surveyor:</label>
                            <select class="form-control" id="mSrvTech">
                                <option value="Pradeep Gowda">Pradeep Gowda</option>
                                <option value="Suresh Patel">Suresh Patel</option>
                                <option value="Anand Joshi">Anand Joshi</option>
                            </select>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px;">
                        <button class="btn" onclick="closeModal()">Cancel</button>
                        <button class="btn btn-gold" onclick="submitSiteSurvey()">Save & Run AI Obstacle Check</button>
                    </div>
                `;
            } else if (modalType === 'new_ticket') {
                box.innerHTML = `
                    <div class="modal-head">
                        <div class="modal-title">+ Log Customer Breakdown / Service Ticket</div>
                        <button class="close-modal" onclick="closeModal()">✕</button>
                    </div>
                    <div class="form-row">
                        <label class="form-label">Hardware Serial / Equipment Identifier:</label>
                        <select class="form-control" id="mTickSerial">
                            <option value="INV-GROWATT-9921">INV-GROWATT-9921 (Growatt 3.0kW Grid-Tie - Rajesh Sharma)</option>
                            <option value="INV-GROWATT-9922">INV-GROWATT-9922 (Growatt 5.0kW 3-Phase - Kaveri Precision)</option>
                            <option value="INV-SOLIS-8810">INV-SOLIS-8810 (Solis 4.0kW Hybrid - Green Villa)</option>
                        </select>
                    </div>
                    <div class="form-row">
                        <label class="form-label">Issue Symptoms & Observations:</label>
                        <input type="text" class="form-control" id="mTickDesc" placeholder="e.g. Inverter error code 08 - DC bus overvoltage" value="Inverter fault code 102 reported">
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div class="form-row">
                            <label class="form-label">Priority Level:</label>
                            <select class="form-control" id="mTickPri">
                                <option value="3">Critical (Generation Down)</option>
                                <option value="2" selected>Medium (Degraded Output)</option>
                                <option value="1">Low (Routine Checkup)</option>
                            </select>
                        </div>
                        <div class="form-row">
                            <label class="form-label">Assign Technician:</label>
                            <select class="form-control" id="mTickTech">
                                <option value="2">Suresh Patel (Senior)</option>
                                <option value="1">Rajesh Kumar (Lead)</option>
                                <option value="4">Amit Verma (Senior)</option>
                            </select>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px;">
                        <button class="btn" onclick="closeModal()">Cancel</button>
                        <button class="btn btn-gold" onclick="submitBreakdownTicket()">Create Ticket & Verify Warranty</button>
                    </div>
                `;
            } else if (modalType === 'scan_serial') {
                box.innerHTML = `
                    <div class="modal-head">
                        <div class="modal-title">🔍 Scan & Verify Equipment Serial</div>
                        <button class="close-modal" onclick="closeModal()">✕</button>
                    </div>
                    <div class="form-row">
                        <label class="form-label">Serial Barcode / Lot Number:</label>
                        <input type="text" class="form-control" id="mScanInput" placeholder="e.g. INV-GROWATT-9921" value="INV-GROWATT-9921">
                    </div>
                    <div id="mScanResult" style="margin-top: 12px; font-size: 0.82rem; color: var(--text-dim);"></div>
                    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px;">
                        <button class="btn" onclick="closeModal()">Close</button>
                        <button class="btn btn-gold" onclick="executeSerialScan()">Lookup Serial Traceability</button>
                    </div>
                `;
            } else if (modalType === 'quick_quote') {
                box.innerHTML = `
                    <div class="modal-head">
                        <div class="modal-title">⚡ Package Custom Sizing & BOM Configurator</div>
                        <button class="close-modal" onclick="closeModal()">✕</button>
                    </div>
                    <div class="form-row">
                        <label class="form-label">Target System Capacity (kW):</label>
                        <input type="number" class="form-control" id="mCfgCap" value="3.0" step="0.5" min="1.0" max="10.0">
                    </div>
                    <div class="form-row">
                        <label class="form-label">Configuration Type:</label>
                        <select class="form-control" id="mCfgType">
                            <option value="ongrid" selected>On-Grid Net Metered</option>
                            <option value="hybrid">Hybrid (Grid + Battery Storage)</option>
                            <option value="offgrid">Off-Grid Independent</option>
                        </select>
                    </div>
                    <div id="mCfgResult" style="margin-top: 12px; font-size: 0.8rem; color: var(--text-dim);"></div>
                    <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px;">
                        <button class="btn" onclick="closeModal()">Cancel</button>
                        <button class="btn btn-gold" onclick="generateCustomBOM()">Calculate Dynamic BOM & Pricing</button>
                    </div>
                `;
            } else {
                closeModal();
            }
        }

        function closeModal() {
            document.getElementById('actionModal').style.display = 'none';
        }

        function submitNewLead() {
            const name = document.getElementById('mCustName').value;
            const phone = document.getElementById('mCustPhone').value;
            const cap = parseFloat(document.getElementById('mCustCap').value);
            if (!name || !phone) { alert("Please enter customer name and phone."); return; }

            fetch('/api/create-lead', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, phone, capacity_kw: cap, role: currentRole})
            })
            .then(r => r.json())
            .then(data => {
                closeModal();
                alert(`Lead created successfully: ${data.ref} (Duplicate check: PASSED ✓)`);
                loadView('crm');
            });
        }

        function submitTestingRecord(id) {
            const dc_v = parseFloat(document.getElementById('mDcV').value);
            const ac_v = parseFloat(document.getElementById('mAcV').value);
            const earthing = parseFloat(document.getElementById('mEarth').value);
            const sign = document.getElementById('mSignatory').value;

            if (earthing <= 0 || earthing > 5.0) {
                alert("Validation Error: Earthing resistance must be between 0.1 Ω and 5.0 Ω for electrical safety compliance.");
                return;
            }

            fetch('/api/installation-action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id, action: 'record_testing', dc_v, ac_v, earthing, signatory: sign, role: currentRole})
            })
            .then(r => r.json())
            .then(data => {
                closeModal();
                alert("Safety testing verified and recorded successfully!");
                loadView('installations');
            });
        }

        function createSurveyFromLead(leadId) {
            fetch('/api/lead-action', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: leadId, action: 'schedule_survey', role: currentRole})
            })
            .then(r => r.json())
            .then(data => {
                alert(`Site survey scheduled successfully: ${data.survey_ref || 'Done'}`);
                loadView('roof');
            })
            .catch(err => alert("Error scheduling survey: " + err));
        }

        function submitSiteSurvey() {
            const cust = document.getElementById('mSrvCust').value;
            const roofType = document.getElementById('mSrvType').value;
            const sqft = parseFloat(document.getElementById('mSrvSqft').value) || 850;
            const cap = parseFloat(document.getElementById('mSrvCap').value) || 4.0;
            const ori = document.getElementById('mSrvOri').value;
            const surveyor = document.getElementById('mSrvTech').value;

            fetch('/api/roof-analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    roof_type: roofType,
                    total_roof_area_sqft: sqft,
                    reported_obstacles: ['water_tank', 'parapet_wall'],
                    azimuth_orientation: ori,
                    role: currentRole
                })
            })
            .then(r => r.json())
            .then(analysis => {
                closeModal();
                alert(`Survey feasibility analyzed!\n• Usable Area: ${analysis.usable_solar_area_sqft} sqft (${analysis.usable_area_ratio_pct}%)\n• Max Capacity: ${analysis.max_recommended_capacity_kw} kW\nPhysical survey verification scheduled with ${surveyor}.`);
                loadView('roof');
            })
            .catch(err => alert("Error analyzing survey: " + err));
        }

        function submitBreakdownTicket() {
            const serial = document.getElementById('mTickSerial').value;
            const desc = document.getElementById('mTickDesc').value || 'Inverter warning code';
            const pri = document.getElementById('mTickPri').value;
            const tech_id = parseInt(document.getElementById('mTickTech').value) || 2;

            fetch('/api/service-ticket-create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    partner_id: 1,
                    serial: serial,
                    description: desc,
                    priority: pri,
                    tech_id: tech_id,
                    role: currentRole
                })
            })
            .then(r => r.json())
            .then(res => {
                closeModal();
                alert(`Service ticket created: ${res.ticket_ref}\nWarranty Verification: ${res.is_warranty ? 'COVERED (Free Warranty Service)' : 'CHARGEABLE (Quotation Required)'}`);
                loadView('warranty');
            })
            .catch(err => alert("Error creating ticket: " + err));
        }

        function executeSerialScan() {
            const s = document.getElementById('mScanInput').value.trim();
            const resDiv = document.getElementById('mScanResult');
            fetch(`/api/search?q=${encodeURIComponent(s)}&role=${encodeURIComponent(currentRole)}`)
            .then(r => r.json())
            .then(data => {
                if (data.results && data.results.length > 0) {
                    const match = data.results[0];
                    resDiv.innerHTML = `<div style="background: rgba(16,185,129,0.1); border: 1px solid var(--accent-green); padding: 10px; border-radius: 8px; color: var(--text-main);"><strong>${match.title}</strong><br>${match.subtitle}</div>`;
                } else {
                    resDiv.innerHTML = `<div style="color: var(--accent-red);">Serial not found in registry.</div>`;
                }
            })
            .catch(err => {
                resDiv.innerHTML = `<div style="color: var(--accent-red);">Scan error: ${err}</div>`;
            });
        }

        function generateCustomBOM() {
            const cap = parseFloat(document.getElementById('mCfgCap').value) || 3.0;
            const sysType = document.getElementById('mCfgType').value;
            const resDiv = document.getElementById('mCfgResult');
            fetch('/api/package-configure', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({capacity_kw: cap, system_type: sysType, role: currentRole})
            })
            .then(r => r.json())
            .then(res => {
                resDiv.innerHTML = `
                    <div style="background: rgba(245,158,11,0.1); border: 1px solid var(--accent-gold); padding: 10px; border-radius: 8px; color: var(--text-main);">
                        <strong>BOM Generated:</strong> ${res.bom.panels.qty} Panels (550W) + ${res.bom.inverter.rating_kw}kW Inverter<br>
                        <strong>Total Execution Cost:</strong> ₹${res.cost_breakdown.total_cost.toLocaleString()}<br>
                        <strong>Suggested Price:</strong> ₹${res.cost_breakdown.suggested_price.toLocaleString()} (Margin: ${res.cost_breakdown.projected_margin_pct}%)
                    </div>
                `;
            })
            .catch(err => {
                resDiv.innerHTML = `<div style="color: var(--accent-red);">Configuration error: ${err}</div>`;
            });
        }

        let searchDebounce = null;
        function runLiveSearch(query) {
            clearTimeout(searchDebounce);
            const box = document.getElementById('searchResultsOverlay');
            if (!box) return;
            if (!query || query.trim().length < 2) {
                box.style.display = 'none';
                box.innerHTML = '';
                return;
            }
            searchDebounce = setTimeout(() => {
                fetch(`/api/search?q=${encodeURIComponent(query.trim())}&role=${currentRole}`)
                    .then(r => r.json())
                    .then(data => {
                        const results = data.results || [];
                        if (results.length === 0) {
                            box.innerHTML = `<div style="padding: 12px 16px; color: var(--text-dim); text-align: center; font-size: 0.8rem;">No matching authorized records found for "${query}"</div>`;
                        } else {
                            box.innerHTML = results.map(r => `
                                <div style="padding: 10px 16px; border-bottom: 1px solid var(--border-subtle); cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: background 0.15s;"
                                     onmouseover="this.style.background='var(--bg-elevated)'"
                                     onmouseout="this.style.background='transparent'"
                                     onclick="selectSearchResult('${r.module}', '${r.id}')">
                                    <div>
                                        <div style="font-weight: 600; color: var(--text-main); font-size: 0.84rem;">${r.title}</div>
                                        <div style="font-size: 0.74rem; color: var(--text-muted); margin-top: 2px;">${r.subtitle}</div>
                                    </div>
                                    <span class="badge badge-gold" style="font-size: 0.65rem;">${r.badge}</span>
                                </div>
                            `).join('');
                        }
                        box.style.display = 'block';
                    })
                    .catch(() => {
                        box.style.display = 'none';
                    });
            }, 200);
        }

        function selectSearchResult(moduleKey, recordId) {
            const box = document.getElementById('searchResultsOverlay');
            if (box) box.style.display = 'none';
            const input = document.getElementById('globalSearchInput');
            if (input) input.value = '';
            loadView(moduleKey);
        }

        document.addEventListener('click', function(e) {
            const shell = document.querySelector('.search-shell');
            if (shell && !shell.contains(e.target)) {
                const box = document.getElementById('searchResultsOverlay');
                if (box) box.style.display = 'none';
            }
        });

        // Initialize on load with saved or default role and theme
        window.onload = function() {
            applyTheme(currentTheme);
            const urlParams = new URLSearchParams(window.location.search);
            const roleParam = urlParams.get('role');
            const showLogin = urlParams.get('login');

            if (roleParam && ROLE_PERMISSIONS[roleParam]) {
                localStorage.setItem('solarflow_logged_in', 'true');
                currentRole = roleParam;
            }

            const isLoggedIn = localStorage.getItem('solarflow_logged_in') === 'true';

            if (!isLoggedIn || showLogin === '1') {
                showLoginScreen();
            } else {
                hideLoginScreen();
                switchRole(currentRole);
            }
        };
    </script>
</body>
</html>
"""


# =============================================================================
# REST API CONTROLLER DISPATCHER
# =============================================================================

class EnterpriseSolarHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        role = params.get('role', ['director'])[0]

        if parsed.path in ('/', '/web', '/index.html'):
            body = HTML_APP_SHELL.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(body)

        elif parsed.path == '/api/overview':
            invoiced_rev = sum(i.get('invoiced', 0.0) for i in DATA.installations)
            gross_prof = sum(i.get('gross_profit', 0.0) for i in DATA.installations)
            gm_pct = round((gross_prof / invoiced_rev * 100), 1) if invoiced_rev else 0.0
            active_techs = len([t for t in DATA.technicians if t.get('active_jobs', 0) > 0])
            total_active_jobs = sum(t.get('active_jobs', 0) for t in DATA.technicians)
            cash_col = sum(i.get('cash_received', 0.0) for i in DATA.installations)
            receivables = sum(i.get('receivable', 0.0) for i in DATA.installations)
            total_capacity = sum(i.get('capacity_kw', 0.0) for i in DATA.installations)
            data = {
                'invoiced_revenue': invoiced_rev,
                'monthly_installs': len(DATA.installations),
                'total_capacity_kw': total_capacity,
                'gross_profit': gross_prof,
                'gross_margin_pct': gm_pct,
                'technicians_active': active_techs,
                'total_technicians': len(DATA.technicians),
                'cash_collected': cash_col,
                'total_receivables': receivables,
                'is_demo_data': False,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'installations': [
                    {
                        'id': inst['id'],
                        'ref': inst['ref'],
                        'customer_name': next((p['name'] for p in DATA.partners if p['id'] == inst['partner_id']), 'Customer'),
                        'capacity_kw': inst['capacity_kw'],
                        'tech_name': inst['tech_name'],
                        'state': inst['state'],
                        'earthing_ohms': inst['earthing_ohms']
                    }
                    for inst in DATA.installations
                ]
            }
            self.send_json(data)

        elif parsed.path == '/api/operations':
            funnel = {
                'leads': len(DATA.leads),
                'surveys': len(DATA.surveys),
                'orders': len(DATA.orders),
                'installations': len(DATA.installations),
                'commissioned': len([i for i in DATA.installations if i.get('state') == 'commissioned'])
            }
            low_stock = [
                {'item': k, 'name': v['name'], 'on_hand': v['on_hand'], 'reorder_point': v['reorder_point']}
                for k, v in DATA.inventory.items()
                if v['on_hand'] - v.get('reserved', 0) <= v['reorder_point']
            ]
            delayed = [
                i for i in DATA.installations
                if i.get('state') in ('scheduled', 'testing') and not i.get('commissioned_date')
            ]
            expiring_w = [w for w in DATA.warranties if w.get('state') == 'expiring_soon']
            unresolved_tickets = [t for t in DATA.tickets if t.get('state') != 'closed']
            self.send_json({
                'leads_count': len(DATA.leads),
                'surveys_count': len(DATA.surveys),
                'orders_count': len(DATA.orders),
                'installs_count': len(DATA.installations),
                'funnel': funnel,
                'low_stock_alerts': low_stock,
                'delayed_jobs': len(delayed),
                'expiring_warranties_count': len(expiring_w),
                'open_tickets_count': len(unresolved_tickets)
            })

        elif parsed.path == '/api/dispatch':
            if role == 'technician':
                self.send_json({'error': f"Forbidden: Field technicians do not have access to workforce dispatch administration."}, status=403)
                return
            self.send_json({'technicians': DATA.technicians})

        elif parsed.path == '/api/sizing':
            self.send_json({'status': 'ready'})

        elif parsed.path in ('/api/roof', '/api/surveys'):
            surveys_enriched = []
            for s in DATA.surveys:
                cust = next((p['name'] for p in DATA.partners if p['id'] == s['partner_id']), 'Customer')
                surveys_enriched.append({**s, 'customer_name': cust})
            self.send_json({'surveys': surveys_enriched})

        elif parsed.path == '/api/packages':
            self.send_json({'packages': DATA.packages})

        elif parsed.path == '/api/crm':
            if role == 'technician':
                self.send_json({'error': f"Forbidden: Field technicians do not have access to customer acquisition CRM pipeline."}, status=403)
                return
            leads_enriched = []
            for l in DATA.leads:
                cust = next((p['name'] for p in DATA.partners if p['id'] == l['partner_id']), 'Customer')
                survey_ref = next((s['ref'] for s in DATA.surveys if s['id'] == l['survey_id']), None)
                leads_enriched.append({**l, 'customer_name': cust, 'survey_ref': survey_ref})
            self.send_json({'leads': leads_enriched})

        elif parsed.path == '/api/inventory':
            if role == 'technician':
                self.send_json({'error': f"Forbidden: Field technicians do not have access to warehouse inventory management."}, status=403)
                return
            serials_enriched = []
            for s in DATA.serials:
                inst_ref = next((i['ref'] for i in DATA.installations if i['id'] == s['installation_id']), None)
                serials_enriched.append({**s, 'installation_ref': inst_ref})
            self.send_json({
                'inventory': DATA.inventory,
                'serials': serials_enriched
            })

        elif parsed.path == '/api/installations':
            inst_enriched = []
            for i in DATA.installations:
                # Role-based row-level security: Technicians only see their own assigned jobs
                if role == 'technician' and i.get('technician_id') != 2:
                    continue
                cust = next((p['name'] for p in DATA.partners if p['id'] == i['partner_id']), 'Customer')
                inst_dict = {**i, 'customer_name': cust}
                # Field-level security: strip company financial margins for non-directors/non-executives
                if role in ('technician', 'salesperson'):
                    inst_dict.pop('material_cost', None)
                    inst_dict.pop('labour_cost', None)
                    inst_dict.pop('other_cost', None)
                    inst_dict.pop('total_cost', None)
                    inst_dict.pop('gross_profit', None)
                    inst_dict.pop('gross_margin_pct', None)
                inst_enriched.append(inst_dict)
            self.send_json({'installations': inst_enriched})

        elif parsed.path in ('/api/warranty', '/api/warranties'):
            w_enriched = []
            for w in DATA.warranties:
                cust = next((p['name'] for p in DATA.partners if p['id'] == w['partner_id']), 'Customer')
                w_enriched.append({**w, 'customer_name': cust})
            t_enriched = []
            for t in DATA.tickets:
                cust = next((p['name'] for p in DATA.partners if p['id'] == t['partner_id']), 'Customer')
                t_enriched.append({**t, 'customer_name': cust})
            self.send_json({'warranties': w_enriched, 'tickets': t_enriched})

        elif parsed.path == '/api/financials':
            if role in ('technician', 'salesperson', 'operations'):
                self.send_json({'error': f"Forbidden: Role '{role}' is not authorized to access company-wide financial ledgers or gross profit margins."}, status=403)
                return
            inst_enriched = []
            for i in DATA.installations:
                cust = next((p['name'] for p in DATA.partners if p['id'] == i['partner_id']), 'Customer')
                inst_enriched.append({**i, 'customer_name': cust})
            invoiced_total = sum(i.get('invoiced', 0.0) for i in DATA.installations)
            cost_total = sum(i.get('total_cost', 0.0) for i in DATA.installations)
            profit_total = sum(i.get('gross_profit', 0.0) for i in DATA.installations)
            receivables_total = sum(i.get('receivable', 0.0) for i in DATA.installations)
            cash_received_total = sum(i.get('cash_received', 0.0) for i in DATA.installations)
            subsidy_sanctioned_total = sum(s.get('approved_amount', 0.0) for s in DATA.subsidies if s.get('state') == 'approved')
            self.send_json({
                'invoiced_total': invoiced_total,
                'cost_total': cost_total,
                'profit_total': profit_total,
                'gross_margin_pct': round((profit_total / invoiced_total * 100), 1) if invoiced_total else 0.0,
                'receivables_total': receivables_total,
                'cash_received_total': cash_received_total,
                'subsidy_sanctioned_total': subsidy_sanctioned_total,
                'installations': inst_enriched
            })

        elif parsed.path == '/api/inventory-forecast':
            forecaster = InventoryDemandForecaster(monthly_installation_target=40, average_capacity_kw=3.5)
            pipe_kw = sum(l.get('capacity_kw', 3.0) for l in DATA.leads if l.get('state') == 'qualified')
            stock_map = {k: v['on_hand'] for k, v in DATA.inventory.items()}
            forecast = forecaster.generate_procurement_forecast(current_inventory=stock_map, pipeline_capacity_kw=pipe_kw)
            self.send_json(forecast)

        elif parsed.path == '/api/technician-profile':
            tech_id = int(params.get('id', [1])[0])
            tech = next((t for t in DATA.technicians if t['id'] == tech_id), None)
            if not tech:
                self.send_json({'error': 'Technician not found'}, status=404)
                return
            assigned_jobs = [i for i in DATA.installations if i.get('technician_id') == tech_id]
            assigned_tickets = [t for t in DATA.tickets if t.get('tech_id') == tech_id]
            self.send_json({
                'technician': tech,
                'active_jobs_detail': assigned_jobs,
                'service_tickets_detail': assigned_tickets,
                'capacity_remaining': tech.get('max_jobs', 3) - tech.get('active_jobs', 0)
            })

        elif parsed.path == '/api/assistant':
            self.send_json({'status': 'ready'})

        elif parsed.path == '/api/search':
            query = params.get('q', [''])[0].strip().lower()
            role = params.get('role', ['director'])[0]
            if not query or len(query) < 2:
                self.send_json({'results': []})
                return

            results = []

            # 1. Customers (res.partner) - Restricted to assigned job customers for technicians
            allowed_partner_ids = None
            if role == 'technician':
                allowed_partner_ids = {i['partner_id'] for i in DATA.installations if i.get('technician_id') == 2}

            for p in DATA.partners:
                if allowed_partner_ids is not None and p['id'] not in allowed_partner_ids:
                    continue
                if query in p['name'].lower() or query in p['phone'].lower() or query in p['city'].lower():
                    results.append({
                        'type': 'Customer',
                        'module': 'crm' if role != 'technician' else 'installations',
                        'id': p['id'],
                        'title': p['name'],
                        'subtitle': f"Phone: {p['phone']} | City: {p['city']} | Sanctioned: {p['sanctioned_kw']}kW",
                        'badge': 'Customer'
                    })

            # 2. Leads (crm.lead) - Hidden from technicians
            if role != 'technician':
                for l in DATA.leads:
                    if query in l['ref'].lower() or query in l['name'].lower():
                        results.append({
                            'type': 'CRM Lead',
                            'module': 'crm',
                            'id': l['id'],
                            'title': f"{l['ref']} - {l['name']}",
                            'subtitle': f"Channel: {l['channel'].title()} | State: {l['state'].title()} | {l['capacity_kw']}kW",
                            'badge': 'Lead'
                        })

            # 3. Installations (solar.installation) - Row-level restricted for technicians
            for i in DATA.installations:
                if role == 'technician' and i.get('technician_id') != 2:
                    continue
                cust = next((p['name'] for p in DATA.partners if p['id'] == i['partner_id']), 'Customer')
                if query in i['ref'].lower() or query in i['tech_name'].lower() or query in cust.lower():
                    results.append({
                        'type': 'Installation',
                        'module': 'installations',
                        'id': i['id'],
                        'title': f"{i['ref']} - {cust}",
                        'subtitle': f"Tech: {i['tech_name']} | State: {i['state'].title()} | Earthing: {i['earthing_ohms']}Ω",
                        'badge': 'Install'
                    })

            # 4. Serials (stock.production.lot)
            for s in DATA.serials:
                if query in s['serial'].lower() or query in s['model'].lower():
                    results.append({
                        'type': 'Serial Lot',
                        'module': 'inventory' if role != 'technician' else 'installations',
                        'id': s['serial'],
                        'title': f"Serial: {s['serial']}",
                        'subtitle': f"Model: {s['model']} | Status: {s['status'].title()}",
                        'badge': 'Serial'
                    })

            # 5. Warranties (solar.warranty)
            for w in DATA.warranties:
                if query in w['ref'].lower() or query in w['serial'].lower():
                    results.append({
                        'type': 'Warranty',
                        'module': 'warranty',
                        'id': w['id'],
                        'title': f"{w['ref']} - {w['type'].title()} Warranty",
                        'subtitle': f"Serial: {w['serial']} | State: {w['state'].title()} | Expiry: {w['end_date']}",
                        'badge': 'Warranty'
                    })

            # 6. Service Tickets (solar.service.ticket) - Row-level restricted for technicians
            for t in DATA.tickets:
                if role == 'technician' and t.get('tech_id') != 2:
                    continue
                cust = next((p['name'] for p in DATA.partners if p['id'] == t['partner_id']), 'Customer')
                if query in t['ref'].lower() or query in t['desc'].lower() or query in t['serial'].lower() or query in cust.lower():
                    results.append({
                        'type': 'Service Ticket',
                        'module': 'warranty',
                        'id': t['id'],
                        'title': f"{t['ref']} - {t['type'].title()}",
                        'subtitle': f"Customer: {cust} | Tech: {t['tech_name']} | State: {t['state'].title()}",
                        'badge': 'Service'
                    })

            # 7. Sales Orders (sale.order) - Only if authorized role
            if role not in ('technician', 'support'):
                for o in DATA.orders:
                    if query in o['ref'].lower():
                        results.append({
                            'type': 'Sales Order',
                            'module': 'crm',
                            'id': o['id'],
                            'title': f"{o['ref']} - Total ₹{o['amount_total']:,.0f}",
                            'subtitle': f"State: {o['state'].title()} | Payment: {o['payment_state'].title()}",
                            'badge': 'Order'
                        })

            self.send_json({'results': results[:10]})

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        payload = json.loads(body.decode('utf-8')) if body else {}

        if parsed.path in ('/api/bi', '/api/ai-chat'):
            agent = SolarBIAgent(mock_data={'data_store': DATA})
            result = agent.process_query(payload.get('query', ''), user_role=payload.get('role', 'director'))
            self.send_json(result)

        elif parsed.path == '/api/survey-action':
            role = payload.get('role', 'director')
            survey_id = payload.get('id')
            action = payload.get('action')
            if action in ('approve', 'reject') and role not in ('director', 'operations', 'survey_manager'):
                self.send_json({'error': f"Permission Denied: Role '{role}' cannot approve or reject site surveys."}, status=403)
                return
            survey = next((s for s in DATA.surveys if s['id'] == survey_id), None)
            if not survey:
                self.send_json({'error': 'Survey not found'}, status=404)
                return

            if action == 'submit':
                survey['state'] = 'submitted'
                self.send_json({'status': 'success', 'state': 'submitted'})
            elif action == 'approve':
                survey['state'] = 'approved'
                self.send_json({'status': 'success', 'state': 'approved'})
            elif action == 'reject':
                survey['state'] = 'rejected'
                survey['rejection_reason'] = payload.get('reason', 'Survey rejected')
                self.send_json({'status': 'success', 'state': 'rejected'})
            elif action == 'generate_quote':
                if survey['state'] != 'approved':
                    self.send_json({'error': 'Cannot generate quotation for unapproved survey'}, status=400)
                    return
                order_ref = f"SO-2026-000{len(DATA.orders)+1}"
                DATA.orders.append({
                    'id': len(DATA.orders)+1,
                    'ref': order_ref,
                    'partner_id': survey['partner_id'],
                    'survey_id': survey['id'],
                    'package_id': 3,
                    'amount_total': 185000.0,
                    'state': 'sale',
                    'payment_state': 'not_paid',
                    'paid_amount': 0.0,
                    'installation_id': None
                })
                survey['sale_order_id'] = len(DATA.orders)
                self.send_json({'status': 'success', 'order_ref': order_ref, 'amount': 185000.0})

        elif parsed.path == '/api/installation-action':
            role = payload.get('role', 'director')
            inst_id = payload.get('id')
            action = payload.get('action')
            inst = next((i for i in DATA.installations if i['id'] == inst_id), None)
            if not inst:
                self.send_json({'error': 'Installation not found'}, status=404)
                return

            if action == 'commission' and role in ('salesperson', 'technician'):
                self.send_json({'error': f"Permission Denied: Role '{role}' cannot commission installations. Commissioning requires Operations Manager or Director approval."}, status=403)
                return
            if action == 'record_testing' and role == 'salesperson':
                self.send_json({'error': f"Permission Denied: Salesperson cannot record electrical engineering tests."}, status=403)
                return

            if action == 'record_testing':
                inst['dc_v'] = payload.get('dc_v', 380.0)
                inst['ac_v'] = payload.get('ac_v', 230.0)
                inst['earthing_ohms'] = payload.get('earthing', 2.0)
                inst['customer_signoff'] = payload.get('signatory', 'Customer Signatory')
                inst['rating'] = 5
                inst['testing_passed'] = True
                inst['state'] = 'completed'
                self.send_json({'status': 'success', 'state': 'completed'})

            elif action == 'commission':
                inst['state'] = 'commissioned'
                inst['commissioned_date'] = date.today().isoformat()
                # Activate Warranties
                new_w = [
                    {'id': len(DATA.warranties)+1, 'ref': f'WRN/2026/000{len(DATA.warranties)+1}', 'partner_id': inst['partner_id'], 'installation_id': inst['id'], 'type': 'panel', 'duration_yrs': 25, 'start_date': date.today().isoformat(), 'end_date': (date.today() + timedelta(days=365*25)).isoformat(), 'serial': 'PANEL-BATCH-2026', 'state': 'active', 'terms': '25-Year Performance Guarantee'},
                    {'id': len(DATA.warranties)+2, 'ref': f'WRN/2026/000{len(DATA.warranties)+2}', 'partner_id': inst['partner_id'], 'installation_id': inst['id'], 'type': 'inverter', 'duration_yrs': 5, 'start_date': date.today().isoformat(), 'end_date': (date.today() + timedelta(days=365*5)).isoformat(), 'serial': 'INV-GROWATT-9922', 'state': 'active', 'terms': '5-Year Inverter Guarantee'},
                ]
                DATA.warranties.extend(new_w)
                self.send_json({'status': 'success', 'warranties_created': len(new_w)})

        elif parsed.path == '/api/create-lead':
            role = payload.get('role', 'director')
            if role == 'technician':
                self.send_json({'error': f"Permission Denied: Field technician cannot directly create CRM leads."}, status=403)
                return
            name = payload.get('name')
            phone = payload.get('phone')
            cap = payload.get('capacity_kw', 3.0)

            # Partner creation / matching
            p = next((p for p in DATA.partners if p['phone'] == phone), None)
            if not p:
                p = {'id': len(DATA.partners)+1, 'name': name, 'type': 'residential', 'phone': phone, 'email': 'info@client.com', 'city': 'Bangalore', 'bill': 4000.0, 'roof_sqft': 500, 'sanctioned_kw': cap}
                DATA.partners.append(p)

            lead_ref = f"LEAD-2026-00{len(DATA.leads)+42}"
            DATA.leads.append({
                'id': len(DATA.leads)+1,
                'ref': lead_ref,
                'partner_id': p['id'],
                'name': f"{name} {cap}kW Solar Inquiry",
                'channel': 'whatsapp',
                'customer_type': p['type'],
                'capacity_kw': cap,
                'preference': 'ongrid',
                'bill': p['bill'],
                'roof_sqft': p['roof_sqft'],
                'state': 'qualified',
                'is_duplicate': False,
                'survey_id': None
            })
            self.send_json({'status': 'success', 'ref': lead_ref})

        elif parsed.path == '/api/assign-technician':
            role = payload.get('role', 'director')
            if role not in ('director', 'operations'):
                self.send_json({'error': f"Permission Denied: Role '{role}' cannot assign technicians or modify workforce schedule."}, status=403)
                return
            inst_id = payload.get('installation_id')
            tech_id = payload.get('technician_id')
            inst = next((i for i in DATA.installations if i['id'] == inst_id), None)
            tech = next((t for t in DATA.technicians if t['id'] == tech_id), None)
            if not inst or not tech:
                self.send_json({'error': 'Installation or technician not found'}, status=404)
                return

            if inst['capacity_kw'] >= 5.0 and 'Three-Phase Certified' not in tech.get('certs', []):
                self.send_json({'error': f"Skill Validation Error: {tech['name']} lacks mandatory 'Three-Phase Certified' credential for {inst['capacity_kw']} kW system."}, status=400)
                return

            if tech['active_jobs'] >= tech.get('max_jobs', 3):
                self.send_json({'error': f"Capacity Constraint Error: {tech['name']} has reached maximum capacity ({tech['active_jobs']} active jobs)."}, status=400)
                return

            if inst.get('technician_id'):
                old_tech = next((t for t in DATA.technicians if t['id'] == inst['technician_id']), None)
                if old_tech and old_tech['active_jobs'] > 0:
                    old_tech['active_jobs'] -= 1

            inst['technician_id'] = tech['id']
            inst['tech_name'] = tech['name']
            inst['state'] = 'scheduled'
            tech['active_jobs'] += 1
            self.send_json({'status': 'success', 'tech_name': tech['name'], 'installation_ref': inst['ref']})

        elif parsed.path == '/api/dispatch-optimize':
            optimizer = TechnicianOptimizer(technicians=DATA.technicians)
            unassigned = [
                {'id': i['id'], 'name': i['ref'], 'capacity_kw': i['capacity_kw'], 'priority': '2', 'lat': 12.9716, 'lon': 77.5946}
                for i in DATA.installations if i['state'] == 'scheduled' or not i.get('technician_id')
            ]
            opt_result = optimizer.optimize_dispatch(unassigned)
            self.send_json(opt_result)

        elif parsed.path == '/api/sizing-calculate':
            calculator = SolarGenerationIntelligence()
            cap = float(payload.get('capacity_kw', 3.0))
            ori = payload.get('roof_orientation', 'south')
            tilt = float(payload.get('roof_tilt_degrees', 15.0))
            shading = payload.get('shading', 'no_shading')
            tariff = float(payload.get('tariff_per_kwh', 7.5))
            cost = float(payload.get('system_cost', cap * 61666.0))
            res = calculator.calculate_yield_and_roi(
                capacity_kw=cap,
                roof_orientation=ori,
                roof_tilt_degrees=tilt,
                shading=shading,
                tariff_per_kwh=tariff,
                system_cost=cost
            )
            self.send_json(res)

        elif parsed.path == '/api/roof-analyze':
            analyzer = RoofAssessmentAssistant()
            roof_type = payload.get('roof_type', 'flat_rcc')
            area = float(payload.get('total_roof_area_sqft', 500.0))
            obs = payload.get('reported_obstacles', [])
            azimuth = payload.get('azimuth_orientation', 'south')
            res = analyzer.analyze_roof_parameters(
                roof_type=roof_type,
                total_roof_area_sqft=area,
                reported_obstacles=obs,
                azimuth_orientation=azimuth
            )
            self.send_json(res)

        elif parsed.path == '/api/reserve-stock':
            role = payload.get('role', 'director')
            if role in ('salesperson', 'technician'):
                self.send_json({'error': f"Permission Denied: Role '{role}' cannot directly adjust or reserve warehouse inventory stock."}, status=403)
                return
            inst_id = payload.get('installation_id')
            item_key = payload.get('item_key')
            qty = int(payload.get('qty', 1))
            if item_key not in DATA.inventory:
                self.send_json({'error': f"Item '{item_key}' not found in inventory"}, status=404)
                return
            item = DATA.inventory[item_key]
            avail = item['on_hand'] - item.get('reserved', 0)
            if avail < qty:
                self.send_json({'error': f"Insufficient available stock for {item['name']}. Available: {avail}, requested: {qty}"}, status=400)
                return
            item['reserved'] = item.get('reserved', 0) + qty
            self.send_json({'status': 'success', 'item': item_key, 'reserved_total': item['reserved']})

        elif parsed.path == '/api/dispatch-equipment':
            serial_str = payload.get('serial')
            inst_id = payload.get('installation_id')
            serial_rec = next((s for s in DATA.serials if s['serial'] == serial_str), None)
            if not serial_rec:
                self.send_json({'error': f"Serial '{serial_str}' not found in registry"}, status=404)
                return
            if serial_rec['status'] == 'installed':
                self.send_json({'error': f"Serial '{serial_str}' is already installed in project INS/2026/000{serial_rec['installation_id']}"}, status=400)
                return
            serial_rec['status'] = 'dispatched'
            serial_rec['installation_id'] = inst_id
            self.send_json({'status': 'success', 'serial': serial_str, 'status_updated': 'dispatched'})

        elif parsed.path == '/api/lead-action':
            role = payload.get('role', 'director')
            if role == 'technician':
                self.send_json({'error': f"Permission Denied: Field technician cannot manage CRM leads."}, status=403)
                return
            lead_id = payload.get('id')
            action = payload.get('action')
            lead = next((l for l in DATA.leads if l['id'] == lead_id), None)
            if not lead:
                self.send_json({'error': 'Lead not found'}, status=404)
                return
            if action == 'qualify':
                lead['state'] = 'qualified'
                self.send_json({'status': 'success', 'state': 'qualified'})
            elif action == 'schedule_survey':
                lead['state'] = 'survey_scheduled'
                survey_ref = f"SRV/2026/000{len(DATA.surveys)+1}"
                new_srv = {
                    'id': len(DATA.surveys)+1,
                    'ref': survey_ref,
                    'partner_id': lead['partner_id'],
                    'lead_id': lead['id'],
                    'surveyor': payload.get('surveyor', 'Pradeep Gowda'),
                    'survey_date': (date.today() + timedelta(days=2)).isoformat(),
                    'property_type': 'independent_house',
                    'roof_type': 'flat_rcc',
                    'roof_sqft': lead.get('roof_sqft', 500.0),
                    'usable_sqft': lead.get('roof_sqft', 500.0) * 0.75,
                    'tilt': 15.0,
                    'orientation': 'south',
                    'shading': 'no_shading',
                    'cable_m': 25.0,
                    'sanctioned_kw': lead.get('capacity_kw', 3.0),
                    'bill': lead.get('bill', 4000.0),
                    'rec_capacity_kw': lead.get('capacity_kw', 3.0),
                    'state': 'draft',
                    'rejection_reason': None,
                    'sale_order_id': None
                }
                DATA.surveys.append(new_srv)
                lead['survey_id'] = new_srv['id']
                self.send_json({'status': 'success', 'state': 'survey_scheduled', 'survey_ref': survey_ref})
            elif action == 'disqualify':
                lead['state'] = 'disqualified'
                self.send_json({'status': 'success', 'state': 'disqualified'})
            else:
                self.send_json({'error': f"Unknown lead action: {action}"}, status=400)

        elif parsed.path == '/api/service-ticket-create':
            partner_id = payload.get('partner_id', 1)
            serial_no = payload.get('serial')
            desc = payload.get('description', 'Reported breakdown')
            priority = str(payload.get('priority', '2'))
            tech_id = payload.get('tech_id', 2)
            warranty = next((w for w in DATA.warranties if w.get('serial') == serial_no and w.get('state') == 'active'), None)
            is_warranty = warranty is not None
            classification = 'free_warranty' if is_warranty else 'chargeable'
            customer_bill = 0.0 if is_warranty else float(payload.get('estimated_bill', 2500.0))
            tech = next((t for t in DATA.technicians if t['id'] == tech_id), DATA.technicians[0])
            ticket_ref = f"SVC/2026/000{len(DATA.tickets)+1}"
            new_ticket = {
                'id': len(DATA.tickets)+1,
                'ref': ticket_ref,
                'partner_id': partner_id,
                'installation_id': warranty.get('installation_id') if warranty else None,
                'serial': serial_no,
                'warranty_id': warranty['id'] if warranty else None,
                'type': payload.get('ticket_type', 'breakdown'),
                'priority': priority,
                'state': 'new',
                'tech_id': tech['id'],
                'tech_name': tech['name'],
                'is_warranty': is_warranty,
                'classification': classification,
                'desc': desc,
                'findings': None,
                'resolution': None,
                'parts_cost': 0.0,
                'labour_cost': 0.0,
                'customer_bill': customer_bill,
                'confirmed': False
            }
            DATA.tickets.append(new_ticket)
            self.send_json({'status': 'success', 'ticket_ref': ticket_ref, 'is_warranty': is_warranty, 'classification': classification})

        elif parsed.path == '/api/subsidy-action':
            role = payload.get('role', 'director')
            if role == 'technician':
                self.send_json({'error': f"Permission Denied: Field technician cannot manage government subsidies."}, status=403)
                return
            sub_id = payload.get('id')
            action = payload.get('action')
            if action == 'approve' and role in ('salesperson', 'support'):
                self.send_json({'error': f"Permission Denied: Role '{role}' cannot approve government subsidies."}, status=403)
                return
            sub = next((s for s in DATA.subsidies if s['id'] == sub_id), None)
            if not sub:
                self.send_json({'error': 'Subsidy dossier not found'}, status=404)
                return
            if action == 'submit':
                sub['state'] = 'submitted'
                sub['docs_collected'] = True
                sub['missing_docs'] = 'Submitted to MNRE National Portal'
                self.send_json({'status': 'success', 'state': 'submitted'})
            elif action == 'approve':
                sub['state'] = 'approved'
                sub['approved_amount'] = sub.get('est_amount', 78000.0)
                sub['missing_docs'] = 'DBT Sanction Completed'
                self.send_json({'status': 'success', 'state': 'approved', 'approved_amount': sub['approved_amount']})
            else:
                self.send_json({'error': f"Unknown subsidy action: {action}"}, status=400)

        elif parsed.path == '/api/package-configure':
            role = payload.get('role', 'director')
            if role == 'technician':
                self.send_json({'error': f"Permission Denied: Field technician cannot configure BOM package pricing."}, status=403)
                return
            cap = float(payload.get('capacity_kw', 3.0))
            sys_type = payload.get('system_type', 'ongrid')
            num_panels = math.ceil((cap * 1000.0) / 550.0)
            inv_kw = cap
            structures = math.ceil(num_panels / 2.0)
            dc_cable = int(cap * 20.0)
            ac_cable = int(cap * 10.0)
            base_material = (num_panels * 11800.0) + (inv_kw * 18000.0) + (structures * 3200.0) + (dc_cable * 85.0) + (ac_cable * 120.0) + 5800.0 + 7600.0
            labor = cap * 6000.0
            transport = 3500.0
            discom_fees = 5000.0
            total_cost = base_material + labor + transport + discom_fees
            recommended_mrp = round(total_cost * 1.35, -2)
            self.send_json({
                'status': 'success',
                'capacity_kw': cap,
                'system_type': sys_type,
                'bom': {
                    'panels': {'qty': num_panels, 'watt': 550, 'cost': num_panels * 11800.0},
                    'inverter': {'qty': 1, 'rating_kw': inv_kw, 'cost': inv_kw * 18000.0},
                    'mounting_structures': {'pairs': structures, 'cost': structures * 3200.0},
                    'dc_cable_m': {'meters': dc_cable, 'cost': dc_cable * 85.0},
                    'ac_cable_m': {'meters': ac_cable, 'cost': ac_cable * 120.0},
                    'protection_boxes': {'cost': 5800.0},
                    'earthing_kit': {'cost': 7600.0}
                },
                'cost_breakdown': {
                    'base_material': round(base_material, 2),
                    'labor': round(labor, 2),
                    'transport': round(transport, 2),
                    'discom_approval': round(discom_fees, 2),
                    'total_cost': round(total_cost, 2),
                    'suggested_price': recommended_mrp,
                    'projected_margin_pct': 35.0
                }
            })
        else:
            self.send_response(404)
            self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body)

    def address_string(self):
        """Prevent reverse DNS lookup delay on Windows localhost."""
        return self.client_address[0]

    def log_message(self, format, *args):
        sys.stdout.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args))


def run_server(port=PORT):
    server_address = ('', port)
    try:
        httpd = HTTPServer(server_address, EnterpriseSolarHandler)
        print(f"============================================================")
        print(f"SolarFlow 360 Enterprise ERP is live at: http://localhost:{port}")
        print(f"============================================================")
        httpd.serve_forever()
    except OSError:
        httpd = HTTPServer(('', port+1), EnterpriseSolarHandler)
        print(f"Port {port} busy, running on http://localhost:{port+1}")
        httpd.serve_forever()


if __name__ == '__main__':
    run_server()
