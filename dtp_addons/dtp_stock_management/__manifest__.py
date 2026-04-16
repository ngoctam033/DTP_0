# -*- coding: utf-8 -*-
{
    'name': 'DTP Teaching Stock',
    'version': '1.0',
    'summary': 'Quản lý kho sản phẩm dạy học và bộ dụng cụ',
    'category': 'Inventory/Inventory',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/dtp_stock_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
