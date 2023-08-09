## -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sincronizacion de Precios',
    'version': '0.1.0',
    'category': 'Productivity',
    'sequence': '10',
    'author': 'MaxCodex.com',
    'description': """
Sincronizacion de la lista de precios
===============
Features:
---------
Extensión 3 Endpoint para la productividad de la listas de precios.

- **Route:** /syncPrices
    - **Description:** Recibe un array de parámetros (Consultar example body) el cual permite actualizar o crear productos dentro de las pricelist existentes.
    - **Method:** POST
    - **Authentication:** True
    - **Example Body:** Recibe un objeto json de la siguiente manera: https://i.imgur.com/XmzbuhQ.png

- **Route:** /deletePrices
    - **Description:** Recibe un array de OdooId (productos) que se desean eliminar de todas las pricelist
    - **Method:** POST
    - **Authentication:** True
    - **Example Body:** Recibe un objeto json de la siguiente manera: https://i.imgur.com/ksU0OCz.png

- **Route:** /deleteInPriceList
    - **Description:** Recibe un array de pricelist_IdS que se desean vaciar.
    - **Method:** POST
    - **Authentication:** True
    - **Example Body:** Recibe un objeto json de la siguiente manera: https://i.imgur.com/miW7LEF.png

Para mas detalles consultar la documentación del repositorio. 
 
**Último cambio:** 2022/11/16
    """,
    'depends': ['sale_management', 'crm', 'payment', 'base', 'product'],
    'data': [],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}