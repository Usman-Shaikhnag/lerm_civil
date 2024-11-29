from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math



class Tile(models.Model):
    _name = "mechanical.tile"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="TILE")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    eln_ref = fields.Many2one('lerm.eln',string="Eln")
    grade = fields.Many2one('lerm.grade.line',string="Grade",compute="_compute_grade_id",store=True)

    @api.depends('eln_ref')
    def _compute_grade_id(self):
        if self.eln_ref:
            self.grade = self.eln_ref.grade_id.id


    # Dimension

    dimension_name1 = fields.Char("Name",default="Dimension")
    dimension_visible = fields.Boolean("Dimension Visible",compute="_compute_visible")   

    # name = fields.Char("Name",default="DIMENSION")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.dimension.tile.line','parent_id',string="Parameter")
    average_length = fields.Float(string="Average Length", compute="_compute_average_length",digits=(16,2))
    average_width = fields.Float(string="Average Width", compute="_compute_average_width",digits=(16,2))
    # plan_area = fields.Float(string="Plan Area", compute="_compute_plan_area", digits=(16, 1))
    average_thickness = fields.Float(string="Average Thickness",compute="_compute_average_thickness", digits=(16, 2))


    @api.depends('child_lines.length1', 'child_lines.length2', 'child_lines.length3', 'child_lines.length4')
    def _compute_average_length(self):
        for record in self:
            if record.child_lines:
                # Calculate the average length per child line
                total = sum((line.length1 + line.length2 + line.length3 + line.length4) / 4 for line in record.child_lines)
                record.average_length = total / len(record.child_lines)  # Average across all child lines
            else:
                record.average_length = 0.0

    @api.depends('child_lines.width1', 'child_lines.width2', 'child_lines.width3', 'child_lines.width4')
    def _compute_average_width(self):
        for record in self:
            if record.child_lines:
                # Calculate the average length per child line
                total = sum((line.width1 + line.width2 + line.width3 + line.width4) / 4 for line in record.child_lines)
                record.average_width = total / len(record.child_lines)  # Average across all child lines
            else:
                record.average_width = 0.0

    @api.depends('child_lines.thickness1', 'child_lines.thickness2', 'child_lines.thickness3', 'child_lines.thickness4','child_lines.thickness5','child_lines.thickness6')
    def _compute_average_thickness(self):
        for record in self:
            if record.child_lines:
                # Calculate the average length per child line
                total = sum((line.thickness1 + line.thickness2 + line.thickness3 + line.thickness4 +line.thickness5 + line.thickness6) / 6 for line in record.child_lines)
                record.average_thickness = total / len(record.child_lines)  # Average across all child lines
            else:
                record.average_thickness = 0.0


    deviation_length = fields.Float(string="Deviation in Length", compute="_compute_deviation_length",digits=(16,2))
    deviation_width = fields.Float(string="Deviation in Width", compute="_compute_deviation_width",digits=(16,2))
    deviation_length_width = fields.Float(string="Deviation in Length & Width", compute="_compute_deviation_length_width",digits=(16,2))
    deviation_thickness = fields.Float(string="Deviation in Thickness", compute="_compute_deviation_thickness",digits=(16,2))

    @api.depends('average_length')
    def _compute_deviation_length(self):
        for record in self:
            if record.average_length:  # Avoid division by zero
                record.deviation_length = ((record.average_length - 600) / 600) * 100
            else:
                record.deviation_length = 0.0

    @api.depends('average_width')
    def _compute_deviation_width(self):
        for record in self:
            if record.average_width:  # Avoid division by zero
                record.deviation_width = ((record.average_width - 600) / 600) * 100
            else:
                record.deviation_width = 0.0

    @api.depends('deviation_length','deviation_width')
    def _compute_deviation_length_width(self):
        for record in self:
            if record.deviation_length and record.deviation_width:  # Avoid division by zero
                record.deviation_length_width = (record.deviation_length + record.deviation_width) / 2
            else:
                record.deviation_length_width = 0.0

    @api.depends('average_thickness')
    def _compute_deviation_thickness(self):
        for record in self:
            if record.average_thickness:  # Avoid division by zero
                record.deviation_thickness = ((record.average_thickness - 8) / 8) * 100
            else:
                record.deviation_thickness = 0.0


     # Straightness

    straightness_name = fields.Char("Name",default="Straightness")
    straightness_visible = fields.Boolean("Straightness Visible",compute="_compute_visible")   

    sample_size = fields.Integer(string="Sample Size")

    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines_straightness = fields.One2many('mechanical.straightness.tile.line','parent_id',string="Parameter")

    average_straightness = fields.Float(string="Average ", compute="_compute_average_straightness",digits=(16,3))

    deviation_straightness = fields.Float(string="Deviation from Straightness ",compute="_compute_deviation_straightness", digits=(16,3))


    @api.depends('child_lines_straightness.straightness1',  'child_lines_straightness.straightness2',  'child_lines_straightness.straightness3',  'child_lines_straightness.straightness4' )
    def _compute_average_straightness(self):
        for record in self:
            if record.child_lines_straightness:
                # Calculate the total sum of all straightness fields across child lines
                total = sum(
                    line.straightness1 + line.straightness2 + line.straightness3 + line.straightness4
                    for line in record.child_lines_straightness
                )
                # Calculate the total number of straightness values
                count = len(record.child_lines_straightness) * 4  # 4 straightness fields per line
                record.average_straightness = total / count if count > 0 else 0.0
            else:
                record.average_straightness = 0.0

    @api.depends('average_straightness', 'sample_size')
    def _compute_deviation_straightness(self):
        for record in self:
            if record.sample_size and record.sample_size > 0:
                record.deviation_straightness = (record.average_straightness / record.sample_size) * 100
            else:
                record.deviation_straightness = 0.0


    deviation_straightness_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_deviation_straightness_conformity", store=True)



    @api.depends('deviation_straightness','eln_ref','grade')
    def _compute_deviation_straightness_conformity(self):
        
        for record in self:
            record.deviation_straightness_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','19999f82-79c0-44a8-9379-f40dd33235aa')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','19999f82-79c0-44a8-9379-f40dd33235aa')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.deviation_straightness - record.deviation_straightness*mu_value
                    upper = record.deviation_straightness + record.deviation_straightness*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.deviation_straightness_conformity = 'pass'
                        break
                    else:
                        record.deviation_straightness_conformity = 'fail'

    deviation_straightness_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_deviation_straightness_nabl", store=True)

    @api.depends('deviation_straightness','eln_ref','grade')
    def _compute_deviation_straightness_nabl(self):
        
        for record in self:
            record.deviation_straightness_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','19999f82-79c0-44a8-9379-f40dd33235aa')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','19999f82-79c0-44a8-9379-f40dd33235aa')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.deviation_straightness - record.deviation_straightness*mu_value
                    upper = record.deviation_straightness + record.deviation_straightness*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.deviation_straightness_nabl = 'pass'
                        break
                    else:
                        record.deviation_straightness_nabl = 'fail'


        # Rectangularity

    rectangularity_name = fields.Char("Name",default="Rectangularity")
    rectangularity_visible = fields.Boolean("Rectangularity Visible",compute="_compute_visible")   

    rectangularity_sample_size = fields.Integer(string="Sample Size")

    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines_rectangularity = fields.One2many('mechanical.rectangularity.tile.line','parent_id',string="Parameter")

    average_rectangularity = fields.Float(string="Average ", compute="_compute_average_rectangularity",digits=(16,3))

    deviation_rectangularity = fields.Float(string="Deviation from Rectangularity ",compute="_compute_deviation_rectangularity", digits=(16,3))


    @api.depends('child_lines_rectangularity.rectangularity1',  'child_lines_rectangularity.rectangularity2',  'child_lines_rectangularity.rectangularity3',  'child_lines_rectangularity.rectangularity4' )
    def _compute_average_rectangularity(self):
        for record in self:
            if record.child_lines_rectangularity:
                # Calculate the total sum of all rectangularity fields across child lines
                total = sum(
                    line.rectangularity1 + line.rectangularity2 + line.rectangularity3 + line.rectangularity4
                    for line in record.child_lines_rectangularity
                )
                # Calculate the total number of rectangularity values
                count = len(record.child_lines_rectangularity) * 4  # 4 rectangularity fields per line
                record.average_rectangularity = total / count if count > 0 else 0.0
            else:
                record.average_rectangularity = 0.0

    @api.depends('average_rectangularity', 'rectangularity_sample_size')
    def _compute_deviation_rectangularity(self):
        for record in self:
            if record.rectangularity_sample_size and record.rectangularity_sample_size > 0:
                record.deviation_rectangularity = (record.average_rectangularity / record.rectangularity_sample_size) * 100
            else:
                record.deviation_rectangularity = 0.0


    deviation_rectangularity_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_deviation_rectangularity_conformity", store=True)



    @api.depends('deviation_rectangularity','eln_ref','grade')
    def _compute_deviation_rectangularity_conformity(self):
        
        for record in self:
            record.deviation_rectangularity_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','4e209b70-f6b9-49b9-bab6-f38292f64b1c')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','4e209b70-f6b9-49b9-bab6-f38292f64b1c')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.deviation_rectangularity - record.deviation_rectangularity*mu_value
                    upper = record.deviation_rectangularity + record.deviation_rectangularity*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.deviation_rectangularity_conformity = 'pass'
                        break
                    else:
                        record.deviation_rectangularity_conformity = 'fail'

    deviation_rectangularity_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_deviation_rectangularity_nabl", store=True)

    @api.depends('deviation_rectangularity','eln_ref','grade')
    def _compute_deviation_rectangularity_nabl(self):
        
        for record in self:
            record.deviation_rectangularity_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','4e209b70-f6b9-49b9-bab6-f38292f64b1c')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','4e209b70-f6b9-49b9-bab6-f38292f64b1c')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.deviation_rectangularity - record.deviation_rectangularity*mu_value
                    upper = record.deviation_rectangularity + record.deviation_rectangularity*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.deviation_rectangularity_nabl = 'pass'
                        break
                    else:
                        record.deviation_rectangularity_nabl = 'fail'




      # Centre Curvature

    centre_curvature_name = fields.Char("Name",default="Centre Curvature")
    centre_curvature_visible = fields.Boolean("Centre Curvature Visible",compute="_compute_visible")   

    centre_curvature_sample_size = fields.Integer(string="Sample Size")
    centre_curvature_diagonal  = fields.Integer(string="Diagonal ")

    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines_centre_curvature = fields.One2many('mechanical.centre.curvature.tile.line','parent_id',string="Parameter")

    average_centre_curvature = fields.Float(string="Average ", compute="_compute_average_centre_curvature",digits=(16,3))

    deviation_centre_curvature = fields.Float(string="Maximum Centre Curvature,% ",compute="_compute_deviation_centre_curvature", digits=(16,3))


    @api.depends('child_lines_centre_curvature.centre_curvature1',  'child_lines_centre_curvature.centre_curvature2',  'child_lines_centre_curvature.centre_curvature3',  'child_lines_centre_curvature.centre_curvature4' )
    def _compute_average_centre_curvature(self):
        for record in self:
            if record.child_lines_centre_curvature:
                # Calculate the total sum of all centre_curvature fields across child lines
                total = sum(
                    line.centre_curvature1 + line.centre_curvature2 + line.centre_curvature3 + line.centre_curvature4
                    for line in record.child_lines_centre_curvature
                )
                # Calculate the total number of centre_curvature values
                count = len(record.child_lines_centre_curvature) * 4  # 4 centre_curvature fields per line
                record.average_centre_curvature = total / count if count > 0 else 0.0
            else:
                record.average_centre_curvature = 0.0

    @api.depends('average_centre_curvature', 'centre_curvature_diagonal')
    def _compute_deviation_centre_curvature(self):
        for record in self:
            if record.centre_curvature_diagonal and record.centre_curvature_diagonal > 0:
                record.deviation_centre_curvature = (record.average_centre_curvature / record.centre_curvature_diagonal) * 100
            else:
                record.deviation_centre_curvature = 0.0


    deviation_centre_curvature_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_deviation_centre_curvature_conformity", store=True)



    @api.depends('deviation_centre_curvature','eln_ref','grade')
    def _compute_deviation_centre_curvature_conformity(self):
        
        for record in self:
            record.deviation_centre_curvature_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','873e02d1-db08-43d8-a88f-f6de09d41955')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','873e02d1-db08-43d8-a88f-f6de09d41955')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.deviation_centre_curvature - record.deviation_centre_curvature*mu_value
                    upper = record.deviation_centre_curvature + record.deviation_centre_curvature*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.deviation_centre_curvature_conformity = 'pass'
                        break
                    else:
                        record.deviation_centre_curvature_conformity = 'fail'

    deviation_centre_curvature_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_deviation_centre_curvature_nabl", store=True)

    @api.depends('deviation_centre_curvature','eln_ref','grade')
    def _compute_deviation_centre_curvature_nabl(self):
        
        for record in self:
            record.deviation_centre_curvature_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','873e02d1-db08-43d8-a88f-f6de09d41955')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','873e02d1-db08-43d8-a88f-f6de09d41955')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.deviation_centre_curvature - record.deviation_centre_curvature*mu_value
                    upper = record.deviation_centre_curvature + record.deviation_centre_curvature*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.deviation_centre_curvature_nabl = 'pass'
                        break
                    else:
                        record.deviation_centre_curvature_nabl = 'fail'




      # Edge Curvature

    edge_curvature_name = fields.Char("Name",default="Edge Curvature")
    edge_curvature_visible = fields.Boolean("Edge Curvature Visible",compute="_compute_visible")   

    edge_curvature_sample_size = fields.Integer(string="Sample Size")
    edge_curvature_diagonal  = fields.Integer(string="Diagonal ")

    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines_edge_curvature = fields.One2many('mechanical.edge.curvature.tile.line','parent_id',string="Parameter")

    average_edge_curvature = fields.Float(string="Average ", compute="_compute_average_edge_curvature",digits=(16,3))

    deviation_edge_curvature = fields.Float(string="Maximum edge Curvature,% ",compute="_compute_deviation_edge_curvature", digits=(16,3))


    @api.depends('child_lines_edge_curvature.edge_curvature1',  'child_lines_edge_curvature.edge_curvature2',  'child_lines_edge_curvature.edge_curvature3',  'child_lines_edge_curvature.edge_curvature4' )
    def _compute_average_edge_curvature(self):
        for record in self:
            if record.child_lines_edge_curvature:
                # Calculate the total sum of all edge_curvature fields across child lines
                total = sum(
                    line.edge_curvature1 + line.edge_curvature2 + line.edge_curvature3 + line.edge_curvature4
                    for line in record.child_lines_edge_curvature
                )
                # Calculate the total number of edge_curvature values
                count = len(record.child_lines_edge_curvature) * 4  # 4 edge_curvature fields per line
                record.average_edge_curvature = total / count if count > 0 else 0.0
            else:
                record.average_edge_curvature = 0.0

    @api.depends('average_edge_curvature', 'edge_curvature_sample_size')
    def _compute_deviation_edge_curvature(self):
        for record in self:
            if record.edge_curvature_sample_size and record.edge_curvature_sample_size > 0:
                record.deviation_edge_curvature = (record.average_edge_curvature / record.edge_curvature_sample_size) * 100
            else:
                record.deviation_edge_curvature = 0.0

    deviation_edge_curvature_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_deviation_edge_curvature_conformity", store=True)



    @api.depends('deviation_edge_curvature','eln_ref','grade')
    def _compute_deviation_edge_curvature_conformity(self):
        
        for record in self:
            record.deviation_edge_curvature_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','2c4efee6-d22a-4eec-afbb-5435f3041f3f')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','2c4efee6-d22a-4eec-afbb-5435f3041f3f')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.deviation_edge_curvature - record.deviation_edge_curvature*mu_value
                    upper = record.deviation_edge_curvature + record.deviation_edge_curvature*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.deviation_edge_curvature_conformity = 'pass'
                        break
                    else:
                        record.deviation_edge_curvature_conformity = 'fail'

    deviation_edge_curvature_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_deviation_edge_curvature_nabl", store=True)

    @api.depends('deviation_edge_curvature','eln_ref','grade')
    def _compute_deviation_edge_curvature_nabl(self):
        
        for record in self:
            record.deviation_edge_curvature_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','2c4efee6-d22a-4eec-afbb-5435f3041f3f')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','2c4efee6-d22a-4eec-afbb-5435f3041f3f')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.deviation_edge_curvature - record.deviation_edge_curvature*mu_value
                    upper = record.deviation_edge_curvature + record.deviation_edge_curvature*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.deviation_edge_curvature_nabl = 'pass'
                        break
                    else:
                        record.deviation_edge_curvature_nabl = 'fail'



       # warpage

    warpage_name = fields.Char("Name",default="Warpage")
    warpage_visible = fields.Boolean("Warpage Visible",compute="_compute_visible")   

    warpage_sample_size = fields.Integer(string="Sample Size")
    warpage_diagonal  = fields.Integer(string="Diagonal ")

    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines_warpage = fields.One2many('mechanical.warpage.tile.line','parent_id',string="Parameter")

    average_warpage = fields.Float(string="Average ", compute="_compute_average_warpage",digits=(16,3))

    deviation_warpage = fields.Float(string="Maximum warpage,% ",compute="_compute_deviation_warpage", digits=(16,3))


    @api.depends('child_lines_warpage.warpage1',  'child_lines_warpage.warpage2',  'child_lines_warpage.warpage3',  'child_lines_warpage.warpage4' )
    def _compute_average_warpage(self):
        for record in self:
            if record.child_lines_warpage:
                # Calculate the total sum of all warpage fields across child lines
                total = sum(
                    line.warpage1 + line.warpage2 + line.warpage3 + line.warpage4
                    for line in record.child_lines_warpage
                )
                # Calculate the total number of warpage values
                count = len(record.child_lines_warpage) * 4  # 4 warpage fields per line
                record.average_warpage = total / count if count > 0 else 0.0
            else:
                record.average_warpage = 0.0

    @api.depends('average_warpage', 'warpage_diagonal')
    def _compute_deviation_warpage(self):
        for record in self:
            if record.warpage_diagonal and record.warpage_diagonal > 0:
                record.deviation_warpage = (record.average_warpage / record.warpage_diagonal) * 100
            else:
                record.deviation_warpage = 0.0


    deviation_warpage_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_deviation_warpage_conformity", store=True)



    @api.depends('deviation_warpage','eln_ref','grade')
    def _compute_deviation_warpage_conformity(self):
        
        for record in self:
            record.deviation_warpage_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','91fc2258-6bd7-40d4-82d8-404af0928ae9')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','91fc2258-6bd7-40d4-82d8-404af0928ae9')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.deviation_warpage - record.deviation_warpage*mu_value
                    upper = record.deviation_warpage + record.deviation_warpage*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.deviation_warpage_conformity = 'pass'
                        break
                    else:
                        record.deviation_warpage_conformity = 'fail'

    deviation_warpage_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_deviation_warpage_nabl", store=True)

    @api.depends('deviation_warpage','eln_ref','grade')
    def _compute_deviation_warpage_nabl(self):
        
        for record in self:
            record.deviation_warpage_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','91fc2258-6bd7-40d4-82d8-404af0928ae9')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','91fc2258-6bd7-40d4-82d8-404af0928ae9')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.deviation_warpage - record.deviation_warpage*mu_value
                    upper = record.deviation_warpage + record.deviation_warpage*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.deviation_warpage_nabl = 'pass'
                        break
                    else:
                        record.deviation_warpage_nabl = 'fail'




     # water absorption and bulk density

    water_bulk_name = fields.Char("Name",default="water absorption and bulk density")
    water_bulk_visible = fields.Boolean("water absorption and bulk density Visible",compute="_compute_visible")   

   

    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines_water_bulk = fields.One2many('mechanical.water.bulk.tile.line','parent_id',string="Parameter")

    average_water_bulk = fields.Float(string="Water Absorption, % (average) ",compute="_compute_average_water_bulk",digits=(16,1))

    individual_water_bulk = fields.Float(string="water Absorption, % (Individual) ",compute="_compute_individual_water_bulk",digits=(16,1))
    bulk_density = fields.Float(string="Bulk Density, g/cc",compute="_compute_bulk_density",digits=(16,2))


    @api.depends('child_lines_water_bulk.water_obsorption')
    def _compute_average_water_bulk(self):
        for record in self:
            # Calculate the average of water_obsorption across child lines
            total = sum(line.water_obsorption for line in record.child_lines_water_bulk if line.water_obsorption)
            count = len(record.child_lines_water_bulk)
            record.average_water_bulk = total / count if count > 0 else 0.0


    @api.depends('child_lines_water_bulk.water_obsorption')
    def _compute_individual_water_bulk(self):
        for record in self:
            # Fetch the maximum water_obsorption value from child lines
            max_value = max(
                (line.water_obsorption for line in record.child_lines_water_bulk if line.water_obsorption), 
                default=0.0
            )
            record.individual_water_bulk = max_value


    @api.depends('child_lines_water_bulk.bulk_density')
    def _compute_bulk_density(self):
        for record in self:
            # Calculate the average of bulk_density across child lines
            total = sum(line.bulk_density for line in record.child_lines_water_bulk if line.bulk_density)
            count = len(record.child_lines_water_bulk)
            record.bulk_density = total / count if count > 0 else 0.0


    bulk_density_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_bulk_density_conformity", store=True)



    @api.depends('bulk_density','eln_ref','grade')
    def _compute_bulk_density_conformity(self):
        
        for record in self:
            record.bulk_density_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','5d81b405-ed58-4374-bda7-2825e12f307c')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','5d81b405-ed58-4374-bda7-2825e12f307c')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.bulk_density - record.bulk_density*mu_value
                    upper = record.bulk_density + record.bulk_density*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.bulk_density_conformity = 'pass'
                        break
                    else:
                        record.bulk_density_conformity = 'fail'

    bulk_density_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_bulk_density_nabl", store=True)

    @api.depends('bulk_density','eln_ref','grade')
    def _compute_bulk_density_nabl(self):
        
        for record in self:
            record.bulk_density_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','5d81b405-ed58-4374-bda7-2825e12f307c')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','5d81b405-ed58-4374-bda7-2825e12f307c')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.bulk_density - record.bulk_density*mu_value
                    upper = record.bulk_density + record.bulk_density*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.bulk_density_nabl = 'pass'
                        break
                    else:
                        record.bulk_density_nabl = 'fail'




    

      # Modulus and rupture and breaking strength

    modulus_name = fields.Char("Name",default="Modulus and rupture and breaking strength")
    modulus_visible = fields.Boolean("Modulus and rupture and breaking strength Visible",compute="_compute_visible")   

   

    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines_modulus = fields.One2many('mechanical.modulus.tile.line','parent_id',string="Parameter")

    average_modulus = fields.Float(string="Modulus of rupture, N/mm2 (Average)",compute="_compute_average_modulus",digits=(16,2))

    individual_modulus = fields.Float(string="Modulus of rupture, N/mm2 (Individual)",compute="_compute_individual_modulus",digits=(16,2))
    breaking_strenght = fields.Float(string="Breaking Strength, N",compute="_compute_breaking_strenght",digits=(16,1))


    @api.depends('child_lines_modulus.mor')
    def _compute_average_modulus(self):
        for record in self:
            # Calculate the average of mor across child lines
            total = sum(line.mor for line in record.child_lines_modulus if line.mor)
            count = len(record.child_lines_modulus)
            record.average_modulus = total / count if count > 0 else 0.0


    @api.depends('child_lines_modulus.mor')
    def _compute_individual_modulus(self):
        for record in self:
            # Fetch the maximum mor value from child lines
            max_value = min(
                (line.mor for line in record.child_lines_modulus if line.mor), 
                default=0.0
            )
            record.individual_modulus = max_value


    @api.depends('child_lines_modulus.bs')
    def _compute_breaking_strenght(self):
        for record in self:
            # Calculate the average of bs across child lines
            total = sum(line.bs for line in record.child_lines_modulus if line.bs)
            count = len(record.child_lines_modulus)
            record.breaking_strenght = total / count if count > 0 else 0.0

    breaking_strenght_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity", compute="_compute_breaking_strenght_conformity", store=True)



    @api.depends('breaking_strenght','eln_ref','grade')
    def _compute_breaking_strenght_conformity(self):
        
        for record in self:
            record.breaking_strenght_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','f9fb0d98-1891-496f-9ef3-4745c5598085')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','f9fb0d98-1891-496f-9ef3-4745c5598085')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.breaking_strenght - record.breaking_strenght*mu_value
                    upper = record.breaking_strenght + record.breaking_strenght*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.breaking_strenght_conformity = 'pass'
                        break
                    else:
                        record.breaking_strenght_conformity = 'fail'

    breaking_strenght_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL", compute="_compute_breaking_strenght_nabl", store=True)

    @api.depends('breaking_strenght','eln_ref','grade')
    def _compute_breaking_strenght_nabl(self):
        
        for record in self:
            record.breaking_strenght_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','f9fb0d98-1891-496f-9ef3-4745c5598085')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','f9fb0d98-1891-496f-9ef3-4745c5598085')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.breaking_strenght - record.breaking_strenght*mu_value
                    upper = record.breaking_strenght + record.breaking_strenght*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.breaking_strenght_nabl = 'pass'
                        break
                    else:
                        record.breaking_strenght_nabl = 'fail'


        # crazing resistance test

    crazing_name = fields.Char("Name",default="Crazing resistance test")
    crazing_visible = fields.Boolean("crazing resistance test Visible",compute="_compute_visible")  


    observations = fields.Selection(
        [
            ('crazing_observed', 'Crazing effect was observed'),
            ('no_crazing_observed', 'No crazing effect was observed')
        ],
        string="Observations",
        default='no_crazing_observed',  # Default to "No crazing effect was observed"
    ) 



        # chemical resistance test

    chemical_name = fields.Char("Name",default="Chemical resistance test")
    chemical_visible = fields.Boolean("chemical resistance test Visible",compute="_compute_visible")  


    observations_chemical = fields.Selection(
        [
            ('stain', 'Stain Resistance - Class 2 '),
            ('chemical', 'Chemical Resistance - A')
        ],
        string="Observations",
        default='chemical',  # Default to "No crazing effect was observed"
    ) 






   ### Compute Visible
    @api.depends('sample_parameters')
    def _compute_visible(self):
        
        for record in self:

            record.dimension_visible = False
            record.straightness_visible = False
            record.rectangularity_visible = False
            record.centre_curvature_visible = False
            record.edge_curvature_visible = False
            record.warpage_visible = False
            record.water_bulk_visible = False
            record.modulus_visible = False
            record.crazing_visible = False
            record.chemical_visible = False
            
            for sample in record.sample_parameters:
                print("Internal Ids",sample.internal_id)

               
                if sample.internal_id == "1db41e6d-550e-4c5d-a923-7510a616beb5":
                    record.dimension_visible = True

                if sample.internal_id == "19999f82-79c0-44a8-9379-f40dd33235aa":
                    record.straightness_visible = True

                if sample.internal_id == "4e209b70-f6b9-49b9-bab6-f38292f64b1c":
                    record.rectangularity_visible = True

                if sample.internal_id == "873e02d1-db08-43d8-a88f-f6de09d41955":
                    record.centre_curvature_visible = True


                if sample.internal_id == "2c4efee6-d22a-4eec-afbb-5435f3041f3f":
                    record.edge_curvature_visible = True
               
                if sample.internal_id == "91fc2258-6bd7-40d4-82d8-404af0928ae9":
                    record.warpage_visible = True

                if sample.internal_id == "5d81b405-ed58-4374-bda7-2825e12f307c":
                    record.water_bulk_visible = True

                if sample.internal_id == "f9fb0d98-1891-496f-9ef3-4745c5598085":
                    record.modulus_visible = True

                if sample.internal_id == "0157651d-76f3-428a-9a89-f47593d1fd42":
                    record.crazing_visible = True

                if sample.internal_id == "daa5edf4-4f0a-4625-a1b8-4b365204be34":
                    record.chemical_visible = True





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
        record = super(Tile, self).create(vals)
        # record.get_all_fields()
        record.eln_ref.write({'model_id':record.id})
        return record







    @api.depends('eln_ref')
    def _compute_sample_parameters(self):
        # records = self.env['lerm.eln'].sudo().search([('id','=', record.eln_id.id)]).parameters_result
        # print("records",records)
        # self.sample_parameters = records
        for record in self:
            records = record.eln_ref.parameters_result.parameter.ids
            record.sample_parameters = records
            print("Records",records)



    def get_all_fields(self):
        record = self.env['mechanical.paver.block'].browse(self.ids[0])
        field_values = {}
        for field_name, field in record._fields.items():
            field_value = record[field_name]
            field_values[field_name] = field_value

        return field_values


