odoo.define(
  "point_of_sale_mobile_payment_p2c.PaymentScreen",
  (require) => {
    "use strict";

    const { Gui } = require("point_of_sale.Gui");
    const Registries = require("point_of_sale.Registries");
    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const rpc = require("web.rpc");

    const ButtonPaymentMobile = (PaymentScreen) =>
      class extends PaymentScreen {
        constructor() {
          super(...arguments);
        }
        async willStart() {
          let order = this.currentOrder;
          this.env.pos.config.payment_method_ids.some((id) => {
            let paymentMethod = this.env.pos.payment_methods_by_id[`${id}`];
            if (paymentMethod.is_turned_mobile_payment)
              order.show_payment_mobile_option = true;
          });
        }

        // _onClickShowPopup(ev) {
        //   let change = this.currentOrder.get_change();
        //   if (change <= 0) {
        //     return;
        //   }
        //   let PaymentMobileLine = this.currentOrder
        //     .get_paymentlines()
        //     .find(
        //       ({ payment_method }) => payment_method.is_turned_mobile_payment
        //     );
        //   let PaymentMobileLineAmount = PaymentMobileLine
        //     ? Math.abs(PaymentMobileLine.amount)
        //     : change;
        //   Gui.showPopup("MobilePaymentPopup", {
        //     amountPaymentMobile:
        //       PaymentMobileLineAmount > 0 ? PaymentMobileLineAmount : 0.0,
        //     // bankPaymentMobileCode: PaymentMobileLine ? PaymentMobileLine.mobile_payment_bank_from : false,
        //     // phone: PaymentMobileLine ? PaymentMobileLine.phone : "",
        //     ci_ve: PaymentMobileLine ? PaymentMobileLine.ci_ve : "",
        //   });
        // }

        async _onClickMobilePayment() {
          try {
            debugger;
            let change = this.currentOrder.get_change();
            let due = this.currentOrder.get_due();
            let client = this.currentOrder.get_client();

            if (!client) {
              this.showPopup("ErrorPopup", {
                title: this.env._t("Cliente requerido"),
                body: this.env._t(
                  "Seleccione el cliente antes de seleccionar el pago móvil!"
                ),
              });
              return;
            } else if (!client.vat) {
              this.showPopup("ErrorPopup", {
                title: this.env._t("Cédula del Cliente requerido"),
                body: this.env._t(
                  "Es requerido la cédula del cliente para el pago móvil."
                ),
              });
              return;
            }

            if (due > 0 || change > 0) {

              const requestOptions = {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({
                  accion: change > 0 ? "cambio" : "tarjeta",
                  montoTransaccion: change > 0 ? change : due,
                  cedula: this.currentOrder.get_client().vat,
                  tipoMoneda: "VES",
                }),
              };
             

              const response = await fetch(
                "http://localhost:8085/vpos/metodo",
                requestOptions
              );

              const data = await response.json();

              let formatText;
              var route = data.nombreVoucher
              if (data.nombreVoucher) {
                  // let dataTxt = await rpc.query({
                  //   model: "pos.order",
                  //   method: "read_txt_mobile_payment",

                  //   args: [data.nombreVoucher],
                  // });
                debugger;


                const requestOptionsPrint = {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                  },
  
           
             
                  body: JSON.stringify({
                    route
                  }),
                };
                debugger;
                const responsePrint = await fetch(
                  "http://localhost:5000/api/file",
                  requestOptionsPrint
                );
                const dataPrint = await responsePrint.text();
          
                
                
        
                formatText = dataPrint.split("\n");
                let formatTextLine;
                if (formatText) {
                  formatTextLine = "";
                  for (let line of formatText) {
                    formatTextLine += line.replace("\r", "") + "<br/>";
                  }
                }
                if (data.codRespuesta == "00") {
                  let PaymentMobileLine = this.currentOrder
                    .get_paymentlines()
                    .find(
                      ({ payment_method }) =>
                        payment_method.is_turned_mobile_payment
                    );
                  if (PaymentMobileLine) {
                    this.currentOrder.remove_paymentline(PaymentMobileLine);
                  }
                  let payment_mobile = this.env.pos.payment_methods.find(
                    ({ is_turned_mobile_payment }) => is_turned_mobile_payment
                  );
                  let line = this.currentOrder.add_paymentline(payment_mobile);
                  let amount = change > 0 ? -change : due;
                  line.set_amount(amount);

                  line.line_is_turned_mobile_payment = true;

                  this.currentOrder.receipt_change_mobile_payment =
                    formatTextLine || '';
                } else {
        
                  await this.showPopup("ErrorPopup", {
                    title: this.env._t("Error"),
                    body: this.env._t(`${data.mensajeRespuesta}`),
                  });
                  let printFrame = document.createElement('iframe');
                  document.body.appendChild(printFrame);
                  printFrame.style.display = 'none';
        
                  printFrame.contentWindow.document.open();
                  printFrame.contentWindow.document.write(`<div style="font-size: 11px; text-align:left; font-family: Arial">${formatTextLine}</div>`);
                  printFrame.contentWindow.document.close();
                  printFrame.contentWindow.print();
                  return;
                }
              } else {
                console.error("No voucher path received");
                throw new Error("No voucher path received");
              }
            }
            debugger;
          } catch (error) {
            console.error("An error occurred:", error);
          }
        }

        deletePaymentLine(event) {
          const res = super.deletePaymentLine(...arguments);
          let order = this.currentOrder;
          let PaymentMobileLine = order
            .get_paymentlines()
            .find(
              ({ payment_method }) => payment_method.is_turned_mobile_payment
            );
          if (!PaymentMobileLine) {
            this.currentOrder.is_turned_mobile_payment = false;
          }
          return res;
        }
      };

    Registries.Component.extend(PaymentScreen, ButtonPaymentMobile);
    return ButtonPaymentMobile;
  }
);
