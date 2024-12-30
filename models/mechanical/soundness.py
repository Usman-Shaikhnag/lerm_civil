from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import math

class Soundness(models.Model):
    _name = "mechanical.soundness"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Soundness")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.soundness.line','parent_id',string="Parameter")
    total = fields.Integer(string="Total",compute="_compute_total")
    soundness = fields.Float(string="Soundness",compute="_compute_soundness")
    

    @api.model
    def create(self, vals):
        record = super(Soundness, self).create(vals)
        record.parameter_id.write({'model_id': record.id})
        return record

    @api.depends('child_lines.weight_before_test')
    def _compute_total(self):
        for record in self:
            record.total = sum(record.child_lines.mapped('weight_before_test'))
    

    @api.depends('child_lines.cumulative_loss_percent')
    def _compute_soundness(self):
        for record in self:
            record.soundness = sum(record.child_lines.mapped('cumulative_loss_percent'))

    

    @api.onchange('total')
    def _onchange_total(self):
        for line in self.child_lines:
            line._compute_grading()
            line._compute_cumulative()

class SieveAnalysisLine(models.Model):
    _name = "mechanical.soundness.line"
    parent_id = fields.Many2one('mechanical.soundness', string="Parent Id")
    
    sieve_size_passing = fields.Char(string="Sieve Size Passing")
    sieve_size_retained = fields.Char(string="Sieve Size Retained")
    weight_before_test = fields.Float(string="Weight of test fraction before test in gm.")
    weight_after_test = fields.Float(string="Weight of test feaction Passing Finer Sieve After test")
    grading_original_sample = fields.Float(string="Grading of Original sample in %", compute="_compute_grading")
    passing_percent = fields.Float(string="Percentage Passing Finer Sieve After test (Percentage Loss)",compute="_compute_passing_percent")
    cumulative_loss_percent = fields.Float(string="Commulative percentage Loss",compute="_compute_cumulative")
    
    @api.depends('parent_id.total','weight_before_test')
    def _compute_grading(self):
        for record in self:
            try:
                record.grading_original_sample = (record.weight_before_test/self.parent_id.total)*100
            except ZeroDivisionError:
                record.grading_original_sample = 0

    @api.depends('weight_before_test','weight_after_test')
    def _compute_passing_percent(self):
        for record in self:
            try:
                record.passing_percent = (record.weight_after_test / record.weight_before_test)*100
            except:
                record.passing_percent = 0

    @api.depends('weight_after_test', 'parent_id.total')
    def _compute_cumulative(self):
        for record in self:
            try:
                record.cumulative_loss_percent = (record.weight_after_test / record.parent_id.total) * 100
            except:
                record.cumulative_loss_percent = 0

