odoo.define("point_of_sale_turned_mobile_payment_ve.models", (require) => {
    "use strict";


    const models = require('point_of_sale.models');
    const _super_order = models.Order.prototype;
    const PaymentlineSuper = models.Paymentline.prototype;
    const BANKS_VE = [
        ['0102', 'Banco de Venezuela'],
        ['0105', 'Banco Mercantil'],
        ['0116', 'Banco Occidental de Descuento'],
        ['0128', 'Banco Caroní'],
        ['0134', 'Banesco Banco Universal'],
        ['0137', 'Banco Sofitasa'],
        ['0138', 'Bancamiga Banco Microfinanciero'],
        ['0146', 'Banco Exterior'],
        ['0149', 'Banco Nacional de Crédito'],
        ['0156', 'Banco Fondo Común'],
        ['0157', 'Banco del Tesoro'],
        ['0163', 'Banco del Caribe'],
        ['0168', 'Banco Plaza'],
        ['0169', 'Banco Caracas']
    ]


    
    models.load_fields('pos.payment.method', ['is_turned_mobile_payment']);


    models.Order = models.Order.extend({
        initialize: function() {
            _super_order.initialize.apply(this,arguments);
            this.is_turned_mobile_payment_order = this.is_turned_mobile_payment_order || false;
            this.show_payment_mobile_option = this.show_payment_mobile_option || false
            this.receipt_change_mobile_payment = this.receipt_change_mobile_payment || false
            // this.show_payment_change_mobile_active = this.show_payment_change_mobile_active || false
            
        },
        init_from_JSON: function (json) {
            _super_order.init_from_JSON.apply(this, arguments);
            this.is_turned_mobile_payment_order = json.is_turned_mobile_payment_order;
            this.show_payment_mobile_option = json.show_payment_mobile_option
        },
        export_as_JSON: function () {
            const json = _super_order.export_as_JSON.call(this);
            json.is_turned_mobile_payment_order = this.is_turned_mobile_payment_order;
            return json
        },
        get_banks_mobile_payment: function () {
            return BANKS_VE
        }
    });

    models.Paymentline = models.Paymentline.extend({
        initialize: function(attributes, options) {
            PaymentlineSuper.initialize.apply(this, arguments);
            this.line_is_turned_mobile_payment = this.line_is_turned_mobile_payment || false;
            this.mobile_payment_bank_from = this.mobile_payment_bank_from || false;
            this.phone = this.phone || false;
            this.ci_ve = this.ci_ve || false
        },
        export_as_JSON: function() {
			let json = PaymentlineSuper.export_as_JSON.apply(this, arguments);
            json.line_is_turned_mobile_payment = this.line_is_turned_mobile_payment;
            json.mobile_payment_bank_from = this.mobile_payment_bank_from;
            json.phone = this.phone;
            json.ci_ve = this.ci_ve
			return json
		},

		init_from_JSON: function(json){
			PaymentlineSuper.init_from_JSON.apply(this,arguments);
            this.mobile_payment_bank_from = json.mobile_payment_bank_from;
            this.line_is_turned_mobile_payment = json.line_is_turned_mobile_payment;
            this.phone = json.phone;
            this.ci_ve = json.ci_ve
		},
    });
})