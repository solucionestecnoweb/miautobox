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

        },
        total_amount_with_igtf: function () {
            this.igtf = 0.0
            var total_lines = 0.0
            var porcentage = 0.0
            var lines = this.paymentlines.models
            lines.forEach(line => {
                if (line['payment_method']['is_dollar_payment'] && line['payment_method']['calculate_wh_itf']) {
                    total_lines += line.get_amount();
                    porcentage = line['payment_method']['porcentage']
                }
            });
            var total_no_igtf = this.get_total_without_tax() + this.get_total_tax()
            if (total_lines > total_no_igtf) {
                var igtf_total = total_no_igtf * porcentage / 100
                this.igtf = parseFloat(igtf_total.toFixed(2))
            } else {
                var igtf_total = total_lines * porcentage / 100
                this.igtf = parseFloat(igtf_total.toFixed(2))
            }
            if (this.igtf >= 0) {

                return this.igtf
            } else {
                return 0.0
            }
        },

        add_paymentline: function (payment_method) {
            debugger;
            this.assert_editable();
            if (this.electronic_payment_in_progress()) {
                return false;
            } else {
                var newPaymentline = new models.Paymentline({}, { order: this, payment_method: payment_method, pos: this.pos });
                if (this.igtf > 0 && payment_method.is_dollar_payment) {

                    var due = this.get_due()
                    if (due > 0) {
                        debugger;
                        var total_amount = this.get_total_without_tax() + this.get_total_tax()
                        var total_no_igtf = parseFloat(total_amount.toFixed(2))
                        due = this.get_due() - this.igtf

                    } else {
                        debugger;
                        due = this.get_due()
                    }
                    debugger;
                    newPaymentline.set_amount(due);
                } else {
                    debugger;
                    var total_amount = this.get_total_without_tax() + this.get_total_tax()
                    var total_no_igtf = parseFloat(total_amount.toFixed(2))
                    var due = this.get_due()
                    if (due >= total_no_igtf) {

                        due = this.get_due() - this.igtf
                    } else {
                        due = this.get_due()
                    }

                    newPaymentline.set_amount(due);
                }
                debugger;
                this.paymentlines.add(newPaymentline);
                this.select_paymentline(newPaymentline);
                if (this.pos.config.cash_rounding) {
                    debugger;
                    this.selected_paymentline.set_amount(0);
                    this.selected_paymentline.set_amount(this.get_due());
                }

                if (payment_method.payment_terminal) {
                    newPaymentline.set_payment_status('pending');
                }
                return newPaymentline;
            }
        },

        get_total_with_tax: function () {
            return this.get_total_without_tax() + this.get_total_tax() + this.total_amount_with_igtf();
        },
        get_due: function (paymentline) {
            var lines = this.paymentlines.models
            var total_lines = 0.0
            var total_lines_bs = 0.0
            var is_pay_igtf = false
            var is_pay_change = false
            lines.forEach(line => {
                if (line['payment_method']['is_dollar_payment'] && line['payment_method']['calculate_wh_itf']) {
                    debugger;
                    if (line.get_amount() < 0) {
                        debugger;
                        is_pay_change = true
                    }
                    if (line.get_amount() > 0) {
                        debugger;
                        total_lines += Math.abs(line.get_amount());
                    }
                }
                if (!line['payment_method']['is_dollar_payment']) {
                    debugger;
                    if (line.get_amount() < 0) {
                        total_lines_bs = line.get_amount();
                    }
                    if (line.get_amount() == 0) {

                        total_lines_bs = 0
                    }
                    if (line.get_amount() > 0) {

                        total_lines_bs += line.get_amount();
                        is_pay_igtf = true
                    }
                }
            });
            var total_amount = this.get_total_without_tax() + this.get_total_tax()
            var total_no_igtf = parseFloat(total_amount.toFixed(2))
            if (total_lines >= total_no_igtf) {
                var due_original = this.get_total_with_tax() - this.get_total_paid() + this.get_rounding_applied();
                var igtf_total = total_no_igtf * 3 / 100
                var due = parseFloat(igtf_total.toFixed(2))
                if (!is_pay_igtf) {
                    if (total_lines_bs >= due) {
                        due = 0
                    } else {
                        due = igtf_total
                    }
                } else {
                    debugger;
                    if (is_pay_change) {
                        debugger;
                        due -= igtf_total
                    } else {
                        debugger;
                        due = due_original
                    }
                }
            } else {
                if (!paymentline) {
                    debugger;
                    var due = this.get_total_with_tax() - this.get_total_paid() + this.get_rounding_applied();
                } else {
                    var due = this.get_total_with_tax();
                    var lines = this.paymentlines.models;
                    for (var i = 0; i < lines.length; i++) {
                        if (lines[i] === paymentline) {
                            break;
                        } else {
                            due -= lines[i].get_amount();
                        }
                    }
                }
            }

            return round_pr(due, this.pos.currency.rounding);

        },

        get_change: function (paymentline) {
            var lines = this.paymentlines.models
            var total_lines = 0.0
            var total_lines_bs = 0.0
            var change = 0.0
            var is_pay_igtf = false
            var is_pay_change = false
            debugger;
            lines.forEach(line => {
                if (line['payment_method']['is_dollar_payment'] && line['payment_method']['calculate_wh_itf']) {
                    debugger;
                    if (line.get_amount() < 0) {

                        is_pay_change = true
                    }
                    if (line.get_amount() > 0) {

                        total_lines += Math.abs(line.get_amount());
                    }
                }
                if (!line['payment_method']['is_dollar_payment']) {
                    debugger;
                    total_lines_bs += line.get_amount();
                    is_pay_igtf = true
                }
            });
            var total_no_igtf = this.get_total_without_tax() + this.get_total_tax()
            var changes = Math.abs(total_no_igtf - total_lines)
            if (total_lines >= total_no_igtf) {
                var change_original = this.get_total_paid() - this.get_total_with_tax() - this.get_rounding_applied();

                if (!is_pay_igtf) {

                    if (total_lines_bs >= changes) {
                        change = 0
                    } else {

                        change = changes
                    }

                } else {
                    if (is_pay_change) {
                        change -= changes
                    } else {
                        change = change_original
                    }
                }
            }
            else {
                if (!paymentline) {
                    debugger;

                    var change = this.get_total_paid() - this.get_total_with_tax() - this.get_rounding_applied();

                } else {
                    debugger;
                    var change = -this.get_total_with_tax();
                    var lines = this.paymentlines.models;
                    for (var i = 0; i < lines.length; i++) {
                        change += lines[i].get_amount();
                        if (lines[i] === paymentline) {
                            break;
                        }
                    }
                }
            }
            return round_pr(Math.max(0, change), this.pos.currency.rounding);
        },

        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.call(this);
            json.igtf = this.igtf;
            return json;
        },
        init_from_JSON: function (json) {
            _super_order.init_from_JSON.apply(this, arguments);

        },
    });

});