# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
from odoo import fields, models, api
import datetime, pytz


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_acquirer = fields.Many2one(
        'payment.acquirer',
        check_company=True,
        required=True,
        domain="[('company_id', '=', company_id), ('state', '!=', 'disabled')]",
        string='Forma de Pago',
        default=None
    )
    rate = fields.Float(
        string='Tasa',
        store="True",
        required=False,
        readonly=True,
        digits = (12, 2)
    )
    x_time = fields.Float(
        string='time',
        required=False,
        store = True,
        copy=False,
        default=0
    )
    es_gerente_tienda = fields.Boolean(
        compute='_set_es_gerente_tienda',
        store=False,
        string='¿-Es gerente de tienda-?',
        default='_set_es_gerente_tienda',
        readonly=True
    )

    @api.onchange('payment_acquirer')
    def _onchange_payment_acquirer(self):
        self._compute_journal_id()
        self._get_rate()


    @api.onchange('date')
    def _onchange_date(self):
        if self.date:
            if not self.x_time or self.x_time == 0:
                tz = pytz.timezone('America/Caracas')
                tm=fields.datetime.now(tz).time()
                self.x_time = tm.hour + tm.minute / 60.0
            self._get_rate()

    @api.onchange('x_time')
    def _onchange_x_time(self):
        if self.date and self.date != 0:
            if not self.x_time or self.x_time == 0:
                tz = pytz.timezone('America/Caracas')
                tm=fields.datetime.now(tz).time()
                self.x_time = tm.hour + tm.minute / 60.0
            self._get_rate()

    @api.depends('payment_acquirer')
    def _compute_journal_id(self):
        for pay in self:
            journal = None
            currency = self.company_id.currency_id
            if pay.payment_acquirer:
                journal = pay.payment_acquirer.journal_id
                currency = journal.currency_id
            pay.journal_id = journal
            pay.currency_id = currency
            self._get_rate()

    @api.depends('currency_id', 'date', 'x_time','manual_currency_exchange_rate')
    def _get_rate(self):
        currency_id = self.currency_id
        hora= datetime.time(hour=int(self.x_time), minute=int((self.x_time - int(self.x_time)) * 60))
        payment_datetime = 0
        tzone = pytz.timezone('America/Caracas')
        self.rate = 1.0
        if self.date and self.currency_id and (self.company_id or self.company_id.env.company.id):
            payment_datetime = datetime.datetime.combine(self.date, hora)
            payment_datetime = payment_datetime + datetime.timedelta(hours=4)
            if currency_id != self.company_id.currency_id and currency_id:
                self.rate = self.manual_currency_exchange_rate

    def _set_es_gerente_tienda(self):
        self.es_gerente_tienda = self.env['res.users'].has_group('abnet_customize.gerente_tienda')

    #@api.model
    #def _default_get(self, fields):
    #    res = super(AccountPayment, self).default_get(fields)
    #    cia = self.env.company
    #    if not self.company_id:
    #        res.update({'company_id': cia})
    #    return res
