# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models



class PosPaymentMotodo(models.Model):

    _inherit = "pos.payment.method"
    motodo_credito_cliente = fields.Boolean(default=False)
