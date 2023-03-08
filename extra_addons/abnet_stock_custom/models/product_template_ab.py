# Part of abnet_customize. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class ProductTemplateAB(models.Model):
    _inherit = 'product.template'

    def action_view_product_kardex_tree(self):
        return {
            'name': 'Kardex',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'product.kardex',
            'view_id': self.env.ref('abnet_stock_custom.view_product_kardex_tree').id,
            'context': {'product_id': self.id},
            'domain': [('product_id', '=', self.id), ('company_id', '=', self.env.company.id)]
        }
