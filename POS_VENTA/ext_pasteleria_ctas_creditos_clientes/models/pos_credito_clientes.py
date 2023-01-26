# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields,models,api,_
import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from datetime import datetime




class PosCreditCliente(models.Model):
    _name = 'pos.creditos'

    date_order = fields.Datetime(string='Fecha')

    payment_method_id = fields.Many2one('pos.payment.method', string='Payment Method', required=True)
    pos_order_id = fields.Many2one('pos.order')
    cliente_id = fields.Many2one('res.partner')
    amount = fields.Float(string='Amount', required=False,readonly=False, help="Total monto adeudado")
    status_credito = fields.Selection(selection=[('no_paid','No Pagado'),('paid','Pagado')],default='no_paid')
    origen = fields.Char(default='manual')

    def aprobar(self):
    	self.status_credito='paid'
    	#pass

    def cancel(self):
    	self.status_credito='no_paid'
    	#pass