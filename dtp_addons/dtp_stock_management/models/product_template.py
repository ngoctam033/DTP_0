from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: (
            self.env.ref('base.VND', raise_if_not_found=False) or self.env.company.currency_id
        ).id,
    )

    is_teaching_product = fields.Boolean(
        string='Sản phẩm dạy học',
        help='Đánh dấu sản phẩm dùng cho giảng dạy hoặc học tập.',
    )
    subject_area = fields.Char(string='Môn học')
    grade_level = fields.Char(string='Khối lớp')
    teaching_note = fields.Text(string='Ghi chú giảng dạy')
