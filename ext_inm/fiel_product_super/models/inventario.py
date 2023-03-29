# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from itertools import product
import json
from datetime import datetime, timedelta
import base64
from io import StringIO
from odoo import api, fields, models
from datetime import date
from odoo.tools.float_utils import float_round
from odoo.exceptions import Warning

import time

class ProductProduct(models.Model):
	_inherit = "product.product"

	modelo = fields.Char(string='Modelo')
	brand_id = fields.Many2one('product.brand', string='Marca')
	filler = fields.Float(string='Nro. Filler', digits=(12, 4))
	group_id = fields.Many2one('product.group', string='Grupo')
	tarps = fields.Char(string='Lonas')
	load_speed = fields.Char(string='Carga/Velocidad')
	rin = fields.Float(string='Rin')
	tier = fields.Selection(string='TIER', selection=[('1', 'TIER-1'), ('2', 'TIER-2'), ('3', 'TIER-3'), ('4', 'TIER-4'), ('5', 'TIER-5')])
	qty_hq = fields.Char(string='Qty Of 40HQ')
	deote = fields.Date(string='Fecha de Fabricación')

	codigo_icg = fields.Char(string='Código ICG')
	iva = fields.Char(string='I.V.A.')
	type_cauchos = fields.Char(string='Tipo de Caucho')
	service_in = fields.Char(string='Service Index')
	medidas = fields.Char(string='Medidas')
	construction_type = fields.Selection(string='Tipo de Construcción', selection=[('c', 'C'), ('r', 'R'),])
	clase = fields.Char(string='Clase', size=6)

	
class ProductTemplate(models.Model):
	_inherit = "product.template"

	modelo = fields.Char(string='Modelo')
	brand_id = fields.Many2one('product.brand', string='Marca')
	filler = fields.Float(string='Nro. Filler', digits=(12, 4))
	group_id = fields.Many2one('product.group', string='Grupo')
	tarps = fields.Char(string='Lonas')
	load_speed = fields.Char(string='Carga/Velocidad')
	rin = fields.Float(string='Rin')
	tier = fields.Selection(string='TIER', selection=[('1', 'TIER-1'), ('2', 'TIER-2'), ('3', 'TIER-3'), ('4', 'TIER-4'), ('5', 'TIER-5')])
	qty_hq = fields.Char(string='Qty Of 40HQ')
	deote = fields.Date(string='Fecha de Fabricación')

	codigo_icg = fields.Char(string='Código ICG')
	iva = fields.Char(string='I.V.A.')
	type_cauchos = fields.Char(string='Tipo de Caucho')
	service_in = fields.Char(string='Service Index')
	medidas = fields.Char(string='Medidas')
	construction_type = fields.Selection(string='Tipo de Construcción', selection=[('c', 'C'), ('r', 'R'),])
	clase = fields.Char(string='Clase', size=6)
	

	# @api.onchange('modelo','iva','type_cauchos','tarps','load_speed','service_in','filler','brand_id','group_id','qty_hq','deote')
	# def values_onchange(self):
	# 	self.update_values()

	# @api.constrains('modelo','iva','type_cauchos','tarps','load_speed','service_in','filler','brand_id','group_id','qty_hq','deote')
	# def values_constrains(self):
	# 	self.update_values()
	
	def _create_variant_ids(self):
		res = super(ProductTemplate, self)._create_variant_ids()

		for item in self.product_variant_ids:
			product = item
			product.modelo = self.modelo
			product.iva = self.iva
			product.type_cauchos = self.type_cauchos
			product.tarps = self.tarps
			product.load_speed = self.load_speed
			product.service_in = self.service_in
			product.filler = self.filler
			product.brand_id = self.brand_id.id
			product.group_id = self.group_id.id
			product.qty_hq = self.qty_hq
			product.deote = self.deote
			product.rin = self.rin
			product.medidas = self.medidas
			product.construction_type = self.construction_type
			product.tier = self.tier
			product.clase = self.clase

		return res

	@api.constrains('modelo','iva','type_cauchos','tarps','load_speed','service_in','filler','brand_id','group_id','qty_hq','deote', 'rin', 'medidas', 'construction_type', 'stock_inicial', 'no_despachado', 'tier', 'clase')
	def update_products(self):

		for item in self.product_variant_ids:
			product = item
			product.modelo = self.modelo
			product.iva = self.iva
			product.type_cauchos = self.type_cauchos
			product.tarps = self.tarps
			product.load_speed = self.load_speed
			product.service_in = self.service_in
			product.filler = self.filler
			product.brand_id = self.brand_id.id
			product.group_id = self.group_id.id
			product.qty_hq = self.qty_hq
			product.deote = self.deote
			product.rin = self.rin
			product.medidas = self.medidas
			product.construction_type = self.construction_type
			product.tier = self.tier
			product.clase = self.clase

class MarcasProductos(models.Model):
	_name = 'product.brand'

	name = fields.Char(string='Nombre')

class GruposProductos(models.Model):
	_name = 'product.group'

	name = fields.Char(string='Nombre')