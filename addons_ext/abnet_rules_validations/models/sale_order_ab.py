# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class Sale(models.Model):
    _inherit = 'sale.order'

    @api.constrains('partner_id')
    def _check_partner_id(self):
        for record in self:
            if record.partner_id:
                cliente = self.env['res.partner'].browse(record.partner_id.id)
                if cliente:
                    if not cliente.vat:
                        raise ValidationError('Cliente no tiene Cédula registrada; '
                                              'favor corregir ficha del cliente (Contacto)')
                    if not cliente.city:
                        raise ValidationError('Cliente no tiene indicada la Ciudad en la dirección; '
                                              'favor corregir ficha del cliente (Contacto)')
                    if not cliente.state_id:
                        raise ValidationError('Cliente no tiene indicado el estado en la dirección; '
                                              'favor corregir ficha del cliente (Contacto)')
                    if not cliente.country_id:
                        raise ValidationError('Cliente no tiene indicado el país en la dirección; '
                                              'favor corregir ficha del cliente (Contacto)')
                    if not cliente.street:
                        raise ValidationError('Cliente no tiene indicada la calle o zona en la dirección; '
                                              'favor corregir ficha del cliente (Contacto)')
                    if not cliente.mobile and not cliente.phone:
                        raise ValidationError('Cliente debe tener indicado número de teléfono fijo o móvil; '
                                              'favor corregir ficha del cliente (Contacto)')
                    if cliente.street:
                        if len(cliente.street) > 150:
                            raise ValidationError('Longitud del campo Calle/Zona del cliente excede los 150 caracteres; '
                                                  'favor corregir ficha del cliente (Contacto)')
                    if cliente.street2:
                        if len(cliente.street2) > 150:
                            raise ValidationError('Longitud del campo Calle2/Zona del cliente excede los 150 caracteres; '
                                                  'favor corregir ficha del cliente (Contacto)')
