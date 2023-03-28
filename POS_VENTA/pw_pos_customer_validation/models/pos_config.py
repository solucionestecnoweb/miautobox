# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class POSConfig(models.Model):
    _inherit = 'pos.config'

    required_email = fields.Boolean('Required Email')
    required_phone = fields.Boolean(string='Telefono Requerido')
    required_barcode = fields.Boolean('Required Barcode')
    required_name = fields.Boolean(string='Razon Social Requerido')
    required_vat = fields.Boolean(string='Cedula/Rif Requerido')
    required_street = fields.Boolean(string='Direccion Requerido')
    required_city = fields.Boolean(string='Ciudad Requerido')

    unique_email = fields.Boolean('Unique Email')
    unique_phone = fields.Boolean('Unique Phone')
    unique_barcode = fields.Boolean('Unique Barcode')
