# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class ProductKardex(models.Model):
    _name = "product.kardex"
    _description = "Kardex de Producto"
    _auto = False
    _order = "company_id, product_name, move_date"

    id = fields.Integer(string='ID Kardex', readonly=True)
    product_id = fields.Many2one('product.template', string='ID de Producto', readonly=True)
#     x_CodGP = fields.Char('Código GP', related='product_id.x_CodGP')
    x_CodICG = fields.Char('Código ICG', related='product_id.x_CodICG')
    default_code = fields.Char('Código Magento', related='product_id.default_code')
    company_id = fields.Many2one('res.company',
                                 string='Compañía', readonly=True, index=True,
                                 domain="[('company_id', 'in', company_ids)]"
                                 )
    product_name = fields.Char(string='Producto', readonly=True)
    move_date = fields.Datetime(string='Fecha Movimiento Stock', readonly=True)
    wh_from = fields.Char(string='Almacén de Origen', readonly=True)
    wh_to = fields.Char(string='Almacén de Destino', readonly=True)
    reference = fields.Char(string='Referencia del Movimiento', readonly=True)
    origin_doc = fields.Char(string='Documento de Origen', readonly=True)
    invoice = fields.Text(string='Facturas', readonly=True)
    move_qty = fields.Integer(string='Cantidad del Movimiento', readonly=True)
    stock_qty = fields.Integer(string='Stock Final', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'product_kardex')
        self.company_id = self.env['res.company'].id or 1
        product_id = self._context.get('product_id') or 10780
        #product_id = self.env['product.template'].id or 1
        query = """ CREATE OR REPLACE view product_kardex as
                with mov as (
                    SELECT m.company_id as company_id, p.name as product_name, 
                        m.date as move_date, d.name as wh_from, h.name as wh_to, m.reference as reference, 
                        coalesce(sp.origin, '') as origin_doc, 
                        p.id as product_id,
                        sum(
                        case 
                            when h.name ilike '%%Stock%%' THEN m.qty_done
                            else m.qty_done * -1
                        end) as move_qty
                    FROM stock_move_line as m 
                    LEFT JOIN product_template as p on m.product_id = p.id
                    LEFT JOIN stock_location as d on m.location_id = d.id
                    LEFT JOIN stock_location as h on m.location_dest_id = h.id
                    LEFT JOIN stock_picking as sp on sp.name = m.reference
                    WHERE h.name ilike '%%Stock%%' OR d.name ilike '%%Stock%%'
                    GROUP BY m.company_id, product_name, move_date, wh_from, wh_to, reference, 
                        origin_doc, p.id 
                    ORDER BY m.company_id, product_name, move_date, wh_from, wh_to, reference, 
                        origin_doc, p.id
                )
                select
                  row_number() over (order by product_name) as id, company_id, product_id,
                  product_name, move_date, wh_from, wh_to, reference, origin_doc, move_qty,
                  sum(move_qty) over (partition by company_id, product_name order by company_id, product_name,
                    move_date, 
                    wh_from asc rows between unbounded preceding and current row) as stock_qty,
                        array_to_string((SELECT array_agg(i.name) as invoice 
                            FROM account_move AS i
                            WHERE i.invoice_origin = origin_doc AND i.move_type = 'out_invoice'
                                  AND i.company_id = mov.company_id
                            GROUP BY invoice_origin
                        ), ', ', '') as invoice	
                from mov  
                order by
                    company_id, product_name, move_date
        """
        #self._cr.execute(query % (self.product_id, self.company_id))
        self.flush
        self._cr.execute(query)
