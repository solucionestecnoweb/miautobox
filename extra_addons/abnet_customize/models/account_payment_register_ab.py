# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime, pytz
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_acquirer = fields.Many2one(
        'payment.acquirer',
        store=True,
        required=True,
        check_company=True,
        domain="[('company_id', '=', company_id), ('state', '!=', 'disabled')]",
        string='Forma de Pago',
        default=None
    )

    journal_id = fields.Many2one('account.journal', store=True, readonly=True,
        compute='_compute_journal_id',
        invisible=True,
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]"
    )
    rate = fields.Float(
        string='Tasa',
        store="True",
        required=False,
        readonly=True,
        digits = (12, 2),
    )
    x_time = fields.Float(
        string='time',
        required=False,
        store = True,
        copy=False,
        default=0,
    )
    es_gerente_tienda = fields.Boolean(
        compute='_set_es_gerente_tienda',
        readonly=True,
        string='¿-Es gerente de tienda-?',
        default='_set_es_gerente_tienda',
        store=False
    )

    @api.onchange('manual_currency_exchange_rate')
    def _onchange_manual_rate_rate(self):
        for rec in self:
            if rec.currency_id and rec.company_id:
                rec._get_rate()

    def _set_es_gerente_tienda(self):
        self.es_gerente_tienda = self.env['res.users'].has_group('abnet_customize.gerente_tienda')

    def _create_payment_vals_from_wizard(self):
        res = super(AccountPaymentRegister,self)._create_payment_vals_from_wizard()
        res.update({
            'x_time':self.x_time,
            'rate':self.rate,
            'payment_acquirer': self.payment_acquirer.id,
            })
        return res
        # payment_vals = {
        #     'date': self.payment_date,
        #     'amount': self.amount,
        #     'payment_type': self.payment_type,
        #     'partner_type': self.partner_type,
        #     'ref': self.communication,
        #     'journal_id': self.journal_id.id,
        #     'currency_id': self.currency_id.id,
        #     'partner_id': self.partner_id.id,
        #     'partner_bank_id': self.partner_bank_id.id,
        #     'payment_method_id': self.payment_method_id.id,
        #     'destination_account_id': self.line_ids[0].account_id.id,
        #     'payment_acquirer': self.payment_acquirer.id,
        #     'x_time': self.x_time,
        #     'rate': self.rate
        # }

        # if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
        #     payment_vals['write_off_line_vals'] = {
        #         'name': self.writeoff_label,
        #         'amount': self.payment_difference,
        #         'account_id': self.writeoff_account_id.id,
        #     }
        # return payment_vals

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegister,self)._create_payment_vals_from_batch(batch_result)
        res.update({
            'x_time':self.x_time,
            'rate':self.rate,
            'payment_acquirer': self.payment_acquirer.id,
            })
        return res
        # batch_values = self._get_wizard_values_from_batch(batch_result)
        # return {
        #     'date': self.payment_date,
        #     'amount': batch_values['source_amount_currency'],
        #     'payment_type': batch_values['payment_type'],
        #     'partner_type': batch_values['partner_type'],
        #     'ref': self._get_batch_communication(batch_result),
        #     'journal_id': self.journal_id.id,
        #     'currency_id': batch_values['source_currency_id'],
        #     'partner_id': batch_values['partner_id'],
        #     'partner_bank_id': batch_result['key_values']['partner_bank_id'],
        #     'payment_method_id': self.payment_method_id.id,
        #     'destination_account_id': batch_result['lines'][0].account_id.id,
        #     'payment_acquirer': self.payment_acquirer.id,
        #     'x_time': self.x_time,
        #     'rate': self.rate
        # }

    @api.depends('company_id', 'source_currency_id', 'payment_acquirer')
    def _compute_journal_id(self):
        for wizard in self:
            domain = [
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', wizard.company_id.id),
            ]
            journal = None
            if wizard.payment_acquirer:
                journal = wizard.payment_acquirer.journal_id
            if wizard.source_currency_id and not journal:
                journal = self.env['account.journal'].search(
                    domain + [('currency_id', '=', wizard.source_currency_id.id)], limit=1)
            if not journal:
                journal = self.env['account.journal'].search(domain, limit=1)
            wizard.journal_id = journal
            #wizard.currency_id = wizard.journal_id.currency_id

    @api.onchange('payment_date')
    def _onchange_payment_date(self):
        if not self.x_time or self.x_time == 0:
            if self.payment_date:
                tz = pytz.timezone('America/Caracas')
                tm=fields.datetime.now(tz).time()
                self.x_time = tm.hour + tm.minute / 60.0
                self._compute_amount()
                self._get_rate()

    # @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id', 'payment_date')
    # def _compute_amount(self):
    #     for wizard in self:
    #         if wizard.source_currency_id == wizard.currency_id:
    #             # Same currency.
    #             wizard.amount = wizard.source_amount_currency
    #         elif wizard.currency_id == wizard.company_id.currency_id:
    #             # Payment expressed on the company's currency.
    #             wizard.amount = wizard.source_amount
    #         else:
    #             # Foreign currency on payment different than the one set on the journal entries.
    #             hora = datetime.time(hour=int(self.x_time), minute=int((self.x_time - int(self.x_time)) * 60))
    #             payment_datetime = 0
    #             tzone = pytz.timezone('America/Caracas')
    #             payment_datetime = datetime.datetime.combine(wizard.payment_date, hora)
    #             amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount, wizard.currency_id, wizard.company_id,
    #                                                                              payment_datetime or fields.Datetime.now(tzone))
    #             wizard.amount = amount_payment_currency

    # @api.depends('amount')
    # def _compute_payment_difference(self):
    #     for wizard in self:
    #         if wizard.source_currency_id == wizard.currency_id:
    #             # Same currency.
    #             wizard.payment_difference = wizard.source_amount_currency - wizard.amount
    #         elif wizard.currency_id == wizard.company_id.currency_id:
    #             # Payment expressed on the company's currency.
    #             wizard.payment_difference = wizard.source_amount - wizard.amount
    #         else:
    #             # Foreign currency on payment different than the one set on the journal entries.
    #             hora = datetime.time(hour=int(self.x_time), minute=int((self.x_time - int(self.x_time)) * 60))
    #             payment_datetime = 0
    #             tzone = pytz.timezone('America/Caracas')
    #             payment_datetime = datetime.datetime.combine(wizard.payment_date, hora)
    #             amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount, wizard.currency_id, wizard.company_id,
    #                                                                              payment_datetime or fields.Datetime.now(tzone))
    #             wizard.payment_difference = amount_payment_currency - wizard.amount

    @api.depends('currency_id', 'payment_date', 'x_time','company_id','manual_currency_exchange_rate')
    def _get_rate(self):
        for wizard in self:
            wizard.rate = 1
            currency_id = wizard.currency_id
            if currency_id != wizard.company_id.currency_id and currency_id and wizard.company_id.currency_id:
                wizard.rate = wizard.manual_currency_exchange_rate
            
            # currency_id = wizard.currency_id
            # hora= datetime.time(hour=int(wizard.x_time), minute=int((wizard.x_time - int(wizard.x_time)) * 60))
            # payment_datetime = 0
            # tzone = pytz.timezone('America/Caracas')
            # wizard.rate = 1.0

            # if wizard.payment_date and wizard.currency_id and wizard.x_time and currency_id:
            #     payment_datetime = datetime.datetime.combine(wizard.payment_date, hora)
            #     payment_datetime = payment_datetime + datetime.timedelta(hours=4)

            # if currency_id != wizard.company_id.currency_id and currency_id and wizard.company_id.currency_id:
            #     wizard.rate = wizard.env['res.currency']._get_conversion_rate(
            #         wizard.company_id.currency_id,
            #         currency_id,
            #         wizard.company_id or wizard.env.company,
            #         payment_datetime or fields.Datetime.now(tzone)
            #     )

    @api.onchange('x_time')
    def _onchange_x_time(self):
        if self.payment_date:
            if not self.x_time or self.x_time == 0:
                tz = pytz.timezone('America/Caracas')
                tm=fields.datetime.now(tz).time()
                self.x_time = tm.hour + tm.minute / 60.0
            self._get_rate()

    @api.onchange('payment_acquirer')
    def _onchange_payment_acquirer(self):
        self._compute_journal_id()
        #self._compute_amount()
        self._get_rate()
