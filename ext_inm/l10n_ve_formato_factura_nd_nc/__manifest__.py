# -*- coding: utf-8 -*-
{
    'name': "Formatos de Factura, NC, ND de forma Libre Miautobox",

    'summary': """Formatos de Factura, NC, ND de forma Libre Miautobox""",

    'description': """
       Formatos de Factura, NC, ND de forma Libre Miautobox.
       Formato de Nota de entrega Miautobox...
    """,
    'version': '14.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A. Ing. MArilynmillan',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['base','account','l10n_ve_igtf_formato_libre','ext_extension_nota_debit','account_debit_note'],

    # always loaded
    'data': [
        'formatos/account_move_view.xml',
        'formatos/factura_libre.xml',
        'formatos/nota_entrega.xml' ,
        'views/inherit_nota_debit.xml' ,
        'views/inherit_nota_credito.xml' ,

     
    ],
    'application': True,
    'active':False,
    'auto_install': False,
}
