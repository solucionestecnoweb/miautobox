# -*- coding: utf-8 -*-
# Part of abnet_customize. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    name = fields.Datetime(
        string='Date',
        required=True,
        index=True,
        default=lambda self: fields.Datetime.now()
    )