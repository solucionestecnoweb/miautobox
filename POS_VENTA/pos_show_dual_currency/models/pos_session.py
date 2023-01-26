

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

class PosSession(models.Model):
    _inherit = 'pos.session'


    def _create_non_reconciliable_move_lines(self, data):
        # Create account.move.line records for
        #   - sales
        #   - taxes
        #   - stock expense
        #   - non-cash split receivables (not for automatic reconciliation)
        #   - non-cash combine receivables (not for automatic reconciliation)
        taxes = data.get('taxes')
        sales = data.get('sales')
        stock_expense = data.get('stock_expense')
        split_receivables = data.get('split_receivables')
        combine_receivables = data.get('combine_receivables')
        rounding_difference = data.get('rounding_difference')
        MoveLine = data.get('MoveLine')

        tax_vals = [self._get_tax_vals(key, amounts['amount'], amounts['amount_converted'], amounts['base_amount_converted']) for key, amounts in taxes.items() if amounts['amount']]
        # Check if all taxes lines have account_id assigned. If not, there are repartition lines of the tax that have no account_id.
        tax_names_no_account = [line['name'] for line in tax_vals if line['account_id'] == False]
        if len(tax_names_no_account) > 0:
            error_message = _(
                'Unable to close and validate the session.\n'
                'Please set corresponding tax account in each repartition line of the following taxes: \n%s'
            ) % ', '.join(tax_names_no_account)
            raise UserError(error_message)
        rounding_vals = []

        if not float_is_zero(rounding_difference['amount'], precision_rounding=self.currency_id.rounding) or not float_is_zero(rounding_difference['amount_converted'], precision_rounding=self.currency_id.rounding):
            rounding_vals = [self._get_rounding_difference_vals(rounding_difference['amount'], rounding_difference['amount_converted'])]
        
        account_igtf = self.env['account.account'].search([('name', 'ilike', 'IGTF')], limit=1)
        total_igtf = 0
        for order in self.order_ids:
            if order.total_igtf > 0:
                total_igtf += order.total_igtf
        MoveLine.create(
            tax_vals
            + [self._get_sale_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in sales.items()]
            + [self._get_stock_expense_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in stock_expense.items()]
            + [self._get_split_receivable_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in split_receivables.items()]
            + [self._get_combine_receivable_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in combine_receivables.items()]
            + [self._get_igtf_vals(account_igtf, total_igtf, total_igtf)]
            + rounding_vals
        )
        return data




    def _get_igtf_vals(self, out_account, amount, amount_converted):
        partial_args = { 'name': out_account.name,'account_id': out_account.id, 'move_id': self.move_id.id}
        return self._credit_amounts(partial_args, amount, amount_converted, force_company_currency=True)



    