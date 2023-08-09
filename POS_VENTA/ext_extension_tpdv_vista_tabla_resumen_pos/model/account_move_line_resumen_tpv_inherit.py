# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning




class ResumenAlicuotaTpv(models.Model):
    _inherit = 'pos.order.line.resumen'

    nb_caja_aux = fields.Char(compute='_compute_nb_caja',store=True)
    nb_caja = fields.Char()

    def _compute_nb_caja(self):
        for selff in self:
            selff.nb_caja_aux=selff.session_id.config_id.name
            selff.nb_caja=selff.session_id.config_id.name