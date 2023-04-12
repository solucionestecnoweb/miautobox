"""Format Checker Utils"""
from odoo.http import request

class FormatChecker():
    """Wrapper for the list sent in the petition """

    def mapping_of_filtered_data(self, object_request_data, only_pricelists=True):
        """Mapping for the list sent in the petition"""

        filter_data = []

        if not only_pricelists:
            for object_items in object_request_data:
                object_items['Odoo_Id'] = int(object_items['Odoo_Id'])
                object_items['UOMPRICE'] = float(object_items['UOMPRICE'])
                object_items['pricelist_IdS'] = object_items['pricelist_IdS'].split(',')

                if object_items['Odoo_Id'] != 0:
                    filter_data.append(object_items)

            for int_in_pricelist in filter_data:
                int_in_pricelist['pricelist_IdS'] = list(
                    map(int, int_in_pricelist['pricelist_IdS']))
        else:
            object_request_items = object_request_data[0]['pricelist_IdS'].split(',')

            for filtered_format in object_request_items:
                filter_data.append(filtered_format)

        return filter_data


    def extract_product_exist(self, data_serialized):
        """Extract products exist"""

        for items_in_data in data_serialized:
            records = request.env['product.pricelist.item'].sudo().search([
                ('product_tmpl_id','=', items_in_data['Odoo_Id'])])

            if records.product_tmpl_id.id == items_in_data['Odoo_Id']:
                yield items_in_data


    def extract_product_not_exist(self, data_serialized, products_exist):
        """Extract products not exist"""

        for items_list_to_create in data_serialized:
            if items_list_to_create not in products_exist:
                yield items_list_to_create


    def get_odoo_id(self, object_request_data):
        """Extract all odoo id"""

        for items_request_data in object_request_data:
            yield int(items_request_data['Odoo_Id'])


    def get_pricelist_id(self, data_serialized):
        """Extract all pricelist id"""

        for items_data_serialized in data_serialized:
            for items_pricelist in items_data_serialized['pricelist_IdS']:
                yield items_pricelist
                        