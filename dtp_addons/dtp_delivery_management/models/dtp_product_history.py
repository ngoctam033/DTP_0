from odoo import api, fields, models


class DtpSchoolProductTrack(models.Model):
    _name = 'dtp.school.product.track'
    _description = 'DTP School Product Track'
    _order = 'school_id, product_code'

    school_id = fields.Many2one('dtp.school', string='Trường học', required=True, index=True)
    product_id = fields.Many2one('product.product', string='Sản phẩm', required=True, index=True)
    product_code = fields.Char(related='product_id.default_code', string='Mã sản phẩm', store=True, readonly=True)
    total_delivered = fields.Float(string='Tổng cấp phát', default=0.0)
    total_returned = fields.Float(string='Tổng thu hồi', default=0.0)
    total_transferred_in = fields.Float(string='Nhận luân chuyển', default=0.0)
    total_transferred_out = fields.Float(string='Xuất luân chuyển', default=0.0)
    qty_balance = fields.Float(string='Số lượng hiện có tại trường', default=0.0)
    history_ids = fields.One2many('dtp.product.history', 'tracking_id', string='Lịch sử')

    _sql_constraints = [
        ('school_product_unique', 'unique(school_id, product_id)', 'Mỗi trường chỉ có một dòng theo dõi cho mỗi sản phẩm.'),
    ]


class DtpProductHistory(models.Model):
    _name = 'dtp.product.history'
    _description = 'DTP Product History'
    _order = 'operation_date desc, id desc'

    operation_type = fields.Selection(
        [
            ('delivery', 'Giao hàng'),
            ('return', 'Thu hồi hàng'),
            ('transfer', 'Luân chuyển hàng'),
        ],
        string='Loại nghiệp vụ',
        required=True,
    )
    operation_date = fields.Date(string='Ngày nghiệp vụ', required=True, default=fields.Date.context_today)
    reference_name = fields.Char(string='Chứng từ', required=True)
    tracking_id = fields.Many2one('dtp.school.product.track', string='Theo dõi trường/sản phẩm', ondelete='cascade')
    school_id = fields.Many2one('dtp.school', string='Trường học', required=True, index=True)
    class_id = fields.Many2one('dtp.school.class', string='Lớp học')
    product_id = fields.Many2one('product.product', string='Sản phẩm', required=True)
    product_code = fields.Char(related='product_id.default_code', string='Mã sản phẩm', store=True, readonly=True)
    quantity = fields.Float(string='Số lượng nghiệp vụ', required=True, default=1.0)
    quantity_delta = fields.Float(string='Biến động (+/-)', required=True, default=0.0)
    balance_qty = fields.Float(string='Số lượng còn tại trường', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Kho')
    source_school_id = fields.Many2one('dtp.school', string='Từ trường')
    source_class_id = fields.Many2one('dtp.school.class', string='Từ lớp')
    destination_school_id = fields.Many2one('dtp.school', string='Đến trường')
    destination_class_id = fields.Many2one('dtp.school.class', string='Đến lớp')
    note = fields.Char(string='Ghi chú')
    delivery_order_id = fields.Many2one('dtp.delivery.order', string='Đơn giao hàng', copy=False)
    return_order_id = fields.Many2one('dtp.return.order', string='Đơn thu hồi', copy=False)
    transfer_order_id = fields.Many2one('dtp.transfer.order', string='Đơn luân chuyển', copy=False)

    @api.model
    def create_school_product_history(self, vals):
        school_id = vals.get('school_id')
        product_id = vals.get('product_id')
        if not school_id or not product_id:
            return self.browse()

        quantity = vals.get('quantity', 0.0)
        delta = vals.get('quantity_delta', quantity)
        track = self.env['dtp.school.product.track'].search([
            ('school_id', '=', school_id),
            ('product_id', '=', product_id),
        ], limit=1)
        if not track:
            track = self.env['dtp.school.product.track'].create({
                'school_id': school_id,
                'product_id': product_id,
            })

        update_vals = {'qty_balance': track.qty_balance + delta}
        operation_type = vals.get('operation_type')
        if operation_type == 'delivery':
            update_vals['total_delivered'] = track.total_delivered + quantity
        elif operation_type == 'return':
            update_vals['total_returned'] = track.total_returned + quantity
        elif operation_type == 'transfer':
            if delta >= 0:
                update_vals['total_transferred_in'] = track.total_transferred_in + quantity
            else:
                update_vals['total_transferred_out'] = track.total_transferred_out + quantity
        track.write(update_vals)

        vals.update({
            'tracking_id': track.id,
            'balance_qty': update_vals['qty_balance'],
        })
        return self.create(vals)
