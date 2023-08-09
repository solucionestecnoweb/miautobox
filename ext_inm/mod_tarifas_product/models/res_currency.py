from odoo import models, fields, api,_
from datetime import timedelta, date, datetime
from odoo.exceptions import UserError


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"


    @api.onchange('rate_real', 'hora')
    def conversion_tarifas(self):
        #raise UserError(_('tasa = %s')%dolar)
        if self.rate_real!=0:
            tasa=self.rate_real
        else:
            lista_tasa = self.env['res.currency.rate'].search([],order='hora desc',limit=1)
            tasa=lista_tasa.rate_real
        lista=self.env['product.pricelist.item'].search([])
        if lista:
            for det in lista:
                det.fixed_price=det.fixed_price_ref*round(tasa,2)

    def central_bank(self):
        super().central_bank()
        self.conversion_tarifas()


class Currency(models.Model):
    _inherit = "res.currency"

    @api.depends('rate_ids.rate_real')
    def conversion_tarifas(self):
        lista=self.env['product.pricelist.item'].search([])
        if lista:
            for det in lista:
                det.fixed_price=det.fixed_price_ref*round(self.rate_real,2)