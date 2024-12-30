from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class SplittingTensileStrengthConcrete(models.Model):
    _name = "split.tensile.strength.concrete"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Compressive Strength of Concrete Cube")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('split.tensile.strength.concrete.line','parent_id',string="Parameter")
    average_splite_tensile_strength = fields.Float(string="Average Compressive Strength in N/mm2",compute="_compute_average_splite_tensile_strength")


    @api.depends('child_lines.splite_tensile_strength')
    def _compute_average_splite_tensile_strength(self):
        for record in self:
            if record.child_lines:
                total_strength = sum(line.splite_tensile_strength for line in record.child_lines)
                record.average_splite_tensile_strength = total_strength / len(record.child_lines)
            else:
                record.average_splite_tensile_strength = 0.0



  
    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(SplittingTensileStrengthConcrete, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

class SplittingTensileStrengthConcreteLine(models.Model):
    _name = "split.tensile.strength.concrete.line"
    parent_id = fields.Many2one('split.tensile.strength.concrete', string="Parent Id")

    sr_no = fields.Integer(string="Sr.No.", readonly=True, copy=False, default=1)
    wt_of_cylinder = fields.Float(string="Weight of Cylinder in Kg")
    heigth = fields.Integer(string="Height in mm")
    diameter = fields.Integer(string="Diameter in mm")
    breaking_load = fields.Float(string="Breaking Load in KN")
    splite_tensile_strength = fields.Float(string="Split Tensile Strength in (N/mm2)", compute="_compute_split_tensile_strength")



    @api.depends('heigth', 'diameter', 'breaking_load')
    def _compute_split_tensile_strength(self):
        for record in self:
            if record.heigth and record.diameter and record.breaking_load:
                record.splite_tensile_strength = (2 * record.breaking_load) / (3.14 * record.heigth * record.diameter) * 1000
            else:
                record.splite_tensile_strength = 0.0



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(SplittingTensileStrengthConcreteLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1


  


   