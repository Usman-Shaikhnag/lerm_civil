from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math


class LooseBulkDensity(models.Model):
    _name = "loose.bulk.density"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Loose Bulk Density (LBD)")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('loose.bulk.density.line','parent_id',string="Parameter")
   


  

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(LooseBulkDensity, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

class LooseBulkDensityLine(models.Model):
    _name = "loose.bulk.density.line"
    parent_id = fields.Many2one('loose.bulk.density',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr.No.", readonly=True, copy=False, default=1)
    weight_empty_bucket = fields.Float(string="Weight of Empty Bucket in kg")
    volume_of_bucket = fields.Float(string="Volume of Bucket in cubic meter")
    sample_plus_bucket = fields.Float(string="[Sample Weight + Bucket  Weight] in kg")
    sample_weight = fields.Float(string="Sample Weight in kg",compute="_compute_sample_weight")
    loose_bulk_density = fields.Float(string="Loose Bulk Density in kg per cubic meter",compute="_compute_loose_bulk_density")


    @api.depends('sample_plus_bucket', 'weight_empty_bucket')
    def _compute_sample_weight(self):
        for record in self:
            record.sample_weight = record.sample_plus_bucket - record.weight_empty_bucket

    

    @api.depends('sample_weight', 'volume_of_bucket')
    def _compute_loose_bulk_density(self):
        for record in self:
            if record.volume_of_bucket:
                record.loose_bulk_density = record.sample_weight / record.volume_of_bucket
            else:
                record.loose_bulk_density = 0.0


    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(LooseBulkDensityLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1





class RoddedBulkDensity(models.Model):
    _name = "rodded.bulk.density"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Rodded Bulk Density (RBD)")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('rodded.bulk.density.line','parent_id',string="Parameter")
   


  

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(RoddedBulkDensity, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

class RoddedBulkDensityLine(models.Model):
    _name = "rodded.bulk.density.line"
    parent_id = fields.Many2one('rodded.bulk.density',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr.No.", readonly=True, copy=False, default=1)
    weight_empty_bucket = fields.Float(string="Weight of Empty Bucket in kg")
    volume_of_bucket = fields.Float(string="Volume of Bucket in cubic meter")
    sample_plus_bucket = fields.Float(string="[Sample Weight + Bucket  Weight] in kg")
    sample_weight = fields.Float(string="Sample Weight in kg",compute="_compute_sample_weight")
    rodded_bulk_density = fields.Float(string="Loose Bulk Density in kg per cubic meter",compute="_compute_roddede_bulk_density")


    @api.depends('sample_plus_bucket', 'weight_empty_bucket')
    def _compute_sample_weight(self):
        for record in self:
            record.sample_weight = record.sample_plus_bucket - record.weight_empty_bucket

    

    @api.depends('sample_weight', 'volume_of_bucket')
    def _compute_roddede_bulk_density(self):
        for record in self:
            if record.volume_of_bucket:
                record.rodded_bulk_density = record.sample_weight / record.volume_of_bucket
            else:
                record.rodded_bulk_density = 0.0



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(RoddedBulkDensityLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1