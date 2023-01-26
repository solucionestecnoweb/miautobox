# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class PosConfig(models.Model):
    _inherit = 'pos.config'

    hacer_asiento_contable=fields.Boolean(default=False,help="Valor verdadero hace que al cerrar el pos, este genere el asiento contable")