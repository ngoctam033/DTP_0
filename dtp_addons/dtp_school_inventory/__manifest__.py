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
        'views/stock_menu_custom_views.xml',
        'views/dashboard_action.xml',
        'wizard/inventory_export_csv_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dtp_school_inventory/static/src/**/*.js',
            'dtp_school_inventory/static/src/**/*.xml',
            'dtp_school_inventory/static/src/**/*.scss',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
