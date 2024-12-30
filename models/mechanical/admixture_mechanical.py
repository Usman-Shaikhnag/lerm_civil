from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math


class MechanicalAdmixture(models.Model):
    _name = 'mechanical.admixture'
    _inherit = "lerm.eln"
    _rec_name = "name"


    name_admixture = fields.Char("Name",default="Admixture")
    parameter_id = fields.Many2one('eln.parameters.result', string="Parameter")

    sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    eln_ref = fields.Many2one('lerm.eln',string="Eln")



    room_temp = fields.Char(string="Room Temp")
    room_rh = fields.Char(string="Room RH")
    child_lines = fields.One2many('mechanical.admixture.line', 'parent_id', string="Parameter", default=lambda self: self._default_sieve_analysis_child_lines())

    @api.model
    def _default_sieve_analysis_child_lines(self):
        default_lines = [
            (0, 0, {'water_content_max1': 'Water Content % of control sample,Max'}),
            (0, 0, {'water_content_max1': 'Slump'}),
            (0, 0, {'water_content_max1': 'Time of setting allowable deviation from control sample hours Initial'}),
            (0, 0, {'water_content_max1': 'Time of setting allowable deviation from control sample hours Final'}),
            (0, 0, {'water_content_max1': 'Compressive Strength (N/mm2)'}),
            (0, 0, {'water_content_max1': 'a) 1 Day'}),
            (0, 0, {'water_content_max1': 'b) 3 Days'}),
            (0, 0, {'water_content_max1': 'c) 7 Days'}),
            (0, 0, {'water_content_max1': 'd)  28 Days'}),
            (0, 0, {'water_content_max1': 'Flexural strength % of control sample,Min'}),
            (0, 0, {'water_content_max1': 'a) 3 Days'}),
            (0, 0, {'water_content_max1': 'b) 7 Days'}),
            (0, 0, {'water_content_max1': 'c) 28 Days'}),
            (0, 0, {'water_content_max1': 'Bleeding (%) over control'}),
            (0, 0, {'water_content_max1': 'Air Content (%) over control Max'}),
        ]
        return default_lines

    
    def open_eln_page(self):
        # import wdb; wdb.set_trace()

        return {
                'view_mode': 'form',
                'res_model': "lerm.eln",
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.eln_ref.id,
                
            }


    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(MechanicalAdmixture, self).create(vals)
        # record.get_all_fields()
        record.eln_ref.write({'model_id':record.id})
        return record

    





    @api.depends('eln_ref')
    def _compute_sample_parameters(self):
        # records = self.env['lerm.eln'].sudo().search([('id','=', record.eln_id.id)]).parameters_result
        # print("records",records)
        # self.sample_parameters = records
        for record in self:
            records = record.eln_ref.parameters_result.parameter.ids
            record.sample_parameters = records
            print("Records",records)



    def get_all_fields(self):
        record = self.env['mechanical.admixture'].browse(self.ids[0])
        field_values = {}
        for field_name, field in record._fields.items():
            field_value = record[field_name]
            field_values[field_name] = field_value

        return field_values



class MechanicalAdmixtureLine(models.Model):
    _name = "mechanical.admixture.line"
    parent_id = fields.Many2one('mechanical.admixture',string="Parent Id")


    water_content_max1 = fields.Char(string='Test Parameter')
    water_content_max2 = fields.Char(string='Control')
    water_content_max3 = fields.Char(string='Admixture')
    water_content_max4 = fields.Char(string='Accelerating admixture')
    water_content_max5 = fields.Char(string='Retarding Admixture')
    water_content_max6 = fields.Char(string='Water Reducing admixture')
    water_content_max7 = fields.Char(string='Air Entering Admixture')
    water_content_max8 = fields.Char(string='Normal')
    water_content_max9 = fields.Char(string='Retarding Type')

    # slump = fields.Char(string='Slump')

    # time_of_setting_initial = fields.Char(string='Time of Setting - Initial')
    # time_of_setting_final = fields.Char(string='Time of Setting - Final')

    # compressive_strength_1_day = fields.Char(string='Compressive Strength (1 Day)')
    # compressive_strength_3_days = fields.Char(string='Compressive Strength (3 Days)')
    # compressive_strength_7_days = fields.Char(string='Compressive Strength (7 Days)')
    # compressive_strength_28_days = fields.Char(string='Compressive Strength (28 Days)')

    # flexural_strength_3_days = fields.Char(string='Flexural Strength (3 Days)')
    # flexural_strength_7_days = fields.Char(string='Flexural Strength (7 Days)')
    # flexural_strength_28_days = fields.Char(string='Flexural Strength (28 Days)')

    # bleeding = fields.Char(string='Bleeding (%) over control')
    # air_content = fields.Char(string='Air Content (%) over control')


    