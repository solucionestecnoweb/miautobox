# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'ABNet Stock Customizations',
    'version': '1.0.2.0',
    'category': 'Sales',
    'sequence': '10',
    'author': 'Grupo Autobox',
    'description': """
ABNet Stock Customizations
===============
Features:
---------
- Simular Kardex en consulta de productos
- Último cambio: 2021/11/12
    """,
    'depends': ['stock', 'product', 'base'],
    'data': ['views/product_kardex_ab.xml',
             'security/ir.model.access.csv'
             ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
