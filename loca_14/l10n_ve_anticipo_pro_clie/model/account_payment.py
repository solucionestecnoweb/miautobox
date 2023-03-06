# coding: utf-8
###########################################################################

import logging

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

#_logger = logging.getLogger(__name__)
class account_payment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'
    #name =fields.Char(compute='_valor_anticipo')
    darrell = fields.Char()

    #Este campo es para el modulo IGTF
    #move_itf_id = fields.Many2one('account.move', 'Asiento contable')

    #Estos Campos son para el modulo de anticipo
    tipo = fields.Char()
    anticipo = fields.Boolean(defaul=False)
    usado = fields.Boolean(defaul=False)
    anticipo_move_id = fields.Many2one('account.move', 'Id de Movimiento de anticipo donde pertenece dicho pago')
    saldo_disponible = fields.Monetary(string='Saldo Disponible')
    move_id = fields.Many2one('account.move')
    factura_id = fields.Many2one('account.move', 'Id de Movimiento o factura donde pertenece dicho pago')

    def _valor_anticipo(self):
        nombre=self.name
        saldo=self.saldo_disponible
        self.name=nombre

    def action_post(self):
        super().action_post()
        #raise UserError(_('cuenta id = %s')%self.id)
        pago_id=self.id
        self.direccionar_cuenta_anticipo(pago_id)


    
    def direccionar_cuenta_anticipo(self,id_pago):
        cuenta_anti_cliente = self.partner_id.account_anti_receivable_id.id
        cuenta_anti_proveedor = self.partner_id.account_anti_payable_id.id
        cuenta_cobrar = self.partner_id.property_account_receivable_id.id
        cuenta_pagar = self.partner_id.property_account_payable_id.id
        anticipo = self.anticipo
        tipo_persona = self.partner_type
        tipo_pago = self.payment_type
        #raise UserError(_('tipo = %s')%tipo_pago)
        if anticipo==True:
            if tipo_persona=="supplier":
                tipoo='in_invoice'
            if tipo_persona=="customer":
                tipoo='out_invoice'
            self.tipo=tipoo
            if not cuenta_anti_proveedor:
                raise UserError(_('Esta Empresa no tiene asociado una cuenta de anticipo para proveedores/clientes. Vaya al modelo res.partner, pestaña contabilidad y configure'))
            if not cuenta_anti_cliente:
                raise UserError(_('Esta Empresa no tiene asociado una cuenta de anticipo para proveedores/clientes. Vaya al modelo res.partner, pestaña contabilidad y configure'))
            if cuenta_anti_cliente and cuenta_anti_proveedor:
                if tipo_persona=="supplier":
                    cursor_move_line = self.env['account.move.line'].search([('payment_id','=',self.id),('account_id','=',cuenta_pagar)])
                    for det_cursor in cursor_move_line:
                        self.env['account.move.line'].browse(det_cursor.id).write({
                            'account_id':cuenta_anti_proveedor,
                            })
                    #raise UserError(_('cuenta id = %s')%cursor_move_line.account_id.id)
                if tipo_persona=="customer":
                    cursor_move_line = self.env['account.move.line'].search([('payment_id','=',self.id),('account_id','=',cuenta_cobrar)])
                    for det_cursor in cursor_move_line:
                        self.env['account.move.line'].browse(det_cursor.id).write({
                            'account_id':cuenta_anti_cliente,
                            })
                    #raise UserError(_('cuenta id = %s')%cursor_move_line.account_id.id)
                self.saldo_disponible=self.amount
        else:
            return 0

        

    @api.model
    def check_partner(self):
        '''metodo que chequea el rif de la empresa y la compañia si son diferentes
        retorna True y si son iguales retorna False'''
        idem = False
        company_id = self._get_company()
        for pago in self:
            if pago.partner_id.vat != company_id.partner_id.vat:
                idem = True
                return idem
        return idem

    def _get_company_itf(self):
        '''Método que retorna verdadero si la compañia debe retener el impuesto ITF'''
        company_id = self._get_company()
        if company_id.calculate_wh_itf:
            return True
        return False

    @api.model
    def _get_company(self):
        '''Método que busca el id de la compañia'''
        company_id = self.env['res.users'].browse(self.env.uid).company_id
        return company_id

    @api.model
    def check_payment_type(self):
        '''metodo que chequea que el tipo de pago si pertenece al tipo outbound'''
        type_bool = False
        for pago in self:
            type_payment = pago.payment_type
            if type_payment == 'outbound':
                type_bool = True
        return type_bool

    def get_name(self):
        '''metodo que crea el Nombre del asiento contable si la secuencia no esta creada, crea una con el
        nombre: 'l10n_account_withholding_itf'''

        self.ensure_one()
        SEQUENCE_CODE = 'l10n_ve_cuenta_retencion_itf'
        company_id = self._get_company()
        IrSequence = self.env['ir.sequence'].with_context(force_company=company_id.id)
        name = IrSequence.next_by_code(SEQUENCE_CODE)

        # si aún no existe una secuencia para esta empresa, cree una
        if not name:
            IrSequence.sudo().create({
                'prefix': 'IGTF',
                'name': 'Localización Venezolana impuesto ITF %s' % company_id.id,
                'code': SEQUENCE_CODE,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': company_id.id,
            })
            name = IrSequence.next_by_code(SEQUENCE_CODE)
        return name
