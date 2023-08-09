# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api

class Sale(models.Model):
    _inherit = 'sale.order'

    payment_acquirer = fields.Many2one(
        'payment.acquirer',
        check_company=True,
        domain="[('company_id', '=', company_id), ('state', '!=', 'disabled')]",
        string='Forma de Pago',
        default=None
    )

    #@api.onchange('partner_id')
    #def onchange_partner_id(self):
    #    res = super(Sale, self).onchange_partner_id()
    #    self.payment_method_id = self.partner_id.sale_payment_method_id.id
    #    return res