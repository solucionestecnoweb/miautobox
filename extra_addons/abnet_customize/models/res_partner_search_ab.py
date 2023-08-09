# -*- coding: utf-8 -*-
# Part of abnet_customize. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    #@api.model
    #def name_search(self, name='', args=None, operator='ilike', limit=100):
    #    if name:
    #        args = args if args else []
    #        args.extend(['|', '|', ['name', 'ilike', name], ['vat', 'ilike', name], ['mobile', 'ilike', name]])
    #        name = ''
    #    return super(Partner, self).name_search(name=name, args=args, operator=operator, limit=limit)
