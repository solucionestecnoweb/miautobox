# -*- coding: utf-8 -*-
import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    branch_office_id = fields.Many2one(related='location_id.branch_office_id', string='Sucursal', store=True)
