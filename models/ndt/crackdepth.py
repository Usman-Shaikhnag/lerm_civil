from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class CrackDepth(models.Model):
    _name = "ndt.crack.depth"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Crack Depth")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    temperature = fields.Float("Temperature °C")
    child_lines = fields.One2many('ndt.crack.depth.line','parent_id',string="Parameter")
    average = fields.Float(string='Average mm', digits=(16, 2), compute='_compute_average')
    # min_cd = fields.Float(string="Min mm")
    min_cd = fields.Float(string="Min mm", compute='_compute_min_cd', store=True)
    # max_cd = fields.Float(string="Max mm")
    max_cd = fields.Float(string="Max mm", compute='_compute_max_cd', store=True)
    structure = fields.Char("Structure")
    notes = fields.One2many('ndt.crack.depth.notes','parent_id',string="Notes")



   
        
    @api.depends('child_lines.cd')
    def _compute_average(self):
        for record in self:
            total_cd = sum(record.child_lines.mapped('cd'))
            num_records = len(record.child_lines)

            if num_records > 0:
                average = round(total_cd / num_records,2)
                record.average = average
            else:
                record.average = 0.0
    
    @api.depends('child_lines.cd')
    def _compute_min_cd(self):
        for record in self:
            min_cd_value = round(min(record.child_lines.mapped('cd'), default=0.0),2)
            record.min_cd = min_cd_value

    @api.depends('child_lines.cd')
    def _compute_max_cd(self):
        for record in self:
            max_cd_value = round(max(record.child_lines.mapped('cd'), default=0.0),2)
            record.max_cd = max_cd_value

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(CrackDepth, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record


class CrackDepthLine(models.Model):
    _name = "ndt.crack.depth.line"
    parent_id = fields.Many2one('ndt.crack.depth',string="Parent Id")
    member = fields.Char("Element Type")
    location = fields.Char("Location")
    tc = fields.Float("Tc")
    ts = fields.Float("Ts")
    distance = fields.Float("Distance")
    tc2 = fields.Float("Tc2",compute="_compute_square")
    ts2 = fields.Float("Ts2",compute="_compute_square")
    tc2_by_ts2 = fields.Float("Tc2/Ts2",compute="_compute_square")
    sqrt_Tc2_by_Ts2minus1 = fields.Float("√Tc2/Ts2-1",compute="_compute_square")
    cd = fields.Float("CD=√Tc2/Ts2-1 x 200",compute="_compute_square")

    @api.depends('tc','ts','tc2','ts2','tc2_by_ts2','distance')
    def _compute_square(self):
        for record in self:
            try:
                record.tc2 = record.tc**2
                record.ts2 = record.ts**2
                try:
                    record.tc2_by_ts2 = record.tc2/record.ts2
                except:
                    record.tc2_by_ts2 = 0 
                try:
                    record.sqrt_Tc2_by_Ts2minus1 = math.sqrt(record.tc2_by_ts2 - 1)
                except:
                    record.sqrt_Tc2_by_Ts2minus1 = 0
                try:
                    record.cd = record.sqrt_Tc2_by_Ts2minus1 * record.distance
                except:
                    record.cd = 0
            except:
                pass
                
                
class CrackDepthNotes(models.Model):
    _name = "ndt.crack.depth.notes"

    parent_id = fields.Many2one('ndt.crack.depth',string="Parent Id")
    notes = fields.Char("Notes")