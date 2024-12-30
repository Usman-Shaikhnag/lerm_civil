from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math


class OpcCementChemical(models.Model):
    _name = "opc.cement.chemical"
    _inherit = "lerm.eln"
    _rec_name = "name"

    grade = fields.Many2one('lerm.grade.line',string="Grade",compute="_compute_grade_id",store=True)
    name = fields.Char("Name",default="OPC Cement Chemical")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    eln_ref = fields.Many2one('lerm.eln',string="Eln")


            #1--- SiO₂ Clause 4.3

    sio2_name = fields.Char("Name",default="SiO₂ Clause 4.3")
    sio2_visible = fields.Boolean("SiO₂ Visible",compute="_compute_visible")
    sample_wt_sio2 = fields.Float(string="Wt of Sample (gm)")
    crucible_residue_ignition_sio2 = fields.Float(string="Wt of crucible +Residue after ignition (gm)")
    crucible_residue_ignition_hf = fields.Float(string="Wt of crucible + Residue after HF (gm)")
    diff_weight_sio2 = fields.Float(string="Diff. in weight (gm)",compute="_compute_diff_weight_sio2")
    sio2 = fields.Float(string="SiO₂",compute="_compute_sio2")

    @api.depends('crucible_residue_ignition_sio2', 'crucible_residue_ignition_hf')
    def _compute_diff_weight_sio2(self):
        for record in self:
            record.diff_weight_sio2 = record.crucible_residue_ignition_sio2 - record.crucible_residue_ignition_hf

    @api.depends('diff_weight_sio2', 'sample_wt_sio2')
    def _compute_sio2(self):
        for record in self:
            if record.sample_wt_sio2 != 0:
                record.sio2 = (record.diff_weight_sio2 * 100) / record.sample_wt_sio2
            else:
                record.sio2 = 0


            #2--- SO3 Clause 4.9

    so3_name = fields.Char("Name",default="SO3 Clause 4.9")
    so3_visible = fields.Boolean("SO3 Visible",compute="_compute_visible")
    sample_wt_so3 = fields.Float(string="Wt of Sample (gm)")
    crucible_residue_ignition_so3 = fields.Float(string="Wt of crucible +Residue after ignition (gm)")
    wt_empty_crucible_so3 = fields.Float(string="Wt of empty crucible (gm)")
    diff_weight_so3 = fields.Float(string="Diff. in weight (gm)",compute="_compute_diff_weight_so3")
    so3 = fields.Float(string="SO3",compute="_compute_so3")

    @api.depends('crucible_residue_ignition_so3', 'wt_empty_crucible_so3')
    def _compute_diff_weight_so3(self):
        for record in self:
            record.diff_weight_so3 = record.crucible_residue_ignition_so3 - record.wt_empty_crucible_so3

    
    @api.depends('diff_weight_so3', 'sample_wt_so3')
    def _compute_so3(self):
        for record in self:
            if record.sample_wt_so3 != 0:
                record.so3 = (record.diff_weight_so3 * 34.3) / record.sample_wt_so3
            else:
                record.so3 = 0

            # IR Clause 4.10

    ir_name = fields.Char("Name",default="IR Clause 4.10")
    ir_visible = fields.Boolean("IR Visible",compute="_compute_visible")
    sample_wt_ir = fields.Float(string="Wt of Sample (gm)")
    crucible_residue_ignition_ir = fields.Float(string="Wt of crucible +Residue after ignition (gm)")
    wt_empty_crucible_ir = fields.Float(string="Wt of empty crucible (gm)")
    diff_weight_ir = fields.Float(string="Diff. in weight (gm)",compute="_compute_diff_weight_ir")
    im = fields.Float(string="IM",compute="_compute_im")



    @api.depends('crucible_residue_ignition_ir', 'wt_empty_crucible_ir')
    def _compute_diff_weight_ir(self):
        for record in self:
            record.diff_weight_ir = record.crucible_residue_ignition_ir - record.wt_empty_crucible_ir

    @api.depends('diff_weight_ir', 'sample_wt_ir')
    def _compute_im(self):
        for record in self:
            if record.sample_wt_ir != 0:
                record.im = (record.diff_weight_ir * 100) / record.sample_wt_ir
            else:
                record.im = 0

    


    





    
   

    ### Compute Visible
    @api.depends('sample_parameters')
    def _compute_visible(self):
       

        for record in self:
            record.sio2_visible = False
            record.so3_visible = False
            record.ir_visible = False
            
            
               
            for sample in record.sample_parameters:
                print("Samples internal id",sample.internal_id)
                #  sio2
                if sample.internal_id == '807c1e3e-c9a2-4fc9-aaf4-6ca86b4d491d':
                    record.sio2_visible = True
                # so3
                if sample.internal_id == 'fb1602f9-1275-4846-b60a-80cf5b5b690c':
                    record.so3_visible = True
                # IR
                if sample.internal_id == '925cf1c1-8f15-41ee-9ffd-e60ccdf9022c':
                    record.ir_visible = True
                
                
                

    


      

    

    


    
     

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(OpcCementChemical, self).create(vals)
        # record.get_all_fields()
        record.eln_ref.write({'model_id':record.id})
        return record

    @api.depends('eln_ref')
    def _compute_grade_id(self):
        if self.eln_ref:
            self.grade = self.eln_ref.grade_id.id
    

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
        record = self.env['opc.cement.chemical'].browse(self.ids[0])
        field_values = {}
        for field_name, field in record._fields.items():
            field_value = record[field_name]
            field_values[field_name] = field_value

        return field_values