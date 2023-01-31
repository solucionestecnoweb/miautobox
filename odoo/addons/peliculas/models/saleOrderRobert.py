import logging
from odoo import fields, models, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):

    _inherit = "sale.order"

    description_sale = fields.Text('Sales Description')

    def SpecialCommand6(self):

        ids = [1, 9]
        self.write({"tax_id": [(6, 0, ids)]})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def taxes_for_button(self):
        ids = [1, 9]
        self.write({"tax_id": [(6, 0, ids)]})


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def taxes(self):
        ids = [1, 9]
        self.write({"tax_id": [(6, 0, ids)]})
