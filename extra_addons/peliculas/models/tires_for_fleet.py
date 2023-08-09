# -*- coding:utf-8 -*-

from odoo import models, fields, api


class FleetAutobox(models.Model):
    _inherit = 'fleet.vehicle.model.brand'

    category_brand = fields.Selection(selection=[
        ('mc', 'Marca de caucho'),  # publico general primer dato se graba en bases de datos
        # y segundo es lo que se muestra en las vista
        ('ma', 'Marca de Auto'),  # se requiere compania de un adulto

    ])


class BrandModel(models.Model):
    _inherit = 'fleet.vehicle'

    category_brand = fields.Selection(selection=[
        ('mc', 'Marca de caucho'),  # publico general primer dato se graba en bases de datos
        # y segundo es lo que se muestra en las vista
        ('ma', 'Marca de Auto'),  # se requiere compania de un adulto

    ])
