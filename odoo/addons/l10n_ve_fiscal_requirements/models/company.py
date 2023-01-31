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

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    #Columns
    rif = fields.Char(string='RIF', required=True)
    currency_id_ref = fields.Many2one('res.currency',string="Monedas de las Retenciones",default=lambda self: self.env['res.currency'].search(['|',('name', '=', 'VES'),('name', '=', 'VEF')], limit=1))

    @api.constrains('rif')
    def _check_rif(self):
        formate = (r"[JG]{1}[-]{1}[0-9]{9}")
        form_rif = re.compile(formate)
        records = self.env['res.company']
        rif_exist = records.search_count([('rif', '=', self.rif),('id', '!=', self.id)])
        for company in self:
            if not form_rif.match(company.rif):
                raise ValidationError(("El formato del RIF es incorrecto por favor introduzca un RIF de la forma J-123456789 (utilice solo las letras J y G)"))
            #elif rif_exist > 0:
            #    raise ValidationError(("Ya existe un registro con este RIF"))
            else:
                return True
