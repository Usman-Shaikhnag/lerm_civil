from odoo import models , fields,api
import json
import base64
import qrcode
from io import BytesIO
from lxml import etree

class FineAggregateDatasheet(models.AbstractModel):
        _name = 'report.lerm_civil.lerm_fine_aggregate_datasheet'
        _description = 'Fine Aggregate DataSheet'
    
        @api.model
        def _get_report_values(self, docids, data):
            if data['fromsample'] == True:
                if 'active_id' in data['context']:
                    eln = self.env['lerm.eln'].sudo().search([('sample_id','=',data['context']['active_id'])])
                else:
                    eln = self.env['lerm.eln'].sudo().browse(docids) 
            else:
                if data['report_wizard'] == True:
                    eln = self.env['lerm.eln'].sudo().search([('id','=',data['eln'])])
                else:
                    eln = self.env['lerm.eln'].sudo().browse(data['eln_id'])
            model_id = eln.model_id
            # differnt location for product based
            # model_name = eln.material.product_based_calculation[0].ir_model.name 
            model_name = eln.material.product_based_calculation.filtered(lambda record: record.grade.id == eln.grade_id.id).ir_model.name
            if model_name:
                general_data = self.env[model_name].sudo().browse(model_id)
            else:
                general_data = self.env['lerm.eln'].sudo().browse(docids)
            return {
                'eln': eln,
                'data' : general_data
            }
        

