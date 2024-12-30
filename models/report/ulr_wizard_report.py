from odoo import models , fields,api
import json
import base64
import qrcode
from io import BytesIO
from lxml import etree

class ULRWizardReports(models.AbstractModel):
    _name = 'report.lerm_civil.ulr_wizard_report_template'
    _description = 'ULR Reports'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        # srf = self.env['lerm.civil.srf'].sudo().browse(srf_id)
        ulr = data.get('ulr')
        


        # import wdb;wdb.set_trace();
        samples = self.env['lerm.srf.sample'].sudo().search([('ulr_no','=',ulr)])

        # samples = data
        
        return {
                'sample_ids' : samples,
                'ulr':ulr,
            }