"""Serialized data formatting"""
from odoo.http import request

class SerializerData():
    """serialization of the data to execute the call"""

    def criteria_filter_head(self, from_request):
        """Build criteria for filtering account move"""
        for items in from_request['filter_documents']:
            yield (items['field'], items['operator'], items['value'])

    def extract_account_move(self, filter_criteria):
        """apply criteria filter on account move"""
        return request.env['account.move'].sudo().search(
            filter_criteria)

    def extract_partner(self, partner):
        """get partner associated with account move"""
        for data in partner:
            partner_associed = {
                'id': data.id,
                'vat': data.vat,
                'name': data.name,
                'display_name': data.display_name,
                'street': data.street,
                'street2': data.street2,
                'zip': data.zip,
                'city': list(self.extract_details(data.city_id)),
                'state': list(self.extract_details(data.state_id)),
                'country': list(self.extract_details(data.country_id)),
                'phone': data.phone,
                'mobile': data.mobile,
                'email': data.email,
                'category': list(self.extract_details(data.category_id))
            }

        return partner_associed

    def extract_items(self, move_id):
        """get details item on account move"""
        details = request.env['account.move.line'].sudo().search([
            ('move_id', '=', move_id),
            ('product_id', '<>', False)
        ])

        items_in_invoice = []
        for data in details:
            items = {
                'id': data.id,
                'move_id': data.move_id.id,
                'move_name': data.move_name,
                'company_id': list(self.extract_details(data.company_id)),
                'product_id': list(self.extract_details(data.product_id)),
                'tax_line_id': list(self.extract_details(data.tax_line_id)),
                'name': data.name,
                'quantity': data.quantity,
                'price_unit': data.price_unit,
                'discount': data.discount,
                'price_subtotal': data.price_subtotal,
                'price_total': data.price_total,
                'currency': list(self.extract_details(data.currency_id))
            }
            items_in_invoice.append(items)

        return items_in_invoice

    def extract_payments(self, move):
        """get payments applied on account move"""
        payments = request.env['account.payment'].sudo().search([
            ('ref', '=', move.name),
            ('state', '=', move.state)
        ])

        payments_associed = []
        for data in payments:
            payment = {
                'id': data.id,
                'name': data.name,
                'date': data.date,
                'reconciled_invoice': list(self.extract_details(data.reconciled_invoice_ids)),
                'ref': data.ref,
                'amount': data.amount,
                'amount_total_signed': data.amount_total_signed,
                'currency_id': list(self.extract_details(data.currency_id)),
                'partner_id': list(self.extract_details(data.partner_id)),
                'company_id': list(self.extract_details(data.company_id)),
                #Custom Fields:
                'payment_acquirer': list(self.extract_details(data.payment_acquirer)),
                'rate': data.rate
            }
            payments_associed.append(payment)

        return payments_associed

    def reversed_entry(self, reserved):
        """get reversed entry applied on account move"""
        for reserves in reserved:
            yield {
                'id': reserves.id,
                'display_name': reserves.display_name
            }

    def extract_details(self, details):
        """get object details"""
        for items in details:
            yield {
                'id': items.id,
                'name': items.name
            }
