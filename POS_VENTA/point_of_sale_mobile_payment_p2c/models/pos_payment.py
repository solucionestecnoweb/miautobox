from odoo import _, api, fields, models
from ..constants import *


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    line_is_turned_mobile_payment = fields.Boolean(string='Linea de Pago movil')
    mobile_payment_bank_from = fields.Selection(string='Banco Receptor', selection=BANKS_VE)
    ci_ve = fields.Integer(string='Cedula')
    phone = fields.Char(string='Telefono')