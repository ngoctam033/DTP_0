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

    subject_id = fields.Many2one(
        'res.partner.subject',
        string='Subject',
        help='The school subject this delivery is for.',
    )

    @api.onchange('subject_id')
    def _onchange_subject_id(self):
        """
        Auto-load products from the subject's supply list into the picking lines.
        Clears existing lines before loading new ones.
        """
        # Command (5, 0, 0) clears all existing records in the One2many field
        new_lines = [(5, 0, 0)]

        if self.subject_id and self.subject_id.supply_product_ids:
            for product in self.subject_id.supply_product_ids:
                new_lines.append((0, 0, {
                    'description_picking': product.display_name,
                    'product_id': product.id,
                    'product_uom_qty': 1.0,
                    'product_uom': product.uom_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'picking_id': self._origin.id if self._origin else False,
                }))
        
        self.move_ids = new_lines

    @api.depends('picking_type_code', 'return_deadline_date')
    def _compute_return_days_left(self):
        for picking in self:
            if picking.picking_type_code != 'outgoing' or not picking.return_deadline_date:
                picking.return_days_left = 0
                continue

            today = fields.Date.context_today(picking)
            picking.return_days_left = (picking.return_deadline_date - today).days

    def _action_done(self):
        """
        Propagate partner_id (school/unit) → owner_id on destination stock.quant
        after an outgoing picking is validated.
        Flow: stock.picking → stock.quant
        """
        result = super()._action_done()

        # Only process outgoing pickings that have a partner (school/unit)
        for picking in self.filtered(
            lambda p: p.picking_type_code == 'outgoing' and p.partner_id and p.state == 'done'
        ):
            partner = picking.partner_id
            for move in picking.move_ids.filtered(lambda m: m.state == 'done'):
                dest_location = move.location_dest_id
                product = move.product_id
                lot_ids = move.move_line_ids.mapped('lot_id').ids

                domain = [
                    ('location_id', '=', dest_location.id),
                    ('product_id', '=', product.id),
                ]
                if lot_ids:
                    domain.append(('lot_id', 'in', lot_ids))

                quants = self.env['stock.quant'].sudo().search(domain)
                if quants:
                    quants.sudo().write({'owner_id': partner.id})

        return result
