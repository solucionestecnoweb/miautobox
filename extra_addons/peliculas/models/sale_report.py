# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)


class SaleReport(models.Model):
    _inherit = 'sale.report'

    confirmed_user_id = fields.Many2one('res.users', string='Confirmed User', readonly=True)
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['confirmed_user_id'] = ", s.confirmed_user_id"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    marca = fields.Char(string='marca')

    def _select(self):
        
        return super()._select() + ", move.marca as marca"


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    modelo = fields.Many2one('product.product', string='Modelo')

    def _select(self):
        return super()._select() + ", move.modelo as modelo"

    @api.onchange('modelo')
    def _onchange_modelo(self):

        logger.info('#############')
        logger.info(self.modelo)

