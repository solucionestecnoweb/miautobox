# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class PosSession(models.Model):
    _inherit = 'pos.session'

    asiento_igtf_id = fields.Many2one('account.move')

    #def action_pos_session_closing_control(self):
        #super().action_pos_session_closing_control()
        #self.recalcula_asiento_igtf()
        ##raise UserError(_('Hola angel'))

    def recalcula_asiento_igtf(self):
        monto_base_igtf=monto_igtf=0
        lista_pos_order = self.env['pos.order'].search([('session_id','=',self.id)],order="id asc")
        if lista_pos_order:
            for det in lista_pos_order:
                if det.payment_ids:
                    for rec in det.payment_ids:
                        if rec.payment_method_id.calculate_wh_itf==True:
                            monto_igtf=monto_igtf+rec.amount*self.config_id.wh_porcentage/100
        if monto_igtf>0:
            cuenta_igtf=self.config_id.account_wh_itf_id.id
            cuenta_otra=self.config_id.company_id.partner_id.property_account_receivable_id.id
            diario_tempo=self.config_id.journal_transi.id
            secuencia=self.get_name_igtf_pos()
            id_move=self.registro_movimiento_asiento(monto_igtf,secuencia,diario_tempo)
            idv_move=id_move.id
            valor=self.registro_movimiento_linea(idv_move,monto_igtf,cuenta_igtf,cuenta_otra)
            moves= self.env['account.move'].search([('id','=',idv_move)])
            moves.action_post()
            self.asiento_igtf_id=id_move
            #raise UserError(_('valor=%s')%monto_igtf)

    def get_name_igtf_pos(self):
        self.ensure_one()
        SEQUENCE_CODE = 'IGTF_POS'
        company_id = self._get_company()
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id.id)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'IGTF/POS/',
                'name': 'Impuesto ITF %s' % company_id.id,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': company_id.id,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        return name

    @api.model
    def _get_company(self):
        '''Método que busca el id de la compañia'''
        company_id = self.env['res.users'].browse(self.env.uid).company_id
        return company_id

    def registro_movimiento_asiento(self,amont_totall,secuencia,diario_tempo):
        #raise UserError(_('darrell = %s')%self.partner_id.vat_retention_rate)
        name = secuencia
        signed_amount_total=0
        signed_amount_total=amont_totall
        id_journal=diario_tempo#self.journal_id.id#loca14
        #raise UserError(_('papa = %s')%signed_amount_total)
        value = {
            'name': name,
            'date': self.start_at, #self.payment_date,#listo
            #'amount_total':self.vat_retentioned,# LISTO
            'partner_id': self.company_id.partner_id.id, #LISTO
            'journal_id':diario_tempo, #id_journal,
            #'ref': "Pago de igtf %s" % (self.communication),
            #'amount_total':signed_amount_total,# LISTO
            'amount_total_signed':signed_amount_total,# LISTO
            'move_type': "entry",# estte campo es el que te deja cambiar y almacenar valores
            'company_id':self.env.company.id,#loca14
            'currency_id':3, #self.currency_id.id if self.currency_id.id!=self.company_currency_id.id else "",
        }
        #raise UserError(_('value= %s')%value)
        move_obj = self.env['account.move']
        move_id = move_obj.create(value)    
        return move_id

    def registro_movimiento_linea(self,id_movv,retencion,cuenta_igtf,cuenta_otra):
        #raise UserError(_('ID MOVE = %s')%id_movv)
        name = "IGTF del pago: "#+self.communication
        valores = retencion #self.conv_div_extranjera(self.vat_retentioned) #VALIDAR CONDICION
        #raise UserError(_('valores = %s')%valores)
        cero = 0.0
              
        ### para clientes
        """if self.payment_type=="inbound":
            cuenta_haber=cuenta_igtf.id
            cuenta_debe=cuenta_otra.id

        ### para proveedores
        if self.payment_type=="outbound":
            cuenta_haber=cuenta_otra.id
            cuenta_debe=cuenta_igtf.id"""

        cuenta_haber=cuenta_igtf
        cuenta_debe=cuenta_otra

        balances=cero-valores
        value = {
             'name': name,
             'ref' : "Pago de igtf/"+self.name,
             'move_id': int(id_movv),
             'date': self.start_at,#self.payment_date,
             'partner_id': self.env.company.partner_id.id,
             'account_id': cuenta_haber,
             #'currency_id':self.invoice_id.currency_id.id,
             #'amount_currency': 0.0,
             #'date_maturity': False,
             'credit': valores,
             'debit': 0.0, # aqi va cero   EL DEBITO CUNDO TIENE VALOR, ES QUE EN ACCOUNT_MOVE TOMA UN VALOR
             'balance':-valores, # signo negativo
             'price_unit':balances,
             'price_subtotal':balances,
             'price_total':balances,
             #'currency_id':self.currency_id.id if self.currency_id.id!=self.company_currency_id.id else "",
             #'amount_currency': -1*self.amount if self.currency_id.id!=self.company_currency_id.id else "",

        }

        move_line_obj = self.env['account.move.line']
        move_line_id1 = move_line_obj.create(value)

        balances=valores-cero
        value['name'] = " "
        value['account_id'] = cuenta_debe
        value['credit'] = 0.0 # aqui va cero
        value['debit'] = valores
        value['balance'] = valores
        value['price_unit'] = balances
        value['price_subtotal'] = balances
        value['price_total'] = balances
        #value['currency_id'] = self.currency_id.id if self.currency_id.id!=self.company_currency_id.id else ""
        #alue['amount_currency'] = self.amount if self.currency_id.id!=self.company_currency_id.id else ""

        move_line_id2 = move_line_obj.create(value)