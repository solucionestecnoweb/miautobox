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

#   Responsable CorpoEureka: Jose Mazzei
##########################################################################-
from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    vendor_invoice_number = fields.Char(string='Nro factura proveedor',
        copy=False,
        help='El número de factura generado por el proveedor' )
    nro_control = fields.Char(string='Nro de Control',
        copy=False,
        help='Nro de control de la factura de proveedor', required=False)
    transaction_type = fields.Selection(([('01-reg','Registro'),
                                          ('02-complemento', 'Complemento'),
                                          ('03-anulacion', 'Anulación'),
                                          ('04-ajuste', 'Ajuste')]), string='Transaction Type', readonly=False,
                                            states={'draft': [('readonly', False)]},
                                            help='This is transaction type', compute='_compute_transaction_type')
    ajust_date = fields.Date(string='Fecha de Ajuste',readonly=False,
                                            states={'draft': [('readonly', False)]})
    
    deductible  =   fields.Boolean('¿No Deducible?')

    @api.depends('move_type', 'state')
    def _compute_transaction_type(self):
        for move in self:
            if move.move_type in ('out_refund','in_refund') and move.state != 'cancel':
                move.transaction_type = '02-complemento'
            elif move.state == 'cancel':
                move.transaction_type = '03-anulacion'
            elif move.debit_origin_id.id != False:
                move.transaction_type = '02-complemento'
            else:
                move.transaction_type = '01-reg'
