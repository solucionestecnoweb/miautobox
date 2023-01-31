# -*- coding:utf-8 -*-

from odoo import models, fields, api
import logging
from odoo.osv import expression
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


def get_years():
    year_list = []
    for i in range(1960, 2024):
        year_list.append((str(i), str(i)))
    return year_list

class AdditionalPartner(models.Model):
    _inherit = 'res.partner'

#     def name_get(self):
#         result = []
#         for record in self:
#             name = record.name + ' ' + str(record.cedula)
#             result.append((record.id, name))
#             # if record.brand_id.name:
#             #     name = record.brand_id.name + '/' + name
#             # res.append((record.id, name))
#         return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', operator, name), ('cedula', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)



class SubCategoryService(models.Model):
    _name = 'subcategory_service'
    _description = 'SubCategory Service'
    _order = 'name asc'
    name = fields.Char('Subcategoria de Servicio', required=True)


class Aditionalcategory(models.Model):
    _inherit = 'fleet.service.type'
    category = fields.Selection(selection=[
        ('servi_basic', 'Servicio basico'),
        ('servi_complementary', 'Servicio complementario'),
        ('servi_mechanic', 'Servicio mecanica ligera'),
        ('servi_outside', 'Servicios externos'),
    ], string='Servicios', required=True, copy=False, tracking=True)
    cantidad = fields.Float(string='Cantidad', default=1.0, digits=(16, 2))
    
    x_operador_serv = fields.Many2one(
        'res.partner', 'Operador Servicios',
        check_company=False,
        domain=lambda self: self._get_custom_domain_category(),
        store=True
    )

    def _get_custom_domain_category(self):
        domain = [('name', '=', 'Operador de Servicios AB')]
        return [('category_id', '=', self.env['res.partner.category'].search(domain, limit=1).id)]




class AditionalInfo(models.Model):
    _inherit = 'fleet.vehicle'
    model_year = fields.Selection(get_years(),'year', help='Transmission Used by the vehicle')
    transmission = fields.Selection([('manual', 'MANUAL'), ('automatic', 'AUTOMATICO'), ('dual','DUAL')], 'Transmission',
                                    help='Transmission Used by the vehicle')
    
    transmi = fields.Selection([('manual', 'MANUAL'), ('automatic', 'AUTOMATICO'), ('dual','DUAL')], 'Transmision ',
                                    help='Transmission Used by the vehicle')
    
    type_vehicle = fields.Selection([('POR FAVOR SELECCIONE UN TIPO DE VEHICULO',
                                      'POR FAVOR SELECCIONE UN TIPO DE VEHICULO'),
                                     ('VEHICULO', 'VEHICULO'),
                                     ('CAMIONETA PEQUEÑA', 'CAMIONETA PEQUEÑA'),
                                     ('CAMIONETA', 'CAMIONETA'),
                                     ('AUTOBUS', 'AUTOBUS'),
                                     ('CAMION PEQUEÑO', 'CAMION PEQUEÑO'),
                                     ('CAMION', 'CAMION')
                                        ,]
                                    , "Tipo de vehiculo",
                                    default='POR FAVOR SELECCIONE UN TIPO DE VEHICULO')

    fuel= fields.Selection([    
         ('gasolin', 'GASOLINA'),
            ('diesel', 'DIESEL'),
            ('glp', 'GASOLINA Y GAS'),
            ('electric', 'ELECTRICO'),
            ('hybrid', 'HYBRIDO'),
             ], 'Fuel Type', help='Fuel Used by the vehicle')
        
    fuel_type = fields.Selection([    
         ('gasolin', 'GASOLINE'),
            ('diesel', 'DIESEL'),
            ('glp', 'GASOLINA Y GAS'),
            ('electric', 'ELECTRIC'),
            ('hybrid', 'HYBRID'),

        ], 'Fuel Type', help='Fuel Used by the vehicle')
    color = fields.Selection([
       ('white', 'BLANCO'),
        ('black', 'NEGRO'),
        ('gris', 'GRIS'),
        ('plateado', 'PLATEADO'),
        ('arena', 'ARENA'),
        ('amarillo', 'AMARILLO'),
        ('azul', 'AZUL'),
        ('rojo', 'ROJO'),
        ('verde', 'VERDE'),
        ('naranja', 'NARANJA'),
        ('beige', 'BEIGE'),
        ], 'Fuel Type', help='Color of the vehicle')
    
    
