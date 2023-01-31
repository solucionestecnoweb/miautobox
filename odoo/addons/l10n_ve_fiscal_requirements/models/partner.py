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
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    rif = fields.Char(string="RIF", required=False)
    vd_rif = fields.Integer(string="Dígito Validador RIF",compute="_compute_vd_rif")
    cedula = fields.Char(string="Cédula o RIF",size=10)
    street = fields.Char(required=True)
    city = fields.Char(required=False)
    state_id = fields.Many2one(required=False)

    country_id = fields.Many2one(required=True)
    residence_type = fields.Selection([('SR','Sin RIF'),
                                      ('R', 'Residenciado'),
                                      ('NR', 'No residenciado'),
                                      ('D', 'Domiciliado'),
                                      ('ND', 'No domiciliado')], help='This is the Supplier Type')

    
    @api.onchange('rif','cedula')
    def _onchange_rif_to_vat(self):
        if self.cedula:
            self.vat = self.cedula.upper()
            self.cedula = self.cedula.upper()
        if self.rif:
            self.vat = self.rif.upper()
            self.rif = self.rif.upper()


    @api.constrains('cedula')
    def _check_cedula(self):
        if self.cedula:
            if self.is_company:
                formate = (r"[JGVEP]{1}[-]{1}[0-9]{8}")
                form_ci = re.compile(formate)
                records = self.env['res.partner']
                cedula_exist = records.search_count([('cedula', '=', self.cedula),('id', '!=', self.id)])
                for partner in self:
                    if not form_ci.match(partner.cedula):
                        raise ValidationError(("El formato es incorrecto. Por favor introduzca de la forma J, G o V  - 12345678"))
                    elif cedula_exist > 0:
                        raise ValidationError(("Ya existe un registro con este número"))
                    else:
                        return True
            else:
                formate = (r"[JGVEP]{1}[-]{1}[0-9]{8}")
                form_ci = re.compile(formate)
                records = self.env['res.partner']
                cedula_exist = records.search_count([('cedula', '=', self.cedula),('id', '!=', self.id)])
                for partner in self:
                    if not form_ci.match(partner.cedula):
                        raise ValidationError(("El formato es incorrecto. Por favor introduzca de la forma V, E o P -12345678"))
                    elif cedula_exist > 0:
                        raise ValidationError(("Ya existe un registro con este número"))
                    else:
                        return True


    @api.depends('cedula')
    def _compute_vd_rif(self):
        for rec in self:
            rec.vd_rif= 0
            rec.rif = rec.cedula
            if rec.cedula and rec.cedula[0] in ('VEJG'):
                cedula = rec.cedula.replace('-','')
                base = {'V': 4, 'E': 8, 'J': 12, 'G': 20}
                oper = [0, 3, 2, 7, 6, 5, 4, 3, 2]
                val = 0
                for i in range(len(cedula[:9])):
                    val += base.get(cedula[0], 0) if i == 0 else oper[i] * int(cedula[i])
                digit = 11 - (val % 11)
                digit = digit if digit < 10 else 0
                rec.vd_rif = digit
                rec.rif = str(cedula[0]) + '-' +  str(cedula[1:]) + str(digit)
