# -*- coding: utf-8 -*-
#######################################################

#   CorpoEureka - Innovation First!
#
#   Copyright (C) 2021-TODAY CorpoEureka (<https://www.corpoeureka.com>)
#   Author: CorpoEureka (<https://www.corpoeureka.com>)
#
#   This software and associated files (the "Software") may only be used (executed,
#   modified, executed after modifications) if you have pdurchased a vali license
#   from the authors, typically via Odoo Apps, or if you have received a written
#   agreement from the authors of the Software (see the COPYRIGHT file).
#
#   You may develop Odoo modules that use the Software as a library (typically
#   by depending on it, importing it and using its resources), but without copying
#   any source code or material from the Software. You may distribute those
#   modules under the license of your choice, provided that this license is
#   compatible with the terms of the Odoo Proprietary License (For example:
#   LGPL, MIT, or proprietary licenses similar to this one).
#
#   It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#   or modified copies of the Software.
#
#   The above copyright notice and this permission notice must be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

#   Responsable CorpoEureka: Jose Mazzei, Jose Ñeri
##########################################################################-
from odoo import api, models, modules,fields
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
class SaleOrder(models.Model):
    _inherit="sale.order"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id, view_type, toolbar, submenu)

        
        if "toolbar" in res and res['toolbar']['action']:
            
            actions = res['toolbar']['action']
            
            for action in actions:
                
                if action.get('id', False) ==539 and not self.env.user.has_group('eu_groups_perssions.marcar_presupuesto_enviado_venta_eu'): #marcar como presupuesto enviado
                    actions.remove(action)
        
        return res 

class AccountMove(models.Model):
    _inherit="account.move"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id, view_type, toolbar, submenu)

        
        if "toolbar" in res and res['toolbar']['action']:
            
            actions = res['toolbar']['action']
            
            for action in actions:
                
                if action.get('id', False) ==539 and not self.env.user.has_group('eu_groups_perssions.change_return_note_credit'): #marcar como presupuesto enviado
                    actions.remove(action)
        
        return res 
# class ProductProduct(models.Model):
#     _inherit="product.product"

#     @api.model
#     def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
#         res = super().fields_view_get(view_id, view_type, toolbar, submenu)

#         if "toolbar" in res and res['toolbar']['action']:
#             actions = res['toolbar']['action']

#             for action in actions:
              
#                 if action.get('name', False) =="Generate Pricelist":
#                     actions.remove(action)

#         return res 

# class StockMoveLine(models.Model):
#     _inherit="stock.move.line"
        