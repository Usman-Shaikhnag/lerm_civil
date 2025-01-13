from odoo import api, fields, models,_
from odoo.exceptions import UserError ,ValidationError
import logging
from datetime import datetime


# _logger = logging.getLogger(__name__)

class SampleTest(models.Model):
    _name = "sample.test.request"
    _description = "Sample Test"
    _rec_name = 'discipline_id'


    customer_id = fields.Many2one(
        'res.partner', 
        string="Customer", 
        
    )

    discipline_id = fields.Many2one(
        'lerm_civil.discipline', 
        string="Discipline", 
        
    )
    group_id = fields.Many2one(
        'lerm_civil.group', 
        string="Group", 
        
    )
    material_id = fields.Many2one(
        'product.template', 
        string="Material", 
        
    )
    grade_ids = fields.Many2one(
        'lerm.grade.line', 
        string="Grade",
        domain="[('product_id', '=', material_id)]",  # Filter grades by the selected material
    )

   
    size_ids = fields.Many2one(
        'lerm.size.line', 
        string="Sizes",
        domain="[('product_id', '=', material_id)]",  # Filter grades by the selected material
    )
    parameters = fields.Many2many(
        'lerm.parameter.master', 
        string="Parameters"
    )
    line_ids = fields.One2many(
        'sample.test.line', 
        'request_id', 
        string="Test Lines", 
     
    )

    @api.model
    def create(self, vals):
        record = super(SampleTest, self).create(vals)
        self._create_lines(record)
        return record

  

    def _create_lines(self, record):
        line_vals = {
            'request_id': record.id,
            'discipline_id': record.discipline_id.id,
            'group_id': record.group_id.id,
            'material_id': record.material_id.id,
            'grade_ids': record.grade_ids.id if record.grade_ids else False,
            'size_ids': record.size_ids.id if record.size_ids else False,
            'parameters': [(6, 0, record.parameters.ids)],
        }
        self.env['sample.test.line'].create(line_vals)

class SampleTestLine(models.Model):
    _name = 'sample.test.line'
    _description = 'Sample Test Line'

    request_id = fields.Many2one(
        'sample.test.request', 
        string="Request Reference", 
        
       
    )
    discipline_id = fields.Many2one(
        'lerm_civil.discipline', 
        string="Discipline", 
        
    )
    group_id = fields.Many2one(
        'lerm_civil.group', 
        string="Group", 
        
    )
    material_id = fields.Many2one(
        'product.template', 
        string="Material", 
        
    )
    grade_ids = fields.Many2one(
        'lerm.grade.line', 
        string="Grade",
        domain="[('product_id', '=', material_id)]",  # Filter grades by the selected material
    )
    size_ids = fields.Many2one(
        'lerm.size.line', 
        string="Size",
        domain="[('product_id', '=', material_id)]",  # Filter sizes by the selected material
    )
    parameters = fields.Many2many(
        'lerm.parameter.master', 
        string="Parameters"
    )