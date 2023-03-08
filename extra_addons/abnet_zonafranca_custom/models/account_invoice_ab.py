# -*- coding: utf-8 -*-
# Part of abnet_customize. See LICENSE file for full copyright and licensing details.
import datetime, pytz
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class account_invoice(models.Model):
    _inherit = "account.move"


    @api.constrains('x_sff_flag')
    def x_sff_flag_constrains(self):
        impuestos = 0
        cia = self.company_id.id
        domain = [('company_id', '=', cia), ('type_tax_use', '=', 'sale'), ('active', '=', True)]
        tax_ids = self.env['account.tax'].search(domain)
        for tax_id in tax_ids:
            tax = self.env['account.tax'].browse(tax_id.id)
            impuestos = impuestos + tax.amount
        tot_iva = 0
        for line in self.line_ids:
            if line.tax_line_id:
                tot_iva = tot_iva + line.price_total
        if self.x_sff_flag is False and tot_iva == 0:
            if impuestos > 0:
                raise UserError("Por favor, ingrese el impuesto a ser aplicado Zona Franca")
        if self.x_sff_flag is True and tot_iva > 0:
            raise UserError("Se ha indicado el impuesto para nota SFF")



