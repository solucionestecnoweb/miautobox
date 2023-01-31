# Part of abnet_customize. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class ProductTemplateAB(models.Model):
    _inherit = 'product.template'

    x_pricelist_usd = fields.Integer(
        store=False,
        string='Pricelist USD',
        readonly=True
    )
    x_pricelist_vef = fields.Integer(
        store=False,
        string='Pricelist Bs.',
        readonly=True
    )
    x_rate_vef = fields.Monetary(
        compute='_get_x_rate_vef',
        store=False,
        string='Tasa Bs.',
        readonly=True
    )
    x_base_price_vef = fields.Monetary(
        compute='_get_price_vef',
        store=False,
        string='Precio Base Bs.',
        readonly=True
    )
    x_base_price_usd = fields.Monetary(
        compute='_get_base_price_usd',
        store=False,
        string='Precio Base USD'
    )
    x_tax_factor = fields.Float(
        compute='_get_x_tax_factor',
        store=False,
        string='Factor IVA'
    )
    x_price_iva_vef = fields.Monetary(
        compute='_get_price_vef',
        store=False,
        string='Monto Incl./IVA Bs.'
    )
    x_price_iva_usd = fields.Monetary(
        compute='_get_price_iva_usd',
        store=False,
        string='Monto Incl./IVA USD'
    )
    es_call_center = fields.Boolean(
        compute='_get_call_center_flag',
        string='¿Es Call Center?',
        store=False
    )
    x_reserved_qty = fields.Integer(
        compute='_get_warehouse_stock',
        string='Cantidad Reservada',
        store=False
    )
    x_default_stock_location = fields.Integer(
        string='Ubicación Inventario',
        store=False
    )

    def _get_x_rate_vef(self):
        self.x_rate_vef = 0.0
        self.x_rate_vef = self.env['ir.config_parameter'].sudo().get_param('global_rate_vef')

    @api.depends('x_base_price_usd', 'x_rate_vef')
    def _get_price_vef(self):
        for template in self:
            template.x_base_price_vef = template.x_base_price_usd * template.x_rate_vef
            template.x_price_iva_vef = template.x_base_price_usd * template.x_tax_factor * template.x_rate_vef

    def _get_base_price_usd(self):
        # x_pricelist_usd está definida como valor por default de usuario por compañía
        for template in self:
            template.x_base_price_usd = 0
            prices = 1
            partner = self._context.get('partner', False)
            quantity = 1
            pricelist = self.env['product.pricelist'].browse(template.x_pricelist_usd)
            if pricelist:
                quantities = [quantity] * len(self)
                partners = [partner] * len(self)
                prices = pricelist.get_products_price(self, quantities, partners)
                template.x_base_price_usd = prices.get(template.id, 0.0)

    def _get_warehouse_stock(self):
        # x_default_stock_location está definido como valor por default de usuario por compañía
        for template in self:
            template.x_reserved_qty = 0
            stock_id = template.x_default_stock_location
            prod = template.id
            domain = [('location_id', '=', stock_id), ('product_id', '=', prod)]
            stock = self.env['stock.quant'].search(domain, limit=1).id
            if stock:
                template.x_reserved_qty =  self.env['stock.quant'].browse(stock).reserved_quantity

    def _get_x_tax_factor(self):
        for template in self:
            template.x_tax_factor = self.env['ir.config_parameter'].sudo().get_param('global_x_tax_factor')

    def _get_price_iva_usd(self):
        for template in self:
            template.x_price_iva_usd = template.x_base_price_usd * template.x_tax_factor

    def _get_call_center_flag(self):
        for template in self:
            callcenter = False
            if self.env.user.has_group('abnet_customize.call_center'):
                callcenter = True
                template.es_call_center = callcenter

    def fields_view_get(self, view_id='abnet_customize.product_template_product_tree_ab', view_type='tree', toolbar=False, submenu=False):
        # Tasa BsS
        global_rate_vef = 0.0
        domain = [('name', 'not in', ['USD', 'EUR']), ('active', '=', True)]
        curr_id = self.env['res.currency'].search(domain, limit=1).id
        if curr_id:
            domain = [('currency_id', '=', curr_id)]
            rate_id = self.env['res.currency.rate'].search(domain, limit=1, order='name desc').id
            if rate_id:
                rate = self.env['res.currency.rate'].browse(rate_id)
                global_rate_vef = rate.rate
        self.env['ir.config_parameter'].sudo().set_param('global_rate_vef', global_rate_vef)
        # Factor de Impuestos
        global_x_tax_factor = 0
        cia = self.company_id.env.company.id
        domain = [('company_id', '=', cia), ('amount', '>', 0), ('type_tax_use', '=', 'sale'), ('active', '=', True)]
        tax_id = self.env['account.tax'].search(domain, limit=1).id
        if tax_id:
            tax = self.env['account.tax'].browse(tax_id)
            global_x_tax_factor = ((tax.amount / 100) + 1)
        self.env['ir.config_parameter'].sudo().set_param('global_x_tax_factor', global_x_tax_factor)

        return super(ProductTemplateAB, self).fields_view_get(view_id, view_type, toolbar, submenu)