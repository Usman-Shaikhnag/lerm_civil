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
    


    @http.route('/sample/create', type='http', auth='user', website=True)
    def create_sample_form(self, **kwargs):
        # Fetch all necessary data for the form
        disciplines = request.env['lerm_civil.discipline'].sudo().search([])
        groups = request.env['lerm_civil.group'].sudo().search([])
        materials = request.env['product.template'].sudo().search([])
        # samples = request.env['lerm.srf.sample'].sudo().search([])
        samples = request.env['sample.test.request'].sudo().search([])
        parameters = request.env['lerm.parameter.master'].sudo().search([])
        # customer = request.env['res.partner'].sudo().search([])
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
            # 'customer': customer,  # Pass sizes to the view
        })

    @http.route('/sample/create/submit', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def submit_sample_form(self, **kwargs):
        discipline_id = kwargs.get('discipline_id')
        group_id = kwargs.get('group_id')  # Ensure this matches the form
        material_id = kwargs.get('material_id')
        # grade_ids = request.httprequest.form.getlist('grade_ids')  # Ensure it returns a list
        grade_ids = kwargs.get('grade_ids')  # Single value
        size_ids = kwargs.get('size_ids')  # Single value
        # customer_id = kwargs.get('customer_id')  # Single value
        # size_ids = request.httprequest.form.getlist('size_ids')
        parameters = request.httprequest.form.getlist('parameters')
    

        # Create the sample record if all required fields are present
        if discipline_id and group_id and material_id:
            request.env['sample.test.request'].sudo().create({
                'discipline_id': int(discipline_id),
                # 'customer_id': int(customer_id),
                'group_id': int(group_id),
                'material_id': int(material_id),
                # 'grade_ids': [(6, 0, [int(grade_id) for grade_id in grade_ids if grade_id])] if grade_ids else [],
                'grade_ids': int(grade_ids) if grade_ids else None, 
                # 'size_ids': [(6, 0, [int(size_id) for size_id in size_ids if size_id])] if size_ids else [],
                'parameters': [(6, 0, list(map(int, parameters)))] if parameters else [],
                'size_ids': int(size_ids) if size_ids else None, 
            
            })

        # Redirect to the form to see the updated samples
        return request.redirect('/sample/create?success=1')

    # @http.route('/sample/create/submit', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    # def submit_sample_form(self, **kwargs):
    #     discipline_id = kwargs.get('discipline_id')
    #     group_id = kwargs.get('group_id')
    #     material_id = kwargs.get('material_id')
    #     grade_id = kwargs.get('grade_ids')  # Single value
    #     size_id = kwargs.get('size_ids')  # Single value
    #     parameters = request.httprequest.form.getlist('parameters')  # List of selected parameters

    #     if discipline_id and group_id and material_id:
    #         # Iterate over the parameters and create a line for each
    #         for parameter_id in parameters:
    #             request.env['sample.test.line'].sudo().create({
    #                 'discipline_id': int(discipline_id),
    #                 'group_id': int(group_id),
    #                 'material_id': int(material_id),
    #                 'grade_ids': int(grade_id) if grade_id else None,
    #                 'size_ids': int(size_id) if size_id else None,
    #                 'parameters': [(4, int(parameter_id))],  # Add parameter to Many2many field
    #             })

    #     # Redirect to the form with a success message
    #     return request.redirect('/sample/create?success=1')





   
    @http.route('/customers', type='http', auth='user', website=True)
    def customer_list(self, **kwargs):
        # Fetch all necessary data for the form
        customer = request.env['res.partner'].sudo().search([])
        samples = request.env['sample.test.request'].sudo().search([])
      

        return request.render('lerm_civil.customer_create_template', {
            'customer': customer,
            'samples': samples,
          
        })

    @http.route('/customers/create/submit', auth='user', website=True, methods=['POST'], csrf=True)
    def customer_create_submit(self, **kwargs):
        """
        Create a new customer based on form submission.
        """
        
        customer_id = kwargs.get('customer_id')
        if customer_id:
                # Create a sample test request associated with the new customer
                request.env['sample.test.request'].sudo().create({
                 'customer_id': int(customer_id),
                    # You can add additional fields here if needed
                })
        return request.redirect('/customers')






    


    @http.route('/sample/delete', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def delete_sample(self, **kwargs):
        sample_id = kwargs.get('sample_id')
        if sample_id:
            sample = request.env['sample.test.request'].sudo().browse(int(sample_id))
            if sample.exists():
                sample.unlink()
        return request.redirect('/sample/create')



   



    