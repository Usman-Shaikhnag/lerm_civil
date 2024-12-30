from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math


class FieldDensitySandReplacement(models.Model):
    _name = "mechanical.field.density.sand.replacement"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Field Density by Sand Replacement method")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")

    mmd = fields.Float(string="MMD gm/cc", default=1.85)
    omc = fields.Float(string="OMC %", default=11.77)

    determination_no = fields.Integer(string="Determination No")
    wt_of_sample = fields.Integer(string="Weight of sample gm")
    water_of_sample = fields.Integer(string="Water content of sample RMM")
    wt_of_before_cylinder = fields.Integer(string="Weight of sand + Cylinder before pouring gm")
    wt_of_after_cylinder = fields.Integer(string="Weight of sand + Cylinder after pouring gm")
    wt_of_sand_cone = fields.Integer(string="Weight of sand in cone gm")
    wt_of_sand_hole = fields.Integer(string="Weight of sand in hole gm", compute="_compute_sand_hole")
    density_of_sand = fields.Float(string="Density of sand gm/cc")
    volume_of_hole = fields.Integer(string="Volume of hole cc", compute="_compute_volume_of_hole")
    bulk_density_of_sample = fields.Float(string="Bulk Density of sample gm/cc",compute="_compute_bulk_density")
    dry_density_of_sample = fields.Float(string="Dry Density of sample",compute="_compute_dry_density")
    degree_of_compaction = fields.Float(string="Degree of Compaction %",compute="_compute_degree_of_compaction")


    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(FieldDensitySandReplacement, self).create(vals)
        return record
    
    @api.depends('wt_of_before_cylinder','wt_of_after_cylinder','wt_of_sand_cone')
    def _compute_sand_hole(self):
        for record in self:
            record.wt_of_sand_hole = record.wt_of_before_cylinder - record.wt_of_after_cylinder - record.wt_of_sand_cone


    @api.depends('wt_of_sand_cone','density_of_sand')
    def _compute_volume_of_hole(self):
        for record in self:
            if record.density_of_sand != 0:  # Avoid division by zero
                record.volume_of_hole = record.wt_of_sand_hole / record.density_of_sand
            else:
                record.volume_of_hole = 0.0

    @api.depends('wt_of_sample','volume_of_hole')
    def _compute_bulk_density(self):
        for record in self:
            if record.volume_of_hole != 0:  # Avoid division by zero
                record.bulk_density_of_sample = record.wt_of_sample / record.volume_of_hole
            else:
                record.bulk_density_of_sample = 0.0

    @api.depends('bulk_density_of_sample', 'water_of_sample')
    def _compute_dry_density(self):
        for record in self:
           if record.water_of_sample + 100 != 0:  # Avoid division by zero
                record.dry_density_of_sample = (100 * record.bulk_density_of_sample) / (record.water_of_sample + 100)
           else:
                record.dry_density_of_sample = 0.0

    @api.depends('dry_density_of_sample', 'mmd')
    def _compute_degree_of_compaction(self):
        for record in self:
            if record.mmd != 0:  # Avoid division by zero
                record.degree_of_compaction = (record.dry_density_of_sample / record.mmd) * 100
            else:
                record.degree_of_compaction = 0.0



