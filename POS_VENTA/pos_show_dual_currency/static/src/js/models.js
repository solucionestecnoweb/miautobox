odoo.define('pos_show_dual_currency.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields('pos.payment.method', ['is_dollar_payment', 'porcentage', 'calculate_wh_itf']);
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    let PaymentlineSuper = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        initialize: function (attributes, options) {
            // Compatibility with pos_cache module
            PaymentlineSuper.initialize.apply(this, arguments);
        },

        // set_amount: function(value){
        //     /* CODE */
        //     PaymentlineSuper.set_amount.apply(this, [value]);
        // },
    });


    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attr, options) {
            _super_order.initialize.call(this, attr, options);
            this.igtf = this.igtf || 0;
            this.additional_dollar_tax = true;

        },


        total_amount_with_igtf: function () {
            var lines = this.paymentlines.models;
            var totalDollarAmount = 0.0;
            var percentage = 0.0;
            var otherAmount = 0.0
            var totalAmountLine = 0.0

            lines.forEach(line => {
                if (line['payment_method']['is_dollar_payment'] && line['payment_method']['calculate_wh_itf']) {
                    totalDollarAmount += line.get_amount();
                    percentage = line['payment_method']['porcentage'];
                } else {
                    otherAmount += line.get_amount();
                }
            });
            totalAmountLine = totalDollarAmount + otherAmount

            var total_no_igtf = this.get_total_without_tax() + this.get_total_tax();

            if (parseFloat(totalAmountLine.toFixed(2)) > total_no_igtf && this.additional_dollar_tax) {

                var igtf = (total_no_igtf - otherAmount) * percentage / 100;
                this.igtf = parseFloat(igtf.toFixed(2));
            }

            else if (this.additional_dollar_tax || parseFloat(totalAmountLine.toFixed(2)) < total_no_igtf) {

                var igtf = totalDollarAmount * percentage / 100;
                this.igtf = parseFloat(igtf.toFixed(2));
            }
            else if (totalDollarAmount == 0) {

                this.igtf = 0
            }

            return this.igtf >= 0 ? this.igtf : 0.0;
        },


        get_total_with_tax: function () {
            return this.get_total_without_tax() + this.get_total_tax() + this.total_amount_with_igtf();
        },


        add_paymentline: function (payment_method) {
            this.assert_editable();
            if (this.electronic_payment_in_progress()) {
                return false;
            } else {

                this.igtf_paid = false
                var newPaymentline = new models.Paymentline({}, { order: this, payment_method: payment_method, pos: this.pos });
                var total_amount = this.get_total_without_tax() + this.get_total_tax()
                var total_no_igtf = parseFloat(total_amount.toFixed(2))
                var due = parseFloat(this.get_due().toFixed(2))
                this.additional_dollar_tax = due > this.igtf;
                if (newPaymentline['payment_method']['is_dollar_payment'] && newPaymentline['payment_method']['calculate_wh_itf']) {
                    if (due > this.igtf && due < total_no_igtf) {

                        due -= this.igtf

                    }
                } else {
                    this.additional_dollar_tax = false
                }

                newPaymentline.set_amount(due);


                this.paymentlines.add(newPaymentline);
                this.select_paymentline(newPaymentline);
                if (this.pos.config.cash_rounding) {

                    this.selected_paymentline.set_amount(0);
                    this.selected_paymentline.set_amount(this.get_due());
                }

                if (payment_method.payment_terminal) {
                    newPaymentline.set_payment_status('pending');
                }
                return newPaymentline;
            }
        },


        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.call(this);
            json.igtf = this.igtf;
            return json;
        },
        init_from_JSON: function (json) {
            _super_order.init_from_JSON.apply(this, arguments);

        },
    })

});