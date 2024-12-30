from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class Coupler(models.Model):
    _name = "mechanical.coupler"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Coupler")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")

    outer_diameter = fields.Integer(string="Outer Diameter")
    nominal_cross_section = fields.Float(string="Nominal Cross Sectional Area, mm2")
    gauge_length = fields.Float(string="Gauge Length L, mm")
    gauge_length_max_force = fields.Float(string="Gauge Length at Maximum Force, mm")
    ultimate_tensile_load = fields.Float(string="Ultimate Tensile Load, KN")
    ultimate_tensile_strength = fields.Float(string="Ultimate Tensile Strength, N/mm2")
    total_elongation = fields.Float(string="Total Elongation at maximum force(%)")
    distance_fracture = fields.Float(string="Distance of fracture From center of Coupler")
    failure_location = fields.Char(string="Location of Failure")
    result = fields.Selection([
        ('satisfactory', 'Satisfactory'),
        ('not_satisfactory', 'Not Satisfactory')], string='Result')


    

    @api.onchange('outer_diameter')
    def _compute_nominal_cross_section(self):
        try:
            self.nominal_cross_section = (3.14*self.outer_diameter*self.outer_diameter)/4
            self.gauge_length = self.outer_diameter*10 + 50
        except ZeroDivisionError:
            self.nominal_cross_section = 0
            self.gauge_length = 0


    @api.onchange('ultimate_tensile_load','nominal_cross_section')
    def _compute_ultimate_tensile_strength(self):
        try:
            self.ultimate_tensile_strength = (self.ultimate_tensile_load/self.nominal_cross_section)*1000
        except ZeroDivisionError:
            self.ultimate_tensile_strength = 0

    @api.onchange('gauge_length_max_force','gauge_length')
    def _compute_total_elongation(self):
        try:
            self.total_elongation = ((self.gauge_length_max_force - self.gauge_length)/self.gauge_length)*100
        except ZeroDivisionError:
            self.total_elongation = 0

    def open_eln_page(self):
        # import wdb; wdb.set_trace()

        return {
                'view_mode': 'form',
                'res_model': "lerm.eln",
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.eln_ref.id,
                
            }        


    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(Coupler, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record



                


