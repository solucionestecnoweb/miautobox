# -*- coding: utf-8 -*-
{
    'name': "Currency Rate",

    'summary': """Module_Res_Currency_Rate""",

    'description': """
      Añadir hora en la tasa que aplica para la moneda.
      Colaboradores: Darrell Sojo
    """,
    'version': '1.0',
    'author': 'INM&LDR',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded ...
    'data': [
        # 'security/ir.model.access.csv',
        #'views/account_invoice_inherit.xml',
        'data/data.xml',
        #'views/exchange_rate.xml',
        'views/res_currency_rate_inherit_.xml',
        'views/product_templete_inherit.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],

    'application': True,
    'qweb': [
        'static/src/xml/systray.xml',
    ],
    'assets':{
        'web.assets_backend': [
            'l10n_ve_res_currency/static/src/js/systray_theme_menu.js'
        ],'web.assets_qweb': [
            'l10n_ve_res_currency/static/src/xml/**/*',
        ],
    },
}
