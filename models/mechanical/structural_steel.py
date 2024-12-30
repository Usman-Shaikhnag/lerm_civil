from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class SturacturalSteel(models.Model):
    _name = "mechanical.structural.steel"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="STRUCTURAL STEEL")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.structural.steel.line','parent_id',string="Parameter")
  
    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(SturacturalSteel, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

class SturacturalSteelLine(models.Model):
    _name = "mechanical.structural.steel.line"
    parent_id = fields.Many2one('mechanical.structural.steel',string="Parent Id")
    sr_no = fields.Integer(string="Sr No", readonly=True, copy=False, default=1)
    width = fields.Float(string="Width , mm",digits=(16, 1))
    thickness = fields.Float(string="Thickness , mm")
    area = fields.Float(string="AREA, mm2", compute="_compute_area")
    gauge_length = fields.Integer(string="GAUGE LENGTH, mm", compute="_compute_gauge_length")
    final_length = fields.Float(string="FINAL LENGTH, mm")
    proof_yield_load = fields.Float(string="0.2% proof Load / Yield Load, KN")
    ultimate_load = fields.Float(string="ULTIMATE LOAD, KN")
    proof_yield_n = fields.Float(string="0.2% proof Load / Yield Stress N/mm2", compute="_compute_proof_yield_n",digits=(12,1))
    ult_tens_strength = fields.Float(string="ULTIMATE TENSILE strength, N/mm2",compute="_compute_ult_tens_strength",digits=(12,1))
    elongation = fields.Float(string="ELONGATION %" , compute="_compute_elongation" , digits=(12,1))
    bend_test = fields.Selection([('satisfactory','Satisfactory'),('unsatisfactory','Unsatisfactory')],string="BEND TEST")
    fracture = fields.Char(string="FRACTURE",default="W.G.L")


    @api.depends('width', 'thickness')
    def _compute_area(self):
        for record in self:
            record.area = record.width * record.thickness

    
    
    @api.depends('area')
    def _compute_gauge_length(self):
        for record in self:
            record.gauge_length = 5.65 * math.sqrt(record.area)

    @api.depends('proof_yield_load', 'area')
    def _compute_proof_yield_n(self):
        for record in self:
            if record.area != 0:
                record.proof_yield_n = (record.proof_yield_load / record.area) * 1000
            else:
                record.proof_yield_n = 0


    @api.depends('ultimate_load', 'area')
    def _compute_ult_tens_strength(self):
        for record in self:
            if record.area != 0:
                record.ult_tens_strength = (record.ultimate_load / record.area) * 1000
            else:
                record.ult_tens_strength = 0


    @api.depends('final_length' , 'gauge_length')
    def _compute_elongation(self):
        for record in self:
            if record.gauge_length != 0:
                record.elongation = (record.final_length - record.gauge_length) / record.gauge_length *100
            else:
                record.elongation = 0


    


   

    
    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(SturacturalSteelLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1