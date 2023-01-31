# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)


from odoo import models, fields, api


class SaleReport(models.Model):
    _inherit = 'sale.order'

    confirmed_user_id = fields.Many2one('res.users', string='Confirmed User', readonly=True)
    opportunity_id = fields.Text(string='Opportunity_id', readonly=True)
    marca = fields.Many2one('product.product', string='marca')


class Account(models.Model):
    _inherit = 'account.move'
    marca = fields.Char(string='marca', related='invoice_line_ids.name', store=True)

    opportunity_id = fields.Text(string='Opportunity_id', readonly=True)
    modelo = fields.Many2one('product.product', string='Modelo', related='invoice_line_ids.product_id', store=True)

    @api.onchange('modelo')
    def _onchange_modelo(self):
        if self.modelo:
            logger.info("Entroooo")
        else:
            logger.info(" No entroooo")

    @api.onchange('marca')
    def _onchange_marca(self):
        if self.marca:
            logger.info("############################# MArca")
            logger.info(self.marca)
            logger.info(self.marca)
        else:
            logger.info("############################# no entro")

            logger.info(self.marca)

    # else:
    #     logger.info("############################# Marca")
    #
    #     logger.info(self.marca)
    #
