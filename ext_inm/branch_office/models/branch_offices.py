# -*- coding: utf-8 -*-

from odoo import fields, models, api


class BranchOffice(models.Model):
    _name = 'branch.office'
    _description = 'Sucursal'

    name = fields.Char(string='Nombre')
    code = fields.Char(string='Codigo')
    description = fields.Text(string='Descripccion')
    active = fields.Boolean(string='Activo')

    def name_get(self):
        """ The _rec_name class attribute is replaced to concatenate several fields of the object
            :return list: the concatenation of the new _rec_name
        """
        res = [(r.id, '[{}] {}'.format(r.code or 'S/N', r.name)) for r in self]
        return res

    @api.model
    def create(self, vals):
        """
        This method is create for sequence wise name.
        :param vals: values
        :return:super
        """
        res = super(BranchOffice, self).create(vals)
        res.code = self.env['ir.sequence'].next_by_code('code.branch.office')
        return res
