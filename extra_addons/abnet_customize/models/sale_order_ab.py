# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    team_x_company_id = fields.Many2many(
        related='team_id.x_company_id', 
        string="Team Companies", 
        readonly=True)

    team_id = fields.Many2one(
        'crm.team', 'Sales Team', 
        check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('company_id', 'in', team_x_company_id)]")
        #domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id), ('company_id', 'in', company_ids)]")

    #def action_confirm(self):
    #    return super(SaleOrder, self.with_context({k:v for k,v in self._context.items() if k != 'default_tag_ids'})).action_confirm()
