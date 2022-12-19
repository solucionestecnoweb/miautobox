# -*- coding: utf-8 -*-
#######################################################

#   CorpoEureka - Innovation First!
#
#   Copyright (C) 2021-TODAY CorpoEureka (<https://www.corpoeureka.com>)
#   Author: CorpoEureka (<https://www.corpoeureka.com>)
#
#   This software and associated files (the "Software") may only be used (executed,
#   modified, executed after modifications) if you have pdurchased a vali license
#   from the authors, typically via Odoo Apps, or if you have received a written
#   agreement from the authors of the Software (see the COPYRIGHT file).
#
#   You may develop Odoo modules that use the Software as a library (typically
#   by depending on it, importing it and using its resources), but without copying
#   any source code or material from the Software. You may distribute those
#   modules under the license of your choice, provided that this license is
#   compatible with the terms of the Odoo Proprietary License (For example:
#   LGPL, MIT, or proprietary licenses similar to this one).
#
#   It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#   or modified copies of the Software.
#
#   The above copyright notice and this permission notice must be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

#   Responsable CorpoEureka: Jose Mazzei
##########################################################################-

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('price_unit','move_id.manual_currency_exchange_rate','currency_id')
    def _compute_price_unit_ref(self):
        for record in self:
            record[("price_unit_ref")] = record['price_unit']
            if record.move_id.manual_currency_exchange_rate != 0 and record.display_type == False:
                record[("price_unit_ref")] = record['price_unit']*record.move_id.manual_currency_exchange_rate if record['currency_id'] == self.env.company.currency_id else record['price_unit']/record.move_id.manual_currency_exchange_rate

    @api.onchange('product_id','quantity','price_subtotal','move_id.manual_currency_exchange_rate')
    def onchange_product_id_ref(self):
        for record in self:  
            record._compute_price_unit_ref()
            record.move_id.sudo()._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
            record[("price_subtotal_ref")] = record.quantity * record.price_unit_ref

    @api.depends('price_unit_ref','quantity')
    def _compute_price_subtotal_ref(self):
        for record in self:
            record[("price_subtotal_ref")] = record[("price_subtotal")]
            if record.move_id.manual_currency_exchange_rate != 0 and record.display_type == False:  
                record[("price_subtotal_ref")] = record.quantity * record.price_unit_ref
    
    @api.onchange('price_unit','price_total')
    def _onchange_price_unit_ref(self):
        for rec in self:
            if rec.move_id:
                rec.move_id.sudo()._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
                rec.move_id._onchange_currency()
                #rec.move_id._recompute_tax_lines(recompute_tax_base_amount=True)
                #rec._get_computed_taxes()
                #rec._onchange_account_id()

    @api.onchange('currency_id')
    def _onchange_currency(self):
        for line in self:
            company = line.move_id.company_id
            line.move_id._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
            line.move_id._onchange_manual_currency_rate()
            if line.move_id.is_invoice(include_receipts=True):
                line._onchange_price_subtotal()
            elif not line.move_id.reversed_entry_id:
                balance = line.amount_currency / line.move_id.manual_currency_exchange_rate if line.currency_id != self.env.company.currency_id else line.amount_currency
                line.debit = balance if balance > 0.0 else 0.0
                line.credit = -balance if balance < 0.0 else 0.0
    # Campos para Calcular la MultiMoneda
    price_unit_ref = fields.Float(string='Monto Ref', store=True,readonly=True, compute='_compute_price_unit_ref', tracking=4, default=0, invisible="1",digits=(20,3))
    price_subtotal_ref = fields.Float(string='Subtotal Ref',store=True, readonly=True, tracking=4, default=0,compute='_compute_price_subtotal_ref',digits=(20,3))
    currency_id_line = fields.Many2one(related="move_id.currency_id_dif",string="Moneda Referencia", invisible="1",store=True)
    company_id = fields.Many2one(related="move_id.company_id",store=True)
    invoice_date = fields.Date(related="move_id.invoice_date",store=True)

    # Añadir Multimoneda en Cuenta Analítica (Centro de Costos)
    def _prepare_analytic_line(self):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            an analytic account. This method is intended to be extended in other modules.
            :return list of values to create analytic.line
            :rtype list
        """
        super(AccountMoveLine, self)._prepare_analytic_line()
        result = []
        amount_usd= 0.0
        for move_line in self:
            amount = (move_line.credit or 0.0) - (move_line.debit or 0.0)
            if amount < 0:
                amount_usd=move_line.price_subtotal_ref * -1
            else:
                amount_usd=move_line.price_subtotal_ref
            default_name = move_line.name or (move_line.ref or '/' + ' -- ' + (move_line.partner_id and move_line.partner_id.name or '/'))
            result.append({
                'name': default_name,
                'date': move_line.date,
                'account_id': move_line.analytic_account_id.id,
                'tag_ids': [(6, 0, move_line._get_analytic_tag_ids())],
                'unit_amount': move_line.quantity,
                'product_id': move_line.product_id and move_line.product_id.id or False,
                'product_uom_id': move_line.product_uom_id and move_line.product_uom_id.id or False,
                'amount': amount,
                'amount_usd': amount_usd,
                'general_account_id': move_line.account_id.id,
                'ref': move_line.ref,
                'move_id': move_line.id,
                'user_id': move_line.move_id.invoice_user_id.id or self._uid,
                'partner_id': move_line.partner_id.id,
                'company_id': move_line.analytic_account_id.company_id.id or self.env.company.id,
            })
        return result

    # Añadir Multimoneda en Cuenta Analítica (Centro de Costos)
    def _prepare_analytic_distribution_line(self, distribution):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            analytic tags with analytic distribution.
        """
        super(AccountMoveLine, self)._prepare_analytic_distribution_line(distribution)
        amount_usd= 0.0
        self.ensure_one()
        amount = -self.balance * distribution.percentage / 100.0
        default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
        if amount < 0:
                amount_usd=self.price_subtotal_ref * -1
        else:
            amount_usd=self.price_subtotal_ref
        return {
            'name': default_name,
            'date': self.date,
            'account_id': distribution.account_id.id,
            'partner_id': self.partner_id.id,
            'tag_ids': [(6, 0, [distribution.tag_id.id] + self._get_analytic_tag_ids())],
            'unit_amount': self.quantity,
            'product_id': self.product_id and self.product_id.id or False,
            'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
            'amount': amount,
            'amount_usd': amount_usd,
            'general_account_id': self.account_id.id,
            'ref': self.ref,
            'move_id': self.id,
            'user_id': self.move_id.invoice_user_id.id or self._uid,
            'company_id': distribution.account_id.company_id.id or self.env.company.id,
        }

    debit_usd   = fields.Monetary('Debit $',default=0.0, currency_field='currency_id_line',compute="_report_usd_fields",store=True)
    credit_usd  = fields.Monetary('Credit $',default=0.0, currency_field='currency_id_line',compute="_report_usd_fields",store=True)
    balance_usd = fields.Monetary('Balance $',default=0.0, currency_field='currency_id_line',compute="_report_usd_fields",store=True)
    
    @api.depends('debit','credit','balance','move_id.manual_currency_exchange_rate','move_id.currency_id','currency_id')
    def _report_usd_fields(self):
        for rec in self:
            rec.debit_usd = 0 
            rec.credit_usd = 0 
            rec.balance_usd = 0
            if rec.move_id.currency_id != self.env.company.currency_id:
                if rec.debit != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.debit_usd = abs(rec.amount_currency)
                if rec.credit != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.credit_usd = abs(rec.amount_currency)
                if rec.balance != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.balance_usd = rec.amount_currency
            else:
                if rec.debit != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.debit_usd = rec.debit * rec.move_id.manual_currency_exchange_rate
                if rec.credit != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.credit_usd = rec.credit * rec.move_id.manual_currency_exchange_rate
                if rec.balance != 0 and rec.manual_currency_exchange_rate != 0:
                    rec.balance_usd = rec.balance * rec.move_id.manual_currency_exchange_rate


    @api.onchange('amount_currency')
    def _onchange_amount_currency_ref(self):
        balance = self.amount_currency if self.env.company.currency_id == self.move_id.currency_id else self.amount_currency / self.manual_currency_exchange_rate
         #balance = currency._convert(amount_currency, company.currency_id, company, date or fields.Date.context_today(self))
        if not self.matched_debit_ids and not self.matched_credit_ids:
            self.debit =  balance > 0.0 and balance or 0.0
            self.credit =  balance < 0.0 and -balance or 0.0

    @api.onchange('currency_id')
    def _onchange_currency(self):
        res = super(AccountMoveLine,self)._onchange_currency()
        for line in self:
            #line.move_id._recompute_tax_lines(recompute_tax_base_amount=True)
            #line._get_computed_taxes()
            line.move_id.sudo()._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
            company = line.move_id.company_id
            if line.move_id.is_invoice(include_receipts=True):
                line._onchange_price_subtotal()
                #line._onchange_account_id()
            elif not line.move_id.reversed_entry_id:
                balance = line.amount_currency / line.move_id.manual_currency_exchange_rate if line.currency_id != self.env.company.currency_id else line.amount_currency
                line.debit = balance if balance > 0.0 else 0.0
                line.credit = -balance if balance < 0.0 else 0.0
                
    def _prepare_reconciliation_partials(self):
        ''' Prepare the partials on the current journal items to perform the reconciliation.
        /!\ The order of records in self is important because the journal items will be reconciled using this order.

        :return: A recordset of account.partial.reconcile.
        '''
        debit_lines = iter(self.filtered(lambda line: line.balance > 0.0 or line.amount_currency > 0.0))
        credit_lines = iter(self.filtered(lambda line: line.balance < 0.0 or line.amount_currency < 0.0))
        debit_line = None
        credit_line = None

        debit_amount_residual = 0.0
        debit_amount_residual_currency = 0.0
        credit_amount_residual = 0.0
        credit_amount_residual_currency = 0.0
        debit_line_currency = None
        credit_line_currency = None

        partials_vals_list = []

        while True:

            # Move to the next available debit line.
            if not debit_line:
                debit_line = next(debit_lines, None)
                if not debit_line:
                    break
                debit_amount_residual = debit_line.amount_residual

                if debit_line.currency_id:
                    debit_amount_residual_currency = debit_line.amount_residual_currency
                    debit_line_currency = debit_line.currency_id
                else:
                    debit_amount_residual_currency = debit_amount_residual
                    debit_line_currency = debit_line.company_currency_id

            # Move to the next available credit line.
            if not credit_line:
                credit_line = next(credit_lines, None)
                if not credit_line:
                    break
                credit_amount_residual = credit_line.amount_residual

                if credit_line.currency_id:
                    credit_amount_residual_currency = credit_line.amount_residual_currency
                    credit_line_currency = credit_line.currency_id
                else:
                    credit_amount_residual_currency = credit_amount_residual
                    credit_line_currency = credit_line.company_currency_id

            min_amount_residual = min(debit_amount_residual, -credit_amount_residual)
            has_debit_residual_left = not debit_line.company_currency_id.is_zero(debit_amount_residual) and debit_amount_residual > 0.0
            has_credit_residual_left = not credit_line.company_currency_id.is_zero(credit_amount_residual) and credit_amount_residual < 0.0
            has_debit_residual_curr_left = not debit_line_currency.is_zero(debit_amount_residual_currency) and debit_amount_residual_currency > 0.0
            has_credit_residual_curr_left = not credit_line_currency.is_zero(credit_amount_residual_currency) and credit_amount_residual_currency < 0.0

            if debit_line_currency == credit_line_currency:
                # Reconcile on the same currency.

                # The debit line is now fully reconciled because:
                # - either amount_residual & amount_residual_currency are at 0.
                # - either the credit_line is not an exchange difference one.
                if not has_debit_residual_curr_left and (has_credit_residual_curr_left or not has_debit_residual_left):
                    debit_line = None
                    continue

                # The credit line is now fully reconciled because:
                # - either amount_residual & amount_residual_currency are at 0.
                # - either the debit is not an exchange difference one.
                if not has_credit_residual_curr_left and (has_debit_residual_curr_left or not has_credit_residual_left):
                    credit_line = None
                    continue

                min_amount_residual_currency = min(debit_amount_residual_currency, -credit_amount_residual_currency)
                min_debit_amount_residual_currency = min_amount_residual_currency
                min_credit_amount_residual_currency = min_amount_residual_currency

            else:
                # Reconcile on the company's currency.

                # The debit line is now fully reconciled since amount_residual is 0.
                if not has_debit_residual_left:
                    debit_line = None
                    continue

                # The credit line is now fully reconciled since amount_residual is 0.
                if not has_credit_residual_left:
                    credit_line = None
                    continue

                min_debit_amount_residual_currency = credit_line.company_currency_id._convert(
                    min_amount_residual,
                    debit_line.currency_id,
                    credit_line.company_id,
                    credit_line.date,
                )
                min_debit_amount_residual_currency = min_amount_residual * credit_line.manual_currency_exchange_rate if debit_line.currency_id != self.env.company.currency_id else min_amount_residual 
                min_credit_amount_residual_currency = debit_line.company_currency_id._convert(
                    min_amount_residual,
                    credit_line.currency_id,
                    debit_line.company_id,
                    debit_line.date,
                )
                min_credit_amount_residual_currency = min_amount_residual * debit_line.manual_currency_exchange_rate if credit_line.currency_id != self.env.company.currency_id else min_amount_residual 
                

            debit_amount_residual -= min_amount_residual
            debit_amount_residual_currency -= min_debit_amount_residual_currency
            credit_amount_residual += min_amount_residual
            credit_amount_residual_currency += min_credit_amount_residual_currency

            partials_vals_list.append({
                'amount': min_amount_residual,
                'debit_amount_currency': min_debit_amount_residual_currency,
                'credit_amount_currency': min_credit_amount_residual_currency,
                'debit_move_id': debit_line.id,
                'credit_move_id': credit_line.id,
            })

        return partials_vals_list

    #def _check_reconciliation(self):
    #    pass
            
