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

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    filler = fields.Float(string='Filler', related='product_id.filler')
    fillert = fields.Float(string='FillerT')
    need_vehicle = fields.Char()
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehículo')


    @api.onchange('product_id', 'quantity')
    def onchange_filler(self):
        for line in self:
            line.fillert = line.filler * line.quantity

    @api.constrains('product_id', 'quantity')
    def constrains_filler(self):
        for line in self:
            line.fillert = line.filler * line.quantity

class AccountMove(models.Model):
    _inherit = 'account.move'
    pago_camion = fields.Boolean('¿Pago contra camión?')
    situacion = fields.Selection(string='Situación', selection=[('Apartado', 'Apartado'), ('Analisis', 'Análisis'),], track_visibility='onchange')
    fillert = fields.Float(string='Filler Total')

    @api.onchange('amount_total','state')
    def onchange_filler(self):
        self.calculate_filler()

    @api.constrains('amount_total','state')
    def constrains_filler(self):
        self.calculate_filler()

    def calculate_filler(self):
        filler = 0
        for line in self.invoice_line_ids:
            filler += line.fillert
        self.fillert = filler

class FlotaAsignaciones(models.Model):
    _name = "fleet.vehicle.log.assignment.control"
    _order = 'id desc'

    name = fields.Char(string='Referencia', default='Nuevo')
    vehicle_id = fields.Many2one('fleet.vehicle2', string='Vehículo')
    driver_id = fields.Many2one('res.partner', string='Conductor')
    date_ini = fields.Date(string='Desde')
    date_end = fields.Date(string='Hasta')
    duration = fields.Float(string='Duración')
    delivery_date = fields.Date('Fecha entrega')
    stock_picking_ids = fields.One2many('stock.picking', 'fleet_assign', string=' Ordenes de Entrega')
    vehicle_odometer_ids = fields.Many2many('fleet.vehicle.odometer', string=' Odómetro del Vehículo',
                                            compute='_compute_odometer')
    company_id = fields.Many2one(comodel_name='res.company', string='Compañía', default=lambda x: x.env.company.id)
    company_ids = fields.Many2many(comodel_name='res.company', string='Compañías', default=lambda x: x.env.companies.ids)
    kilom_est = fields.Float(string='Kilometraje estimado')
    kilom_ini = fields.Float(string='Kilometraje inicial')
    kilom_fin = fields.Float(string='Kilometraje final')
    kilom_tot = fields.Float(string='Kilometraje total')
    status = fields.Selection(string='Estado', selection=[
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'), ('done', 'Realizado'), ('cancel', 'Cancelado')], default="draft")
    vehicle_filler = fields.Float(string='Filler del Vehículo', related='vehicle_id.vehicle_filler')
    loaded_filler = fields.Float(string='Filler Cargado')

class FleetVehicle(models.Model):
    _name = 'fleet.vehicle2'
    _description = 'Vehicle'
    _order = 'license_plate asc, acquisition_date asc'

    def _get_default_state(self):
        state = self.env.ref('fleet.fleet_vehicle_state_registered', raise_if_not_found=False)
        return state if state and state.id else False

    name = fields.Char(compute="_compute_vehicle_name", store=True)
    description = fields.Text("Vehicle Description")
    active = fields.Boolean('Active', default=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    license_plate = fields.Char(tracking=True,
        help='License plate number of the vehicle (i = plate number for a car)')
    vin_sn = fields.Char('Chassis Number', help='Unique number written on the vehicle motor (VIN/SN number)', copy=False)
    driver_id = fields.Many2one('res.partner', 'Driver', tracking=True, help='Driver of the vehicle', copy=False)
    future_driver_id = fields.Many2one('res.partner', 'Future Driver', tracking=True, help='Next Driver of the vehicle', copy=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    model_id = fields.Many2one('fleet.vehicle.model', 'Model',
        tracking=True, required=True, help='Model of the vehicle')
    manager_id = fields.Many2one('res.users', compute='_compute_manager_id', domain=lambda self: [('groups_id', 'in', self.env.ref('fleet.fleet_group_manager').id)], store=True, readonly=False)






