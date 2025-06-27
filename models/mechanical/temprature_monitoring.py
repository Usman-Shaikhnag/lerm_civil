from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import math
import re
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.ticker as ticker
import numpy as np
import math
from scipy.interpolate import CubicSpline , interp1d , Akima1DInterpolator
from scipy.optimize import minimize_scalar
from io import BytesIO
from scipy.interpolate import make_interp_spline


class EnviromentTemprature(models.Model):
    _name = 'enviroment.temprature'  
    _inherit = "lerm.eln" 

    _rec_name = "name"

    name = fields.Char("Name",default="Temperature Monitoring Of  Concreate")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    eln_ref = fields.Many2one('lerm.eln',string="Eln")
    grade = fields.Many2one('lerm.grade.line',string="Grade",compute="_compute_grade_id",store=True)

    @api.depends('eln_ref')
    def _compute_grade_id(self):
        if self.eln_ref:
            self.grade = self.eln_ref.grade_id.id

    # lab_name = fields.Selection([
    #         ('wadala', 'WADALA'),
    #         ('taloja', 'TALOJA')], string="Lab Name")
    concrete_pouring = fields.Text(string="Concrete Pouring and Data Recording")

    child_lines_temprature = fields.One2many('enviroment.tempraturee.line','parent_id',string="Parameter", copy=True)

    

    peak_max_temp = fields.Char(
        string="Peak Concrete Temperature ",  compute="_compute_peak_max_middle1", store=True
      )

    peak_max_temp_middle1_observed = fields.Char(
        string="Peak Concrete Temperature Observed At ", compute="_compute_peak_max_middle1", store=True
      )



    peak_max_temp_diff = fields.Char(
        string="Maximum Thermal Gradient ",  compute="_compute_peak_max_temp_diff", store=True
      )

    peak_max_temp_diff_observed = fields.Char(
        string="Maximum Thermal Gradient Observed At",  compute="_compute_peak_max_temp_diff", store=True
      )

    peak_max_temp_ambient = fields.Char(
        string="Peak Ambient Temperature  ",digits=(12,1),  compute="_compute_peak_max_ambient", store=True
      )

    peak_max_temp_ambient_observed = fields.Char(
        string="Peak Ambient Temperature Observed At " ,compute="_compute_peak_max_ambient",store=True
      )



    # @api.depends('child_lines_temprature.temp_diff')
    # def _compute_peak_max_temp_diff(self):
    #     for record in self:
    #         max_temp_diff = max(
    #             record.child_lines_temprature.mapped('temp_diff') or [0]
    #         )  # Use `or [0]` to handle cases with no child lines
    #         record.peak_max_temp_diff = max_temp_diff


    @api.depends('child_lines_temprature.ambient')
    def _compute_peak_max_ambient(self):
        for record in self:
            if record.child_lines_temprature:
                max_line = max(record.child_lines_temprature, key=lambda line: line.ambient)
                max_ambient = max_line.ambient
                measurement_time = max_line.measurement_time  # Assuming this field exists in `child_lines_temprature`
                day = max_line.day  # Assuming this field exists in `child_lines_temprature`
                
                if measurement_time and day:
                    formatted_time = measurement_time
                    formatted_day = day
                    record.peak_max_temp_ambient_observed = f"At {formatted_time} on {formatted_day}"
                else:
                    record.peak_max_temp_ambient_observed = "No measurement time available"
                
                # record.peak_max_temp_ambient = max_ambient
                record.peak_max_temp_ambient = f"{max_ambient} °C"
            else:
                # Default values if no child lines exist
                record.peak_max_temp_ambient = 0.0
                record.peak_max_temp_ambient_observed = "No data"



    @api.depends('child_lines_temprature.middle1')
    def _compute_peak_max_middle1(self):
        for record in self:
            if record.child_lines_temprature:
                # Find the maximum value of middle1
                max_middle1 = max(line.middle1 for line in record.child_lines_temprature)
                
                # Filter lines with the maximum value of middle1
                max_lines = [line for line in record.child_lines_temprature if line.middle1 == max_middle1]
                
                # Extract times and days from the matching lines
                if max_lines:
                    measurement_times = []
                    day = max_lines[0].day  # Assuming all lines with max middle1 have the same day
                    
                    for max_line in max_lines:
                        measurement_time = max_line.measurement_time
                        if measurement_time:
                            measurement_times.append(measurement_time)
                    
                    # Format observed data
                    if len(measurement_times) == 1:
                        record.peak_max_temp_middle1_observed = f"At {measurement_times[0]} on {day}"
                    elif len(measurement_times) > 1:
                        record.peak_max_temp_middle1_observed = (
                            f"Between {measurement_times[0]} - {measurement_times[-1]} on {day}"
                        )
                    else:
                        record.peak_max_temp_middle1_observed = "No measurement time available"
                    
                    # Set the peak max temperature with °C
                    record.peak_max_temp = f"{max_middle1:.1f} °C"
            else:
                # Default values when no child lines exist
                record.peak_max_temp = "0.0 °C"
                record.peak_max_temp_middle1_observed = "No data"


    @api.depends('child_lines_temprature.temp_diff')
    def _compute_peak_max_temp_diff(self):
        for record in self:
            if record.child_lines_temprature:
                # Find the maximum value of temp_diff
                max_temp_diff = max(line.temp_diff for line in record.child_lines_temprature)
                
                # Filter lines with the maximum value of temp_diff
                max_lines = [line for line in record.child_lines_temprature if line.temp_diff == max_temp_diff]
                
                # Extract times and days from the matching lines
                if max_lines:
                    measurement_times = []
                    day = max_lines[0].day  # Assuming all lines with max temp_diff have the same day
                    
                    for max_line in max_lines:
                        measurement_time = max_line.measurement_time
                        if measurement_time:
                            measurement_times.append(measurement_time)
                    
                    # Format observed data
                    if len(measurement_times) == 1:
                        record.peak_max_temp_diff_observed = f"At {measurement_times[0]} on {day}"
                    elif len(measurement_times) > 1:
                        record.peak_max_temp_diff_observed = (
                            f"Between {measurement_times[0]} - {measurement_times[-1]} on {day}"
                        )
                    else:
                        record.peak_max_temp_diff_observed = "No measurement time available"
                    
                    # Set the peak max temperature with °C
                    record.peak_max_temp_diff = f"{max_temp_diff:.1f} °C"
            else:
                # Default values when no child lines exist
                record.peak_max_temp_diff = "0.0 °C"
                record.peak_max_temp_diff_observed = "No data"



    graph_image_20mm = fields.Binary("Line Chart", compute="_compute_graph_image_20mm", store=True)



    # def generate_line_chart_20mm(self):
    #     days = []
    #     core_bottom = []
    #     core_middle = []
    #     core_top = []
    #     cover_bottom = []
    #     cover_middle = []
    #     cover_top = []
    #     ambient = []

    #     # Process data for alignment
    #     for line in self.child_lines_temprature:
    #         day = line.day
    #         if isinstance(line.bottom, list):  # Handle multiple entries for the same day
    #             for i in range(len(line.bottom)):
    #                 days.append(day)  # Same day for all entries
    #                 core_bottom.append(line.bottom[i])
    #                 core_middle.append(line.middle[i])
    #                 core_top.append(line.top[i])
    #                 cover_bottom.append(line.bottom1[i])
    #                 cover_middle.append(line.middle1[i])
    #                 cover_top.append(line.top1[i])
    #                 ambient.append(line.ambient[i])
    #         else:  # Single value per day
    #             days.append(day)
    #             core_bottom.append(line.bottom)
    #             core_middle.append(line.middle)
    #             core_top.append(line.top)
    #             cover_bottom.append(line.bottom1)
    #             cover_middle.append(line.middle1)
    #             cover_top.append(line.top1)
    #             ambient.append(line.ambient)

    #     # Create the plot
    #     plt.figure(figsize=(14, 8))

    #     # Unique days for plotting
    #     unique_days = sorted(set(days))
        
    #     # Create a mapping from days to indices for plotting
    #     day_to_index = {day: i for i, day in enumerate(unique_days)}

    #     # Plot the temperature data, using indices for x values
    #     plt.plot([day_to_index[day] for day in days], core_bottom, label='Core Area - Bottom', marker='o', color='blue')
    #     plt.plot([day_to_index[day] for day in days], core_middle, label='Core Area - Middle', marker='o', color='orange')
    #     plt.plot([day_to_index[day] for day in days], core_top, label='Core Area - Top', marker='o', color='green')
    #     plt.plot([day_to_index[day] for day in days], cover_bottom, label='Cover Area - Bottom', marker='o', color='red')
    #     plt.plot([day_to_index[day] for day in days], cover_middle, label='Cover Area - Middle', marker='o', color='purple')
    #     plt.plot([day_to_index[day] for day in days], cover_top, label='Cover Area - Top', marker='o', color='brown')
    #     plt.plot([day_to_index[day] for day in days], ambient, label='Ambient', linestyle='--', color='black')

    #     # Add vertical lines for each day
    #     for i, day in enumerate(unique_days):
    #         plt.axvline(x=i, color='gray', linestyle='--', linewidth=0.5)

    #     # Customize the graph
    #     plt.xlabel('Days', fontsize=14)
    #     plt.ylabel('Temperature (°C)', fontsize=14)
    #     plt.xticks(ticks=range(len(unique_days)), labels=unique_days, fontsize=12)  # Set x-ticks to unique days
    #     plt.yticks(fontsize=12)
    #     plt.legend(fontsize=12)
    #     plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    #     # Save the plot to a binary field
    #     buf = io.BytesIO()
    #     plt.savefig(buf, format='png', bbox_inches='tight')
    #     buf.seek(0)
    #     chart_image20mm = base64.b64encode(buf.read()).decode('utf-8')
    #     buf.close()
    #     plt.close()  # Free up memory

    #     return chart_image20mm


    # def generate_line_chart_20mm(self):
  
    #     # Data preparation
    #     sr_no = []  # Serial numbers for x-axis
    #     core_bottom = []
    #     core_middle = []
    #     core_top = []
    #     cover_bottom = []
    #     cover_middle = []
    #     cover_top = []
    #     ambient = []

    #     current_sr_no = 1  # Starting serial number

    #     # Process data for alignment
    #     for line in self.child_lines_temprature:
    #         if isinstance(line.bottom, list):  # Handle multiple entries for the same day
    #             for i in range(len(line.bottom)):
    #                 sr_no.append(current_sr_no)  # Use `sr_no` instead of days
    #                 core_bottom.append(line.bottom[i])
    #                 core_middle.append(line.middle[i])
    #                 core_top.append(line.top[i])
    #                 cover_bottom.append(line.bottom1[i])
    #                 cover_middle.append(line.middle1[i])
    #                 cover_top.append(line.top1[i])
    #                 ambient.append(line.ambient[i])
    #             current_sr_no += 1  # Increment serial number for each day
    #         else:  # Single value per day
    #             sr_no.append(current_sr_no)  # Use `sr_no` instead of days
    #             core_bottom.append(line.bottom)
    #             core_middle.append(line.middle)
    #             core_top.append(line.top)
    #             cover_bottom.append(line.bottom1)
    #             cover_middle.append(line.middle1)
    #             cover_top.append(line.top1)
    #             ambient.append(line.ambient)
    #             current_sr_no += 1  # Increment serial number for the next day

    #     # Create the plot
    #     plt.figure(figsize=(14, 8))

    #     # Plot the temperature data using `sr_no` for x values
    #     plt.plot(sr_no, core_bottom, label='Core Area - Bottom', marker='o', color='blue')
    #     plt.plot(sr_no, core_middle, label='Core Area - Middle', marker='o', color='orange')
    #     plt.plot(sr_no, core_top, label='Core Area - Top', marker='o', color='green')
    #     plt.plot(sr_no, cover_bottom, label='Cover Area - Bottom', marker='o', color='red')
    #     plt.plot(sr_no, cover_middle, label='Cover Area - Middle', marker='o', color='purple')
    #     plt.plot(sr_no, cover_top, label='Cover Area - Top', marker='o', color='brown')
    #     plt.plot(sr_no, ambient, label='Ambient', linestyle='--', color='black')

    #     # Add vertical lines for each `sr_no`
    #     for serial in sr_no:
    #         plt.axvline(x=serial, color='cyan', linestyle='-', linewidth=1)  # Draw vertical line

    #     # Add labels inside the plot area at the bottom for each sr_no
    #     for i, serial in enumerate(sr_no):
    #         # Place the label slightly below the minimum y limit of the plot
    #         plt.text(serial, plt.ylim()[0] - (0.05 * (plt.ylim()[1] - plt.ylim()[0])), 
    #                 f'SR {serial}', color='cyan', rotation=90, fontsize=10,
    #                 verticalalignment='top', horizontalalignment='center')

    #     # Customize the graph
    #     plt.xlabel('Serial Number (SR No.)', fontsize=14)
    #     plt.ylabel('Temperature (°C)', fontsize=14)
    #     plt.xticks(ticks=sr_no, labels=[f'SR {serial}' for serial in sr_no], fontsize=10, rotation=45)  # Set x-ticks
    #     plt.yticks(fontsize=12)
    #     plt.legend(fontsize=12)
    #     plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    #     # Save the plot to a binary field
    #     buf = io.BytesIO()
    #     plt.savefig(buf, format='png', bbox_inches='tight')
    #     buf.seek(0)
    #     chart_image20mm = base64.b64encode(buf.read()).decode('utf-8')
    #     buf.close()
    #     plt.close()  # Free up memory

    #     return chart_image20mm

    def generate_line_chart_20mm(self):
        import matplotlib.pyplot as plt
        import io
        import base64

        # Data preparation
        days = []  # Days for x-axis
        core_bottom = []
        core_middle = []
        core_top = []
        cover_bottom = []
        cover_middle = []
        cover_top = []
        ambient = []

        # Process data for alignment
        for line in self.child_lines_temprature:
            day = line.day
            if isinstance(line.bottom, list):  # Handle multiple entries for the same day
                for i in range(len(line.bottom)):
                    days.append(day)  # Same day for all entries
                    core_bottom.append(line.bottom[i])
                    core_middle.append(line.middle[i])
                    core_top.append(line.top[i])
                    cover_bottom.append(line.bottom1[i])
                    cover_middle.append(line.middle1[i])
                    cover_top.append(line.top1[i])
                    ambient.append(line.ambient[i])
            else:  # Single value per day
                days.append(day)
                core_bottom.append(line.bottom)
                core_middle.append(line.middle)
                core_top.append(line.top)
                cover_bottom.append(line.bottom1)
                cover_middle.append(line.middle1)
                cover_top.append(line.top1)
                ambient.append(line.ambient)

        # Create the plot
        plt.figure(figsize=(14, 8))

        # Create a list of x positions for each entry
        x_positions = list(range(len(days)))  # Create x positions based on the number of entries

        # Plot the temperature data using x positions for plotting
        plt.plot(x_positions, core_bottom, label='Core Area - Bottom', marker='o', color='blue')
        plt.plot(x_positions, core_middle, label='Core Area - Middle', marker='o', color='orange')
        plt.plot(x_positions, core_top, label='Core Area - Top', marker='o', color='green')
        plt.plot(x_positions, cover_bottom, label='Cover Area - Bottom', marker='o', color='red')
        plt.plot(x_positions, cover_middle, label='Cover Area - Middle', marker='o', color='purple')
        plt.plot(x_positions, cover_top, label='Cover Area - Top', marker='o', color='brown')
        plt.plot(x_positions, ambient, label='Ambient', linestyle='--', color='black')

        # Add vertical lines for each day
        for pos in x_positions:
            plt.axvline(x=pos, color='cyan', linestyle='-', linewidth=1)  # Draw vertical line

        # Add day labels inside the plot area for each position
        for i, day in enumerate(days):
            # Place the label slightly below the minimum y limit of the plot
            plt.text(i, plt.ylim()[0] - (0.05 * (plt.ylim()[1] - plt.ylim()[0])), 
                    day, color='cyan', rotation=90, fontsize=10,
                    verticalalignment='top', horizontalalignment='center')

        # Customize the graph
        plt.xlabel('Days', fontsize=14)
        plt.ylabel('Temperature (°C)', fontsize=14)
        plt.xticks(ticks=x_positions, labels=days, fontsize=10, rotation=45)  # Set x-ticks to days
        plt.yticks(fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Save the plot to a binary field
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        chart_image20mm = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close()  # Free up memory

        return chart_image20mm






    @api.depends('child_lines_temprature')
    def _compute_graph_image_20mm(self):
        try:
            for record in self:
                chart_image20mm = record.generate_line_chart_20mm()
                record.graph_image_20mm = chart_image20mm
        except:
            pass 




    def open_eln_page(self):
        # import wdb; wdb.set_trace()

        return {
                'view_mode': 'form',
                'res_model': "lerm.eln",
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': self.eln_ref.id,
                
            }           


    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(EnviromentTemprature, self).create(vals)
        # record.get_all_fields()
        record.eln_ref.write({'model_id':record.id})
        return record







    @api.depends('eln_ref')
    def _compute_sample_parameters(self):
        # records = self.env['lerm.eln'].sudo().search([('id','=', record.eln_id.id)]).parameters_result
        # print("records",records)
        # self.sample_parameters = records
        for record in self:
            records = record.eln_ref.parameters_result.parameter.ids
            record.sample_parameters = records
            print("Records",records)



    def get_all_fields(self):
        record = self.env['enviroment.temprature'].browse(self.ids[0])
        field_values = {}
        for field_name, field in record._fields.items():
            field_value = record[field_name]
            field_values[field_name] = field_value

        return field_values




class EnviromentTempratureLine(models.Model):
    _name = "enviroment.tempraturee.line"
    parent_id = fields.Many2one('enviroment.temprature',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr No.",readonly=True, copy=False, default=1)

    day = fields.Char(string="Day")
    date = fields.Date("Date")

   
    measurement_time = fields.Char(string="Time")
    bottom = fields.Float(string="bottom",digits=(12,1))
    middle = fields.Float(string="Middle",digits=(12,1))
    top = fields.Float(string="Top",digits=(12,1))
    temp_diff = fields.Float(string="Thermal Gradient",digits=(12,1),compute="_compute_temp_diff", store=True)

     
    bottom1 = fields.Float(string="bottom",digits=(12,1))
    middle1 = fields.Float(string="Middle",digits=(12,1))
    top1 = fields.Float(string="Top",digits=(12,1))
    temp_diff1 = fields.Float(string="Thermal Gradient",digits=(12,1),compute="_compute_temp_diff1", store=True)

    ambient = fields.Float(string="Ambient",digits=(12,1))


    @api.depends('middle', 'top')
    def _compute_temp_diff(self):
        for record in self:
            record.temp_diff = record.middle - record.top

    @api.depends('middle1', 'top1')
    def _compute_temp_diff1(self):
        for record in self:
            record.temp_diff1 = record.top1 - record.middle1




    

    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(EnviromentTempratureLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1


   