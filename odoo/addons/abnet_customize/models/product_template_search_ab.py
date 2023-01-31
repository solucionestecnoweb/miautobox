# -*- coding: utf-8 -*-
# Part of abnet_customize. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api

class ProductTemplateSearch(models.Model):
    _inherit = 'product.template'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if name:
            xgp = False
            if 'x_CodGP' in self.env['product.template']._fields:
                xgp = True
            xicg = False
            if 'x_CodICG' in self.env['product.template']._fields:
                xicg = True
            if xgp and xicg:
                args = args if args else []
                args.extend(
                    ['|', '|', ['name', 'ilike', name], ['x_CodGP', 'ilike', name], ['x_CodICG', 'ilike', name]])
                name = ''
            else:
                if xgp:
                    args = args if args else []
                    args.extend(['|', ['name', 'ilike', name], ['x_CodGP', 'ilike', name]])
                    name=''
                else:
                    if xicg:
                        args = args if args else []
                        args.extend(['|', ['name', 'ilike', name], ['x_CodICG', 'ilike', name]])
                        name = ''
        return super(ProductTemplateSearch, self).name_search(name=name, args=args, operator=operator, limit=limit)
