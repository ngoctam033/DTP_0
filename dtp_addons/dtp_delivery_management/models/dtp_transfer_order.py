from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DtpTransferOrder(models.Model):
    _name = 'dtp.transfer.order'
    _description = 'DTP Transfer Order'
    _order = 'transfer_date desc, id desc'

    name = fields.Char(string='Mã luân chuyển', required=True, copy=False, default='New', readonly=True)
    source_school_id = fields.Many2one('dtp.school', string='Từ trường', required=True)
    source_class_id = fields.Many2one('dtp.school.class', string='Từ lớp', domain="[('school_id', '=', source_school_id)]")
    destination_school_id = fields.Many2one('dtp.school', string='Đến trường', required=True)
    destination_class_id = fields.Many2one('dtp.school.class', string='Đến lớp', domain="[('school_id', '=', destination_school_id)]")
    salesperson_ids = fields.Many2many(
        'dtp.school.salesperson',
        string='Sale phụ trách',
        related='source_school_id.salesperson_ids',
        readonly=True,
    )
    transfer_date = fields.Date(string='Ngày luân chuyển', default=fields.Date.context_today, required=True)
    note = fields.Text(string='Ghi chú')
    state = fields.Selection(
        [('draft', 'Nháp'), ('done', 'Hoàn tất'), ('cancelled', 'Đã hủy')],
        string='Trạng thái',
        default='draft',
    )
    line_ids = fields.One2many('dtp.transfer.order.line', 'order_id', string='Sản phẩm')
    total_qty = fields.Float(string='Tổng số lượng', compute='_compute_total_qty')

    @api.depends('line_ids.quantity')
    def _compute_total_qty(self):
        for order in self:
            order.total_qty = sum(order.line_ids.mapped('quantity'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('dtp.transfer.order') or 'New'
        return super().create(vals_list)

    def _create_history_entries(self):
        history_model = self.env['dtp.product.history']
        for order in self:
            if history_model.search_count([('transfer_order_id', '=', order.id)]):
                continue
            history_vals = []
            for line in order.line_ids:
                history_vals.append({
                    'operation_type': 'transfer',
                    'operation_date': order.transfer_date,
                    'reference_name': order.name,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'source_school_id': order.source_school_id.id,
                    'source_class_id': order.source_class_id.id,
                    'destination_school_id': order.destination_school_id.id,
                    'destination_class_id': order.destination_class_id.id,
                    'note': line.note or order.note,
                    'transfer_order_id': order.id,
                })
            if history_vals:
                history_model.create(history_vals)

    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise UserError(_('Vui lòng thêm ít nhất một sản phẩm để luân chuyển.'))
            if order.source_school_id == order.destination_school_id and order.source_class_id == order.destination_class_id:
                raise UserError(_('Nơi đi và nơi đến không được trùng nhau.'))
            order.state = 'done'
            order._create_history_entries()

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_view_history(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lịch sử hàng hóa'),
            'res_model': 'dtp.product.history',
            'view_mode': 'list,form',
            'domain': [('transfer_order_id', '=', self.id)],
        }


class DtpTransferOrderLine(models.Model):
    _name = 'dtp.transfer.order.line'
    _description = 'DTP Transfer Order Line'
    _order = 'id'

    order_id = fields.Many2one('dtp.transfer.order', string='Đơn luân chuyển', required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm',
        required=True,
        domain=[('product_tmpl_id.is_teaching_product', '=', True)],
    )
    quantity = fields.Float(string='Số lượng', default=1.0, required=True)
    note = fields.Char(string='Ghi chú')
