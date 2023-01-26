# -*- coding: utf-8 -*-
{
    'name': "Módulo ctas creditos a clientes",

    'summary': """Módulo ctas creditos a clientes""",

    'description': """
       Módulo ctas creditos a clientes
       Colaborador: TSU. José Rafael Machado
    """,
    'version': '1.0',
    'author': 'Particular',
    'category': 'Extension Módulo Terminal Punto de Venta',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','account'],

    # always loaded
    'data': [
        #'vista_view.xml',
        #'buttom_menu_view.xml',
        'vista/vista_pos_paymet_inheret.xml',
        #'vista_pos_order_inherit.xml',
        'vista/pos_config_inherit.xml',
        'security/ir.model.access.csv',
        'vista/credito_cliente.xml',
        #'reports/report_libro_pos.xml',
        #'wizards/wizard_libro_ventas_pos.xml',
        #'vista_session_inherit.xml',
    ],
    'application': True,
}
