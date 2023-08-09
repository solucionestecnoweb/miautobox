# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    @api.onchange("street")
    def _set_street(self):
        if self.street:
            if len(self.street) > 150:
                raise ValidationError('Campo Calle/Zona excede los 150 caracteres. Utilice la segunda línea (Calle 2) '
                                      'y los campos de Ciudad, Estado, País y C.P. para completar los detalles de la dirección')

    @api.onchange("street2")
    def _set_street2(self):
        if self.street2:
            if len(self.street2) > 150:
                raise ValidationError('Campo Calle2/Zona excede los 150 caracteres. Utilice la primera línea (Calle 1) '
                                      'y los campos de Ciudad, Estado, País y C.P. para completar los detalles de la dirección')