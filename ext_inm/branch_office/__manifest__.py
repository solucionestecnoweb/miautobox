# -*- coding: utf-8 -*-

{
    'name': 'Sucursales',
    'description': '',
    'version': '14.0.1.0.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'maintainer': 'Bryan Gomez',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['account', 'purchase', 'stock', 'analytic', 'purchase_stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/branch_office_views.xml',
        'views/purchase_views.xml',
        'views/account_analytic_account_views.xml',
        'views/stock_location_views.xml',
        'views/stock_quant_views.xml',
        'views/stock_picking_views.xml',
        'views/branch_office_menuitem.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}