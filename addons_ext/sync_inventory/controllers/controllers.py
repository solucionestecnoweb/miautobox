
from odoo import http
from odoo.http import request

class StockController(http.Controller):
    """Stock Controller"""

    @http.route('/sync_stock', auth='user', type='json', methods=['POST'])
    def post_sync_stock(self):
        """Get data to build a new receipts in stock"""
        try:
            return self.load_items_in_stock(request.jsonrequest['data'])
        except Exception as message_error:
            return message_error

    def load_items_in_stock(self, data_serialized):
        """Load stock in 5 steps
        #Step 1: Create the new header to which the stock will be uploaded.
        #Step 2: Prepare the items to upload to the stocks.
        #Step 3: Filled the items in the stock.
        #Step 4: Clear the items to confirm the stock.
        #Step 5: Confirm items in stock.
        #Step 6: Update status in stock
        @return: cant_object_processed
        """

        stock = self.create_new_stock(data_serialized)
        prepare_items = self.prepare_items_for_stock(data_serialized, stock)
        stock_moves = self.create_stock_move(prepare_items)
        prepare_items_confirm = self.clean_items_for_confirm(stock_moves)
        stock_moves_line = self.confirm_stock_move_line(prepare_items_confirm)

        self.update_status_to_stock(stock['stock'])

        return {
            'cant_object_processed': stock_moves_line
        }

    def create_new_stock(self, data_serialized):
        """Create the new header to which the stock will be uploaded."""

        head_request = {
                'company_id': data_serialized['company_id'],
		    	'picking_type_id': data_serialized['picking_type_id'],
		    	'location_id': data_serialized['location_id'],
		    	'location_dest_id': data_serialized['location_dest_id'],
		    	'origin': data_serialized['origin'],
		    	'scheduled_date': data_serialized['scheduled_date']
        }

        if 'partner_id' in data_serialized:
            if data_serialized['partner_id'] != 0:
                head_request.update({'partner_id': data_serialized['partner_id']})

        stock = request.env['stock.picking'].sudo().create(head_request)
        return {
            'head': head_request,
            'stock': stock
        }

    def prepare_items_for_stock(self, data_serialized, stock):
        """Prepare the items to upload to the stock"""

        for items in data_serialized['details']:
            new_item = {
                'picking_id': stock['stock'].id,
                'company_id': stock['head']['company_id'],
                'location_dest_id': stock['head']['location_dest_id'],
                'location_id': stock['head']['location_id'],
                'name': items['name'],
                'procure_method': 'make_to_stock',
                'product_id': items['product_id'],
                'product_uom': items['product_uom_id'],
                'product_uom_qty': items['product_uom_qty'],
            }

            if 'partner_id' in stock['head']:
                new_item.update({'picking_partner_id': stock['head']['partner_id']})

            yield new_item

    def create_stock_move(self, prepare_items):
        """Filled the items in the stock."""

        items_with_stock = []
        for items in prepare_items:
            move = request.env['stock.move'].sudo().create(items)
            items['move_id'] = move.id
            items_with_stock.append(items)

        return items_with_stock

    def clean_items_for_confirm(self, stock_moves):
        """Clear the items to confirm the stock"""

        for items in stock_moves:
            if 'picking_partner_id' in items:
                del items['picking_partner_id']

            del items['name']
            del items['procure_method']
            items['product_uom_id'] = items['product_uom']
            del items['product_uom']
            items['qty_done'] = items['product_uom_qty']

            yield items


    def confirm_stock_move_line(self, stock_moves):
        """Confirm items in stock"""

        cant_object_processed = 0

        for items in stock_moves:
            request.env['stock.move.line'].sudo().create(items)
            cant_object_processed += 1

        return cant_object_processed

    def update_status_to_stock(self, stock):
        """Update status in stock"""
        return stock.sudo().update({
            'state': 'done'
        })

    @http.route('/update_products', auth='user', type='json', methods=['POST'])
    def sync_product(self):
        """Massive product updates"""
        try:
            return self.update_exist_products(request.jsonrequest)
        except Exception as message_error:
            return message_error

    def update_exist_products(self, data_serialized):
        """Update exist products"""

        cant_product_update = 0

        fields_update = self.prepare_fields_for_update(data_serialized['products'])

        for items_products in fields_update['products']:
            product = request.env['product.template'].sudo().search([(
                'id', '=', items_products['id']
            )])

            if 'default_code' in items_products and (
                items_products['default_code'] == product.default_code):

                del items_products['default_code']
                del items_products['id']

                product.sudo().update(items_products)

            else:
                del items_products['id']
                product.sudo().update(items_products)

            cant_product_update += 1

        self.update_traslate_name(fields_update['translation'])

        return {
            'cant_object_processed': cant_product_update
        }

    def prepare_fields_for_update(self, products):
        """mapping of products to be updated"""

        translation_fields = []
        products_fields = []

        for items in products:
            if 'us_name' in items:
                translation_fields.append({
                    'id': items['id'],
                    'us_name': items['us_name'],
                    'name': items['name']
                })

            del items['us_name']

            products_fields.append(items)

        return {
            'translation': translation_fields,
            'products': products_fields
        }

    def update_traslate_name(self, product_translation):
        """English and Spanish(VE) translation of the product name"""

        for items in product_translation:
            translate_us = request.env['ir.translation'].sudo().search([
                    ('lang', '=', 'en_US'),
                    ('name', '=', 'product.template,name'),
                    ('res_id', '=', items['id'])
                ])

            translate_us.sudo().update({
                'value': items['us_name']
            })

            translate_ve = request.env['ir.translation'].sudo().search([
                ('lang', '=', 'es_VE'),
                ('name', '=', 'product.template,name'),
                ('res_id', '=', items['id'])
            ])

            translate_ve.sudo().update({
                'value': items['name']
            })
