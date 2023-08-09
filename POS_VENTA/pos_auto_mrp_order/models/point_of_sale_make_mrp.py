# -*- coding: utf-8 -*-
##############################################################################
#
#    you can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def create_mrp_from_pos(self, products):
        product_ids = []
        if products:
            for product in products:
                flag = 1
                if product_ids:
                    for product_id in product_ids:
                        if product_id['id'] == product['id']:
                            product_id['qty'] += product['qty']
                            flag = 0
                if flag:
                    product_ids.append(product)
            for prod in product_ids:
                if prod['qty'] > 0:
                    product = self.env['product.product'].search([('id', '=', prod['id'])])
                    bom_count = self.env['mrp.bom'].search([('product_tmpl_id', '=', prod['product_tmpl_id'])])
                    if bom_count:
                        bom_temp = self.env['mrp.bom'].search([('product_tmpl_id', '=', prod['product_tmpl_id']),
                                                               ('product_id', '=', False)])
                        bom_prod = self.env['mrp.bom'].search([('product_id', '=', prod['id'])])
                        if bom_prod:
                            bom = bom_prod[0]
                        elif bom_temp:
                            bom = bom_temp[0]
                        else:
                            bom = []
                        if bom:
                            vals = {
                                'origin': 'POS-' + prod['pos_reference'],
                                'state': 'confirmed',
                                'product_id': prod['id'],
                                'product_tmpl_id': prod['product_tmpl_id'],
                                'product_uom_id': prod['uom_id'],
                                'product_qty': prod['qty'],
                                'qty_produced': prod['qty'],
                                'bom_id': bom.id,
                            }
                            mrp_order = self.sudo().create(vals)
                            list_value = []
                            for bom_line in mrp_order.bom_id.bom_line_ids:
                                list_value.append((0, 0, {
                                    'raw_material_production_id': mrp_order.id,
                                    'name': mrp_order.name,
                                    'product_id': bom_line.product_id.id,
                                    'product_uom': bom_line.product_uom_id.id,
                                    'product_uom_qty': bom_line.product_qty * mrp_order.product_qty,
                                    'picking_type_id': mrp_order.picking_type_id.id,
                                    'location_id': mrp_order.location_src_id.id,
                                    'location_dest_id': bom_line.product_id.property_stock_production.id,
                                    'company_id': mrp_order.company_id.id,
                                }))
                            vals0 = {
                                'product_uom': prod['uom_id'],
                                'name': str(product['default_code']) + ": Production>Stock",
                                'product_id': prod['id'],
                                'product_uom_qty': prod['qty'],
                                'reference': mrp_order.name,
                                'company_id': mrp_order.company_id.id,
                                'location_dest_id': mrp_order.location_src_id.id,
                                'location_id': bom_line.product_id.property_stock_production.id,
                                'picking_type_id': mrp_order.picking_type_id.id,
                                'origin': mrp_order.name,
                     
                            }
                            move_finished_ids = self.env['stock.move'].sudo().create(vals0)
                            mrp_order.update({'move_raw_ids': list_value, 'move_finished_ids': move_finished_ids})
                            if prod['to_make_mrp']:
                                mrp_order.action_confirm()
                                context = mrp_order.button_mark_done()
                                vals2 = {
                                    'mo_ids': [(4, mo.id) for mo in mrp_order],
                                }
                                mrp_immediate_production = self.env['mrp.immediate.production'].sudo().with_context(context['context']).create(vals2)
                                mrp_immediate_production.process()
        return True


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    to_make_mrp = fields.Boolean(string='Auto Complete MRP Order',
                                 help="Check if the product should be make mrp order")
    to_make_mrp_draft = fields.Boolean(string='To Create draft MRP Order',
                                 help="Check if the product should be make mrp order")

    @api.onchange('to_make_mrp')
    def onchange_to_make_mrp(self):
        if self.to_make_mrp:
            if not self.bom_count:
                raise Warning('Please set Bill of Material for this product.')

    @api.onchange('to_make_mrp_draft')
    def onchange_to_make_mrp(self):
        if self.to_make_mrp_draft:
            if not self.bom_count:
                raise Warning('Please set Bill of Material for this product.')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('to_make_mrp')
    def onchange_to_make_mrp(self):
        if self.to_make_mrp:
            if not self.bom_count:
                raise Warning('Please set Bill of Material for this product.')

    @api.onchange('to_make_mrp_draft')
    def onchange_to_make_mrp(self):
        if self.to_make_mrp_draft:
            if not self.bom_count:
                raise Warning('Please set Bill of Material for this product.')
