from odoo import api,fields,models
import logging


_logger = logging.getLogger(__name__)


class LermSrf(models.Model):
    _name = "lerm.srf"
    _description = "Lerm SRF"

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
        contact_obj = self.env['res.partner'].search([('id','=', self.customer.id)])
        self.contact_person = contact_obj.name
        


    @api.onchange('customer')
    def _compute_email(self):
        contact_obj = self.env['res.partner'].search([('id','=', self.customer.id)])
        self.email_id = contact_obj.email
        
    

    @api.onchange('customer')
    def _compute_mobile_no(self):
        contact_obj = self.env['res.partner'].search([('id','=', self.customer.id)])
        self.mobile_no = contact_obj.mobile
