# -*- coding: utf-8 -*-
import base64
import csv
import io
import zipfile

from odoo import fields, models


class InventoryExportCSV(models.TransientModel):
    _name = 'inventory.export.csv'
    _description = 'Export Inventory to CSV'

    name = fields.Char(string='File Name', default='inventory_export.zip')
    export_file = fields.Binary(string='Export File', readonly=True)
    state = fields.Selection([('choose', 'Choose'), ('get', 'Get')], default='choose')

    def _get_export_specs(self):
        return [
            {
                'filename': 'product_template.csv',
                'model': 'product.template',
                'fields': [
                    'id', 'name', 'default_code', 'barcode', 'type', 'categ_id', 'uom_id',
                    'list_price', 'standard_price', 'qty_available', 'virtual_available',
                    'need_recall', 'active', 'create_date', 'write_date',
                ],
            },
            {
                'filename': 'product_product.csv',
                'model': 'product.product',
                'fields': [
                    'id', 'display_name', 'product_tmpl_id', 'default_code', 'barcode',
                    'active', 'create_date', 'write_date',
                ],
            },
            {
                'filename': 'stock_warehouse.csv',
                'model': 'stock.warehouse',
                'fields': [
                    'id', 'name', 'code', 'company_id', 'partner_id', 'view_location_id',
                    'lot_stock_id', 'active', 'create_date', 'write_date',
                ],
            },
            {
                'filename': 'stock_location.csv',
                'model': 'stock.location',
                'fields': [
                    'id', 'name', 'complete_name', 'usage', 'location_id', 'company_id',
                    'active', 'create_date', 'write_date',
                ],
            },
            {
                'filename': 'stock_quant.csv',
                'model': 'stock.quant',
                'fields': [
                    'id', 'product_id', 'location_id', 'lot_id', 'package_id', 'owner_id',
                    'quantity', 'reserved_quantity', 'available_quantity', 'in_date',
                    'create_date', 'write_date',
                ],
            },
            {
                'filename': 'stock_picking_type.csv',
                'model': 'stock.picking.type',
                'fields': [
                    'id', 'name', 'code', 'warehouse_id', 'default_location_src_id',
                    'default_location_dest_id', 'active', 'create_date', 'write_date',
                ],
            },
            {
                'filename': 'stock_picking.csv',
                'model': 'stock.picking',
                'fields': [
                    'id', 'name', 'origin', 'partner_id', 'picking_type_id', 'state',
                    'scheduled_date', 'date_done', 'return_deadline_date', 'return_days_left',
                    'subject_id', 'create_date', 'write_date',
                ],
            },
            {
                'filename': 'stock_move.csv',
                'model': 'stock.move',
                'fields': [
                    'id', 'name', 'reference', 'picking_id', 'product_id', 'product_uom_qty',
                    'quantity', 'product_uom', 'location_id', 'location_dest_id', 'state',
                    'date', 'create_date', 'write_date',
                ],
            },
            {
                'filename': 'stock_move_line.csv',
                'model': 'stock.move.line',
                'fields': [
                    'id', 'picking_id', 'move_id', 'product_id', 'lot_id', 'owner_id',
                    'package_id', 'result_package_id', 'location_id', 'location_dest_id',
                    'quantity', 'state', 'create_date', 'write_date',
                ],
            },
            {
                'filename': 'school_partner.csv',
                'model': 'res.partner',
                'domain': [('is_school', '=', True)],
                'fields': [
                    'id', 'name', 'school_type', 'address', 'district', 'province', 'region',
                    'sale_user_ids', 'active', 'create_date', 'write_date',
                ],
            },
            {
                'filename': 'school_class.csv',
                'model': 'res.partner.class',
                'fields': [
                    'id', 'grade', 'class_count', 'school_id', 'subject_ids', 'region',
                    'create_date', 'write_date',
                ],
            },
            {
                'filename': 'school_subject.csv',
                'model': 'res.partner.subject',
                'fields': [
                    'id', 'name', 'class_ids', 'supply_product_ids', 'create_date', 'write_date',
                ],
            },
        ]

    def _serialize_value(self, record, field_name):
        if field_name not in record._fields:
            return ''

        field = record._fields[field_name]
        value = record[field_name]

        if field.type == 'many2one':
            return value.display_name if value else ''
        if field.type in ('many2many', 'one2many'):
            return ', '.join(value.mapped('display_name'))
        if field.type == 'boolean':
            return '1' if value else '0'
        if field.type in ('date', 'datetime'):
            return value or ''
        return value if value not in (False, None) else ''

    def _build_csv_content(self, model_name, field_names, domain=None):
        records = self.env[model_name].search(domain or [])
        output = io.StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(field_names)
        for record in records:
            writer.writerow([self._serialize_value(record, field_name) for field_name in field_names])
        content = output.getvalue()
        output.close()
        return content

    def action_export_csv(self):
        self.ensure_one()

        folder_name = 'inventory_export'
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for spec in self._get_export_specs():
                csv_content = self._build_csv_content(
                    spec['model'],
                    spec['fields'],
                    domain=spec.get('domain'),
                )
                zip_file.writestr(
                    '%s/%s' % (folder_name, spec['filename']),
                    csv_content.encode('utf-8-sig'),
                )

        self.write({
            'export_file': base64.b64encode(zip_buffer.getvalue()),
            'state': 'get',
            'name': '%s.zip' % folder_name,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.export.csv',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }
