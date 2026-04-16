# -*- coding: utf-8 -*-
{
    'name': 'DTP School Management',
    'version': '1.0',
    'summary': 'Quản lý trường học, lớp học và bộ dụng cụ theo môn',
    'category': 'Education',
    'depends': ['contacts', 'dtp_stock_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/dtp_school_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
