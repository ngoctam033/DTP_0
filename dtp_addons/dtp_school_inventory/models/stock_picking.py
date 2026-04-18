# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    return_deadline_date = fields.Date(
        string='Return Deadline',
        help='Expected return date for this delivery.',
    )
    return_days_left = fields.Integer(
        string='Days Until Return',
        compute='_compute_return_days_left',
    )

    partner_id = fields.Many2one(
        'res.partner', 'Contact',
        required=True,
        check_company=True, index='btree_not_null')

    @api.depends('picking_type_code', 'return_deadline_date')
    def _compute_return_days_left(self):
        for picking in self:
            if picking.picking_type_code != 'outgoing' or not picking.return_deadline_date:
                picking.return_days_left = 0
                continue

            today = fields.Date.context_today(picking)
            picking.return_days_left = (picking.return_deadline_date - today).days
