# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    apply_manual_currency_exchange = fields.Boolean(string='Aplicar cambio de tasa manual',default=False)
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(10,10),store=True,readonly=False)#,compute="_compute_manual_currency_exchange_rate")
    active_manual_currency_rate = fields.Boolean('Activar Moneda manual', default=True)
    

    #@api.depends('date','currency_id')
    #def _compute_manual_currency_exchange_rate(self):
    #    for rec in self:
    #        moneda = self.env['res.currency.rate'].search([('currency_id','=',171),('name','<=',rec.date)],order='name desc',limit=1).rate
    #        rec.manual_currency_exchange_rate = moneda

    @api.onchange('apply_manual_currency_exchange','invoice_date')
    def _onchange_apply_manual_currency_exchange(self):
        for rec in self:
            rec.manual_currency_exchange_rate = self.tasa_account_move()#self.env.company.currency_id.parent_id.rate

    def tasa_account_move(self):
        valor=1
        busca=self.env['res.currency.rate'].search([('name','<=',self.invoice_date)],order='name desc',limit=1)
        if busca:
            valor=busca.rate_real
        return valor
    
    @api.onchange('manual_currency_exchange_rate', 'apply_manual_currency_exchange','invoice_line_ids.price_unit','line_ids')
    def _onchange_manual_currency_rate(self):
        if not self.has_reconciled_entries:
            self._onchange_currency()
        # for rec in self.invoice_line_ids:
        #     rec._get_computed_taxes()
        #     rec._onchange_account_id()
        #for rec in self:
        #    rec._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
        #    raise UserError('Hola mundo')

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
        
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    active_manual_currency_rate = fields.Boolean('Activar Moneda manual', default=False,related='move_id.active_manual_currency_rate')
    apply_manual_currency_exchange = fields.Boolean(string='Aplicar cambio de tasa manual',related='move_id.apply_manual_currency_exchange')
    manual_currency_exchange_rate = fields.Float(string='Tipo de tasa manual', digits=(10,10),related="move_id.manual_currency_exchange_rate")
    #manual_currency_exchange_rate_inverter = fields.Float(string='Tipo de tasa manual Inverter', digits=(10,10),related="move_id.manual_currency_exchange_rate_inverter")
    
    
    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        ''' This method is used to recompute the values of 'amount_currency', 'debit', 'credit' due to a change made
        in some business fields (affecting the 'price_subtotal' field).

        :param price_subtotal:  The untaxed amount.
        :param move_type:       The type of the move.
        :param currency:        The line's currency.
        :param company:         The move's company.
        :param date:            The move's date.
        :return:                A dictionary containing 'debit', 'credit', 'amount_currency'.
        '''
        balance = 0.0
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        price_subtotal *= sign
        if currency and currency != company.currency_id:
            # Multi-currencies.
            if self.move_id.manual_currency_exchange_rate != 0:
                balance = price_subtotal/self.move_id.manual_currency_exchange_rate
            #raise UserError(balance)
            
            return {
                'amount_currency': price_subtotal,
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
            }
        else:
            # Single-currency.
            return {
                'amount_currency': price_subtotal,
                'debit': price_subtotal > 0.0 and price_subtotal or 0.0,
                'credit': price_subtotal < 0.0 and -price_subtotal or 0.0,
            }
