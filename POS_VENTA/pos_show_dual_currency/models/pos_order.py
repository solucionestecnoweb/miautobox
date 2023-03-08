# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from functools import partial

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"


    total_igtf = fields.Float(string='IGTF 3%')

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['total_igtf'] = ui_order.get('igtf')
        return order_fields

