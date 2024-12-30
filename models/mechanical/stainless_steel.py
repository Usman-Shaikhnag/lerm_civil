from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math


class StainlessSteel(models.Model):
    _name = "mechanical.stainless.steel"
    _inherit = "lerm.eln"
   
    
    Id_no = fields.Char("ID No")
    grade = fields.Many2one('lerm.grade.line',string="Grade",compute="_compute_grade_id")
    diameter = fields.Float(string="Dia. in mm")
    length = fields.Float(string="Length in mm",digits=(10, 3))
    area = fields.Float(string="Area",compute="_compute_area")
    weight = fields.Float(string="Weight, in kg",digits=(10, 3))
    weight_per_meter = fields.Float(string="Weight per meter, kg/m",compute="_compute_weight_per_meter",store=True)
    gauge_length = fields.Integer(string="Gauge Length",compute="_compute_gauge_length",store=True)
    final_length = fields.Float(string="Final Length, mm")
    percent_elongation = fields.Float(string="% Elongation",compute="_compute_elongation_percent")
    yeild_load = fields.Float(string="0.2% Proof Load / Yield Load, KN")
    ultimate_load = fields.Float(string="Ultimate Load, Kn")
    proof_yeid_stress = fields.Float(string="0.2% Proof Stress",compute="_compute_proof_yeid_stress",store=True)
    ult_tens_strgth = fields.Float(string="Ultimate Tensile Strength, N/mm2",compute="_compute_ult_tens_strgth")
    fracture = fields.Char("Fracture (Within Gauge Length)",default="W.G.L")
    eln_ref = fields.Many2one('lerm.eln',string="ELN")
    weight_meter_result = fields.Char("",compute="_compute_weight_meter_result")
    # requirment = fields.Char(string="Requirment")
    
    bend_test = fields.Selection([
        ('satisfactory', 'Satisfactory'),
        ('non-satisfactory', 'Non-Satisfactory')],"Bend Test")
    
    re_bend_test = fields.Selection([
        ('satisfactory', 'Satisfactory'),
        ('non-satisfactory', 'Non-Satisfactory')],"Re-Bend Test")

    eln_ref = fields.Many2one('lerm.eln',string="Eln ref")

    @api.depends('weight_per_meter','diameter')
    def _compute_weight_meter_result(self):
        for record in self:
            if record.diameter == 6 and record.weight_per_meter <= 0.20646 and record.weight_per_meter >= 0.23754:
                record.weight_meter_result = "TRUE"
            elif record.diameter == 8 and record.weight_per_meter <= 0.36735 and record.weight_per_meter >= 0.42265:
                record.weight_meter_result = "TRUE"
            elif record.diameter == 10 and record.weight_per_meter <= 0.57381 and record.weight_per_meter >= 0.66019:
                print("w/m",record.weight_per_meter)
                record.weight_meter_result = "TRUE"
            elif record.diameter == 12 and record.weight_per_meter <= 0.8436 and record.weight_per_meter >= 0.9324:
                record.weight_meter_result = "TRUE"
            elif record.diameter == 16 and record.weight_per_meter <= 1.501 and record.weight_per_meter >= 1.659:
                record.weight_meter_result = "TRUE"
            else:
                record.weight_meter_result = "FALSE"



            



    @api.depends('weight', 'length')
    def _compute_weight_per_meter(self):
        for record in self:
            if record.length != 0:
                record.weight_per_meter = record.weight / record.length
            else:
                record.weight_per_meter = 0.0
    
    @api.depends('length','weight')
    def _compute_area(self):
        for record in self:
            if record.length != 0:
                record.area = record.weight/record.length/0.00774
            else:
                record.area = 0


    @api.depends('gauge_length', 'final_length')
    def _compute_elongation_percent(self):
        for record in self:
            if record.gauge_length != 0:  # Use record.gauge_length instead of gauge_length
                record.percent_elongation = (record.final_length - record.gauge_length) / record.gauge_length * 100
            else:
                record.percent_elongation = 0.0


    @api.depends('area')
    def _compute_gauge_length(self):
        for record in self:
            record.gauge_length = round(5.65 * math.sqrt(record.area))


    @api.depends('yeild_load','area')
    def _compute_proof_yeid_stress(self):
        for record in self:
            if record.area != 0:
                record.proof_yeid_stress = record.yeild_load / record.area * 1000
            else:
                record.proof_yeid_stress = 0.0

    @api.depends('ultimate_load')
    def _compute_ult_tens_strgth(self):
        for record in self:
            if record.area != 0:
                record.ult_tens_strgth = record.ultimate_load / record.area * 1000
            else:
                record.ult_tens_strgth = 0.0

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(StainlessSteel, self).create(vals)
        # record.get_all_fields()
        record.eln_ref.write({'model_id':record.id})
        return record


    @api.depends('eln_ref')
    def _compute_grade_id(self):
        if self.eln_ref:
            self.grade = self.eln_ref.grade_id.id

    


  
          
   