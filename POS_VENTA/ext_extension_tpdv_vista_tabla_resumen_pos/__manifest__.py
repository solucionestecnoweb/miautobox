# -*- coding: utf-8 -*-
{
    'name': "Extencion Terminal Punto de Venta Vista resumen tabla libro pos",

    'summary': """Extencion Terminal Punto de Venta Vista resumen tabla libro pos""",

    'description': """
       Extencion Terminal Punto de Venta Vista resumen tabla libro pos
       Colaborador: Ing. Darrell Sojo
    """,
    'version': '1.0',
    'author': 'INM&LDR Soluciones Tecnologicas',
    'category': 'Punto de venta',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','ext_extension_tpdv'],

    # always loaded
    'data': [
        'vista/vista_tabla_libro_pos.xml',
    ],
    'application': True,
}
