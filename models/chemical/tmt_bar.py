from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class TMTBar(models.Model):
    _name = "chemical.tmt.bar"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="TMT BAR")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    eln_ref = fields.Many2one('lerm.eln',string="Eln")
    grade = fields.Many2one('lerm.grade.line',string="Grade",compute="_compute_grade_id",store=True)


    # Carbon (IS : 228 part 1)	
    carbon_name = fields.Char("Name",default="Carbon (IS : 228 part 1)")
    carbon_visible = fields.Boolean("Carbon",compute="_compute_visible")

    carbon_sample = fields.Float("A)Wt of Sample taken (gm)")
    carbon_bur = fields.Float("B)Burette reading for blank (ml)")
    carbon_bur_sample = fields.Float("C)Burette reading for Sample (ml)")
    carbon_factor = fields.Float("D)Correction Factor")
    carbon = fields.Float("% Carbon=(C-B)xD / wt of sample",compute="_compute_carbon",digits=(12,3))

    @api.depends('carbon_bur_sample', 'carbon_bur', 'carbon_factor', 'carbon_sample')
    def _compute_carbon(self):
        for record in self:
            if record.carbon_sample != 0:
                record.carbon = ((record.carbon_bur_sample - record.carbon_bur) * record.carbon_factor) / record.carbon_sample
            else:
                record.carbon = 0
  
    

    carbon_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity",compute="_compute_carbon_conformity", store=True)

    @api.depends('carbon','eln_ref','grade')
    def _compute_carbon_conformity(self):
        
        for record in self:
            record.carbon_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ee5b7bb7-65ad-4970-b2eb-1a45e3ab2332')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ee5b7bb7-65ad-4970-b2eb-1a45e3ab2332')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.carbon - record.carbon*mu_value
                    upper = record.carbon + record.carbon*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.carbon_conformity = 'pass'
                        break
                    else:
                        record.carbon_conformity = 'fail'

    carbon_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL",compute="_compute_carbon_nabl", store=True)

    @api.depends('carbon','eln_ref','grade')
    def _compute_carbon_nabl(self):
        
        for record in self:
            record.carbon_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ee5b7bb7-65ad-4970-b2eb-1a45e3ab2332')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ee5b7bb7-65ad-4970-b2eb-1a45e3ab2332')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.carbon - record.carbon*mu_value
                    upper = record.carbon + record.carbon*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.carbon_nabl = 'pass'
                        break
                    else:
                        record.carbon_nabl = 'fail'


    #  Manganese (IS : 228 part 2)		
    manganese_name = fields.Char("Name",default="Manganese (IS : 228 part 2)")
    manganese_visible = fields.Boolean("Manganese",compute="_compute_visible")

    manganese_sample = fields.Float("A)Wt of Sample taken (gm)")
    manganese_crm = fields.Float("B)Manganese equivalent of CRM taken")
    manganese_reading = fields.Float("C)Burette reading in (ml)")
    manganese = fields.Float("% Manganese = CxBx100/A",compute="_compute_manganese",digits=(12,2))

    @api.depends('manganese_reading', 'manganese_crm', 'manganese_sample')
    def _compute_manganese(self):
        for record in self:
            if record.manganese_sample != 0:
                record.manganese = (record.manganese_reading * record.manganese_crm) / record.manganese_sample
            else:
                record.manganese = 0


    manganese_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity",compute="_compute_manganese_conformity", store=True)

    @api.depends('manganese','eln_ref','grade')
    def _compute_manganese_conformity(self):
        
        for record in self:
            record.manganese_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','3bc58369-dcc7-4021-9b02-760f3d6cbd87')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','3bc58369-dcc7-4021-9b02-760f3d6cbd87')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.manganese - record.manganese*mu_value
                    upper = record.manganese + record.manganese*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.manganese_conformity = 'pass'
                        break
                    else:
                        record.manganese_conformity = 'fail'

    manganese_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL",compute="_compute_manganese_nabl", store=True)

    @api.depends('manganese','eln_ref','grade')
    def _compute_manganese_nabl(self):
        
        for record in self:
            record.manganese_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','3bc58369-dcc7-4021-9b02-760f3d6cbd87')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','3bc58369-dcc7-4021-9b02-760f3d6cbd87')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.manganese - record.manganese*mu_value
                    upper = record.manganese + record.manganese*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.manganese_nabl = 'pass'
                        break
                    else:
                        record.manganese_nabl = 'fail'

    #    Silicon (IS : 228 part 8)		
    silicon_name = fields.Char("Name",default="Silicon (IS : 228 part 8)")
    silicon_visible = fields.Boolean("Silicon",compute="_compute_visible")

    silicon_sample = fields.Float("A)Wt of Sample taken (gm)")
    silicon_wt_res = fields.Float("B)(Wt of  residue + Empty Crucible), gm")
    silicon_wt_res_emp = fields.Float("C)(Wt of  residue + Empty Crucible after HF), gm")
    silicon_diff = fields.Float("D)Difference in weight = ( B - C ) gm",compute="_compute_silicon_diff",digits=(12,3))
    silicon = fields.Float("%  Silcon= D  x 46.75 /A",digits=(12,2),compute="_compute_silicon")


    @api.depends('silicon_wt_res', 'silicon_wt_res_emp')
    def _compute_silicon_diff(self):
        for record in self:
            record.silicon_diff = record.silicon_wt_res - record.silicon_wt_res_emp

    @api.depends('silicon_diff', 'silicon_sample')
    def _compute_silicon(self):
        for record in self:
            if record.silicon_sample != 0:
                record.silicon = (record.silicon_diff * 46.75) / record.silicon_sample
            else:
                record.silicon = 0.0

  
    

    silicon_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity",compute="_compute_silicon_conformity", store=True)

    @api.depends('silicon','eln_ref','grade')
    def _compute_silicon_conformity(self):
        
        for record in self:
            record.silicon_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','3c96ee94-7af5-4525-8def-951d69554357')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','3c96ee94-7af5-4525-8def-951d69554357')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.silicon - record.silicon*mu_value
                    upper = record.silicon + record.silicon*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.silicon_conformity = 'pass'
                        break
                    else:
                        record.silicon_conformity = 'fail'

    silicon_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL",compute="_compute_silicon_nabl", store=True)

    @api.depends('silicon','eln_ref','grade')
    def _compute_silicon_nabl(self):
        
        for record in self:
            record.silicon_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','3c96ee94-7af5-4525-8def-951d69554357')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','3c96ee94-7af5-4525-8def-951d69554357')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.silicon - record.silicon*mu_value
                    upper = record.silicon + record.silicon*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.silicon_nabl = 'pass'
                        break
                    else:
                        record.silicon_nabl = 'fail'

    #   Carbon Equivalent		
		
    carbon_equivalent_name = fields.Char("Name",default="Carbon Equivalent")
    carbon_equivalent_visible = fields.Boolean("Silicon",compute="_compute_visible")

    carbon_equivalent = fields.Float("Carbon Equivalent",compute="_compute_carbon_equivalent",digits=(12,2))

    @api.depends('carbon', 'manganese')
    def _compute_carbon_equivalent(self):
        for record in self:
            record.carbon_equivalent = record.carbon + (record.manganese / 6)


    carbon_equivalent_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity",compute="_compute_carbon_equivalent_conformity", store=True)

    @api.depends('carbon_equivalent','eln_ref','grade')
    def _compute_carbon_equivalent_conformity(self):
        
        for record in self:
            record.carbon_equivalent_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ecdb4dc9-db86-4eb2-9fca-228fcf598db3')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ecdb4dc9-db86-4eb2-9fca-228fcf598db3')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.carbon_equivalent - record.carbon_equivalent*mu_value
                    upper = record.carbon_equivalent + record.carbon_equivalent*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.carbon_equivalent_conformity = 'pass'
                        break
                    else:
                        record.carbon_equivalent_conformity = 'fail'

    carbon_equivalent_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL",compute="_compute_carbon_equivalent_nabl", store=True)

    @api.depends('carbon_equivalent','eln_ref','grade')
    def _compute_carbon_equivalent_nabl(self):
        
        for record in self:
            record.carbon_equivalent_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ecdb4dc9-db86-4eb2-9fca-228fcf598db3')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','ecdb4dc9-db86-4eb2-9fca-228fcf598db3')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.carbon_equivalent - record.carbon_equivalent*mu_value
                    upper = record.carbon_equivalent + record.carbon_equivalent*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.carbon_equivalent_nabl = 'pass'
                        break
                    else:
                        record.carbon_equivalent_nabl = 'fail'


      #   Sulphur ( IS 228 part 9 )		
    sulphur_name = fields.Char("Name",default="Sulphur ( IS 228 part 9 )")
    sulphur_visible = fields.Boolean("Sulphur",compute="_compute_visible")

    sulphur_vl_po = fields.Float("A) volume, in ml, of potassium iodate  added	")
    sulphur_vl_un = fields.Float("B) volume, in ml, of potassium iodate  unused")
    sulphur_no = fields.Float("C)normality of Sodium thiosulphate")
    sulphur_mass = fields.Float("D)mass, in g, of sample taken.")
    sulphur = fields.Float("% Sulphur =B x C /A",compute="_compute_sulphur",digits=(12,3))

    @api.depends('sulphur_vl_po', 'sulphur_vl_un', 'sulphur_no', 'sulphur_mass')
    def _compute_sulphur(self):
        for record in self:
            if record.sulphur_mass != 0:
                record.sulphur = ((record.sulphur_vl_po - record.sulphur_vl_un) * record.sulphur_no * 1.6) / record.sulphur_mass
            else:
                record.sulphur = 0


   
  
    

    sulphur_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity",compute="_compute_sulphur_conformity", store=True)

    @api.depends('sulphur','eln_ref','grade')
    def _compute_sulphur_conformity(self):
        
        for record in self:
            record.sulphur_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','c69460b7-2c6f-4a77-b045-5f72ed3294fc')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','c69460b7-2c6f-4a77-b045-5f72ed3294fc')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.sulphur - record.sulphur*mu_value
                    upper = record.sulphur + record.sulphur*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.sulphur_conformity = 'pass'
                        break
                    else:
                        record.sulphur_conformity = 'fail'

    sulphur_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL",compute="_compute_sulphur_nabl", store=True)

    @api.depends('sulphur','eln_ref','grade')
    def _compute_sulphur_nabl(self):
        
        for record in self:
            record.sulphur_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','c69460b7-2c6f-4a77-b045-5f72ed3294fc')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','c69460b7-2c6f-4a77-b045-5f72ed3294fc')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.sulphur - record.sulphur*mu_value
                    upper = record.sulphur + record.sulphur*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.sulphur_nabl = 'pass'
                        break
                    else:
                        record.sulphur_nabl = 'fail'



       #   Phosphorous(IS : 228 part 3)				
    phosphorous_name = fields.Char("Name",default="Phosphorous(IS : 228 part 3)")
    phosphorous_visible = fields.Boolean("Phosphorous",compute="_compute_visible")

    phosphorous_sample = fields.Float("A)Wt of Sample taken (gm)")
    phosphorous_bu = fields.Float("B)Burette reading of 0.1N. NaOH Added (ml)")
    phosphorous_re = fields.Float("C)Burette reading of 0.1N. HNO3 Required (ml) for sample.")
    phosphorous_blank = fields.Float("D)Blank Reading in ml")
    phosphorous_diff = fields.Float("E)Difference = (D - C ) ml",compute="_compute_phosphorous_diff",digits=(12,4))
    phosphorous_no = fields.Float("F)Normality of  0.1N. HNO3")
    phosphorous = fields.Float("% P=E x F x  0.001354 x100 / wt of sample",compute="_compute_phosphorous",digits=(12,3))

    @api.depends('phosphorous_blank', 'phosphorous_re')
    def _compute_phosphorous_diff(self):
        for record in self:
            record.phosphorous_diff = record.phosphorous_blank - record.phosphorous_re

    @api.depends('phosphorous_diff', 'phosphorous_no', 'phosphorous_sample')
    def _compute_phosphorous(self):
        for record in self:
            if record.phosphorous_sample != 0:
                record.phosphorous = (record.phosphorous_diff * record.phosphorous_no * 0.001354 * 100) / record.phosphorous_sample
            else:
                record.phosphorous = 0

   
   
  
    

    phosphorous_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity",compute="_compute_phosphorous_conformity", store=True)

    @api.depends('phosphorous','eln_ref','grade')
    def _compute_phosphorous_conformity(self):
        
        for record in self:
            record.phosphorous_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','e66bf431-dafa-4e10-b140-79a890d1fc4b')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','e66bf431-dafa-4e10-b140-79a890d1fc4b')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.phosphorous - record.phosphorous*mu_value
                    upper = record.phosphorous + record.phosphorous*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.phosphorous_conformity = 'pass'
                        break
                    else:
                        record.phosphorous_conformity = 'fail'

    phosphorous_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL",compute="_compute_phosphorous_nabl", store=True)

    @api.depends('phosphorous','eln_ref','grade')
    def _compute_phosphorous_nabl(self):
        
        for record in self:
            record.phosphorous_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','e66bf431-dafa-4e10-b140-79a890d1fc4b')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','e66bf431-dafa-4e10-b140-79a890d1fc4b')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.phosphorous - record.phosphorous*mu_value
                    upper = record.phosphorous + record.phosphorous*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.phosphorous_nabl = 'pass'
                        break
                    else:
                        record.phosphorous_nabl = 'fail'



      #   Sulphur + Phosphorous	
		
    sulphur_phosphorous_name = fields.Char("Name",default="Sulphur + Phosphorous")
    sulphur_phosphorous_visible = fields.Boolean("Sulphur + Phosphorous",compute="_compute_visible")

    sulphur_phosphorous = fields.Float("Sulphur + Phosphorous",compute="_compute_sulphur_phosphorous",digits=(12,3))

    @api.depends('sulphur', 'phosphorous')
    def _compute_sulphur_phosphorous(self):
        for record in self:
            record.sulphur_phosphorous = record.sulphur + record.phosphorous

   

    sulphur_phosphorous_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity",compute="_compute_sulphur_phosphorous_conformity", store=True)

    @api.depends('sulphur_phosphorous','eln_ref','grade')
    def _compute_sulphur_phosphorous_conformity(self):
        
        for record in self:
            record.sulphur_phosphorous_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','d9b9cf1a-e726-4331-9a94-e7db04bfec71')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','d9b9cf1a-e726-4331-9a94-e7db04bfec71')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.sulphur_phosphorous - record.sulphur_phosphorous*mu_value
                    upper = record.sulphur_phosphorous + record.sulphur_phosphorous*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.sulphur_phosphorous_conformity = 'pass'
                        break
                    else:
                        record.sulphur_phosphorous_conformity = 'fail'

    sulphur_phosphorous_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL",compute="_compute_sulphur_phosphorous_nabl", store=True)

    @api.depends('sulphur_phosphorous','eln_ref','grade')
    def _compute_sulphur_phosphorous_nabl(self):
        
        for record in self:
            record.sulphur_phosphorous_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','d9b9cf1a-e726-4331-9a94-e7db04bfec71')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','d9b9cf1a-e726-4331-9a94-e7db04bfec71')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.sulphur_phosphorous - record.sulphur_phosphorous*mu_value
                    upper = record.sulphur_phosphorous + record.sulphur_phosphorous*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.sulphur_phosphorous_nabl = 'pass'
                        break
                    else:
                        record.sulphur_phosphorous_nabl = 'fail'


      #   Chromium (IS : 228 part 6)			
    chromium_name = fields.Char("Name",default="Chromium (IS : 228 part 6)")
    chromium_visible = fields.Boolean("Chromium",compute="_compute_visible")

    chromium_vl_po = fields.Float("A) Wt of Sample taken (gm)")
    chromium_vl_un = fields.Float("B) Burette reading for blank (ml)")
    chromium_no = fields.Float("C) burette reading of Kmno4 in ml for sample")
    chromium_mass = fields.Float("D) Normality of 0.1 N KMNO4")
    chromium = fields.Float("% Chromium =(B-C )x 0.01734 x D x 100/A",compute="_compute_chromium",digits=(12,2))

    @api.depends('chromium_vl_un', 'chromium_no', 'chromium_mass', 'chromium_vl_po')
    def _compute_chromium(self):
        for record in self:
            if record.chromium_vl_po != 0:
                record.chromium = ((record.chromium_vl_un - record.chromium_no) * 0.01734 * record.chromium_mass * 100) / record.chromium_vl_po
            else:
                record.chromium = 0

 
   
  
    

    chromium_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity",compute="_compute_chromium_conformity", store=True)

    @api.depends('chromium','eln_ref','grade')
    def _compute_chromium_conformity(self):
        
        for record in self:
            record.chromium_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','344403ea-5f80-4bb4-8e12-18be7aa2f65b')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','344403ea-5f80-4bb4-8e12-18be7aa2f65b')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.chromium - record.chromium*mu_value
                    upper = record.chromium + record.chromium*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.chromium_conformity = 'pass'
                        break
                    else:
                        record.chromium_conformity = 'fail'

    chromium_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL",compute="_compute_chromium_nabl", store=True)

    @api.depends('chromium','eln_ref','grade')
    def _compute_chromium_nabl(self):
        
        for record in self:
            record.chromium_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','344403ea-5f80-4bb4-8e12-18be7aa2f65b')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','344403ea-5f80-4bb4-8e12-18be7aa2f65b')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.chromium - record.chromium*mu_value
                    upper = record.chromium + record.chromium*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.chromium_nabl = 'pass'
                        break
                    else:
                        record.chromium_nabl = 'fail'



       #  Nickel (IS : 228 part 5)				
    nickel_name = fields.Char("Name",default="Nickel (IS : 228 part 5)")
    nickel_visible = fields.Boolean("Nickel",compute="_compute_visible")

    nickel_wt = fields.Float("A) Wt of Sample taken (gm)")
    nickel_wt_re = fields.Float("B) ( Wt of  residue + Empty Crucible ), gm")
    nickel_wt_empty = fields.Float("C) (Wt of empty crucible), gm")
    nickel_diff = fields.Float("D) Difference in weight = ( B - C ), gm",compute="_compute_nickel_diff",digits=(12,4))
    nickel = fields.Float("% Nickel = D x 0.2032 x 100 /A",compute="_compute_nickel",digits=(12,2))

    @api.depends('nickel_wt_re', 'nickel_wt_empty')
    def _compute_nickel_diff(self):
        for record in self:
            record.nickel_diff = record.nickel_wt_re - record.nickel_wt_empty

    @api.depends('nickel_diff', 'nickel_wt')
    def _compute_nickel(self):
        for record in self:
            if record.nickel_wt != 0:
                record.nickel = (record.nickel_diff * 0.2032 * 100) / record.nickel_wt
            else:
                record.nickel = 0

   
   
  
    

    nickel_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity",compute="_compute_nickel_conformity", store=True)

    @api.depends('nickel','eln_ref','grade')
    def _compute_nickel_conformity(self):
        
        for record in self:
            record.nickel_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','bae8f4e5-4f48-44ae-88bb-6ab69023b89b')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','bae8f4e5-4f48-44ae-88bb-6ab69023b89b')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.nickel - record.nickel*mu_value
                    upper = record.nickel + record.nickel*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.nickel_conformity = 'pass'
                        break
                    else:
                        record.nickel_conformity = 'fail'

    nickel_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL",compute="_compute_nickel_nabl", store=True)

    @api.depends('nickel','eln_ref','grade')
    def _compute_nickel_nabl(self):
        
        for record in self:
            record.nickel_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','bae8f4e5-4f48-44ae-88bb-6ab69023b89b')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','bae8f4e5-4f48-44ae-88bb-6ab69023b89b')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.nickel - record.nickel*mu_value
                    upper = record.nickel + record.nickel*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.nickel_nabl = 'pass'
                        break
                    else:
                        record.nickel_nabl = 'fail'




     # Molybdenum (IS : 228 part 7)						
    molybdenum_name = fields.Char("Name",default="Molybdenum (IS : 228 part 7)")
    molybdenum_visible = fields.Boolean("Molybdenum",compute="_compute_visible")

    molybdenum_wt = fields.Float("A) Wt of Sample taken (gm)")
    molybdenum_wt_re = fields.Float("B) Wt of empty crucible + residue, gm")
    molybdenum_wt_empty = fields.Float("C) Wt of empty crucible , gm")
    molybdenum_diff = fields.Float("D) Difference in weight = ( B - C ), gm",compute="_compute_molybdenum_diff",digits=(12,4))
    molybdenum = fields.Float("% Molybdenum = D x 66.7/A",compute="_compute_molybdenum",digits=(12,2))
    

    @api.depends('molybdenum_wt_re', 'molybdenum_wt_empty')
    def _compute_molybdenum_diff(self):
        for record in self:
            record.molybdenum_diff = record.molybdenum_wt_re - record.molybdenum_wt_empty

    @api.depends('molybdenum_diff', 'molybdenum_wt')
    def _compute_molybdenum(self):
        for record in self:
            if record.molybdenum_wt != 0:
                record.molybdenum = (record.molybdenum_diff * 66.7) / record.molybdenum_wt
            else:
                record.molybdenum = 0
    

   
   
  
    

    molybdenum_conformity = fields.Selection([
            ('pass', 'Pass'),
            ('fail', 'Fail')], string="Conformity",compute="_compute_molybdenum_conformity", store=True)

    @api.depends('molybdenum','eln_ref','grade')
    def _compute_molybdenum_conformity(self):
        
        for record in self:
            record.molybdenum_conformity = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','a56a1c53-aeda-4fd8-ace1-b00828550266')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','a56a1c53-aeda-4fd8-ace1-b00828550266')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    req_min = material.req_min
                    req_max = material.req_max
                    mu_value = line.mu_value
                    
                    lower = record.molybdenum - record.molybdenum*mu_value
                    upper = record.molybdenum + record.molybdenum*mu_value
                    if lower >= req_min and upper <= req_max:
                        record.molybdenum_conformity = 'pass'
                        break
                    else:
                        record.molybdenum_conformity = 'fail'

    molybdenum_nabl = fields.Selection([
        ('pass', 'NABL'),
        ('fail', 'Non-NABL')], string="NABL",compute="_compute_molybdenum_nabl", store=True)

    @api.depends('molybdenum','eln_ref','grade')
    def _compute_molybdenum_nabl(self):
        
        for record in self:
            record.molybdenum_nabl = 'fail'
            line = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','a56a1c53-aeda-4fd8-ace1-b00828550266')])
            materials = self.env['lerm.parameter.master'].sudo().search([('internal_id','=','a56a1c53-aeda-4fd8-ace1-b00828550266')]).parameter_table
            for material in materials:
                if material.grade.id == record.grade.id:
                    lab_min = line.lab_min_value
                    lab_max = line.lab_max_value
                    mu_value = line.mu_value
                    
                    lower = record.molybdenum - record.molybdenum*mu_value
                    upper = record.molybdenum + record.molybdenum*mu_value
                    if lower >= lab_min and upper <= lab_max:
                        record.molybdenum_nabl = 'pass'
                        break
                    else:
                        record.molybdenum_nabl = 'fail'







	



  


    

    @api.depends('sample_parameters')
    def _compute_visible(self):
        for record in self:
            record.carbon_visible = False
            record.manganese_visible = False
            record.silicon_visible = False
            record.carbon_equivalent_visible = False
            record.sulphur_visible = False
            record.phosphorous_visible = False
            record.sulphur_phosphorous_visible = False
            record.chromium_visible = False
            record.nickel_visible = False
            record.molybdenum_visible = False
          
            for sample in record.sample_parameters:
                print("Samples internal id",sample.internal_id)
                if sample.internal_id == 'ee5b7bb7-65ad-4970-b2eb-1a45e3ab2332':
                    record.carbon_visible = True
                if sample.internal_id == '3bc58369-dcc7-4021-9b02-760f3d6cbd87':
                    record.manganese_visible = True
                if sample.internal_id == '3c96ee94-7af5-4525-8def-951d69554357':
                    record.silicon_visible = True
                if sample.internal_id == 'ecdb4dc9-db86-4eb2-9fca-228fcf598db3':
                    record.carbon_equivalent_visible = True
                if sample.internal_id == 'c69460b7-2c6f-4a77-b045-5f72ed3294fc':
                    record.sulphur_visible = True
                if sample.internal_id == 'e66bf431-dafa-4e10-b140-79a890d1fc4b':
                    record.phosphorous_visible = True
                if sample.internal_id == 'd9b9cf1a-e726-4331-9a94-e7db04bfec71':
                    record.sulphur_phosphorous_visible = True
                if sample.internal_id == '344403ea-5f80-4bb4-8e12-18be7aa2f65b':
                    record.chromium_visible = True
                if sample.internal_id == 'bae8f4e5-4f48-44ae-88bb-6ab69023b89b':
                    record.nickel_visible = True
                if sample.internal_id == 'a56a1c53-aeda-4fd8-ace1-b00828550266':
                    record.molybdenum_visible = True
                    
                    
             

    
          

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(TMTBar, self).create(vals)
        # record.get_all_fields()
        record.eln_ref.write({'model_id':record.id})
        return record


        
    def get_all_fields(self):
        record = self.env['chemical.tmt.bar'].browse(self.ids[0])
        field_values = {}
        for field_name, field in record._fields.items():
            field_value = record[field_name]
            field_values[field_name] = field_value

        return field_values
    


    @api.depends('eln_ref')
    def _compute_sample_parameters(self):
        for record in self:
            records = record.eln_ref.parameters_result.parameter.ids
            record.sample_parameters = records
            print("Records",records)

    @api.depends('eln_ref')
    def _compute_grade_id(self):
        if self.eln_ref:
            self.grade = self.eln_ref.grade_id.id
    