from odoo import http
from odoo.http import request
from .format_checker import FormatChecker


class SalesOrderController(http.Controller, FormatChecker):
    """Sales order Controller"""

    @http.route('/syncPrices', auth='public', type='json', methods=['POST'])
    def format_verify_pricelist(self):
        """Checking the price list format for creating or updating the price list"""

        try:
            data_serialized = self.mapping_of_filtered_data(request.jsonrequest['data'], False)
            return self.verify_pricelist(data_serialized)

        except Exception as message_error:
            return message_error

    def verify_pricelist(self, data_serialized):
        """Verify the price list"""

        products_exist = list(self.extract_product_exist(data_serialized))
        products_not_exist = list(self.extract_product_not_exist(
            data_serialized, products_exist))

        cant_product_update  = self.update_item_in_pricelist(products_exist)
        cant_product_create = self.create_item_in_pricelist(products_not_exist) if (
            len(products_not_exist) > 0) else 0

        return {
            'products_not_exist': products_not_exist,
            'products_exist': products_exist,
            'sync': True,
            'cant_items_updated':  cant_product_update,
            'cant_items_created': cant_product_create
        }

    def update_item_in_pricelist(self, products_exist):
        """Update items in the price list"""

        cant_product_update = 0

        for items_in_product_exist in products_exist:
            for items_in_pricelist_id in items_in_product_exist['pricelist_IdS']:
                records = request.env['product.pricelist.item'].sudo().search(
                    [('product_tmpl_id','=', items_in_product_exist['Odoo_Id'])])
                for items_in_records in records:
                    if items_in_records.pricelist_id.id == items_in_pricelist_id:
                        items_in_records.sudo().update(
                            {'fixed_price': items_in_product_exist['UOMPRICE']})
                        cant_product_update += 1

        return cant_product_update

    def create_item_in_pricelist(self, products_not_exist):
        """Create items in the price list"""

        cant_product_create = 0

        for items_in_products_not_exists in products_not_exist:
            for items_in_pricelist_id in items_in_products_not_exists['pricelist_IdS']:
                cant_product_create += 1
                request.env['product.pricelist.item'].sudo().create({
                    'product_tmpl_id': items_in_products_not_exists['Odoo_Id'],
                    'applied_on': '1_product',
                    'pricelist_id': items_in_pricelist_id,
                    'min_quantity': 1,
                    'compute_price': 'fixed',
                    'fixed_price': items_in_products_not_exists['UOMPRICE']
                })

        return cant_product_create

    @http.route('/deletePrices', auth='public', type='json', methods=['POST'])
    def empty_all_records_in_pricelists(self):
        """Empty all records in pricelists"""

        products_id = list(self.get_odoo_id(request.jsonrequest['data']))

        request.env['product.pricelist.item'].sudo().search([
            ('product_tmpl_id','=', products_id)]).unlink()

        return {
            'cant_product_delete': len(products_id)
        }

    @http.route('/deleteInPriceList', auth='public', type='json', methods=['POST'])
    def format_empty_specific_pricelist(self):
        """Checking the format of the emptying request in specific lists"""

        try:
            data_serialized = self.mapping_of_filtered_data(request.jsonrequest, True)
            return self.empty_specific_pricelist(data_serialized)

        except Exception as message_error:
            return message_error

    def empty_specific_pricelist(self, data_serialized):
        """Empty specific pricelist"""

        cant_product_delete = 0

        for items_pricelist_id in data_serialized:
            res = request.env['product.pricelist.item'].sudo().search(
                [('pricelist_id','=', int(items_pricelist_id))])
            for item in res:
                if item.pricelist_id.id == int(items_pricelist_id):
                    item.unlink()
                    cant_product_delete += 1

        return {
            'cant_product_delete': cant_product_delete
        }
