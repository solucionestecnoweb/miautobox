# -*- coding: utf-8 -*-
# Part of abnet_customize. See LICENSE file for full copyright and licensing details.
import datetime, pytz
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class account_invoice(models.Model):
    _inherit = "account.move"

    x_sff_flag = fields.Boolean(
        string="Supply Fast Forward",
        tracking=1,
        default=True
    )
    x_procesado_flag = fields.Boolean(
        string="Procesado/Integrado",
        default=False,
        copy=False
    )
    payment_acquirer = fields.Many2one(
        'payment.acquirer',
        check_company=True,
        domain="[('company_id', '=', company_id), ('state', '!=', 'disabled')]",
        string='Forma de Pago',
        default=None
    )

    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=False, readonly=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="[('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.",
        default=None
    )

    show_update_pricelist = fields.Boolean(
        string='Has Pricelist Changed',
        help="Technical Field, True if the pricelist was changed;\nthis will then display a recomputation button",
        store=False
    )

    rate = fields.Float(
        string='Tasa',
        store="True",
        tracking = 1,
        required=False,
        readonly=True,
        digits = (12, 2)
    )
    x_time = fields.Float(
        string='time',
        required=False,
        tracking=1,
        store = True,
        copy=False,
        default=0
    )
    es_gerente_tienda_hdg = fields.Boolean(
        string='¿-Es gerente de tienda  -?',
        readonly=True,
        store=False
    )

    @api.onchange("pricelist_id")
    def _set_pricelist_currency(self):
        self.show_update_pricelist = True
        if (
            self.is_invoice()
            and self.pricelist_id
        ):
            self.currency_id = self.pricelist_id.currency_id
            self._get_rate()
        self.currency_id = self.pricelist_id.currency_id

    @api.depends('pricelist_id', 'invoice_date', 'x_time','apply_manual_currency_exchange','manual_currency_exchange_rate')
    def _get_rate(self):
        currency_id = self.currency_id
        hora= datetime.time(hour=int(self.x_time), minute=int((self.x_time - int(self.x_time)) * 60))
        invoice_datetime = 0
        tzone = pytz.timezone('America/Caracas')
        self.rate = 1
        if self.invoice_date:
            invoice_datetime = datetime.datetime.combine(self.invoice_date, hora)
            invoice_datetime = invoice_datetime + datetime.timedelta(hours=4)
        if currency_id.id != self.company_currency_id.id:
            self.rate = self.manual_currency_exchange_rate

    def button_update_prices_from_pricelist(self):
        currency_id_saved = self.pricelist_id.currency_id
        for inv in self.filtered(lambda r: r.state == "draft"):
            inv.invoice_line_ids._onchange_product_id_account_invoice_pricelist()
        self.filtered(lambda r: r.state == "draft").with_context(
            check_move_validity=False
        )._move_autocomplete_invoice_lines_values()
        self.filtered(lambda r: r.state == "draft").with_context(
            check_move_validity=False
        )._recompute_tax_lines()
        self.pricelist_id.currency_id = currency_id_saved
        self.currency_id = currency_id_saved
        self.show_update_pricelist = False

    @api.constrains('pricelist_id')
    def _check_pricelist_id(self):
        lines = self.env['account.move.line']
        for line in lines:
            if any(self.env['account.move.line'].currency_id != self.pricelist_id.currency_id):
                raise UserError("Hay discrepancia entre la moneda de la lista de precios y la de los productos. \n Cambie la lista de precios o recalcule")

    # @api.constrains('x_sff_flag')
    # def x_sff_flag_constrains(self):
    #     tot_iva = 0
    #     for line in self.line_ids:
    #         if line.tax_line_id:
    #             tot_iva = tot_iva + line.price_total
    #     if self.x_sff_flag is False and tot_iva == 0:
    #         raise UserError("Por favor, ingrese el impuesto a ser aplicado")
    #     if self.x_sff_flag is True and tot_iva > 0:
    #         raise UserError("Se ha indicado el impuesto para nota SFF")

    @api.onchange('invoice_date')
    def _onchange_invoice_date(self):
        if self.invoice_date:
            if not self.invoice_payment_term_id and (not self.invoice_date_due or self.invoice_date_due < self.invoice_date):
                self.invoice_date_due = self.invoice_date
            if self.date != self.invoice_date:  # Don't flag date as dirty if not needed
                self.date = self.invoice_date
            self._onchange_currency()
        if not self.x_time or self.x_time == 0:
            if self.invoice_date:
                tz = pytz.timezone('America/Caracas')
                tm=fields.datetime.now(tz).time()
                self.x_time = tm.hour + tm.minute / 60.0

    @api.model
    def default_get(self, fields):
        gerente = False
        res = super(account_invoice, self).default_get(fields)
        if self.env.user.has_group('abnet_customize.gerente_tienda'):
            gerente = True
        res.update({'es_gerente_tienda_hdg': gerente})
        return res

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    es_gerente_tienda_det = fields.Boolean(
        string='¿Es gerente de tienda?',
        readonly=True,
        store=False
    )

    @api.onchange("product_id", "quantity")
    def _onchange_product_id_account_invoice_pricelist(self):
        for sel in self:
            if not sel.move_id.pricelist_id:
                return
            sel.with_context(check_move_validity=False).update(
                {"price_unit": sel._get_price_with_pricelist()}
            )

    @api.onchange("product_uom_id")
    def _onchange_uom_id(self):
        for sel in self:
            if (
                sel.move_id.is_invoice()
                and sel.move_id.state == "draft"
                and sel.move_id.pricelist_id
            ):
                price_unit = sel._get_computed_price_unit()
                taxes = sel._get_computed_taxes()
                if taxes and sel.move_id.fiscal_position_id:
                    price_subtotal = sel._get_price_total_and_subtotal(
                        price_unit=price_unit, taxes=taxes
                    )["price_subtotal"]
                    accounting_vals = sel._get_fields_onchange_subtotal(
                        price_subtotal=price_subtotal,
                        currency=self.move_id.company_currency_id,
                    )
                    balance = accounting_vals["debit"] - accounting_vals["credit"]
                    price_unit = sel._get_fields_onchange_balance(balance=balance).get(
                        "price_unit", price_unit
                    )
                sel.with_context(check_move_validity=False).update(
                    {"price_unit": price_unit}
                )
            else:
                super(AccountMoveLine, self)._onchange_uom_id()

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        PricelistItem = self.env["product.pricelist.item"]
        field_name = "lst_price"
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            while (
                pricelist_item.base == "pricelist"
                and pricelist_item.base_pricelist_id
                and pricelist_item.base_pricelist_id.discount_policy
                == "without_discount"
            ):
                price, rule_id = pricelist_item.base_pricelist_id.with_context(
                    uom=uom.id
                ).get_product_price_rule(product, qty, self.move_id.partner_id)
                pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == "standard_price":
                field_name = "standard_price"
                product_currency = product.cost_currency_id
            elif (
                pricelist_item.base == "pricelist" and pricelist_item.base_pricelist_id
            ):
                field_name = "price"
                product = product.with_context(
                    pricelist=pricelist_item.base_pricelist_id.id
                )
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id


        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                hora = datetime.time(hour=int(self.move_id.x_time), minute=int((self.move_id.x_time - int(self.move_id.x_time)) * 60))
                invoice_datetime = 0
                tzone = pytz.timezone('America/Caracas')
                if self.move_id.invoice_date:
                    invoice_datetime = datetime.datetime.combine(self.move_id.invoice_date, hora)
                    invoice_datetime = invoice_datetime + datetime.timedelta(hours=4)
                cur_factor = currency_id._get_conversion_rate(
                    product_currency,
                    currency_id,
                    self.company_id or self.env.company,
                    invoice_datetime or fields.Datetime.now(tzone),
                )

        product_uom = self.env.context.get("uom") or product.uom_id.id
        if uom and uom.id != product_uom:
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0
        #currency_id = self.env['account.move'].pricelist_id.currency_id
        return product[field_name] * uom_factor * cur_factor, currency_id

    def _calculate_discount(self, base_price, final_price):
        discount = (base_price - final_price) / base_price * 100
        if (discount < 0 and base_price > 0) or (discount > 0 and base_price < 0):
            discount = 0.0
        return discount

    def _get_price_with_pricelist(self):
        price_unit = 0.0
        if self.move_id.pricelist_id and self.product_id and self.move_id.is_invoice():
            if self.move_id.pricelist_id.discount_policy == "with_discount":
                hora = datetime.time(hour=int(self.move_id.x_time),
                                     minute=int((self.move_id.x_time - int(self.move_id.x_time)) * 60))
                invoice_datetime = 0
                if self.move_id.invoice_date:
                    invoice_datetime = datetime.datetime.combine(self.move_id.invoice_date, hora)
                    invoice_datetime = invoice_datetime + datetime.timedelta(hours=4)
                product = self.product_id.with_context(
                    lang=self.move_id.partner_id.lang,
                    partner=self.move_id.partner_id.id,
                    quantity=self.quantity,
                    invoice_date=invoice_datetime,
                    pricelist=self.move_id.pricelist_id.id,
                    product_uom_id=self.product_uom_id.id,
                    fiscal_position=(
                        self.move_id.partner_id.property_account_position_id.id
                    ),
                )
                tax_obj = self.env["account.tax"]
                recalculated_price_unit = round((
                    product.price * self.product_id.uom_id.factor
                ) / (self.product_uom_id.factor or 1.0), 2)
                price_unit = tax_obj._fix_tax_included_price_company(
                    recalculated_price_unit,
                    product.taxes_id,
                    self.tax_ids,
                    self.company_id,
                )
                self.with_context(check_move_validity=False).discount = 0.0
            else:
                hora = datetime.time(hour=int(self.move_id.x_time),
                                     minute=int((self.move_id.x_time - int(self.move_id.x_time)) * 60))
                invoice_datetime = 0
                tzone = pytz.timezone('America/Caracas')
                if self.move_id.invoice_date:
                    invoice_datetime = datetime.datetime.combine(self.move_id.invoice_date, hora)
                    invoice_datetime = invoice_datetime + datetime.timedelta(hours=4)
                product_context = dict(
                    self.env.context,
                    partner_id=self.move_id.partner_id.id,
                    date=invoice_datetime or fields.Datetime.now(tzone),
                    uom=self.product_uom_id.id,
                )
                final_price, rule_id = self.move_id.pricelist_id.with_context(
                    product_context
                ).get_product_price_rule(
                    self.product_id, self.quantity or 1.0, self.move_id.partner_id
                )
                base_price, currency = self.with_context(
                    product_context
                )._get_real_price_currency(
                    self.product_id,
                    rule_id,
                    self.quantity,
                    self.product_uom_id,
                    self.move_id.pricelist_id.id,
                )
                if currency != self.move_id.pricelist_id.currency_id:
                    hora = datetime.time(hour=int(self.move_id.x_time), minute=int((self.move_id.x_time - int(self.move_id.x_time)) * 60))
                    invoice_datetime = 0
                    tzone = pytz.timezone('America/Caracas')
                    if self.move_id.invoice_date:
                        invoice_datetime = datetime.datetime.combine(self.move_id.invoice_date, hora)
                        invoice_datetime = invoice_datetime + datetime.timedelta(hours=4)
                    base_price = currency._convert(
                        base_price,
                        self.move_id.pricelist_id.currency_id,
                        self.move_id.company_id or self.env.company,
                        invoice_datetime or fields.Datetime.now(tzone)
                    )
                price_unit = max(base_price, final_price)
                self.with_context(
                    check_move_validity=False
                ).discount = self._calculate_discount(base_price, final_price)
        return price_unit

    def _get_computed_price_unit(self):
        price_unit = super(AccountMoveLine, self)._get_computed_price_unit()
        if self.move_id.pricelist_id and self.move_id.is_invoice():
            price_unit = self._get_price_with_pricelist()
        return price_unit

    @api.constrains('tax_line_id', 'price_total')
    def tax_line_id_constrains(self):
        tot_iva = 0
        for line in self.move_id.line_ids:
            tot_iva += line.price_total
        #if self.move_id.x_sff_flag is False and tot_iva == 0:
        #    raise ValidationError("Por favor, ingrese el impuesto a ser aplicado TAXES LINES " + str(tot_iva))
        #if self.move_id.x_sff_flag is True and tot_iva > 0:
        #    raise ValidationError("Se ha indicado el impuesto en SFF TAXES LINES " + str(tot_iva))

    @api.model
    def default_get(self, fields):
        gerente = False
        res = super(AccountMoveLine, self).default_get(fields)
        if self.env.user.has_group('abnet_customize.gerente_tienda'):
            gerente = True
        res.update({'es_gerente_tienda_det': gerente})
        return res
