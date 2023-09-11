# -*- coding: utf-8 -*-
{
    'name': 'Point of Sale Vpos P2C',
    'version': '14.0.1.0.0',
    'summary': 'change mobile payment vpos P2C',
    'description': 'change mobile payment vpos P2C',
    'author': 'Carlos Fernandez <cfernandez.wx@gmail.com>',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        # 'data/data.xml',
        'views/assets.xml',
        'views/pos_payment_method.xml',
        # 'views/point_of_sale.xml',
        # 'views/pos_payment_view.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],

    'installable': True,
}