import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError


class POSQuotation(models.Model):
    _name = "pos.quotation"
    _description = "POS Quotation"
    _rec_name = "ref"

    name = fields.Char(required=True, readonly=True, copy=False, default='POS Quotation')
    pos_session_id = fields.Many2one("pos.session", readonly=True)
    company_id = fields.Many2one('res.company', related="config_id.company_id", string='Company', required=True,
                                 readonly=True)
    config_id = fields.Many2one("pos.config", string="POS Config", related="pos_session_id.config_id")
    account_analytic_id = fields.Many2one(related='config_id.account_analytic_id', string='Cuenta analitica')
    quotation_date = fields.Datetime(default=datetime.datetime.now())
    ref = fields.Char("Reference", required=True)
    user_id = fields.Many2one(
        comodel_name='res.users', string='Seller',
        default=lambda self: self.env.uid,
    )
    amount_tax = fields.Float(string='Taxes', digits=0, readonly=True, required=True)
    amount_total = fields.Float(string='Total', digits=0, readonly=True, required=True)
    employee_id = fields.Many2one('hr.employee', string='Empleado')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', change_default=True, index=True)

    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position', string='Fiscal Position',
        readonly=True,
    )
    notes = fields.Text()
    lines = fields.One2many('pos.quotation.line', 'quotation_id', string='Order Lines', readonly=True, copy=True)
    currency_id = fields.Many2one('res.currency', related='config_id.currency_id', string="Currency")

    _sql_constraints = [
        ('name_ref', 'unique(ref)', 'Quotation Ref must be unique !'),
    ]
    state = fields.Selection([('draft', 'Borrador'), ('loaded', 'Cargada')], default='draft')

    @api.model
    def get_quotation_number(self):
        sequence = self.env.ref('pos_order_quotation.sequence_quote_sequence')
        return 'QUOTE ID ' + str(sequence.number_next_actual)

    @api.model
    def create_quotation(self, vals):
        location = self.env['stock.location'].browse(self.config_id.picking_type_id.default_location_src_id.id)
        quant = self.env['stock.quant']
        sequence = self.env.ref('pos_order_quotation.sequence_quote_sequence')
        quote_id = self.create(vals)
        quotation = self.search_read([('id', '=', quote_id.id)])
        return [quotation, sequence._next()]

    def get_quotation_details(self):
        location = self.env['stock.location'].browse(self.config_id.picking_type_id.default_location_src_id.id)
        quant = self.env['stock.quant']
        lines = []
        vals = {
            'partner_id': self.partner_id.id,
            'quotation_id': self.id,
            'quotation_name': self.ref,
            'seller_id': self.user_id.id,
            'fiscal_position_id': self.fiscal_position_id,
            'id': self.id,
            'ref': self.ref,
            'lines': lines
        }
        for line in self.lines:
            domian = [('product_id', '=', line.product_id.id), ('location_id',  '=', location.id)]
            t = quant.search(domian)
            rest = t.available_quantity - line.qty
            if line.qty < t.available_quantity:
                lines.append({
                    'price_unit': line.price_unit, 'discount': line.discount, 'qty': line.qty,
                    'product_id': line.product_id.id
                })
            if rest == 0.0:
                lines.append({
                    'price_unit': line.price_unit, 'discount': line.discount, 'qty': line.qty,
                    'product_id': line.product_id.id
                })
        return vals

        #return vals
        # vals = {
        #
        #     'lines': lines, # [{'price_unit': line.price_unit, 'discount': line.discount, 'qty': line.qty,
        #     #            'product_id': line.product_id.id} for line in
        #     #           self.lines],
        # }

        # return {
        #     'partner_id': self.partner_id.id,
        #     'lines': [{'price_unit': line.price_unit, 'discount': line.discount, 'qty': line.qty,
        #                'product_id': line.product_id.id} for line in
        #               self.lines],
        #     'quotation_id': self.id,
        #     'quotation_name': self.ref,
        #     'seller_id': self.user_id.id,
        #     'fiscal_position_id': self.fiscal_position_id,
        #     'id': self.id,
        #     'ref': self.ref,
        # }

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        results = super(POSQuotation, self).search_read(domain, fields, offset, limit, order)
        for result in results:
            partner_id = result.get('partner_id')
            if partner_id:
                partner = self.env['res.partner'].browse(partner_id[0])
                result['partner_id'] = list(result['partner_id'])
                result['partner_id'].append(partner.name)
        return results


class POSQuotationLines(models.Model):
    _name = "pos.quotation.line"
    _description = "Point of Sale Order Lines"
    _rec_name = "product_id"

    company_id = fields.Many2one('res.company', string='Company', related="quotation_id.company_id", store=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], required=True,
                                 change_default=True)
    price_unit = fields.Float(string='Unit Price', digits=0)
    qty = fields.Float('Quantity', digits='Product Unit of Measure', default=1)
    price_subtotal = fields.Float(string='Subtotal w/o Tax', digits=0,
                                  readonly=True, required=True)

    price_subtotal_incl = fields.Float(string='Subtotal', digits=0,
                                       readonly=True, required=True)
    discount = fields.Float(string='Discount (%)', digits=0, default=0.0)
    quotation_id = fields.Many2one('pos.quotation', string='Quotation Ref', ondelete='cascade', required=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes', readonly=True)
    currency_id = fields.Many2one('res.currency', related='quotation_id.currency_id')
    tax_ids_after_fiscal_position = fields.Many2many('account.tax', compute='_get_tax_ids_after_fiscal_position',
                                                     string='Taxes to Apply')
    product_uom_id = fields.Many2one('uom.uom', string='Product UoM', related='product_id.uom_id')

    @api.depends('quotation_id', 'quotation_id.fiscal_position_id')
    def _get_tax_ids_after_fiscal_position(self):
        for line in self:
            line.tax_ids_after_fiscal_position = line.quotation_id.fiscal_position_id.map_tax(line.tax_ids,
                                                                                              line.product_id,
                                                                                              line.quotation_id.partner_id)
