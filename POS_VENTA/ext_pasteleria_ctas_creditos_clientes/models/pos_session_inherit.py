# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class PosSession(models.Model):
    _inherit = 'pos.session'


    def action_pos_session_closing_control(self):
        super().action_pos_session_closing_control()
        self.anula_asiento()
        self.registra_creditos_clientes()
        ##raise UserError(_('Hola bebe'))

    def anula_asiento(self):
        if self.config_id.hacer_asiento_contable==False:
            self.move_id.filtered(lambda move: move.state == 'posted').button_draft()
            self.move_id.with_context(force_delete=True).unlink()

    def registra_creditos_clientes(self):
    	busca=self.env['pos.payment'].search([('pos_order_id.session_id.id','=',self.id),('payment_method_id.motodo_credito_cliente','=',True)])
    	if busca:
    		for det in busca:
    			valores=({
    				'pos_order_id':det.pos_order_id.id,
    				'cliente_id':det.pos_order_id.partner_id.id,
    				'amount':det.amount,
    				'origen':"automatico",
    				'payment_method_id':det.payment_method_id.id,
    				'date_order':det.payment_date,
    				})
    			self.env['pos.creditos'].create(valores)
