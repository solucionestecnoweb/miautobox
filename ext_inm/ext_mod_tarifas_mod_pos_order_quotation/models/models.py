from odoo import models, fields, api,_
from datetime import timedelta, date, datetime
from odoo.exceptions import UserError


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"


    @api.onchange('rate_real', 'hora')
    def conversion_tarifas_pos(self):
         if self.rate_real!=0:
            tasa=self.rate_real
        else:
            lista_tasa = self.env['res.currency.rate'].search([],order='hora desc',limit=1)
            tasa=lista_tasa.rate_real
            
        for compania in self.env['res.company'].search([]):
            lista=self.env['pos.quotation'].search([('company_id','=',compania.id)])
            if lista:
                for det in lista:
                    acum=0
                    for lines in det.lines:
                        lines.price_unit=self.actualiza(lines.product_id,det.company_id,round(tasa,2))
                        lines.price_subtotal=lines.qty*lines.price_unit
                        lines.price_subtotal_incl=lines.price_subtotal #*
                        acum=acum+lines.price_subtotal_incl
                    det.amount_total=acum


    def actualiza(self,product_id,company_id,tasa):
        valor=0
        busca=self.env['product.pricelist'].search([('company_id','=',company_id.id)])
        if busca:
            for item in busca:
                if item.item_ids:
                    for rec in item.item_ids.search([('product_tmpl_id','=',product_id.product_tmpl_id.id)]):
                        valor=rec.fixed_price_ref*tasa
        return valor

    def central_bank(self):
        super().central_bank()
        self.conversion_tarifas_pos()


class Currency(models.Model):
    _inherit = "res.currency"

    @api.depends('rate_ids.rate_real')
    def conversion_tarifas_pos(self):
        for compania in self.env['res.company'].search([]):
            lista=self.env['pos.quotation'].search([('company_id','=',compania.id)])
            if lista:
                for det in lista:
                    acum=0
                    for lines in det.lines:
                        lines.price_unit=self.actualiza(lines.product_id,det.company_id,round(self.rate_real,2))
                        lines.price_subtotal=lines.qty*lines.price_unit
                        lines.price_subtotal_incl=lines.price_subtotal #*
                        acum=acum+lines.price_subtotal_incl
                    det.amount_total=acum


    def actualiza(self,product_id,company_id,tasa):
        valor=0
        busca=self.env['product.pricelist'].search([('company_id','=',company_id.id)])
        if busca:
            for item in busca:
                if item.item_ids:
                    for rec in item.item_ids.search([('product_tmpl_id','=',product_id.product_tmpl_id.id)]):
                        valor=rec.fixed_price_ref*tasa
        return valor