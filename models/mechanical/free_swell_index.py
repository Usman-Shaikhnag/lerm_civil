from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class FreeSwellIndex(models.Model):
    _name = "mechanical.free.swell.index"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Free Swell Index")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.soil.free.swell.index.line','parent_id',string="Parameter")

   

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(FreeSwellIndex, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record



class TensileSplittingStrengthLine(models.Model):
    _name = "mechanical.soil.free.swell.index.line"
    parent_id = fields.Many2one('mechanical.free.swell.index',string="Parent Id")

    wt_sample = fields.Float(string="Mass of wet sample")
    dry_sample = fields.Float(string="Volume of dry sample in cc")
    v_sample_kerosin = fields.Float(string="Volume of sample after immersing in kerosin for 24 Hrs. in cc, V1")
    v_sample_water = fields.Float(string="Volume of sample after immersing in water for 24 Hrs. in cc, V2")
    increase_volume = fields.Float(string="Increase in Volume, (V2-V1) in cc", compute="_compute_volume")
    fsi = fields.Float(string="% FSI = (V2-V1)/V1 x 100", compute="_compute_fsi")


    @api.depends('v_sample_water', 'v_sample_kerosin')
    def _compute_volume(self):
        for record in self:
            record.increase_volume = record.v_sample_water - record.v_sample_kerosin


    @api.depends('v_sample_water', 'v_sample_kerosin')
    def _compute_volume(self):
        for record in self:
            record.increase_volume = record.v_sample_water - record.v_sample_kerosin

    @api.depends('increase_volume', 'v_sample_kerosin')
    def _compute_fsi(self):
        for record in self:
            if record.v_sample_kerosin != 0:
                record.fsi = (record.increase_volume / record.v_sample_kerosin) * 100
            else:
                record.fsi = 0.0




    


   