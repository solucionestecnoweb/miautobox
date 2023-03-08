# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class Sale(models.Model):
    _inherit = 'sale.order'

    team_x_company_id = fields.Many2many(
        related='team_id.x_company_id', 
        string="Team Companies", 
        readonly=True
    )
    team_id = fields.Many2one(
        'crm.team', 'Sales Team', 
        check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('company_id', 'in', team_x_company_id)]"
    )
    es_call_center = fields.Boolean(
        string='¿Es parte del Call Center?',
        store=False
    )
    pricelist_id = fields.Many2one(
        'product.pricelist', 'Pricelist',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )
    rate = fields.Float(
        string='Tasa',
        store ="True",
        required=False, readonly=True,
        digits = (12, 2)
    )
    es_gerente_tienda = fields.Boolean(
        string='¿Es gerente de tienda?',
        readonly=True,
        store=False
    )


    @api.onchange("pricelist_id")
    def _set_pricelist_currency(self):
        if self.pricelist_id:
            self.currency_id = self.pricelist_id.currency_id
            self._get_rate()

    @api.onchange('manual_currency_exchange_rate')
    def _onchange_manual_rate_rate(self):
        for rec in self:
            if rec.currency_id and rec.pricelist_id and rec.date_order and rec.company_id:
                rec._get_rate()


    @api.depends('pricelist_id', 'date_order','currency_id','manual_currency_exchange_rate')
    def _get_rate(self):
        self.rate = 1
        currency_id = self.currency_id
        if currency_id.id != self.company_id.currency_id.id:
            self.rate = self.manual_currency_exchange_rate
        # else:
        #     currency_id = self.env['res.currency'].search([('name', '=', 'VED')], limit=1, order='id desc')
        #     self.rate = self.env['res.currency']._get_conversion_rate(
        #         self.company_id.currency_id,
        #         currency_id,
        #         self.company_id or self.env.company,
        #         self.date_order or fields.Date.today()
        #     )


    def _prepare_invoice(self):
        res = super(Sale, self)._prepare_invoice()
        res['payment_acquirer'] = self.payment_acquirer
        res['pricelist_id'] = self.pricelist_id
        res['rate'] = self.rate
        if self.amount_tax > 0:
           #raise UserError(self.amount_tax)
           res['x_sff_flag'] = False
        return res

    @api.constrains('company_id', 'pricelist_id')
    def _check_pricelist_id(self):
        for record in self:
            if record.pricelist_id.company_id != record.company_id:
                if not self.es_call_center:
                    raise ValidationError('No se permiten tarifas publicas, seleccione otra')

    @api.model
    def default_get(self, fields):
        res = super(Sale, self).default_get(fields)
        gerente = False
        if self.env.user.has_group('abnet_customize.gerente_tienda'):
            gerente = True
        callcenter = False
        if self.env.user.has_group('abnet_customize.call_center'):
            callcenter = True

        domain = [('name', '=', 'USD')]
        currency_id = self.env['res.currency'].search(domain, limit=1, order='id desc').id
        cia = self.company_id.env.company.id
        domain = [('company_id', '=', cia),
                  ('currency_id', '=', currency_id)]  # returns only the records matching this domain
        x_pricelist_id = self.env['product.pricelist'].search(domain, limit=1, order='id desc').id

        if x_pricelist_id:
            if not callcenter:
                res.update({'es_gerente_tienda': gerente,
                            'es_call_center': callcenter,
                            'pricelist_id': x_pricelist_id})
        else:
            res.update({'es_gerente_tienda': gerente,
                        'es_call_center': callcenter})
        return res
