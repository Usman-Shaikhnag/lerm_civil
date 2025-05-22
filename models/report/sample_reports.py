from odoo import models , fields,api
import json
import base64
import qrcode
from io import BytesIO
from lxml import etree

class SampleReports(models.AbstractModel):
    _name = 'report.lerm_civil.sample_wizard_report_template'
    _description = 'Sample Reports'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        # srf = self.env['lerm.civil.srf'].sudo().browse(srf_id)
        customer = data.get('customer')
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        sample = data.get('samples')



        # import wdb;wdb.set_trace();
        samples = self.env['lerm.srf.sample'].sudo().search([('customer_id','=',customer),('srf_id.srf_date','>=',from_date),('srf_id.srf_date','<=',to_date)])
        customer = self.env['res.partner'].sudo().search([('id','=',customer)]).name

        # samples = data
        
        return {
                'sample_ids' : samples,
                'from_date':from_date,
                'to_date':to_date,
                'customer':customer
            }