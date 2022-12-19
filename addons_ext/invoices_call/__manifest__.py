## -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Invoices call',
    'version': '0.1.0',
    'category': 'Productivity',
    'sequence': '10',
    'author': 'MaxCodex.com',
    'description': """
Llamada de Facturas
===============
Features:
---------
Extensión 1 Endpoint para la productividad de facturas.

- **Route:** /call_invoices
    - **Description:**: Permite traerse todas las facturas de acuerdo a un criterio especificado.  
    - **Method:** POST
    - **Authentication:** True
    - **Example Body:** Recibe un objeto json de la siguiente manera: https://i.imgur.com/XmzbuhQ.png

Fields in JSON:
---------
- **filter_documents:** Array de parámetros compuesto por field, operator and value el cual permite filtrar sobre las facturas generadas en odoo.  (véase el ejemplo en la imagen)
    - **field:** (Consulte los campos existentes en el modelo de **account.move**)
    - **operator:** Admite los operadores lógicos estándares (=, in, !=, >=, <=) ect.
    - **value:** Valor a filtrar de acuerdo el field y el operator.
 
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