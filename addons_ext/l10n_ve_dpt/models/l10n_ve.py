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

from odoo import api, fields, models, _

class CountryState(models.Model):
    """ Add Municipalities reference in State """
    _name = 'res.country.state'
    _inherit = 'res.country.state'
    _description="Country states"

    municipality_id = fields.One2many('res.country.state.municipality', 'state_id', 'Municipalities in this state')
    city_id = fields.One2many('res.country.state.city', 'state_id', 'Ciudades en este Estado')


class StateMunicipality(models.Model):
    """States Municipalities"""
    _name = 'res.country.state.municipality'
    _description="State municipalities"

    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one('res.country.state', 'State', required=True, help='Name of the State to which the municipality belongs')
    city_id = fields.Many2one('res.country.state.city', 'Ciudad')
    name = fields.Char('Municipality', required=True, help='Municipality name')
    code = fields.Char('Code', size=3, required=True, help='Municipality code in max. three chars.')
    parish_id = fields.One2many('res.country.state.municipality.parish', 'municipality_id', 'Parishes in this municipality')


class MunicipalityParish(models.Model):
    """States Parishes"""
    _name = 'res.country.state.municipality.parish'
    _description="Municipality parishes"

    municipality_id = fields.Many2one('res.country.state.municipality', 'Municipality', help='Name of the Municipality to which the parish belongs')
    name = fields.Char('Parish', required=True, help='Parish name')
    code = fields.Char('Name',size=3, required=True, help='Parish Code in max. three chars.')