#     @api.onchange("odometer")
#     def _set_odometer(self):
#         if self.odometer:
#             if len(str(self.odometer)) < 1.0:
#                 raise ValidationError( 'Odometro deber ser valido mayor que 0; '
#                 'favor corregir la observacion del vehiculo')
                


    @api.constrains('description')
    def _check_description(self):
        if self.description:
            if len(self.description) > 120:
                raise ValidationError(
                    'Longitud del campo Observacion del vehiculo excede los 120 caracteres; '
                    'favor corregir la observacion del vehiculo')
                

                

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.location = self.company_id.name
            self.company_id = None
        else:
            logger.info(self.company_id)

    @api.onchange('license_plate')
    def _onchange_plate(self):
        if self.license_plate:
            self.license_plate = self.license_plate.upper()

            
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quantity_tire = fields.Float(string='Cantidad', default=1.0, digits=(16, 2))


class SheetService(models.Model):

    _inherit = 'fleet.vehicle.log.services'
    product_tire = fields.Many2many('product.template', string='Neumaticos')
    image_128 = fields.Image("Firma", max_width=128, max_height=128)
    cantidad = fields.Float(string='Cantidad', default=1.0, digits=(16, 4))
    # service_type_id = fields.Many2many('fleet.service.type', string='Detalle de servicios', relation="service_types")
    service_types = fields.Many2many('fleet.service.type', string='Detalle de servicios')
    service_type = fields.Many2many('fleet.service.type', string='Detalle de servicios', relation="service_types")
    oil_leaks = fields.Many2many('subcategory_service', string='Sitios donde se detecto fuga', relation='name')
    fail_light = fields.Many2many('subcategory_service', string='Luces Revisadas', relation='oi_leaks')
    service_basic_bool = fields.Boolean(Default=True)
    service_oil_bool = fields.Boolean(Default=False)
    bool_sign = fields.Boolean(string="Firma",default=False,required=True)
    service_lightf_bool = fields.Selection([('0','No aplica'),
                                            ('1','1'),
                                            ('2', '2'),
                                            ('3', '3'),
                                            ('4', '4'),
                                            ],string='Esparragos', )
    service_lightf_text = fields.Char('Comentarios')

    service_lightb_bool = fields.Selection([('0','No aplica'),('1','1'),
                                            ('2', '2'),
                                            ('3', '3'),
                                            ('4', '4'),
                                            ], 'Tuercas',)
    service_lightb_text = fields.Char('Comentarios')

    pressure_valve = fields.Selection([('0','No aplica'),('1','1'),
                                            ('2', '2'),
                                            ('3', '3'),
                                            ('4', '4'),
                                            ], 'Valvula de presion',)
    pressure_valve_text = fields.Char('Comentarios')

    security_valve = fields.Selection([('0','No aplica'),('1','1'),
                                            ('2', '2'),
                                            ('3', '3'),
                                            ('4', '4'),
                                            ], 'Valvula de seguridad',)
    security_valve_text = fields.Char('Comentarios')

    bucket_lid = fields.Selection([('0','No aplica'),('1','1'),
                                            ('2', '2'),
                                            ('3', '3'),
                                            ('4', '4'),
                                            ], 'Tapa cubo',)
    bucket_lid_text = fields.Char('Comentarios')

    wheel_fees = fields.Selection([('0','No aplica'),('1','1'),
                                            ('2', '2'),
                                            ('3', '3'),
                                            ('4', '4'),
                                            ], 'Tasas de rueda',)
    wheel_fees_text = fields.Char('Comentarios')

    defective_rim = fields.Selection([('0','No aplica'),('1','1'),
                                            ('2', '2'),
                                            ('3', '3'),
                                            ('4', '4'),
                                            ], 'Rin',)
    defective_rim_text = fields.Char('Comentarios')

    rim_conditions = fields.Selection([('0','No aplica'),('1','1'),
                                            ('2', '2'),
                                            ('3', '3'),
                                            ('4', '4'),
                                            ], 'Condiciones del Rin',)
    rim_conditions_text = fields.Char('Comentarios')

    lightd = fields.Boolean(Default=False)
    lightt = fields.Boolean(Default=False)
    rearview = fields.Boolean(Default=False)
    trunk = fields.Boolean(Default=False)
    wiper = fields.Boolean(Default=False)
    paint = fields.Boolean(Default=False)

    light_description = fields.Text(string="Descripcion sobre donde se encuentra la falla electrica")
    oil_description = fields.Selection([
        ('seleccionar tipo de Aceite', 'Seleccionar tipo de Aceite'),
        ('motor', 'MOTOR'),
        ('caja', 'CAJA'),
        ('direccion', 'SINTETICO'),
        ('liga', 'Diesel'), ], string="Descripcion sobre donde se encuentra la fuga", help="Descripcion sobre donde se encuentra la fuga")

    type_oil = fields.Selection([
        ('seleccionar tipo de Aceite', 'Seleccionar tipo de Aceite'),
        ('mineral', 'Mineral'),
        ('semi_synthetic', 'Semi Sintético'),
        ('synthetic', 'Sintético'),
        ('diesel', 'Diesel'), ], string="Tipo de Aceite", help="Seleccionar tipo de Aceite",

        default="seleccionar tipo de Aceite")

    oil_viscosity = fields.Selection([
        ('seleccionar viscocidad del aceite', 'Seleccionar viscocidad del Aceite'),
        ('0w-20', '0w-20'),
        ('0w-30', '0w-30'),
        ('5w-30', '5w-30'),
        ('5w-40', '5w-40'),
        ('10w-30', '10w-30'),
        ('10w-40', '10w-40'),
        ('15w-40', '15w-40'),
        ('20w-50', '20w-50'),
        ('25w-50', '20w-60'),], string="Viscosidad del Aceite", help="Seleccionar viscosidad del Aceite",
        default='seleccionar viscocidad del aceite')

    selection = [
        ('Por favor seleccionar Ancho', 'Por favor seleccionar Ancho'),
        ('10', '10'),
        ('10.00', '10.00'),
        ('100', '100'),
        ('11', '11'),
        ('11.2', '11.2'),
        ('110', '110'),
        ('12', '12'),
        ('12.4', '12.4'),
        ('12.5', '12.5'),
        ('120', '120'),
        ('13', '13'),
        ('13.6', '13.6'),
        ('130', '130'),
        ('14', '14'),
        ('14.9', '14.9'),
        ('15', '15'),
        ('15.5', '15.5'),
        ('155', '155'),
        ('16.9', '16.9'),
        ('165', '165'),
        ('17.5', '17.5'),
        ('175', '175'),
        ('18.4', '18.4'),
        ('185', '185'),
        ('19.5', '19.5'),
        ('195', '195'),
        ('2.75', '2.75'),
        ('20.5', '20.5'),
        ('20.8', '20.8'),
        ('205', '205'),
        ('21', '21'),
        ('215', '215'),
        ('225', '225'),
        ('23.1', '23.1'),
        ('23.5', '23.5'),
        ('235', '235'),
        ('245', '245'),
        ('255', '255'),
        ('26.5', '26.5'),
        ('265', '265'),
        ('275', '275'),
        ('28', '28'),
        ('285', '285'),
        ('29.5', '29.5'),
        ('295', '295'),
        ('3.00', '3.00'),
        ('3.25', '3.25'),
        ('30', '30'),
        ('305', '305'),
        ('31', '31'),
        ('315', '315'),
        ('32', '32'),
        ('325', '325'),
        ('33', '33'),
        ('35', '35'),
        ('360', '360'),
        ('365', '365'),
        ('37', '37'),
        ('385', '385'),
        ('4.10', '4.10'),
    ]

    image = fields.Image(string="Image")
    marca_id = fields.Many2many('marca_cauchos', string="Marca_id")

    marca = fields.Char(required=True, related="marca_id.name")

    modelo_id = fields.Many2many('fleet.vehicle.model.tire', string="Modelo_id")

    medidas_id = fields.Many2many('measure_tire', string="Medidas_id")

    profundidad = fields.Integer()

    width = fields.Selection(selection, string="Ancho", help="Por favor seleccionar Ancho",
                             default="Por favor seleccionar Ancho")

    profile = fields.Selection([('Por favor seleccione un perfil',
                                 'Por favor seleccione un perfil'),('35', '35'), ('40', '40'), ('45', '45'),
                                ('50', '50'), ('55', '55'), ('60', '60'),
                                ('70', '70'), ('75', '75'), ('80', '80'), ], "Models",
                               default='Por favor seleccione un perfil')

    diameter = fields.Selection([('Por favor seleccione un diametro',
                                  'Por favor seleccione un diametro'),
                                 ('13', '13'), ('14', '14'), ('15', '15'),
                                 ('16', '16'), ('17', '17'), ('18', '18'),
                                 ('19', '19'), ('20', '20'), ('20', '20')],
                                "Models", default='Por favor seleccione un diametro')

    # cauchos #2
    marca_id2 = fields.Many2many('marca_cauchos', relation="marca")

    modelo_id2 = fields.Many2many('fleet.vehicle.model.tire', string="Modelo_id", relation="modelo")


    profundidad2 = fields.Integer()
    width2 = fields.Selection(selection, string="Ancho", help="Por favor seleccionar Ancho",
                              default="Por favor seleccionar Ancho")

    profile2 = fields.Selection([('Por favor seleccione un perfil',
                                 'Por favor seleccione un perfil'),('35', '35'), ('40', '40'), ('45', '45'),
                                ('50', '50'), ('55', '55'), ('60', '60'),
                                ('70', '70'), ('75', '75'), ('80', '80'), ], "Models",
                               default='Por favor seleccione un perfil')

    diameter2 = fields.Selection([('Por favor seleccione un diametro',
                                  'Por favor seleccione un diametro'),
                                 ('13', '13'), ('14', '14'), ('15', '15'),
                                 ('16', '16'), ('17', '17'), ('18', '18'),
                                 ('19', '19'), ('20', '20'), ('20', '20')],
                                "Models", default='Por favor seleccione un diametro')

    # cauchos #3
    marca_id3 = fields.Many2many('marca_cauchos', relation="marca3")

    modelo_id3 = fields.Many2many('fleet.vehicle.model.tire', string="Modelo_id", relation="modelo3")
    profundidad3 = fields.Integer()

    width3 = fields.Selection(selection, string="Ancho", help="Por favor seleccionar Ancho",
                              default="Por favor seleccionar Ancho")

    profile3 = fields.Selection([('Por favor seleccione un perfil',
                                 'Por favor seleccione un perfil'),('35', '35'), ('40', '40'), ('45', '45'),
                                ('50', '50'), ('55', '55'), ('60', '60'),
                                ('70', '70'), ('75', '75'), ('80', '80'), ], "Models",
                               default='Por favor seleccione un perfil')

    diameter3 = fields.Selection([('Por favor seleccione un diametro',
                                  'Por favor seleccione un diametro'),
                                 ('13', '13'), ('14', '14'), ('15', '15'),
                                 ('16', '16'), ('17', '17'), ('18', '18'),
                                 ('19', '19'), ('20', '20'), ('20', '20')],
                                "Models", default='Por favor seleccione un diametro')


    # cauchos #4
    marca_id4 = fields.Many2many('marca_cauchos', relation="marca4")

    modelo_id4 = fields.Many2many('fleet.vehicle.model.tire', string="Modelo_id", relation="modelo4")
    profundidad4 = fields.Integer()

    width4 = fields.Selection(selection, string="Ancho", help="Por favor seleccionar Ancho",
                              default="Por favor seleccionar Ancho")

    profile4 = fields.Selection([('Por favor seleccione un perfil',
                                  'Por favor seleccione un perfil'),('35', '35'), ('40', '40'), ('45', '45'),
                                 ('50', '50'), ('55', '55'), ('60', '60'),
                                 ('70', '70'), ('75', '75'), ('80', '80'), ], "Models",
                                default='Por favor seleccione un perfil')

    diameter4 = fields.Selection([('Por favor seleccione un diametro',
                                  'Por favor seleccione un diametro'),
                                 ('13', '13'), ('14', '14'), ('15', '15'),
                                 ('16', '16'), ('17', '17'), ('18', '18'),
                                 ('19', '19'), ('20', '20'), ('20', '20')],
                                "Models", default='Por favor seleccione un diametro')

    @api.onchange('service_type')
    def _onchange_service_types(self):

        self.service_type_id = 35
        
                     

    @api.onchange('service_type')
    def _onchange_company_id(self):
        if self.company_id:
            self.company_id = None
        else:
            self.company_id = None
    
            
            
    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.company_id = None
        else:
            self.company_id = None
            
    @api.constrains('lightd')
    def firmacheck6(self):
        if self.lightd == False:
            raise ValidationError("Chequear faros delanteros")
            
            
    @api.constrains('lightt')
    def firmacheck5(self):       
        if self.lightt == False:
            raise ValidationError("Chequear Luces traseras")
            
    @api.constrains('rearview')
    def firmacheck4(self):
        if self.rearview == False:
            raise ValidationError("Chequear retrovisores")
            
            
    @api.constrains('trunk')
    def firmacheck3(self):
        if self.trunk == False:
            raise ValidationError("Chequear maletero")
            
            
    @api.constrains('wiper')
    def firmacheck2(self):
        if self.wiper == False:
            raise ValidationError("Chequear cepillos limpiaparabrisas")
            
            
    @api.constrains('paint','lightd','lightt','rearview','trunk','wiper')
    def firmacheck1(self):
        if self.paint == False  :
            raise ValidationError("Chequear Revision General pintura")
        if self.lightd == False  :
            raise ValidationError("Chequear Revision General faros delanteros")
        if self.lightt == False  :
            raise ValidationError("Chequear Revision General luces traseras")
        if self.rearview == False  :
            raise ValidationError("Chequear Revision General retrovisores")
        if self.trunk == False  :
            raise ValidationError("Chequear Revision General maletero")
        if self.wiper == False  :
            raise ValidationError("Chequear Revision General cepillos limpiaparabrisas")




