{
    'name': "Localizacion Venezolana Modulo de Anticipo",

    'summary': """Módulo de Anticipo""",

    'description': """
       Ejecuta tambien los anticipos de pagos clientes/proveedores

    """,
    'version': '2.0',
    'author': 'INM & LDR Soluciones Tecnológicas y Empresariales C.A',
    'category': 'Tools',
    'website': 'http://soluciones-tecno.com/',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
    'vista/res_partner_view.xml',
    'vista/account_payment_view.xml',
    'vista/account_move_view.xml',
    'vista/account_journal_views.xml',
    ],
    'application': True,
}
