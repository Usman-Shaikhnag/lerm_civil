from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class SplitTensileStrength(models.Model):
    _name = "mechanical.split.tensile.strength"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Split Tensile Strength")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    # sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    # eln_ref = fields.Many2one('lerm.eln',string="Eln")
    child_lines = fields.One2many('mechanical.split.tensile.strength.line','parent_id',string="Parameter")

    average = fields.Float(string="Average Split Tensile Strength in (N/mm2)",compute="_compute_average")

    @api.onchange('child_lines.split_tensile')
    def _compute_average(self):
        for record in self:
            self.average = sum(record.child_lines.mapped('split_tensile'))/3

   



    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(SplitTensileStrength, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

class CarbonationnLine(models.Model):
    _name = "mechanical.split.tensile.strength.line"
    parent_id = fields.Many2one('mechanical.split.tensile.strength',string="Parent Id")
    
    weight = fields.Float(string='Weight of Cylinder in Kg')
    height = fields.Integer(string="Height in mm")
    diameter = fields.Integer(string="Diameter in mm")
    breaking_load = fields.Float(string="Breaking Load in Kn")
    split_tensile = fields.Float(string="Split Tensile Strength in (N/mm2)", compute="_compute_split_tensile")


    @api.depends('height','diameter','breaking_load')
    def _compute_split_tensile(self):
        for record in self:
            try:
                record.split_tensile = ((2*record.breaking_load)/(3.14*record.height*record.diameter))*1000
            except ZeroDivisionError:
                record.split_tensile = 0


                