class FleetVehicleBrandTire(models.Model):
    _name = 'marca_cauchos'
    _description = 'Brand of tire of the vehicle'
    _order = 'model_count desc, name asc'

    name = fields.Char('Marca', required=True)
    image_128 = fields.Image("Logo", max_width=128, max_height=128)
    model_count = fields.Integer(compute="_compute_model_count", string="", store=True)

    model_ids = fields.One2many('fleet.vehicle.model.tire', 'brand_id')

    @api.depends('model_ids')
    def _compute_model_count(self):
        Model = self.env['fleet.vehicle.model.tire']
        for record in self:
            record.model_count = Model.search_count([('brand_id', '=', record.id)])

    def action_brand_model(self):
        self.ensure_one()
        view = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'fleet.vehicle.model.tire',
            'name': 'Models',
            'context': {'search_default_brand_id': self.id, 'default_brand_id': self.id}
        }

        return view


class FleetVehicleModelTire(models.Model):
    _name = 'fleet.vehicle.model.tire'
    _description = 'Model of a vehicle'
    _order = 'name asc'

    name = fields.Char('Model name', required=True)
    brand_id = fields.Many2one('marca_cauchos', 'Marca', required=True, help='Manufacturer of the vehicle')
    image_128 = fields.Image(related='brand_id.image_128', readonly=True)
    active = fields.Boolean(default=True)
    vehicle_type = fields.Selection([('car', 'Car'), ('bike', 'Bike')], default='car', required=True)

    @api.depends('name', 'brand_id')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.brand_id.name:
                name = record.brand_id.name + '/' + name
            res.append((record.id, name))
        return res

    def write(self, vals):
        if 'manager_id' in vals:
            old_manager = self.manager_id.id if self.manager_id else None

            self.env['fleet.vehicle'].search([('model_id', '=', self.id), ('manager_id', '=', old_manager)]).write(
                {'manager_id': vals['manager_id']})

        return super(FleetVehicleModelTire, self).write(vals)


class MeasureModelTire(models.Model):
    _name = 'measure_tire'
    _description = 'Measure of a vehicle'
    _order = 'name asc'

    name = fields.Char('Model name', required=True, invisible=True)

    profile = fields.Char('Perfil del caucho', required=True)
    diameter = fields.Char('Diametro del rin', required=True)

    vehicle_type = fields.Selection([('car', 'Car'), ('Truck', 'Truck')], default='car', required=True)
