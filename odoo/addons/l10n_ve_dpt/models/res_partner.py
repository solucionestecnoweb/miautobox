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

from odoo import models, fields, api, _

class ResPartnerInherit(models.Model):

	_inherit = 'res.partner'

	country_id=fields.Many2one(default=lambda self: self.env['res.country'].search([('code','=','VE')]))
	city_id = fields.Many2one('res.country.state.city', 'Ciudad')
	municipality_id = fields.Many2one('res.country.state.municipality', 'Municipality')
	parish_id = fields.Many2one('res.country.state.municipality.parish', 'Parish')

	def write(self, vals):

		if 'name' in vals:
			vals['name'] = str(vals['name']).upper()
		res= super(ResPartnerInherit,self).write(vals)
		return res


	@api.onchange('country_id')
	def _onchage_country_id(self):
		if self.state_id:
			self.state_id = self.city_id = self.municipality_id = self.parish_id = self.zip = False
			
	@api.onchange('state_id')
	def _onchage_state(self):
		if self.state_id:
			self.city_id = self.municipality_id = self.parish_id = self.zip = False

	@api.onchange('city_id')
	def _onchage_city(self):
		if self.city_id:
			self.city = self.city_id.name
			self.municipality_id = self.parish_id = self.zip = False

	@api.onchange('municipality_id')
	def _onchage_municipality(self):
		if self.municipality_id:
			self.parish_id = self.zip = False

	@api.model
	def _address_fields(self):
		address_fields = set(super(ResPartnerInherit, self)._address_fields())
		address_fields.add('municipality_id')
		address_fields.add('parish_id')
		return list(address_fields)

	# @api.multi
	def _display_address(self, without_company=False):

		'''
		The purpose of this function is to build and return an address formatted accordingly to the
		standards of the country where it belongs.

		:param address: browse record of the res.partner to format
		:returns: the address formatted in a display that fit its country habits (or the default ones
			if not country is specified)
		:rtype: string
		'''
		# get the information that will be injected into the display format
		# get the address format
		address_format = self.country_id.address_format or \
			  "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
		args = {
			'state_code': self.state_id.code or '',
			'state_name': self.state_id.name or '',
			'municipality_code': self.municipality_id.code or '',
			'municipality_name': self.municipality_id.name or '',
			'parish_code': self.parish_id.code or '',
			'parish_name': self.parish_id.name or '',
			'country_code': self.country_id.code or '',
			'country_name': self.country_id.name or '',
			'company_name': self.commercial_company_name or '',
		}
		for field in self._address_fields():
			args[field] = getattr(self, field) or ''
		if without_company:
			args['company_name'] = ''
		elif self.commercial_company_name:
			address_format = '%(company_name)s\n' + address_format
		return address_format % args
