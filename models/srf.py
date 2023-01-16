from odoo import api, fields, models


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
    reason_id = fields.Char(string="Sample Rejected / Reason")
    date_of_casting = fields.Date(string="Date Of Casting")
    sample_entry_id = fields.Many2one('lerm.srf',string="Sample id")


class LermSrf(models.Model):
    _name = "lerm.srf"
    _description = "Lerm SRF"

    srf_no = fields.Char(string="SRF No")
    srf_date = fields.Date("SRF Date")
    customer = fields.Many2one('res.partner', string="Customer")
    billing_customer = fields.Many2one('res.partner', string="Billing Customer")
    contact_person = fields.Char(string="Contact Person", compute='_compute_contact_person')
    mobile_no = fields.Char(string="Person Mobile No",compute='_compute_mobile_no')
    email_id = fields.Char(string="Person Email id", compute='_compute_email')
    client_ref = fields.Char(string="Client Reference")
    job_no = fields.Char(string="Job No")
    job_date = fields.Date(string="Job Date")
    sample_entry = fields.One2many("lerm.sampleentry", "sample_entry_id", string="Sample Entry")

    @api.onchange('customer')
    def _compute_contact_person(self):
        contact_obj = self.env['res.partner'].search([('id', '=', self.customer.id)])
        self.contact_person = contact_obj.name

    @api.onchange('customer')
    def _compute_email(self):
        contact_obj = self.env['res.partner'].search([('id', '=', self.customer.id)])
        self.email_id = contact_obj.email

    @api.onchange('customer')
    def _compute_mobile_no(self):
        contact_obj = self.env['res.partner'].search([('id', '=', self.customer.id)])
        self.mobile_no = contact_obj.mobile
