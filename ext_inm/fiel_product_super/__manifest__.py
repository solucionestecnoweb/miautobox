# Copyright 2020 GregorioCode <Info@gregoriocode.com>


{
    "name": "Inventario Tama",
    "version": "14.0.1.0.1",
    "category": "app",
    "author": "Ing Darrell Sojo",
    "website": "",
    "license": "AGPL-3",
    "depends": ['base', 'product','stock'],
    "data": [
       # "static/src/js/subst.xml",
        "security/ir.model.access.csv",
        "security/situacion_groups.xml",
        "views/inventory_products.xml",
        "views/brands_views.xml",
        "views/id_almacenes.xml",
        "views/id_ubicaciones.xml",
        "views/id_categ_product.xml",
        'views/id_tipo_operaciones.xml',
        'views/id_tarifas.xml',
        #"report/inventario_toma_fisica.xml",
        #"report/inventario_picking_salidas.xml",
        #"report/delivery_order_report.xml",
        #"views/wizard_inventory_picking_salida.xml",
        #"views/wizard_inventory_toma_fisica.xml",
    ],
    'installable': True,
}
