# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import os
import platform


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _payment_fields(self, order, ui_paymentline):
        res = super(PosOrder, self)._payment_fields(order, ui_paymentline)
        res.update({
            'line_is_turned_mobile_payment': ui_paymentline.get('line_is_turned_mobile_payment'),
            'mobile_payment_bank_from': ui_paymentline.get('mobile_payment_bank_from'),
            'phone': ui_paymentline.get('phone'),
            'ci_ve': ui_paymentline.get('ci_ve')
        })
        return res
  

    def is_wsl(self):
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.readline().lower()
        except Exception:
            return False

    def adjust_path(self, route):
        system = platform.system()

        if system == "Windows" or (system == "Linux" and not self.is_wsl()):
            return route
        elif self.is_wsl():
            if ':' in route: 
                drive = route[0].lower()  # Get the drive letter, e.g., 'c'
                path = route[2:]  # Remove drive letter and colon
                return '/mnt/' + drive + path.replace('\\', '/')
            else:
            # If no drive letter format, just replace backslashes
                return '/mnt/c/' + route.replace('\\', '/')
            
        else:
            raise ValueError("Unsupported OS")
        
    @api.model
    def read_txt_mobile_payment(self, route):
        try:
            adjusted_route = self.adjust_path(route)
            with open(adjusted_route, 'r', encoding='utf8') as txt_file:
                data = txt_file.read()
                return data
            
        except Exception as e:
            print("Error reading file:", str(e))
            return str(e)


