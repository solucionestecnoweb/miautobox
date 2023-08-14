from odoo import models, fields, api,_
from datetime import timedelta, date, datetime
from odoo.exceptions import UserError


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"


    @api.onchange('rate_real', 'hora')
    def conversion_tarifas(self):
        lista=self.env['product.pricelist.item'].search([])
        if lista:
            for det in lista:
                det.fixed_price=det.fixed_price_ref*self.rate_real


class Currency(models.Model):
    _inherit = "res.currency"

    @api.depends('rate_ids.rate_real')
    def conversion_tarifas(self):
        lista=self.env['product.pricelist.item'].search([])
        if lista:
            for det in lista:
                det.fixed_price=det.fixed_price_ref*self.rate_real