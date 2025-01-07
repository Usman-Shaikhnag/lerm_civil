from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math



class NaturalBuildingStone(models.Model):
    _name = "mechanical.natural.bulding.stone"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Natural Building Stone")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    eln_ref = fields.Many2one('lerm.eln',string="Eln")
    grade = fields.Many2one('lerm.grade.line',string="Grade",compute="_compute_grade_id",store=True)

    @api.depends('eln_ref')
    def _compute_grade_id(self):
        if self.eln_ref:
            self.grade = self.eln_ref.grade_id.id

   
    asgapw_name = fields.Char("Name",default="Apparent Specific Gravity, Apparent Porosity and Water Absorption")
    asgapw_visible = fields.Boolean("Visible",compute="_compute_visible")   

   

    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines_asgapw = fields.One2many('mechanical.asgapwline.line','parent_id',string="Parameter")

    average_asg = fields.Float(string="Apparent Specific Gravity ",compute="_compute_average_asg",digits=(12,3),store=True)

    @api.depends('child_lines_asgapw.apparent_specific')
    def _compute_average_asg(self):
        for record in self:
            asg = record.child_lines_asgapw.mapped('apparent_specific')
            if asg:
                record.average_asg = sum(asg) / len(asg)
            else:
                record.average_asg = 0.0

    average_ap = fields.Float(string="Apparent Porosity, %",compute="_compute_average_ap",digits=(12,3),store=True)

    @api.depends('child_lines_asgapw.apparent_porosity')
    def _compute_average_ap(self):
        for record in self:
            ap = record.child_lines_asgapw.mapped('apparent_porosity')
            if ap:
                record.average_ap = sum(ap) / len(ap)
            else:
                record.average_ap = 0.0


    average_wa = fields.Float(string="Water Absorption, %",compute="_compute_average_wa",digits=(12,3),store=True)

    @api.depends('child_lines_asgapw.water_absorption')
    def _compute_average_wa(self):
        for record in self:
            wa = record.child_lines_asgapw.mapped('water_absorption')
            if wa:
                record.average_wa = sum(wa) / len(wa)
            else:
                record.average_wa = 0.0



         ### Compute Visible
    @api.depends('sample_parameters')
    def _compute_visible(self):
        
        for record in self:

            record.asgapw_visible = False
          
            
            for sample in record.sample_parameters:
                print("Internal Ids",sample.internal_id)

               
                if sample.internal_id == "7c729ec4-ddf2-49ce-9839-715d30f9ccb5":
                    record.asgapw_visible = True

             
              




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
        record = super(NaturalBuildingStone, self).create(vals)
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
        record = self.env['mechanical.natural.bulding.stone'].browse(self.ids[0])
        field_values = {}
        for field_name, field in record._fields.items():
            field_value = record[field_name]
            field_values[field_name] = field_value

        return field_values


class AsgapwLine(models.Model):
    _name = "mechanical.asgapwline.line"
    parent_id = fields.Many2one('mechanical.natural.bulding.stone',string="Parent Id")
   
    sr_no = fields.Integer(string="Observations",readonly=True, copy=False, default=1)

    weight_of_saturated = fields.Float(string="Weight of Saturated Surface Dry Test piece, g (B)",digits=(12,2))
    quantity_of_water = fields.Float(string="Quantity of water added in 1000-ml jar containing the test piece, g (C)",digits=(12,2))
    weight_of_oven = fields.Float(string="Weight of oven-dry test piece (A)",digits=(12,2))
    apparent_specific = fields.Float(string="Apparent Specific Gravity A/(1000-C)" ,compute="_compute_apparent_specific",digits=(12,2))
    apparent_porosity = fields.Float(string="Apparent Porosity, % (B-A)/(1000-C)*100",digits=(12,2),compute="_compute_apparent_porosity")
    water_absorption = fields.Float(string="Water Absorption, % (B-A)/A*100",digits=(12,2),compute="_compute_water_absorption")


    @api.depends('weight_of_oven', 'quantity_of_water')
    def _compute_apparent_specific(self):
        for record in self:
            if record.quantity_of_water != 1000:
                record.apparent_specific = record.weight_of_oven / (1000 - record.quantity_of_water)
            else:
                record.apparent_specific = 0.0  # Avoid division by zero

    @api.depends('weight_of_saturated', 'weight_of_oven','quantity_of_water')
    def _compute_apparent_porosity(self):
        for record in self:
            if record.quantity_of_water != 1000:
                record.apparent_porosity = (
                    (record.weight_of_saturated - record.weight_of_oven) / 
                    (1000 - record.quantity_of_water)
                ) * 100
            else:
                record.apparent_porosity = 0.0  # Avoid division by zero

    @api.depends('weight_of_saturated', 'weight_of_oven')
    def _compute_water_absorption(self):
        for record in self:
            if record.weight_of_oven != 0:
                record.water_absorption = (
                    (record.weight_of_saturated - record.weight_of_oven) / 
                    record.weight_of_oven
                ) * 100
            else:
                record.water_absorption = 0.0  # Avoid division by zero
    

  
    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(AsgapwLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1