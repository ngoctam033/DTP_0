from odoo import fields, models


class DtpTeachingKit(models.Model):
    _name = 'dtp.teaching.kit'
    _description = 'Teaching Kit'
    _order = 'name'

    name = fields.Char(string='Tên bộ dụng cụ', required=True)
    code = fields.Char(string='Mã bộ')
    warehouse_id = fields.Many2one('stock.warehouse', string='Kho áp dụng')
    description = fields.Text(string='Mô tả')
    active = fields.Boolean(default=True)
    line_ids = fields.One2many('dtp.teaching.kit.line', 'kit_id', string='Thành phần')


class DtpTeachingKitLine(models.Model):
    _name = 'dtp.teaching.kit.line'
    _description = 'Teaching Kit Line'
    _order = 'id'

    kit_id = fields.Many2one('dtp.teaching.kit', string='Bộ dụng cụ', required=True, ondelete='cascade')
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Sản phẩm',
        required=True,
        domain=[('is_teaching_product', '=', True)],
    )
    quantity = fields.Float(string='Số lượng', default=1.0, required=True)
    note = fields.Char(string='Ghi chú')
