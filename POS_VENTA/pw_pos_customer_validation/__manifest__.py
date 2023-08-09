# -*- coding: utf-8 -*-
{
    'name': 'POS Customer Validation',
    'version': '14.0',
    'author': 'Preway IT Solutions',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'summary': 'This apps helps you add validation on customer in pos interface | pos required customer fields | POS Customer phone required | POS Customer Email Required | POS Customer Barcode Required | POS Validation',
    'description': """
- Odoo POS Customer phone unique
- Odoo POS Customer phone require
- Odoo POS Customer email unique
- Odoo POS Customer email require
- Odoo POS Customer barcode unique
- Odoo POS Customer barcode require
    """,
    'data': [
        "views/assets.xml",
        "views/pos_config_view.xml",
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'price': 15.0,
    'currency': "EUR",
    'application': True,
    'installable': True,
    "images":["static/description/Banner.png"],
}

