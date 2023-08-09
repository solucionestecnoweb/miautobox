## -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sincronizacion de Inventario',
    'version': '0.1.0',
    'category': 'Productivity',
    'sequence': '10',
    'author': 'MaxCodex.com',
    'description': """
Sincronizacion de Recep. de Inventarios
===============
Features:
---------
Extensión 2 Endpoint para la productividad de los inventarios.

- **Route:** /update_products
    - **Description:** Recibe un array de items (productos) a actualizar (Consultar los campos disponibles en **product.template**). Adicionalmente recibe el parámetro **'us_name'** el cual permite modificar la traduccion en ingles del campo **'name'**
    - **Method:** POST
    - **Authentication:** True
    - **Example Body:** Recibe un objeto json de la siguiente manera: https://i.imgur.com/HmkAMop.png

- **Route:** /sync_stock
    - **Description:** Recibe un array de parámetros el cual permite crear un inventario y automaticamente validarlo. 
    - **Method:** POST
    - **Authentication:** True
    - **Example Body:** Recibe un objeto json de la siguiente manera: https://i.imgur.com/YxgRCDC.png

Para mas detalles consultar la documentación del repositorio. 
 
**Último cambio:** 2022/11/16
    """,
    'depends': ['stock', 'base', 'product'],
    'data': [],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}