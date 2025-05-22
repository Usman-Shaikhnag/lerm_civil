from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class CompressiveStrengthConcreteCube(models.Model):
    _name = "mechanical.compressive.strength.concrete.cube"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Compressive Strength of Concrete Cube")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.compressive.strength.concrete.cube.line','parent_id',string="Parameter")
    average_strength = fields.Float(string="Average Compressive Strength in N/mm2", compute="_compute_average_strength",digits=(12,4))


    @api.depends('child_lines.compressive_strength')
    def _compute_average_strength(self):
        for record in self:
            total_strength = sum(line.compressive_strength for line in record.child_lines)
            record.average_strength = total_strength / len(record.child_lines) if len(record.child_lines) > 0 else 0.0



    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(CompressiveStrengthConcreteCube, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

class CompressiveStrengthConcreteCubeLine(models.Model):
    _name = "mechanical.compressive.strength.concrete.cube.line"
    parent_id = fields.Many2one('mechanical.compressive.strength.concrete.cube',string="Parent Id")

    sr_no = fields.Integer(string="Sr.No.",readonly=True, copy=False, default=1)
    length = fields.Float(string="Length (mm)")
    width = fields.Float(string="Width (mm)")
    area = fields.Float(string="Area (mm²)",compute="_compute_area" ,digits=(12,4))
    id_mark = fields.Integer(string="ID Mark")
    wt_sample = fields.Float(string="Weight of Sample in kgs")
    crushing_load = fields.Float(string="Crushing Load in kN")
    compressive_strength = fields.Float(string="Compressive Strength N/mm²",compute="_compute_compressive_strength" ,digits=(12,4))
   


    @api.depends('length', 'width')
    def _compute_area(self):
        for record in self:
            record.area = round((record.length * record.width) , 4)


    @api.depends('crushing_load', 'area')
    def _compute_compressive_strength(self):
        for record in self:
            if record.area != 0:
                record.compressive_strength = record.crushing_load / record.area * 1000
            else:
                record.compressive_strength = 0.0


    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(CompressiveStrengthConcreteCubeLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1


