# -*- coding: utf-8 -*-
"""
Dashboard controller for DTP School Inventory.
Provides JSON endpoints for the OWL dashboard component.
Each method corresponds to a specific visual/widget on the dashboard.
"""

from odoo import http, fields
from odoo.http import request

import logging
import json

_logger = logging.getLogger(__name__)

class DtpSchoolInventoryDashboard(http.Controller):

    @http.route('/dtp_school_inventory/dashboard/data', type='jsonrpc', auth='user')
    def get_dashboard_data(self, filters=None):
        """
        Main endpoint: returns all dashboard data in one call to minimize round-trips.
        `filters` is a dict that may contain:
            - region: str | None
            - school_type: str | None
            - school_id: int | None
        """
        filters = filters or {}
        _logger.info("Dashboard Filters: %s", json.dumps(filters, indent=4, default=str))
        result = {
            'kpis': self._get_kpi_cards(filters),
            'pickings_by_state': self._get_pickings_by_state(filters),
            'top_products': self._get_top_products(filters),
            'schools_overview': self._get_schools_overview(filters),
            'pickings_trend': self._get_pickings_trend(filters),
            'filter_options': self._get_filter_options(),
        }
        _logger.info("Dashboard Data Result:\n%s", json.dumps(result, indent=4, default=str))
        return result

    # ------------------------------------------------------------------
    # Private helpers – each one owns a single visual
    # ------------------------------------------------------------------

    def _build_school_domain(self, filters):
        """Build a base domain for res.partner filtered by dashboard context."""
        domain = [('is_school', '=', True)]
        if filters.get('region'):
            domain.append(('region', '=', filters['region']))
        if filters.get('school_type'):
            domain.append(('school_type', '=', filters['school_type']))
        if filters.get('school_id'):
            domain.append(('id', '=', filters['school_id']))
        return domain

    def _build_picking_domain(self, filters):
        """Build a domain for stock.picking filtered by school (partner_id)."""
        school_domain = self._build_school_domain(filters)
        schools = request.env['res.partner'].search(school_domain)
        domain = [('partner_id', 'in', schools.ids)]
        return domain

    # --- KPI Cards ---

    def _get_kpi_cards(self, filters):
        """
        Visual: KPI summary cards at top of dashboard.
        Returns counts for schools, pending deliveries, done deliveries, waiting transfers.
        """
        School = request.env['res.partner']
        Picking = request.env['stock.picking']

        school_domain = self._build_school_domain(filters)
        picking_domain = self._build_picking_domain(filters)

        total_schools = School.search_count(school_domain)
        total_classes = request.env['res.partner.class'].search_count(
            [('school_id', 'in', School.search(school_domain).ids)]
        )
        pending_pickings = Picking.search_count(picking_domain + [('state', 'in', ['confirmed', 'waiting', 'assigned'])])
        draft_pickings = Picking.search_count(picking_domain + [('state', '=', 'draft')])
    
        late_pickings = Picking.search_count(picking_domain + [
            ('state', 'in', ['confirmed', 'waiting', 'assigned']),
            ('scheduled_date', '<=', fields.Datetime.now()),
        ])

        low_stock_products = request.env['stock.warehouse.orderpoint'].search_count(
            [('qty_to_order', '>', 0.0)]
        )

        return {
            'total_schools': total_schools,
            'total_classes': total_classes,
            'pending_pickings': pending_pickings,
            'draft_pickings': draft_pickings,
            'late_pickings': late_pickings,
            'low_stock_products': low_stock_products,
        }

    # --- Bar / Donut: Pickings by state ---

    def _get_pickings_by_state(self, filters):
        """
        Visual: Donut chart – breakdown of stock.picking by state.
        """
        Picking = request.env['stock.picking']
        picking_domain = self._build_picking_domain(filters)

        state_labels = {
            'draft': 'Nháp',
            'waiting': 'Chờ',
            'confirmed': 'Đã xác nhận',
            'assigned': 'Sẵn sàng',
            'done': 'Hoàn thành',
            'cancel': 'Đã hủy',
        }

        result = []
        for state, label in state_labels.items():
            count = Picking.search_count(picking_domain + [('state', '=', state)])
            if count:
                result.append({'state': state, 'label': label, 'count': count})
        return result

    # --- Bar chart: Top products by outgoing quantity ---

    def _get_top_products(self, filters):
        """
        Visual: Horizontal bar chart – top 8 products delivered to schools.
        Groups stock.move.line by product where picking state = done.
        """
        Picking = request.env['stock.picking']
        picking_domain = self._build_picking_domain(filters) + [('state', '=', 'done')]
        done_pickings = Picking.search(picking_domain)

        if not done_pickings:
            return []

        MoveLines = request.env['stock.move.line']
        data = MoveLines._read_group(
            domain=[('picking_id', 'in', done_pickings.ids)],
            groupby=['product_id'],
            aggregates=['quantity:sum'],
            order='quantity:sum desc',
            limit=8,
        )
        return [
            {
                'product_id': product.id,
                'product_name': product.display_name,
                'qty': qty_sum,
            }
            for product, qty_sum in data if product
        ]

    # --- Table: Schools overview ---

    def _get_schools_overview(self, filters):
        """
        Visual: Table – per-school stats: #classes, #subjects, #pending pickings, #done pickings.
        """
        School = request.env['res.partner']
        Picking = request.env['stock.picking']
        school_domain = self._build_school_domain(filters)
        schools = School.search(school_domain, limit=20)

        school_type_labels = {
            'kindergarten': 'Mầm non',
            'primary': 'Tiểu học',
            'secondary': 'THCS',
        }
        region_labels = {
            'hcm': 'HCM',
            'mekong': 'Mekong',
            'hue': 'Huế',
        }

        rows = []
        for school in schools:
            class_count = len(school.class_ids)
            subject_count = sum(len(c.subject_ids) for c in school.class_ids)
            pending = Picking.search_count([('partner_id', '=', school.id), ('state', 'in', ['confirmed', 'waiting', 'assigned'])])
            done = Picking.search_count([('partner_id', '=', school.id), ('state', '=', 'done')])
            rows.append({
                'id': school.id,
                'name': school.name,
                'school_type': school_type_labels.get(school.school_type, school.school_type),
                'school_type_raw': school.school_type,
                'region': region_labels.get(school.region, school.region),
                'class_count': class_count,
                'subject_count': subject_count,
                'pending_pickings': pending,
            })
        return rows

    # --- Line/Bar chart: Pickings trend last 6 months ---

    def _get_pickings_trend(self, filters):
        """
        Visual: Line chart – number of done pickings per month, last 6 months.
        """
        cr = request.env.cr
        picking_domain = self._build_picking_domain(filters) + [('state', '=', 'done')]
        school_domain = self._build_school_domain(filters)
        schools = request.env['res.partner'].search(school_domain)

        partner_ids_str = ','.join(str(i) for i in schools.ids) if schools.ids else '0'

        cr.execute("""
            SELECT
                TO_CHAR(date_done, 'YYYY-MM') AS month,
                COUNT(*) AS count
            FROM stock_picking
            WHERE state = 'done'
              AND partner_id IN (%s)
              AND date_done >= NOW() - INTERVAL '6 months'
            GROUP BY month
            ORDER BY month ASC
        """ % partner_ids_str)

        rows = cr.fetchall()
        return [{'month': r[0], 'count': r[1]} for r in rows]

    # --- Filter options ---

    def _get_filter_options(self):
        """
        Returns available filter values for the context filter panel.
        """
        return {
            'regions': [
                {'value': 'hcm', 'label': 'HCM'},
                {'value': 'mekong', 'label': 'Mekong'},
                {'value': 'hue', 'label': 'Huế'},
            ],
            'school_types': [
                {'value': 'kindergarten', 'label': 'Mầm non'},
                {'value': 'primary', 'label': 'Tiểu học'},
                {'value': 'secondary', 'label': 'THCS'},
            ],
            'schools': request.env['res.partner'].search_read(
                [('is_school', '=', True)],
                fields=['id', 'name'],
                order='name asc',
            ),
        }
