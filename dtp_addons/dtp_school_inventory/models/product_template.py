# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_storable = fields.Boolean(
        'Track Inventory', store=True, compute='compute_is_storable', readonly=False,
        default=True, precompute=True, tracking=True, help='A storable product is a product for which you manage stock.')

    need_recall = fields.Boolean(string='Cần thu hồi', default=False, tracking=True)
