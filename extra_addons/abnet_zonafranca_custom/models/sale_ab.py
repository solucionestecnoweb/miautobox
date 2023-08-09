# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class Sale(models.Model):
    _inherit = 'sale.order'


    def _prepare_invoice(self):
        res = super(Sale, self)._prepare_invoice()
        impuestos = 0
        cia = self.company_id.id
        domain = [('company_id', '=', cia), ('type_tax_use', '=', 'sale'), ('active', '=', True)]
        tax_ids = self.env['account.tax'].search(domain)
        for tax_id in tax_ids:
            tax = self.env['account.tax'].browse(tax_id.id)
            impuestos = impuestos + tax.amount
        if impuestos == 0:
            res['x_sff_flag'] = False
        return res

