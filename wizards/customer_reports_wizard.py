from odoo import api, fields, models,_
from odoo.exceptions import UserError
import logging



class SampleReportsWizard(models.TransientModel):
    _name = "sample.reports.wizard"

    customer = fields.Many2one('res.partner',string="Customer")
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')

    def print_srf_reports(self):

        template_name = self.env['ir.actions.report'].search([('report_name','=','	lerm_civil.sample_wizard_report_template')]).report_name
        samples = self.env['lerm.srf.sample'].sudo().search([('customer_id','=',self.customer.id),('srf_id.srf_date','>=',self.from_date),('srf_id.srf_date','<=',self.to_date)])
        
        # import wdb ; wdb.set_trace()
        customer = self.customer
        return {
            'type': 'ir.actions.report',
            'report_type': 'qweb-html',
            'report_name': 'lerm_civil.sample_wizard_report_template',
            # 'report_name': template_name,
            'report_file': template_name,
            'data' : {'customer': customer.id,'from_date':self.from_date,'to_date':self.to_date}
        }

    def discard_print(self):
        return {'type': 'ir.actions.act_window_close'}