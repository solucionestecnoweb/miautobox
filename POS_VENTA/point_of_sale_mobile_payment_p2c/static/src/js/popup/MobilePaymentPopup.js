odoo.define(
  "point_of_sale_turned_mobile_payment_ve.MobilePaymentPopup",
  function (require) {
    "use strict";

    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const Registries = require("point_of_sale.Registries");
    const rpc = require("web.rpc");

    class MobilePaymentPopup extends AbstractAwaitablePopup {
      constructor() {
        super(...arguments);
        this.props.errorInputBank = false;
        this.props.errorInputAmount = false;
        this.props.errorInputCi = false;
        this.props.errorInputPhone = false;
      }
      get currentOrder() {
        return this.env.pos.get_order();
      }
      close(ev) {
        this.confirm();
      }
      cancel(ev) {
        let linePaymentMobile = this.currentOrder
          .get_paymentlines()
          .find(
            ({ payment_method }) => payment_method.is_turned_mobile_payment
          );
        if (linePaymentMobile) {
          this.currentOrder.remove_paymentline(linePaymentMobile);
        }
        this.currentOrder.is_turned_mobile_payment = false;
        this.confirm();
      }
      _onChange(ev) {
        let change = this.currentOrder.get_change();
        let valueAmount = parseFloat(ev.target.value);
        if (valueAmount > change) $(ev.target).val(change);
      }
      async confirmLoad(ev) {
        let change = this.currentOrder.get_change();
        if (change > 0) {
          let $bankPaymentAmount = $("#payment-mobile-amount");
          // let $bankPaymentMobile = $("#bank-payment-mobile");
          // let $paymentMobilePhone = $("#payment-mobile-phone");
          let $paymentMobileCi = $("#payment-mobile-ci");
          // $bankPaymentMobile.val().trim() === ""
          //   ? (this.props.errorInputBank = true)
          //   : (this.props.errorInputBank = false);
          $bankPaymentAmount.val() === ""
            ? (this.props.errorInputAmount = true)
            : (this.props.errorInputAmount = false);
          // $paymentMobilePhone.val() === ""
          //   ? (this.props.errorInputPhone = true)
          //   : (this.props.errorInputPhone = false);
          $paymentMobileCi.val() === ""
            ? (this.props.errorInputCi = true)
            : (this.props.errorInputCi = false);
          this.render();

          if (
            // !this.props.errorInputBank &&
            !this.props.errorInputAmount &&
            // !this.props.errorInputPhone &&
            !this.props.errorInputCi
          ) {
            this.currentOrder.is_turned_mobile_payment = true;
            let payment_mobile = this.env.pos.payment_methods.find(
              ({ is_turned_mobile_payment }) => is_turned_mobile_payment
            );
            let PaymentMobileLine = this.currentOrder
              .get_paymentlines()
              .find(
                ({ payment_method }) => payment_method.is_turned_mobile_payment
              );
            if (PaymentMobileLine) {
              this.currentOrder.remove_paymentline(PaymentMobileLine);
            }
            let line = this.currentOrder.add_paymentline(payment_mobile);
            line.set_amount(-parseFloat($bankPaymentAmount.val()));
            // line.mobile_payment_bank_from = $(
            //   `option[value="${$bankPaymentMobile.val()}"]`
            // ).val();
            line.line_is_turned_mobile_payment = true;
            // line.phone = $paymentMobilePhone.val();
            line.ci_ve = $paymentMobileCi.val();
            // this.props.bankPaymentMobileCode = $(
            //   `option[value="${$bankPaymentMobile.val()}"]`
            // ).val();
            await this.onClickMobilePayment(
              $bankPaymentAmount.val(),
              line.ci_ve
            );
            this.confirm();
            debugger;
          }
        }
      }

      async _onClickMobilePayment(amount, ci) {
        try {
          const requestOptions = {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              accion: "cambio",
              montoTransaccion: amount,
              cedula: ci,
              tipoMoneda: "VES",
            }),
          };

          const response = await fetch(
            "http://localhost:8085/vpos/metodo",
            requestOptions
          );
          const data = await response.json();
          let formatText;
          debugger;
          if (data.nombreVoucher) {
            let dataTxt = await rpc.query({
              model: "pos.order",
              method: "read_txt_mobile_payment",

              args: [data.nombreVoucher],
            });
            debugger;
            formatText = dataTxt.split("\n");
            let formatTextLine;
            if (formatText) {
              formatTextLine = "";
              for (let line of formatText) {
                formatTextLine += line.replace("\r", "") + "<br/>";
              }
            }

            this.currentOrder.receipt_change_mobile_payment =
              formatTextLine || false;
          } else {
            console.error("No voucher path received");
            throw new Error("No voucher path received");
          }
          debugger;
        } catch (error) {
          console.error("An error occurred:", error);
        }
      }
    }

    MobilePaymentPopup.template = "MobilePaymentPopup";
    MobilePaymentPopup.defaultProps = {
      confirmText: "Guardar",
      cancelText: "Cancelar",
      title: "Informacion Pago movil",
      amountPaymentMobile: 0.0,
      bankPaymentMobileCode: "",
      phone: "",
      ci: "",
      body: "",
    };

    Registries.Component.add(MobilePaymentPopup);
    return MobilePaymentPopup;
  }
);
