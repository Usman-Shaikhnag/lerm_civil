from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math


class WaterAbsorptionBricks(models.Model):
    _name = "mechanical.water.absorption.bricks"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Water Absorption")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.water.absorption.bricks.line','parent_id',string="Parameter")
   


  

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(WaterAbsorptionBricks, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

class WaterAbsorptionBricksLine(models.Model):
    _name = "mechanical.water.absorption.bricks.line"
    parent_id = fields.Many2one('mechanical.water.absorption.bricks',string="Parent Id")
   
    sr_no = fields.Integer(string="Sample No", readonly=True, copy=False, default=1)
    initial_wt = fields.Float(string="Initial wt ater 24 hr emersion water")
    final_wt = fields.Float(string="Final wt after 24 hr oven")
    water_absorption = fields.Float(string="Water Absorption %", compute="_compute_water_absorption")


    @api.depends('initial_wt' , 'final_wt')
    def _compute_water_absorption(self):
        for record in self:
            if record.final_wt != 0:
                record.water_absorption = (record.initial_wt - record.final_wt) / record.final_wt * 100
            else:
                record.water_absorption = 0






    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(WaterAbsorptionBricksLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1




class CompressiveStrengthBrick(models.Model):
    _name = "mechanical.compressive.strength.brick"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Water Absorption")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.compressive.strength.brick.line','parent_id',string="Parameter")
   


  

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(CompressiveStrengthBrick, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

class CompressiveStrengthBrickLine(models.Model):
    _name = "mechanical.compressive.strength.brick.line"
    parent_id = fields.Many2one('mechanical.compressive.strength.brick',string="Parent Id")
   
    sr_no = fields.Integer(string="Sample No", readonly=True, copy=False, default=1)
    length = fields.Float(string="Length mm")
    width = fields.Float(string="Width mm")
    area = fields.Float(string="Area (mm²)", digits=(12,4),compute="_compute_area")
    load = fields.Float(string=" Load in, KN", digits=(12,1))
    compressive_strength = fields.Float(string="Compressive strength MPa",compute="_compute_compressive_strength")


    @api.depends('length', 'width')
    def _compute_area(self):
        for record in self:
            record.area = record.length * record.width


    @api.depends('load' , 'area')
    def _compute_compressive_strength(self):
        for record in self:
            if record.area != 0:
                record.compressive_stregnth = record.load / record.area * 1000
            else:
                record.compressive_stregnth = 0






    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(CompressiveStrengthBrickLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1

   
   