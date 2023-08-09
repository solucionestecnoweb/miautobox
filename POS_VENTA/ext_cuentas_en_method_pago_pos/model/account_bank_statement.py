# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

class PosPaymentMethodInheret(models.Model):

    _inherit = "pos.payment.method"

    receivable_account_id = fields.Many2one('account.account',
        string='Intermediary Account',
        required=True,
        domain=[('user_type_id.type', 'in',('receivable','liquidity'))],
        default=lambda self: self.env.company.account_default_pos_receivable_account_id,
        ondelete='restrict',
        help='Account used as counterpart of the income account in the accounting entry representing the pos sales.')
