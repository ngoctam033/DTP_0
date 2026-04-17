# -*- coding: utf-8 -*-
{
    'name': 'DTP Branding',
    'version': '1.0',
    'summary': 'Branding customization for DTP',
    'category': 'Hidden',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'dtp_branding/static/src/scss/primary_variables.scss')
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
