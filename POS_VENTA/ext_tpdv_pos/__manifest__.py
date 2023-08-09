# -*- coding: utf-8 -*-
{
    'name': "Extencion Terminal Punto de Venta JS",

    'summary': """Extencion Terminal Punto de Venta JS""",

    'description': """
       Extencion Terminal Punto de Venta JS
     
    """,
    'version': '1.0',
    'author': 'INM&LDR Soluciones Tecnologicas',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
            'views/pos.xml',
            'views/pos_config.xml'
        ],

    'qweb': ['static/src/xml/PaymentScreen.xml', 'static/src/xml/ReceiptScreen.xml', 'static/src/xml/ClientLine.xml'],

    
    'application': True,
}
