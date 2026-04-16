from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DtpDeliveryOrder(models.Model):
    _name = 'dtp.delivery.order'
    _description = 'DTP Delivery Order'
    _order = 'delivery_date desc, id desc'

    name = fields.Char(string='Mã giao hàng', required=True, copy=False, default='New', readonly=True)
    school_id = fields.Many2one('dtp.school', string='Trường học', required=True)
    class_id = fields.Many2one('dtp.school.class', string='Lớp học', domain="[('school_id', '=', school_id)]")
    partner_id = fields.Many2one('res.partner', string='Liên hệ', related='school_id.partner_id', store=True, readonly=True)
    delivery_date = fields.Date(string='Ngày giao', default=fields.Date.context_today, required=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Kho xuất',
        required=True,
        default=lambda self: self.env['stock.warehouse'].search([], limit=1),
    )
    responsible_id = fields.Many2one('res.users', string='Phụ trách', default=lambda self: self.env.user)
    carrier_name = fields.Char(string='Đơn vị giao hàng')
    note = fields.Text(string='Ghi chú')
    state = fields.Selection(
        [
            ('draft', 'Nháp'),
            ('in_transit', 'Đang giao'),
            ('delivered', 'Đã giao'),
            ('cancelled', 'Đã hủy'),
        ],
        string='Trạng thái',
        default='draft',
    )
    picking_id = fields.Many2one('stock.picking', string='Phiếu xuất kho', readonly=True, copy=False)
    line_ids = fields.One2many('dtp.delivery.order.line', 'order_id', string='Sản phẩm')
    total_qty = fields.Float(string='Tổng số lượng', compute='_compute_total_qty')

    @api.depends('line_ids.quantity')
    def _compute_total_qty(self):
        for order in self:
            order.total_qty = sum(order.line_ids.mapped('quantity'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('dtp.delivery.order') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise UserError(_('Vui lòng thêm ít nhất một sản phẩm để giao.'))
            if not order.picking_id:
                customer_location = self.env.ref('stock.stock_location_customers')
                picking = self.env['stock.picking'].create({
                    'partner_id': order.partner_id.id if order.partner_id else False,
                    'picking_type_id': order.warehouse_id.out_type_id.id,
                    'location_id': order.warehouse_id.lot_stock_id.id,
                    'location_dest_id': customer_location.id,
                    'origin': order.name,
                    'scheduled_date': order.delivery_date,
                    'dtp_delivery_order_id': order.id,
                })
                for line in order.line_ids:
                    self.env['stock.move'].create({
                        'name': line.product_id.display_name,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.quantity,
                        'product_uom': line.product_id.uom_id.id,
                        'picking_id': picking.id,
                        'location_id': order.warehouse_id.lot_stock_id.id,
                        'location_dest_id': customer_location.id,
                    })
                picking.action_confirm()
                picking.action_assign()
                order.picking_id = picking.id
            order.state = 'in_transit'

    def action_mark_delivered(self):
        for order in self:
            if order.picking_id and order.picking_id.state not in ('done', 'cancel'):
                raise UserError(_('Hãy hoàn tất phiếu xuất kho trước khi đánh dấu đã giao.'))
            order.state = 'delivered'

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
            raise UserError(_('Đơn giao hàng này chưa có phiếu xuất kho.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Phiếu xuất kho'),
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.picking_id.id,
        }


class DtpDeliveryOrderLine(models.Model):
    _name = 'dtp.delivery.order.line'
    _description = 'DTP Delivery Order Line'
    _order = 'id'

    order_id = fields.Many2one('dtp.delivery.order', string='Đơn giao hàng', required=True, ondelete='cascade')
    product_id = fields.Many2one(
        'product.product',
        string='Sản phẩm',
        required=True,
        domain=[('product_tmpl_id.is_teaching_product', '=', True)],
    )
    quantity = fields.Float(string='Số lượng', default=1.0, required=True)
    note = fields.Char(string='Ghi chú')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dtp_delivery_order_id = fields.Many2one('dtp.delivery.order', string='Đơn giao hàng DTP', copy=False)
