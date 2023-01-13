from odoo import api,fields,models

class SampleEntry(models.Model):
    _name = "lerm.sampleentry"
    _description = "Lerm SRF Sample"

    sample_id = fields.Char(string="Sample Id Mark")
    brand = fields.Char(string="Brand")
    size = fields.Char(string="Size")
    grade = fields.Char(string="Grade")
    sample_qty = fields.Char(string="Sample Qty")
    sample_received_by = fields.Char(string="Sample Received By")
    sample_received_date = fields.Date(string="Sample Received Date")
    Sample_description = fields.Char(string="Sample Description")
    reason_id = fields.Char(string="SSample Rejected / Reason")
    date_of_casting = fields.Date(string="Date Of Casting")



class LermSrf(models.Model):
    _name = "lerm.srf"
    _description = "Lerm SRF"
    _inherit=['lerm.sampleentry']

    srf_no = fields.Char(string="SRF No")
    srf_date = fields.Date("SRF Date")
    customer = fields.Many2one('res.partner',string="Customer")
    billing_customer = fields.Many2one('res.partner',string="Billing Customer")
    contact_person = fields.Char(string="Contact Person")
    mobile_no = fields.Char(string="Person Mobile No")
    email_id = fields.Char(string="Person Email id")
    client_ref = fields.Char(string="Client Reference")
    job_no = fields.Char(string="Job No")
    job_date = fields.Date(string="Job Date")

    @api.onchange('customer')
    def _compute_contact_person(self):
        self.contact_person = "Contact Person"
        


    @api.onchange('customer')
    def _compute_email(self):
        self.email_id = "Email id"
        
    

    @api.onchange('customer')
    def _compute_mobile_no(self):
        contact_obj = self.env['res.partner'].search([('name','=', self.customer.name)])
        self.mobile_no = ''
