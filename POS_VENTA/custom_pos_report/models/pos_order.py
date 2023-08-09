# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from email.policy import default
from odoo import models, api, fields


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
        data = super(ReportSaleDetails, self).get_sale_details(date_start, date_stop, config_ids, session_ids)
        conf = []
        config = self.env['pos.config'].search([('id', 'in', config_ids)])
        for c in config:
            conf.append({'id': c.id, 'name': c.name})
        report_update = {'sessions': conf}
        data.update(report_update)
        currency_rate = self.env['res.currency.rate'].search([('currency_id', '=',2), ('hora','<=', date_stop)], limit=1)
        data['rate'] = currency_rate.rate_real if currency_rate.rate_real > 0 else 1
        data['default_pos_report'] = self._context.get('default_pos_report') if self._context.get('default_pos_report') else '0'
        wizard_id = self.env['pos.details.wizard'].search([('id', '=', self._context['active_id'])])
        data['view_product'] = wizard_id.view_product
        return data

    @api.model
    def _get_report_values(self, docids, data=None):
        data = super(ReportSaleDetails, self)._get_report_values(docids, data)
        conf = []
        data = dict(data or {})
        if 'config_ids' in data:
            config = self.env['pos.config'].search([('id', 'in', data['config_ids'])])
            for c in config:
                conf.append({'id': c.id, 'name': c.name})
            report_update = {'sessions': conf}
            data.update(report_update)
        return data



class PosDetails(models.TransientModel):
    _inherit = 'pos.details.wizard'


    view_product = fields.Boolean('Mostra productos', default=False)
    pos_config_ids = fields.Many2many('pos.config', default=False)