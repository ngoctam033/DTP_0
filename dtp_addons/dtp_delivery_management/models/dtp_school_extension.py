from odoo import fields, models


class DtpSchool(models.Model):
    _inherit = 'dtp.school'

    delivery_order_ids = fields.One2many('dtp.delivery.order', 'school_id', string='Đơn giao hàng')
    return_order_ids = fields.One2many('dtp.return.order', 'school_id', string='Đơn thu hồi')
    delivery_count = fields.Integer(string='Số đơn giao', compute='_compute_logistics_counts')
    return_count = fields.Integer(string='Số đơn thu hồi', compute='_compute_logistics_counts')
    transfer_count = fields.Integer(string='Số đơn luân chuyển', compute='_compute_logistics_counts')
    history_count = fields.Integer(string='Lịch sử hàng hóa', compute='_compute_logistics_counts')

    def _compute_logistics_counts(self):
        transfer_model = self.env['dtp.transfer.order']
        history_model = self.env['dtp.product.history']
        for school in self:
            school.delivery_count = len(school.delivery_order_ids)
            school.return_count = len(school.return_order_ids)
            school.transfer_count = transfer_model.search_count([
                '|',
                ('source_school_id', '=', school.id),
                ('destination_school_id', '=', school.id),
            ])
            school.history_count = history_model.search_count([
                ('school_id', '=', school.id),
            ])

    def action_view_delivery_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đơn giao hàng',
            'res_model': 'dtp.delivery.order',
            'view_mode': 'list,form',
            'domain': [('school_id', '=', self.id)],
            'context': {'default_school_id': self.id},
        }

    def action_view_return_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đơn thu hồi',
            'res_model': 'dtp.return.order',
            'view_mode': 'list,form',
            'domain': [('school_id', '=', self.id)],
            'context': {'default_school_id': self.id},
        }

    def action_view_transfer_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Đơn luân chuyển',
            'res_model': 'dtp.transfer.order',
            'view_mode': 'list,form',
            'domain': ['|', ('source_school_id', '=', self.id), ('destination_school_id', '=', self.id)],
            'context': {'default_source_school_id': self.id},
        }

    def action_view_product_history(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lịch sử cấp phát thiết bị',
            'res_model': 'dtp.product.history',
            'view_mode': 'list,form',
            'domain': [('school_id', '=', self.id)],
        }
