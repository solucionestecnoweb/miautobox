# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'ABNet Rules/Validations',
    'version': '1.0.1.0',
    'category': 'Sales',
    'sequence': '10',
    'author': 'Grupo Autobox',
    'description': """
ABNet Stock Customizations
===============
Features:
---------
- Validaciones Varias
- Cédula, estado, ciudad y país en pedido de ventas
- Longitud mayor a 150 caracteres en dirección del contacto
- Último cambio: 2021/11/12
    """,
    'depends': ['sale', 'crm', 'payment', 'base', 'product'],
    'data': [
             ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
