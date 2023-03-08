# -*- coding: utf-8 -*-
# Part of abnet_customize. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api

class crm_team(models.Model):
    _inherit = "crm.team"

    x_company_id = fields.Many2many('res.company', string="Compañías Atendidas")