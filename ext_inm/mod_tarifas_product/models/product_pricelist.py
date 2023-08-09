# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from itertools import product
import json
from datetime import datetime, timedelta
import base64
from io import StringIO
from odoo import api, fields, models
from datetime import date
from odoo.tools.float_utils import float_round
from odoo.exceptions import Warning

import time

class ProductPriceList(models.Model):
    _inherit = "product.pricelist"

    currency_id_dif = fields.Many2one('res.currency',default=lambda self: self.env.company.currency_secundaria_id.id)
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company.id)
    tasa_del_dia = fields.Float("Tasa del día", compute="_compute_tasa_del_dia")

    def  _compute_tasa_del_dia(self):
        tasa=1
        busca=self.env['res.currency.rate'].search([('currency_id','=',self.currency_id_dif.id)],limit=1,order='hora desc')
        if busca:
            tasa=busca.rate_real
        self.tasa_del_dia=round(tasa,2)

    @api.onchange('currency_id_dif','tasa_del_dia')
    def recalcula(self):
        tasa=1
        busca=self.env['res.currency.rate'].search([('currency_id','=',self.currency_id_dif.id)],limit=1,order='hora desc')
        if busca:
            tasa=busca.rate_real
        for item in self.item_ids:
            item.fixed_price=item.fixed_price_ref*round(tasa,2)

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    currency_id_dif = fields.Many2one('res.currency',default=lambda self: self.env.company.currency_secundaria_id.id)
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company.id,)

    fixed_price_ref = fields.Float('Precio Referencia $', digits='Product Price')