class DimensionTile(models.Model):
    _name = "mechanical.dimension.tile.line"
    parent_id = fields.Many2one('mechanical.tile',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr No.",readonly=True, copy=False, default=1)
    length1 = fields.Float(string="Length 1")
    length2 = fields.Float(string="Length 2")
    length3 = fields.Float(string="Length 3")
    length4 = fields.Float(string="Length 4")

    width1 = fields.Float(string="Width 1")
    width2 = fields.Float(string="Width 2")
    width3 = fields.Float(string="Width 3")
    width4 = fields.Float(string="Width 4")

    thickness1 = fields.Float(string="Thickness 1")
    thickness2 = fields.Float(string="Thickness 2")
    thickness3 = fields.Float(string="Thickness 3")
    thickness4 = fields.Float(string="Thickness 4")
    thickness5 = fields.Float(string="Thickness 5")
    thickness6 = fields.Float(string="Thickness 6")

  



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(DimensionTile, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1


class StraightnessTile(models.Model):
    _name = "mechanical.straightness.tile.line"
    parent_id = fields.Many2one('mechanical.tile',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr No.",readonly=True, copy=False, default=1)

    straightness1 = fields.Float(string="Straightness 1",digits=(12,3))
    straightness2 = fields.Float(string="Straightness 2",digits=(12,3))
    straightness3 = fields.Float(string="Straightness 3",digits=(12,3))
    straightness4 = fields.Float(string="Straightness 4",digits=(12,3))

   

  



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(StraightnessTile, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1



class RectangularityTile(models.Model):
    _name = "mechanical.rectangularity.tile.line"
    parent_id = fields.Many2one('mechanical.tile',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr No.",readonly=True, copy=False, default=1)

    rectangularity1 = fields.Float(string="Rectangularity 1",digits=(12,3))
    rectangularity2 = fields.Float(string="Rectangularity 2",digits=(12,3))
    rectangularity3 = fields.Float(string="Rectangularity 3",digits=(12,3))
    rectangularity4 = fields.Float(string="Rectangularity 4",digits=(12,3))

   

  



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(RectangularityTile, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1


class CentreCurvatureTile(models.Model):
    _name = "mechanical.centre.curvature.tile.line"
    parent_id = fields.Many2one('mechanical.tile',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr No.",readonly=True, copy=False, default=1)

    centre_curvature1 = fields.Float(string="Centre Curvature 1",digits=(12,3))
    centre_curvature2 = fields.Float(string="Centre Curvature 2",digits=(12,3))
    centre_curvature3 = fields.Float(string="Centre Curvature 3",digits=(12,3))
    centre_curvature4 = fields.Float(string="Centre Curvature 4",digits=(12,3))

   

  



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(CentreCurvatureTile, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1



class EdgeCurvatureTile(models.Model):
    _name = "mechanical.edge.curvature.tile.line"
    parent_id = fields.Many2one('mechanical.tile',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr No.",readonly=True, copy=False, default=1)

    edge_curvature1 = fields.Float(string="Edge Curvature 1",digits=(12,3))
    edge_curvature2 = fields.Float(string="Edge Curvature 2",digits=(12,3))
    edge_curvature3 = fields.Float(string="Edge Curvature 3",digits=(12,3))
    edge_curvature4 = fields.Float(string="Edge Curvature 4",digits=(12,3))

   

  



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(EdgeCurvatureTile, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1



class WarpageTile(models.Model):
    _name = "mechanical.warpage.tile.line"
    parent_id = fields.Many2one('mechanical.tile',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr No.",readonly=True, copy=False, default=1)

    warpage1 = fields.Float(string="Warpage 1",digits=(12,3))
    warpage2 = fields.Float(string="Warpage 2",digits=(12,3))
    warpage3 = fields.Float(string="Warpage 3",digits=(12,3))
    warpage4 = fields.Float(string="Warpage 4",digits=(12,3))

   

  



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(WarpageTile, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1


class WaterAndBulkTile(models.Model):
    _name = "mechanical.water.bulk.tile.line"
    parent_id = fields.Many2one('mechanical.tile',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr No.",readonly=True, copy=False, default=1)

    lenght = fields.Float(string="Length",digits=(12,2))
    width = fields.Float(string="Width",digits=(12,2))
    thickness = fields.Float(string="Thickness",digits=(12,2))
    oven_dry = fields.Float(string="Oven Dry Weight",digits=(12,3))
    wet_weight = fields.Float(string="Wet Weight",digits=(12,3))
    water_obsorption = fields.Float(string="Water Absorption",compute="_compute_water_absorption",digits=(12,3))
    bulk_density = fields.Float(string="Bulk Density",compute="_compute_bulk_density",digits=(12,3))


    @api.depends('wet_weight', 'oven_dry')
    def _compute_water_absorption(self):
        for record in self:
            if record.oven_dry and record.oven_dry > 0:  # Ensure oven_dry is not zero to avoid division by zero
                record.water_obsorption = ((record.wet_weight - record.oven_dry) / record.oven_dry) * 100
            else:
                record.water_obsorption = 0.0  # Default to 0 if calculation is invalid

    @api.depends('oven_dry', 'lenght', 'width', 'thickness')
    def _compute_bulk_density(self):
        for record in self:
            if record.lenght > 0 and record.width > 0 and record.thickness > 0:  # Ensure dimensions are valid
                volume = record.lenght * record.width * record.thickness
                record.bulk_density = (record.oven_dry / volume) * 1000
            else:
                record.bulk_density = 0.0  # Default to 0 if dimensions are invalid

   

  



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(WaterAndBulkTile, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1



class ModulusTile(models.Model):
    _name = "mechanical.modulus.tile.line"
    parent_id = fields.Many2one('mechanical.tile',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr No.",readonly=True, copy=False, default=1)

   
    width = fields.Float(string="Width",digits=(12,2))
    span = fields.Float(string="Span",digits=(12,2))
    thickness = fields.Float(string="Thickness",digits=(12,2))
    peak_load = fields.Float(string="PEAK LOAD (NN)",digits=(12,2))
    mor = fields.Float(string="MOR (N/mm2)",compute="_compute_mor_and_bs",digits=(12,2))
    bs = fields.Float(string="BS (N)",compute="_compute_mor_and_bs",digits=(12,1))


    @api.depends('peak_load', 'span', 'width', 'thickness')
    def _compute_mor_and_bs(self):
        for record in self:
            # Calculate MOR
            if record.width > 0 and record.thickness > 0:  # Ensure valid inputs
                record.mor = (3 * record.peak_load * record.span) / (2 * record.width * (record.thickness ** 2))
            else:
                record.mor = 0.0  # Default to 0 if inputs are invalid

            # Calculate BS
            if record.width > 0:  # Ensure valid input
                record.bs = (record.peak_load * record.span) / record.width
            else:
                record.bs = 0.0  # Default to 0 if width is invalid

    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(ModulusTile, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1