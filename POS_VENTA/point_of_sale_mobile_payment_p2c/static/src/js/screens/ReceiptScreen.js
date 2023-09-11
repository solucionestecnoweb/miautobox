odoo.define(
  "point_of_sale_turned_mobile_payment_ve.print_receipt_mobile_payment", function (require) {
    "use strict";

    const ReceiptScreen = require("point_of_sale.ReceiptScreen");
    const Registries = require("point_of_sale.Registries");

    const CustomReceiptScreen = (ReceiptScreen) =>
      class extends ReceiptScreen {
        printMobilePaymentReceipt() {
          debugger;
          const formatTextLine = this.env.pos.get_order().receipt_change_mobile_payment
          let printFrame = document.createElement('iframe');
          document.body.appendChild(printFrame);
          printFrame.style.display = 'none';

          printFrame.contentWindow.document.open();
          printFrame.contentWindow.document.write(`<div style="font-size: 11px; text-align:left; font-family: Arial">${formatTextLine}</div>`);
          printFrame.contentWindow.document.close();
          printFrame.contentWindow.print();
       
        }
      };
    Registries.Component.extend(ReceiptScreen, CustomReceiptScreen);
  }
);
