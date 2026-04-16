from odoo import fields, models


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
    product_id = fields.Many2one('product.product', string='Sản phẩm', required=True)
    product_code = fields.Char(related='product_id.default_code', string='Mã sản phẩm', store=True, readonly=True)
    quantity = fields.Float(string='Số lượng', required=True, default=1.0)
    warehouse_id = fields.Many2one('stock.warehouse', string='Kho')
    source_school_id = fields.Many2one('dtp.school', string='Từ trường')
    source_class_id = fields.Many2one('dtp.school.class', string='Từ lớp')
    destination_school_id = fields.Many2one('dtp.school', string='Đến trường')
    destination_class_id = fields.Many2one('dtp.school.class', string='Đến lớp')
    note = fields.Char(string='Ghi chú')
    delivery_order_id = fields.Many2one('dtp.delivery.order', string='Đơn giao hàng', copy=False)
    return_order_id = fields.Many2one('dtp.return.order', string='Đơn thu hồi', copy=False)
    transfer_order_id = fields.Many2one('dtp.transfer.order', string='Đơn luân chuyển', copy=False)
