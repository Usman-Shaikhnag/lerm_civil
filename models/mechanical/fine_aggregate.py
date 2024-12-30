from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class SpecificAndWater(models.Model):
    _name = "specific.and.water.fine.aggregate"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Specific Gravity & Water Absorption")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('specific.and.water.fine.aggregate.line','parent_id',string="Parameter")


    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(SpecificAndWater, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

    

class SpecificAndWaterLine(models.Model):
    _name = "specific.and.water.fine.aggregate.line"
    parent_id = fields.Many2one('specific.and.water.fine.aggregate',string="Parent Id")

    sample_no = fields.Integer(string="Sr.No.",readonly=True, copy=False, default=1)
    wt_of_empty_pycnometer = fields.Integer(string="Weight of empty Pycnometer in gms")
    wt_of_pycnometer = fields.Integer(string="Weight of Pycnometer with full of water in gms")
    wt_of_pycnometer_surface_dry = fields.Integer(string="Weight of Pycnometer + Saturated surface dry Aggregate in gms")
    wt_of_pycnometer_surface_dry_water = fields.Integer(string="Weight of Pycnometer + Saturated surface dry Aggregate + Water in gms")
    wt_of_saturated_surface_dry = fields.Integer(string="Weight of Saturated surface dry Aggregate in gms",compute='_compute_wt_of_saturated_surface_dry')
    wt_of_oven_dried = fields.Float(string="Weight of Oven dried Aggregate in gms")
    volume_of_water = fields.Integer(string="Volume of water displaced by saturated surface dry aggregate",compute="_compute_volume_of_water")
    specific_gravity = fields.Float(string="SPECIFIC GRAVITY", compute="_compute_specific_gravity")
    water_absorption = fields.Float(string="Water Absorption %",compute="_compute_water_absorption")



    @api.depends('wt_of_pycnometer_surface_dry', 'wt_of_empty_pycnometer')
    def _compute_wt_of_saturated_surface_dry(self):
        for line in self:
            line.wt_of_saturated_surface_dry = line.wt_of_pycnometer_surface_dry - line.wt_of_empty_pycnometer


    @api.depends('wt_of_pycnometer', 'wt_of_empty_pycnometer', 'wt_of_pycnometer_surface_dry', 'wt_of_pycnometer_surface_dry_water')
    def _compute_volume_of_water(self):
        for line in self:
            volume_of_water = (line.wt_of_pycnometer - line.wt_of_empty_pycnometer) - (line.wt_of_pycnometer_surface_dry_water - line.wt_of_pycnometer_surface_dry)
            line.volume_of_water = volume_of_water

    @api.depends('wt_of_oven_dried', 'volume_of_water')
    def _compute_specific_gravity(self):
        for line in self:
            if line.volume_of_water:
                line.specific_gravity = line.wt_of_oven_dried / line.volume_of_water
            else:
                line.specific_gravity = 0.0


    @api.depends('wt_of_empty_pycnometer', 'wt_of_oven_dried')
    def _compute_water_absorption(self):
        for line in self:
            if line.wt_of_oven_dried:
                line.water_absorption = ((line.wt_of_empty_pycnometer - line.wt_of_oven_dried) / line.wt_of_oven_dried) * 100
            else:
                line.water_absorption = 0.0


  


   
   

    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('sample_no'):
            existing_records = self.search([('sample_no', '=', vals['sample_no'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sample_no'))
                vals['sample_no'] = max_serial_no + 1

        return super(SpecificAndWaterLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sample_no = index + 1

