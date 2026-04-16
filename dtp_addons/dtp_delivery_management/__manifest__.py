# -*- coding: utf-8 -*-
{
    'name': 'DTP Delivery Management',
    'version': '1.0',
    'summary': 'Quản lý giao hàng cho trường học và lớp học',
    'category': 'Inventory/Delivery',
    'depends': ['stock', 'contacts', 'dtp_school_management'],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/dtp_delivery_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
