# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'ABNet Sales Customizations',
    'version': '1.0.3.0',
    'category': 'Sales',
    'sequence': '10',
    'author': 'Grupo Autobox',
    'description': """
ABNet Sales Customizations
===============
Features:
---------
- Nuevo campo en detalle de factura para indicar el operador de servicios. Depende de asignar al contacto la categoría: Operador de Servicios AB
- Modificaciones a Análisis de facturas para incluir agrupamiento por operador
- Último cambio: 2021/08/01
    """,
    'depends': ['sale', 'crm', 'base', 'product'],
    'data': ['views/account_move_form_service_operator_ab.xml'
             ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
