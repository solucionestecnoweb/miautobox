odoo.define('pos_auto_mrp_order.models_mrp_order', function (require) {
"use strict";
var pos_model = require('point_of_sale.models');
var models = pos_model.PosModel.prototype.models;
var rpc = require('web.rpc');
const PaymentScreen = require('point_of_sale.PaymentScreen');
const Registries = require('point_of_sale.Registries');

for(var i=0; i<models.length; i++){
    var model=models[i];
        if(model.model === 'product.product'){
            model.fields.push('to_make_mrp','to_make_mrp_draft');
        }
    }
const PosMrpOrder = PaymentScreen =>
    class extends PaymentScreen {
        async validateOrder(isForceValidate) {
            var self = this
            await super.validateOrder();
            var order = self.env.pos.get_order();
            var order_line = order.orderlines.models;
            var due = order.get_due();
            for (var i in order_line)
              {
		         var list_product = []
                 if (order_line[i].product.to_make_mrp || order_line[i].product.to_make_mrp_draft)
                 {
                   if (order_line[i].quantity>0)
                   {
                     var product_dict = {
                        'id': order_line[i].product.id,
                        'qty': order_line[i].quantity,
                        'product_tmpl_id': order_line[i].product.product_tmpl_id,
                        'pos_reference': order.name,
                        'uom_id': order_line[i].product.uom_id[0],
                        'to_make_mrp': order_line[i].product.to_make_mrp,
                   };
                  list_product.push(product_dict);
                 }
              }
              if (list_product.length)
              {
                rpc.query({
                    model: 'mrp.production',
                    method: 'create_mrp_from_pos',
                    args: [1,list_product],
                    });
              }
            }
        }
    };

Registries.Component.extend(PaymentScreen, PosMrpOrder);
});
