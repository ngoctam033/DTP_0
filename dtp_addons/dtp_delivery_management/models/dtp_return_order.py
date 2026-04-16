from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DtpReturnOrder(models.Model):
    _name = 'dtp.return.order'
    _description = 'DTP Return Order'
    _order = 'return_date desc, id desc'

    name = fields.Char(string='Mã thu hồi', required=True, copy=False, default='New', readonly=True)
    school_id = fields.Many2one('dtp.school', string='Trường học', required=True)
    class_id = fields.Many2one('dtp.school.class', string='Lớp học', domain="[('school_id', '=', school_id)]")
    salesperson_ids = fields.Many2many(
        'dtp.school.salesperson',
        string='Sale phụ trách',
        related='school_id.salesperson_ids',
        readonly=True,
    )
    return_date = fields.Date(string='Ngày thu hồi', default=fields.Date.context_today, required=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Nhập về kho',
        required=True,
        default=lambda self: self.env['stock.warehouse'].search([], limit=1),
    )
    reason = fields.Text(string='Lý do thu hồi')
    state = fields.Selection(
        [('draft', 'Nháp'), ('returned', 'Đã thu hồi'), ('cancelled', 'Đã hủy')],
        string='Trạng thái',
        default='draft',
    )
    picking_id = fields.Many2one('stock.picking', string='Phiếu nhập kho', readonly=True, copy=False)
    line_ids = fields.One2many('dtp.return.order.line', 'order_id', string='Sản phẩm')
    total_qty = fields.Float(string='Tổng số lượng', compute='_compute_total_qty')

    @api.depends('line_ids.quantity')
    def _compute_total_qty(self):
        for order in self:
            order.total_qty = sum(order.line_ids.mapped('quantity'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('dtp.return.order') or 'New'
        return super().create(vals_list)

    def _create_history_entries(self):
        history_model = self.env['dtp.product.history']
        for order in self:
            if history_model.search_count([('return_order_id', '=', order.id)]):
                continue
            history_vals = []
            for line in order.line_ids:
                history_vals.append({
                    'operation_type': 'return',
                    'operation_date': order.return_date,
                    'reference_name': order.name,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'warehouse_id': order.warehouse_id.id,
                    'source_school_id': order.school_id.id,
                    'source_class_id': order.class_id.id,
                    'note': line.note or order.reason,
                    'return_order_id': order.id,
                })
            if history_vals:
                history_model.create(history_vals)

    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise UserError(_('Vui lòng thêm ít nhất một sản phẩm để thu hồi.'))
            if not order.picking_id:
                customer_location = self.env.ref('stock.stock_location_customers')
                picking = self.env['stock.picking'].create({
                    'picking_type_id': order.warehouse_id.in_type_id.id,
                    'location_id': customer_location.id,
                    'location_dest_id': order.warehouse_id.lot_stock_id.id,
                    'origin': order.name,
                    'scheduled_date': order.return_date,
                })
                for line in order.line_ids:
                    self.env['stock.move'].create({
                        'name': line.product_id.display_name,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.quantity,
                        'product_uom': line.product_id.uom_id.id,
                        'picking_id': picking.id,
                        'location_id': customer_location.id,
                        'location_dest_id': order.warehouse_id.lot_stock_id.id,
                    })
                picking.action_confirm()
                order.picking_id = picking.id
            order.state = 'returned'
            order._create_history_entries()

    def action_cancel(self):
        for order in self:
            if order.picking_id and order.picking_id.state not in ('done', 'cancel'):
                order.picking_id.action_cancel()
            order.state = 'cancelled'

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_view_picking(self):
        self.ensure_one()
        if not self.picking_id:
            raise UserError(_('Đơn thu hồi này chưa có phiếu nhập kho.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Phiếu nhập kho'),
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.picking_id.id,
        }

    def action_view_history(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lịch sử hàng hóa'),
            'res_model': 'dtp.product.history',
            'view_mode': 'list,form',
            'domain': [('return_order_id', '=', self.id)],
        }


class DtpReturnOrderLine(models.Model):
    _name = 'dtp.return.order.line'
    _description = 'DTP Return Order Line'
    _order = 'id'

    order_id = fields.Many2one('dtp.return.order', string='Đơn thu hồi', required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm',
        required=True,
        domain=[('product_tmpl_id.is_teaching_product', '=', True)],
    )
    quantity = fields.Float(string='Số lượng', default=1.0, required=True)
    note = fields.Char(string='Ghi chú')
