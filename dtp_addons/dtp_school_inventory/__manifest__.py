# -*- coding: utf-8 -*-
{
    'name': 'DTP School Inventory Management',
    'version': '1.0',
    'summary': 'School management schema integrated in Inventory app',
    'category': 'Inventory/Inventory',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/school_sample_data.xml',
        'views/school_management_views.xml',
        'views/stock_menu_disable_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
