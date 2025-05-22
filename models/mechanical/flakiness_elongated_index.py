from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math


class FlakinessElongationIndex(models.Model):
    _name = "mechanical.flakiness.elongation.index"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Flakiness & Elongation Index")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.flakiness.elongation.index.line','parent_id',string="Parameter")
    wt_retained_total = fields.Float(string="Wt Retained Total",compute="_compute_wt_retained_total")
    elongated_retain_total = fields.Float(string="Elongated Retained Total",compute="_compute_elongated_retain")
    flaky_passing_total = fields.Float(string="Flaky Passing Total",compute="_compute_flaky_passing")
    aggregate_elongation = fields.Float(string="aggregate Elongation Value in %",compute="_compute_aggregate_elongation")
    aggregate_flakiness = fields.Float(string="aggregate Flakiness Value in %",compute="_compute_aggregate_flakiness")
    combine_elongation_flakiness = fields.Float(string="Combine Elongation & Flakiness Value in %",compute="_compute_combine_elongation_flakiness")


    @api.depends('child_lines.wt_retained')
    def _compute_wt_retained_total(self):
        for record in self:
            record.wt_retained_total = sum(record.child_lines.mapped('wt_retained'))

    @api.depends('child_lines.elongated_retain')
    def _compute_elongated_retain(self):
        for record in self:
            record.elongated_retain_total = sum(record.child_lines.mapped('elongated_retain'))

    @api.depends('child_lines.flaky_passing')
    def _compute_flaky_passing(self):
        for record in self:
            record.flaky_passing_total = sum(record.child_lines.mapped('flaky_passing'))

    @api.depends('wt_retained_total','elongated_retain_total')
    def _compute_aggregate_elongation(self):
        for record in self:
            if record.elongated_retain_total != 0:
                record.aggregate_elongation = record.elongated_retain_total / record.wt_retained_total * 100
            else:
                record.aggregate_elongation = 0.0


    @api.depends('wt_retained_total','flaky_passing_total')
    def _compute_aggregate_flakiness(self):
        for record in self:
            if record.flaky_passing_total != 0:
                record.aggregate_flakiness = record.flaky_passing_total / record.wt_retained_total * 100
            else:
                record.aggregate_flakiness = 0.0

    @api.depends('aggregate_elongation','aggregate_flakiness')
    def _compute_combine_elongation_flakiness(self):
        for record in self:
            if record.aggregate_flakiness != 0:
                record.combine_elongation_flakiness = record.aggregate_elongation + record.aggregate_flakiness
            else:
                record.combine_elongation_flakiness = 0.0




    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(FlakinessElongationIndex, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record


class FlakinessElongationIndexLine(models.Model):
    _name = "mechanical.flakiness.elongation.index.line"
    parent_id = fields.Many2one('mechanical.flakiness.elongation.index',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr No", readonly=True, copy=False, default=1)
    sieve_size = fields.Char(string="I.S Sieve Size")
    wt_retained = fields.Integer(string="Wt Retained (in gms)")
    elongated_retain = fields.Float(string="Elongated Retained (in gms)")
    flaky_passing = fields.Float(string="Flaky Passing (in gms)")
    

    

    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(FlakinessElongationIndexLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1