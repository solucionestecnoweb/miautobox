# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_turned_mobile_payment = fields.Boolean(string='Vuelto digital por Pago Movil?')