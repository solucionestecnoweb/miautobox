# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'ABNet Customizations',
    'version': '1.0.7.22',
    'category': 'Sales',
    'sequence': '10',
    'author': 'Grupo Autobox',
    'description': """
ABNet Customize
===============
Features:
---------
- Template de Presupuestos para encabezado personalizado y tamaño de font necesario para el manejo de cantidades en moneda local,
- Habilitación de Sales Team multi-company para permitir la creación de pedidos en las distintas organizaciones del grupo desde el Sales Team común,
- Manejo de Listas de Precios individuales y dedicadas por compañía en la factura,
- Permitir indicar más de una tasa de cambio al día y su correcto manejo durante el proceso de presupuesto, facturación y registro de pagos,
- Formato personalizado de notas de entrega para clientes (SFF),
- Creación de flag de procesado para facturación para registro de intregración con GP,
- Grupo de seguridad para Gerente de tiendas a fin de limitar el manejo de tasas de cambio y precios durante la facturación
- Grupo de seguridad para Operadores de Call Center para permitirles el uso de Tarifas públicas
- Búsqueda de contactos por C.I./RIF en creación de presupuestos y facturas
- Adecuación Vista de Producto en Ventas para colocar ambas divisas (con y sin IVA) y cantidades reservadas
- Búsqueda de productos por nombre, referencia interna, código GP y/o código ICG
- Mejora velocidad pantalla consulta de productos (agregada stock location como default por compañía)
- Cambio de Default_Code a x_CodGP en product.get_name
- Último cambio: 2021/10/21
    """,
    'depends': ['sale', 'crm', 'payment', 'base', 'product','eu_multi_currency'],
    'data': ['report/assets.xml',
             'report/quote_ab.xml',
             'views/account_move_form_ab.xml',
             'views/account_payment_form_ab.xml',
             'views/crm_ab.xml',
             'views/assets_ab.xml',
             'views/sale_ab.xml',
             'views/account_payment_register_views_ab.xml',
             'report/report_invoice_document_sff_view_ab.xml',
             'report/report_invoice_document_sff_ab.xml',
             'security/groups_ab.xml',
             'views/web_widget_timepicker_assets.xml',
             'views/account_move_view_currency_ab.xml',
             'views/product_tree_view_ab.xml'
             ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
