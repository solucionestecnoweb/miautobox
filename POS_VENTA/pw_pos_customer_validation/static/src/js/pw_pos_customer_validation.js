odoo.define('pw_pos_customer_validation.ClientListScreen', function (require) {
    'use strict';

    const ClientListScreen = require('point_of_sale.ClientListScreen');
    const Registries = require('point_of_sale.Registries');

    const PosCustomerValidation = (ClientListScreen) =>
        class extends ClientListScreen {
            async saveChanges(event) {
                var phone_list = [];
                var email_list = [];
                var barcode_list = [];

                var partners = this.env.pos.db.get_partners_sorted()
                var fields = event.detail.processedChanges
                for (var i = 0; i < partners.length; i++) {
                    if (partners[i].phone) {
                        phone_list.push(partners[i].phone);
                        email_list.push(partners[i].email);
                        barcode_list.push(partners[i].barcode);
                    }
                }
                if (this.env.pos.config.required_phone && ((fields.id === false && !fields.phone) || (fields.id && !fields.phone))) {
                    return this.showPopup('ErrorPopup', {
                        title: _('El número de teléfono del cliente es obligatorio!'),
                    });
                }
                if (this.env.pos.config.required_vat && ((fields.id === false && !fields.vat) || (fields.id && !fields.vat))) {
                    return this.showPopup('ErrorPopup', {
                        title: _('Se requiere el número de Cédula/Rif del cliente'),
                    });
                }
                if (this.env.pos.config.required_name && ((fields.id === false && !fields.name) || (fields.id && !fields.name))) {
                    return this.showPopup('ErrorPopup', {
                        title: _('El nombre del cliente es obligatorio!'),
                    });
                }
                if (this.env.pos.config.required_street && ((fields.id === false && !fields.street) || (fields.id && !fields.street))) {
                    return this.showPopup('ErrorPopup', {
                        title: _('La Direccion es obligatoria!'),
                    });
                }
                if (this.env.pos.config.required_city && ((fields.id === false && !fields.city) || (fields.id && !fields.city))) {
                    return this.showPopup('ErrorPopup', {
                        title: _('La cuidad es obligatoria!'),
                    });
                }
                if (this.env.pos.config.unique_phone && fields.phone && phone_list.indexOf(fields.phone) > -1) {
                    return this.showPopup('ErrorPopup', {
                        title: _('Phone '+fields.phone+' is already exist!'),
                    });
                }
                if (this.env.pos.config.required_email && ((fields.id === false && !fields.email) || (fields.id && !fields.email))) {
                    return this.showPopup('ErrorPopup', {
                        title: _('Customer email is required!'),
                    });
                }
                if (this.env.pos.config.unique_email && fields.email && email_list.indexOf(fields.email) > -1) {
                    return this.showPopup('ErrorPopup', {
                        title: _('Email '+fields.email+' is already exist!'),
                    });
                }
                if (this.env.pos.config.required_barcode && ((fields.id === false && !fields.barcode) || (fields.id && !fields.barcode))) {
                    return this.showPopup('ErrorPopup', {
                        title: _('Customer barcode is required!'),
                    });
                }
                if (this.env.pos.config.unique_barcode && fields.barcode && barcode_list.indexOf(fields.barcode) > -1) {
                    return this.showPopup('ErrorPopup', {
                        title: _('Barcode '+fields.barcode+' is already exist!'),
                    });
                }
                super.saveChanges(...arguments);
            }
        };
    Registries.Component.extend(ClientListScreen, PosCustomerValidation);
    return PosCustomerValidation;
});
