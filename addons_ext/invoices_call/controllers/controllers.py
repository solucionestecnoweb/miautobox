from odoo import http
from odoo.http import request
from .serializers import SerializerData

class InvoicesCallController(http.Controller, SerializerData):
    """Invoices call controller"""

    @http.route('/call_invoices', auth='user', type='json', methods=['POST'])
    def data_formatting(self):
        """data formatting from the request"""
        try:
            return self.mapping_all_invoices(request.jsonrequest)
        except Exception as message_error:
            return message_error

    def mapping_all_invoices(self, from_request):
        """mapping_all_invoices"""
        filter_invoices = list(self.criteria_filter_head(from_request))
        get_invoices = self.extract_account_move(filter_invoices)

        all_invoices = []

        for items in get_invoices:
            invoice = {
                'id': items.id,
                'name': items.name,
                'date': items.date,
                'ref': items.ref,
                'state': items.state,
                'move_type': items.move_type,
                'type_name': items.type_name,
                'journal_id': items.journal_id.id,
                'company_id': list(self.extract_details(items.company_id)),
                'company_currency_id': items.company_currency_id.id,
                'currency_id': items.currency_id.id,
                'partner_id': items.partner_id.id,
                'partner': self.extract_partner(items.partner_id),
                'commercial_partner_id': items.commercial_partner_id.id,
                'user_id': list(self.extract_details(items.user_id)),
                'amount_untaxed': items.amount_untaxed,
                'amount_tax': items.amount_tax,
                'amount_total': items.amount_total,
                'payment_state': items.payment_state,
                'reversed_entry': list(self.reversed_entry(items.reversed_entry_id)),
                'reversal_move_id': items.reversal_move_id.id,
                'invoice_payment_term': list(self.extract_details(items.invoice_payment_term_id)),
                'create_date': items.create_date,
                'amount_untaxed_signed': items.amount_untaxed_signed,
                'amount_tax_signed': items.amount_tax_signed,
                'amount_total_signed': items.amount_total_signed,
                #Custom Fields:
                'x_sff_flag': items.x_sff_flag,
                'x_procesado_flag': items.x_procesado_flag,
                'x_fiscal_document_number': items.x_fiscal_document_number,
                'x_printer_serial': items.x_printer_serial,
                'x_affected_document_date': items.x_affected_document_date,
                'x_affected_document_number': items.x_affected_document_number,
                'x_affected_document_printer_serial': items.x_affected_document_printer_serial,
                'payment_acquirer': list(self.extract_details(items.payment_acquirer)),
                'pricelist': list(self.extract_details(items.pricelist_id)),
                'apply_manual_currency_exchange': items.apply_manual_currency_exchange,
                'rate': items.rate,
                'manual_currency_exchange_rate': items.manual_currency_exchange_rate,
                'items': self.extract_items(items.id),
                'payments': self.extract_payments(items)
            }
            all_invoices.append(invoice)

        return all_invoices

    @http.route('/verify_invoice', auth='user', type='json', methods=['POST'])
    def processed_invoices(self):
        """data formatting from the request"""
        try:
            return self.status_update(request.jsonrequest)
        except Exception as message_error:
            return message_error

    def status_update(self, from_request):
        """change the status of processed invoices"""

        cant_invoices_processed = 0

        for items in from_request['invoices']:
            invoice = request.env['account.move'].sudo().search([
                ('id', '=', items['id'])
            ])

            invoice.sudo().update({
                'x_procesado_flag': items['x_procesado_flag']
            })

            cant_invoices_processed += 1

        return {
            'cant_object_processed': cant_invoices_processed
        }
