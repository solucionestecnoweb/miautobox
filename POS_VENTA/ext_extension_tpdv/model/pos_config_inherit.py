# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class PosConfig(models.Model):
    _inherit = 'pos.config'

    reg_maquina=fields.Char(string="Registro de Máquina Fiscal")
    secuencia_nr_reporte_z = fields.Integer(default=2)
    nb_identificador_caja=fields.Char(string="Nombre de identificador caja")
    ordenes_impr=fields.Boolean(default=False)

    wh_porcentage = fields.Float(string="Percentage IGTF", help="El porcentaje a aplicar para retener ")
    account_wh_itf_id = fields.Many2one('account.account', string="Cuenta cuenta IGTF", help="Esta cuenta se usará en lugar de la predeterminada"
                                                       "uno como la cuenta por cobrar para el cliente")
    journal_transi = fields.Many2one('account.journal',help="Esta cuenta se coloca de forma temporal para que haga el asiento"
                                                        "y luego se pasa al diario del pago")