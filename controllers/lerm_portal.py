from odoo.addons.portal.controllers.portal import CustomerPortal , pager
from odoo.http import request
from odoo import http
from werkzeug.utils import secure_filename
import base64
import csv
import io
from io import StringIO
from datetime import datetime
import xlsxwriter
from odoo.exceptions import UserError,ValidationError
import json
from io import BytesIO
import xlrd
import logging
from odoo.exceptions import ValidationError



from odoo import http
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class LermSampleController(http.Controller):
    

    # @http.route('/sample/create', type='http', auth='user', website=True)
    # def create_sample_form(self, **kwargs):
    #     disciplines = request.env['lerm_civil.discipline'].sudo().search([])
    #     groups = request.env['lerm_civil.group'].sudo().search([])
    #     materials = request.env['product.template'].sudo().search([])
    #     samples = request.env['lerm.srf.sample'].sudo().search([])
    #     parameters = request.env['lerm.parameter.master'].sudo().search([])
    #     product_id = kwargs.get('product_id')

    #     grade_ids = []
    #     size_ids = []

    #     if product_id:
    #         product_id = int(product_id)
    #         grade_ids = request.env['lerm.grade.line'].sudo().search([('product_id', '=', product_id)])
    #         size_ids = request.env['lerm.size.line'].sudo().search([('product_id', '=', product_id)])
        
      
    #     return request.render('lerm_civil.create_sample_form', {
    #         'disciplines': disciplines,
    #         'groups': groups,
    #         'materials': materials,
    #         'samples': samples,
    #         'parameters': parameters,
    #         'grade_ids': grade_ids,
    #         'size_ids': size_ids,  # Pass sizes to the view
          
    #     })

    
    # @http.route('/sample/create/submit', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    # def submit_sample_form(self, **kwargs):
    #     discipline_id = kwargs.get('discipline_id')
    #     group_id = kwargs.get('group_ids')
    #     material_id = kwargs.get('material_id')
      
    #     grade_ids = request.httprequest.form.getlist('grade_ids')  # Ensure it returns a list
    #     size_ids = request.httprequest.form.getlist('size_ids')
    #     parameters = request.httprequest.form.getlist('parameters')

      
    #     # Create the sample record if all required fields are present
    #     if discipline_id and group_id and material_id:
    #         request.env['lerm.srf.sample'].sudo().create({
    #             'discipline_id': int(discipline_id),
    #             'group_id': int(group_id),
    #             'material_id': int(material_id), 
             
    #             'grade_ids': [(6, 0, [int(grade_id) for grade_id in grade_ids if grade_id])] if grade_ids else [],
    #             'size_ids': [(6, 0, [int(size_id) for size_id in size_ids if size_id])] if size_ids else [],
    #             'parameters': [(6, 0, list(map(int, parameters)))] if parameters else [],
               
    #         })

    #     return request.redirect('/sample/create')



  

    # @http.route('/sample/delete', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    # def delete_sample(self, **kwargs):
    #     sample_id = kwargs.get('sample_id')
    #     if sample_id:
    #         sample = request.env['lerm.srf.sample'].sudo().browse(int(sample_id))
    #         if sample.exists():
    #             sample.unlink()
    #     return request.redirect('/sample/create')

    @http.route('/sample/create', type='http', auth='user', website=True)
    def create_sample_form(self, **kwargs):
        # Fetch all necessary data for the form
        disciplines = request.env['lerm_civil.discipline'].sudo().search([])
        groups = request.env['lerm_civil.group'].sudo().search([])
        materials = request.env['product.template'].sudo().search([])
        samples = request.env['lerm.srf.sample'].sudo().search([])
        parameters = request.env['lerm.parameter.master'].sudo().search([])
        product_id = kwargs.get('product_id')

        grade_ids = []
        size_ids = []

        if product_id:
            product_id = int(product_id)
            grade_ids = request.env['lerm.grade.line'].sudo().search([('product_id', '=', product_id)])
            size_ids = request.env['lerm.size.line'].sudo().search([('product_id', '=', product_id)])

        

        return request.render('lerm_civil.create_sample_form', {
            'disciplines': disciplines,
            'groups': groups,
            'materials': materials,
            'samples': samples,
            'parameters': parameters,
            'grade_ids': grade_ids,
            'size_ids': size_ids,  # Pass sizes to the view
        })

    @http.route('/sample/create/submit', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def submit_sample_form(self, **kwargs):
        discipline_id = kwargs.get('discipline_id')
        group_id = kwargs.get('group_id')  # Ensure this matches the form
        material_id = kwargs.get('material_id')
        grade_ids = request.httprequest.form.getlist('grade_ids')  # Ensure it returns a list
        size_ids = request.httprequest.form.getlist('size_ids')
        parameters = request.httprequest.form.getlist('parameters')
        brand = kwargs.get('brand')

        # Create the sample record if all required fields are present
        if discipline_id and group_id and material_id:
            request.env['lerm.srf.sample'].sudo().create({
                'discipline_id': int(discipline_id),
                'group_id': int(group_id),
                'material_id': int(material_id),
                 'grade_ids': [(6, 0, [int(grade_id) for grade_id in grade_ids if grade_id])] if grade_ids else [],
                'size_ids': [(6, 0, [int(size_id) for size_id in size_ids if size_id])] if size_ids else [],
                'parameters': [(6, 0, list(map(int, parameters)))] if parameters else [],
                'brand': brand,
            })

        # Redirect to the form to see the updated samples
        return request.redirect('/sample/create?success=1')


   



  

    @http.route('/sample/delete', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def delete_sample(self, **kwargs):
        sample_id = kwargs.get('sample_id')
        if sample_id:
            sample = request.env['lerm.srf.sample'].sudo().browse(int(sample_id))
            if sample.exists():
                sample.unlink()
        return request.redirect('/sample/create')



   



    