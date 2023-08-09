odoo.define('eu_groups_perssions.BasicView', function (require) {
    "use strict";
    
    var session = require('web.session');
    var BasicView = require('web.BasicView');
    BasicView.include({
            init: function(viewInfo, params) {
                var self = this;
                this._super.apply(this, arguments);
                var models_to_deny_archive_partner=['res.partner','product.template','product.product'];

                var models_to_deny_archive_product=['res.partner','product.template','product.product'];
                var models_to_deny_duplicate=['sale.order','account.move'];

                var models_to_deny_duplicate_test=models_to_deny_duplicate.includes(self.controllerParams.modelName);
                var model_archivate =  models_to_deny_archive_partner.includes(self.controllerParams.modelName);
                var model_archivate_product =  models_to_deny_archive_product.includes(self.controllerParams.modelName);

                var model_export = self.controllerParams.modelName in ['product.template'] ? 'True' : 'False';

                if(model_archivate) {
                    session.user_has_group('eu_groups_perssions.archive_contacts').then(function(has_group) {
                        if(!has_group) {
                            self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                        }
                    });
                    
                };
                if(model_archivate_product) {
                    session.user_has_group('eu_groups_perssions.archive_products_eu').then(function(has_group) {
                        if(!has_group) {
                            self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                        }
                    });
                    
                };

                if(models_to_deny_duplicate_test) {
                    session.user_has_group('eu_groups_perssions.duplica_eu').then(function(has_group) {
                        if(!has_group) {
                            self.controllerParams.activeActions['duplicate'] = 'False' in viewInfo.fields;
                        }
                    });
                    
                };

                var buttonUpload=$(".o_button_upload_bill");
   
                
                if (buttonUpload){
                    session.user_has_group('eu_groups_perssions.cargar_facturacion_eu').then(function(has_group) {
                        
                        if(!has_group) {

                            buttonUpload.hide();
                        }
                    });
                }
                
                    
                
            },
    });
    });