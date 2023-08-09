# -*- coding: utf-8 -*-
# Part of abnet_customize. See LICENSE file for full copyright and licensing details.
import datetime, pytz
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_custom_domain_category(self):
        domain = [('name', '=', 'Operador de Servicios AB')]
        return [('category_id', '=', self.env['res.partner.category'].search(domain, limit=1).id)]

    x_operador_serv = fields.Many2one(
        'res.partner', 'Operador Servicios',
        check_company=False,
        domain=lambda self: self._get_custom_domain_category(),
        store=True
    )


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    # ==== Invoice line fields ====
    x_responsable = fields.Many2one('res.partner', string='Operador/ Comercial', readonly=True)
    team_id = fields.Many2one('crm.team', string='Sales Team')
    
    @api.model
    def _select(self):
        return '''
            SELECT
                line.id,
                line.move_id,
                line.product_id,
                line.account_id,
                line.analytic_account_id,
                line.journal_id,
                line.company_id,
                line.company_currency_id,
                line.partner_id AS commercial_partner_id,
                COALESCE(line.x_operador_serv, commercial.partner_id) AS x_responsable,
                move.state,
                move.move_type,
                move.partner_id,
                move.invoice_user_id,
                move.fiscal_position_id,
                move.payment_state,
                move.invoice_date,
                move.invoice_date_due,
                uom_template.id                                             AS product_uom_id,
                template.categ_id                                           AS product_categ_id,
                line.quantity / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
                                                                            AS quantity,
                -line.balance * currency_table.rate                         AS price_subtotal,
                -line.balance / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * currency_table.rate
                                                                            AS price_average,
                COALESCE(partner.country_id, commercial_partner.country_id) AS country_id,
                move.team_id as team_id
        '''

    @api.model
    def _from(self):
        return '''
            FROM account_move_line line
                LEFT JOIN res_partner partner ON partner.id = line.partner_id
                LEFT JOIN product_product product ON product.id = line.product_id
                LEFT JOIN account_account account ON account.id = line.account_id
                LEFT JOIN account_account_type user_type ON user_type.id = account.user_type_id
                LEFT JOIN product_template template ON template.id = product.product_tmpl_id
                LEFT JOIN uom_uom uom_line ON uom_line.id = line.product_uom_id
                LEFT JOIN uom_uom uom_template ON uom_template.id = template.uom_id
                INNER JOIN account_move move ON move.id = line.move_id
                LEFT JOIN res_partner commercial_partner ON commercial_partner.id = move.commercial_partner_id
                LEFT JOIN res_users commercial ON commercial.id = move.invoice_user_id
                JOIN {currency_table} ON currency_table.company_id = line.company_id
        '''.format(
            currency_table=self.env['res.currency']._get_query_currency_table({'multi_company': True, 'date': {'date_to': fields.Date.today()}}),
        )
    
    #def _select(self):
    #    return super(AccountInvoiceReport, self)._select() + ", move.team_id as team_id"
