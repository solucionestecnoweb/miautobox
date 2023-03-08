# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.exceptions import Warning
from odoo.tools.misc import formatLang, format_date, get_lang


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = "account.move"

    igtf_ids=fields.One2many('account.payment.igtf','move_id', string='Cobros IGTF')

    amount_exento = fields.Monetary(compute='_compute_exento')
    amount_imponible = fields.Monetary(compute='_compute_exento')
    amount_exento_signed = fields.Monetary(default=0)

    pago_bs = fields.Monetary(compute='_compute_pago_bs')
    pago_divisa = fields.Monetary(compute='_compute_pago_div')
    impuesto_igtf = fields.Monetary(compute='_compute_pago_div')
    
    total_pagar = fields.Monetary(compute='_compute_total_paga')

    ########## CAMPOS EQUIVALENTE DEL GROUP 2 ########
    total_lineas_eq = fields.Float(compute='_compute_total_lineas')
    amount_by_group_eq = fields.Binary(string="Tax amount by group",compute='_compute_taxes_group')
    base_imponible_eq = fields.Float()
    exemto_eq = fields.Float()
    sub_total_eq = fields.Float(compute='_compute_sub_total_eq')
    pago_bs_eq = fields.Float(compute='_compute_pago_bs_eq')
    pago_usd_eq = fields.Float(compute='_compute_pago_usd_eq')
    impuesto_igtf_eq = fields.Float(compute='_compute_igtf_eq')
    total_pagar_eq = fields.Float(compute='_compute_total_eq')


 ########## FUNCIONES DE CAMPOS EQUIVALENTE DEL GROUP 2 ########
    def _compute_total_lineas(self):
        total_lineas=total_imponible=total_exemto=0
        for rec in self.invoice_line_ids:
            total_lineas=total_lineas+rec.price_subtotal
            if rec.tax_ids.amount!=0:
                total_imponible=total_imponible+rec.price_subtotal
            else:
                total_exemto=total_exemto+rec.price_subtotal
        self.total_lineas_eq=abs(total_lineas*self.busca_tasa()) if self.currency_id.id!=self.env.company.currency_id.id else abs(total_lineas/self.busca_tasa())
        self.base_imponible_eq=abs(total_imponible*self.busca_tasa()) if self.currency_id.id!=self.env.company.currency_id.id else abs(total_imponible/self.busca_tasa())
        self.exemto_eq=abs(total_exemto*self.busca_tasa()) if self.currency_id.id!=self.env.company.currency_id.id else abs(total_exemto/self.busca_tasa())

    def _compute_sub_total_eq(self):
        if self.currency_id.id==self.env.company.currency_id.id:
            self.sub_total_eq=abs(self.amount_total/self.busca_tasa())
        else:
            self.sub_total_eq=abs(self.amount_total*self.busca_tasa())

    def _compute_pago_bs_eq(self):
        if self.currency_id.id==self.env.company.currency_id.id:
            self.pago_bs_eq=abs(self.pago_bs/self.busca_tasa())
        else:
            self.pago_bs_eq=abs(self.pago_bs*self.busca_tasa())

    def _compute_pago_usd_eq(self):
        if self.currency_id.id==self.env.company.currency_id.id:
            self.pago_usd_eq=abs(self.pago_divisa/self.busca_tasa())
        else:
            self.pago_usd_eq=abs(self.pago_divisa*self.busca_tasa())

    def _compute_igtf_eq(self):
        if self.currency_id.id==self.env.company.currency_id.id:
            self.impuesto_igtf_eq=abs(self.impuesto_igtf/self.busca_tasa())
        else:
            self.impuesto_igtf_eq=abs(self.impuesto_igtf*self.busca_tasa())

    def _compute_total_eq(self):
        if self.currency_id.id==self.env.company.currency_id.id:
            self.total_pagar_eq=abs(self.total_pagar/self.busca_tasa())
        else:
            self.total_pagar_eq=abs(self.total_pagar*self.busca_tasa())


    def busca_tasa(self):
        tasa=1
        if self.currency_id.id==self.env.company.currency_id.id:
            #busca=self.env['res.currency.rate'].search([('currency_id','=',self.currency_id.id),('name','<=',self.invoice_date)],order='name asc')
            busca=self.env['res.currency.rate'].search([('currency_id','=',2),('name','<=',self.invoice_date)],order='name asc')
            if busca:
                for det in busca:
                    tasa=1/det.rate
        else:
            if self.amount_total or self.amount_total!=0:
                tasa=self.amount_total_signed/self.amount_total
        return tasa

    def _compute_taxes_group(self):
        ''' Helper to get the taxes grouped according their account.tax.group.
        This method is only used when printing the invoice.
        '''
        for move in self:
            lang_env = move.with_context(lang=move.partner_id.lang).env
            tax_lines = move.line_ids.filtered(lambda line: line.tax_line_id)
            tax_balance_multiplicator = -1 if move.is_inbound(True) else 1
            res = {}
            # There are as many tax line as there are repartition lines
            done_taxes = set()
            for line in tax_lines:
                res.setdefault(line.tax_line_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
                ##res[line.tax_line_id.tax_group_id]['amount'] += tax_balance_multiplicator * (line.amount_currency if line.currency_id else line.balance)
                res[line.tax_line_id.tax_group_id]['amount'] += abs(line.balance)/self.busca_tasa() if self.currency_id.id==self.env.company.currency_id.id else abs(line.balance)
                tax_key_add_base = tuple(move._get_tax_key_for_group_add_base(line))
                if tax_key_add_base not in done_taxes:
                    if line.currency_id and line.company_currency_id and line.currency_id != line.company_currency_id:
                        amount = line.company_currency_id._convert(line.tax_base_amount, line.currency_id, line.company_id, line.date or fields.Date.context_today(self))
                    else:
                        amount = line.tax_base_amount
                    res[line.tax_line_id.tax_group_id]['base'] += amount
                    # The base should be added ONCE
                    done_taxes.add(tax_key_add_base)

            # At this point we only want to keep the taxes with a zero amount since they do not
            # generate a tax line.
            for line in move.line_ids:
                for tax in line.tax_ids.flatten_taxes_hierarchy():
                    if tax.tax_group_id not in res:
                        res.setdefault(tax.tax_group_id, {'base': 0.0, 'amount': 0.0})
                        res[tax.tax_group_id]['base'] += tax_balance_multiplicator * (line.amount_currency if line.currency_id else line.balance)

            res = sorted(res.items(), key=lambda l: l[0].sequence)
            move.amount_by_group_eq = [(
                group.name, amounts['amount'],
                amounts['base'],
                formatLang(lang_env, amounts['amount']),
                formatLang(lang_env, amounts['base']),
                ##formatLang(lang_env, amounts['amount'], currency_obj=move.company_id.currency_id),
                ##formatLang(lang_env, amounts['base'], currency_obj=move.company_id.currency_id),
                len(res),
                group.id
            ) for group, amounts in res]
##################################################################
    def _compute_exento(self):
        valor_exemto=valor_imponible=0
        for selff in self:
            for rec in selff.invoice_line_ids:
                if rec.tax_ids.amount==0:
                    valor_exemto=valor_exemto+rec.price_subtotal
                if rec.tax_ids.amount!=0:
                    valor_imponible=valor_imponible+rec.price_subtotal
            selff.amount_exento=valor_exemto
            selff.amount_imponible=valor_imponible

    def _compute_pago_div(self):
        valor=igtf=0
        for selff in self:
            if selff.igtf_ids:
                for rec in selff.igtf_ids:
                    if selff.currency_id.id==selff.env.company.currency_id.id:
                        valor=valor+rec.monto_base
                        igtf=igtf+rec.monto_ret
                    else:
                        valor=valor+rec.monto_base_usd
                        igtf=igtf+rec.monto_ret/rec.tasa
            selff.pago_divisa=valor
            selff.impuesto_igtf=igtf

    def _compute_pago_bs(self):
        monto_bs=0
        self.pago_bs=self.amount_total-self.pago_divisa-self.amount_residual

    def _compute_total_paga(self):
        self.total_pagar=self.amount_total+self.impuesto_igtf


    def _check_balanced(self):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return

        # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
        # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
        # It happens as the ORM makes the create with the 'no_recompute' statement.
        self.env['account.move.line'].flush(['debit', 'credit', 'move_id'])
        self.env['account.move'].flush(['journal_id'])
        self._cr.execute('''
            SELECT line.move_id, ROUND(SUM(debit - credit), currency.decimal_places)
            FROM account_move_line line
            JOIN account_move move ON move.id = line.move_id
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_company company ON company.id = journal.company_id
            JOIN res_currency currency ON currency.id = company.currency_id
            WHERE line.move_id IN %s
            GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(debit - credit), currency.decimal_places) != 0.0;
        ''', [tuple(self.ids)])

        query_res = self._cr.fetchall()
        if query_res:
            ids = [res[0] for res in query_res]
            sums = [res[1] for res in query_res]
            #raise UserError(_("Cannot create unbalanced journal entry. Ids: %s\nDifferences debit - credit: %s") % (ids, sums))

    @api.constrains('amount_total','amount_residual')
    def asocia_asiento_igtf_factura_clie(self):
        for selff in self:
            ### CODIGO QUE LIMPIA INICIALMENTE EL CAMPO DONDE SE GUARDAS LOS ASIENTOS IGTF ASOCIADOS A LA FACT
            for limpia_linea in selff.igtf_ids:
                        limpia_linea.with_context(force_delete=True).unlink()
            ### fin
            cuenta_cli=selff.partner_id.property_account_receivable_id.id # cliente
            cuenta_prov=selff.partner_id.property_account_payable_id.id # proveedor
            if selff.move_type in ('out_invoice','out_refund'):
                cuenta_gene=cuenta_cli
            if selff.move_type in ('in_invoice','in_refund'):
                cuenta_gene=cuenta_prov
            # CLIENTES
            if selff.move_type in ('out_invoice','out_refund','in_invoice','in_refund'):
                for rec in selff.line_ids:
                    if rec.account_id.id==cuenta_gene:
                        id_move=rec.id
                #raise UserError(_('cursor3=%s')%id_move)
                if selff.state=='posted':
                    if selff.move_type in ('out_invoice','out_refund'):
                        cursor=selff.env['account.partial.reconcile'].search([('debit_move_id','=',id_move)])
                    if selff.move_type in ('in_invoice','in_refund'):
                        cursor=selff.env['account.partial.reconcile'].search([('credit_move_id','=',id_move)])
                else:
                    cursor=""##selff.env['account.partial.reconcile'].search([('debit_move_id','=',0)])
                if cursor:
                    for rec in cursor:
                        if selff.move_type in ('out_invoice','out_refund'):
                            pago_move_id=rec.credit_move_id.move_id.payment_id
                        if selff.move_type in ('in_invoice','in_refund'):
                            pago_move_id=rec.debit_move_id.move_id.payment_id
                        monto=pago_move_id.amount
                        if pago_move_id.payment_method_id.calculate_wh_itf==True:
                            if pago_move_id.currency_id.id!=self.company_currency_id.id:
                                busca=selff.env['res.currency.rate'].search([('currency_id','=',2),('name','<=',pago_move_id.date)],order='name asc')
                                if busca:
                                    for det in busca:
                                        tasa=1/det.rate
                                        if pago_move_id.currency_id.id!=self.env.company.currency_id.id:
                                            monto_base=pago_move_id.amount*tasa
                                            monto_base_usd=pago_move_id.amount
                                        else:
                                            monto_base=pago_move_id.amount
                                            monto_base_usd=pago_move_id.amount/tasa
                            retencion=monto_base*pago_move_id.payment_method_id.wh_porcentage/100
                            vols={
                            'move_id':selff.id,
                            'asiento_igtf':pago_move_id.asiento_cobro_igtf.id,
                            'metodo_pago':pago_move_id.payment_method_id.id,
                            'monto_base_usd':monto_base_usd,
                            'tasa':tasa,
                            'monto_base':monto_base,
                            'porcentaje':pago_move_id.payment_method_id.wh_porcentage,
                            'monto_ret':retencion,
                            }
                            verifica_asiento_igtf_fact=self.env['account.payment.igtf'].search([('asiento_igtf','=',pago_move_id.asiento_cobro_igtf.id)])
                            if not verifica_asiento_igtf_fact:
                                crear=selff.env['account.payment.igtf'].create(vols)
                                selff.igtf_ids=selff.env['account.payment.igtf'].search([('move_id','=',selff.id)])
                            #raise UserError(_('credit=%s')%pago_move_id)

class AccountMoveIgtf(models.Model):

    _name = 'account.payment.igtf'

    move_id = fields.Many2one('account.move')
    asiento_igtf = fields.Many2one('account.move')
    metodo_pago = fields.Many2one('account.payment.method')
    monto_base_usd = fields.Float()
    tasa = fields.Float()
    monto_base = fields.Float()
    porcentaje = fields.Float()
    monto_ret = fields.Float()