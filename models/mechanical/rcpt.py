from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math


class RcptConcreteCube(models.Model):
    _name = "mechanical.rcpt.concrete.cube"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name1 = fields.Char("Name",default="Concrete RCPT")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    eln_ref = fields.Many2one('lerm.eln',string="ELN")

    age_of_days = fields.Selection([
        ('3days', '3 Days'),
        ('7days', '7 Days'),
        ('14days', '14 Days'),
        ('28days', '28 Days'),
    ], string='Age', default='28days',required=True,compute="_compute_age_of_days")
    date_of_casting = fields.Date(string="Date of Casting",compute="compute_date_of_casting")
    date_of_testing = fields.Date(string="Date of Testing")

    age_of_test = fields.Integer("Age of Test, days",compute="compute_age_of_test")
    difference = fields.Integer("Difference",compute="compute_difference")

    temp_conc_surface = fields.Char("Temp.of Concrete Surface(°C)")
    temp_around_specimen = fields.Char("Temp.around the Specimen(°C)")
    date_conditioning = fields.Date(string="Date Of Conditiong")
    current_apply = fields.Char("Current Applied")
    int_temp_naoh = fields.Char("Initial Temp of NaOH(°C)")
    int_temp_nacl = fields.Char("Initial Temp of Nacl(°C)")

    date_specimen_prepared = fields.Datetime(string="Date & time Specimen Prepared")
    date_conditioning_started = fields.Datetime(string="Date & time Conditioning Started")
    date_vaccum_started = fields.Datetime(string="Date & time Vaccum Started:")
    date_water_added = fields.Datetime(string="Date & time Water Added:")
    date_vaccum_turn_of = fields.Datetime(string="Date & time Vaccum Turn Off:")
    date_soaking_started = fields.Datetime(string="Date & time Soaking Started:")
    date_soaking_completed = fields.Datetime(string="Date & time Soaking Completed:")










    





    @api.onchange('eln_ref')
    def _compute_age_of_days(self):
        for record in self:
            if record.eln_ref.sample_id:
                sample_record = self.env['lerm.srf.sample'].sudo().search([('id','=', record.eln_ref.sample_id.id)]).days_casting
                if sample_record == '3':
                    record.age_of_days = '3days'
                elif sample_record == '7':
                    record.age_of_days = '7days'
                elif sample_record == '14':
                    record.age_of_days = '14days'
                elif sample_record == '28':
                    record.age_of_days = '28days'
                else:
                    record.age_of_days = None
            else:
                record.age_of_days = None

    @api.onchange('eln_ref')
    def compute_date_of_casting(self):
        for record in self:
            if record.eln_ref.sample_id:
                sample_record = self.env['lerm.srf.sample'].sudo().search([('id','=', record.eln_ref.sample_id.id)]).date_casting
                record.date_of_casting = sample_record
            else:
                record.date_of_casting = None

    @api.depends('date_of_testing','date_of_casting')
    def compute_age_of_test(self):
        for record in self:
            if record.date_of_casting and record.date_of_testing:
                date1 = fields.Date.from_string(record.date_of_casting)
                date2 = fields.Date.from_string(record.date_of_testing)
                date_difference = (date2 - date1).days
                record.age_of_test = date_difference
            else:
                record.age_of_test = 0

    @api.depends('age_of_test','age_of_days')
    def compute_difference(self):
        for record in self:
            age_of_days = 0
            if record.age_of_days == '3days':
                age_of_days = 3
            elif record.age_of_days == '7days':
                age_of_days = 7
            elif record.age_of_days == '14days':
                age_of_days = 14
            elif record.age_of_days == '28days':
                age_of_days = 28
            else:
                age_of_days = 0
            record.difference = record.age_of_test - age_of_days



    child_lines = fields.One2many('mechanical.rcpt.concrete.cube.line','parent_id',string="Parameter")
    # io_sample1 = fields.Float(string="Io",compute="_compute_io_sample1", store=True)
    # io_sample2 = fields.Float(string="Io",compute="_compute_io_sample2",store=True)
    # io_sample3 = fields.Float(string="Io",compute="_compute_io_sample3",store=True)
    # i30_sample1 = fields.Float(string="I30",compute="_compute_i30_sample1",store=True)
    # i30_sample2 = fields.Float(string="I30",compute="_compute_i30_sample2",store=True)
    # i30_sample3 = fields.Float(string="I30",compute="_compute_i30_sample3",store=True)
    # i60_sample1 = fields.Float(string="I60",compute="_compute_i60_sample1",store=True)
    # i60_sample2 = fields.Float(string="I60",compute="_compute_i60_sample2",store=True)
    # i60_sample3 = fields.Float(string="I60",compute="_compute_i60_sample3",store=True)
    # i90_sample1 = fields.Float(string="I90",compute="_compute_i90_sample1",store=True)
    # i90_sample2 = fields.Float(string="I90",compute="_compute_i90_sample2",store=True)
    # i90_sample3 = fields.Float(string="I90",compute="_compute_i90_sample3",store=True)
    # i120_sample1 = fields.Float(string="I120",compute="_compute_i120_sample1",store=True)
    # i120_sample2 = fields.Float(string="I120",compute="_compute_i120_sample2",store=True)
    # i120_sample3 = fields.Float(string="I120",compute="_compute_i120_sample3",store=True)
    # i150_sample1 = fields.Float(string="I150",compute="_compute_i150_sample1",store=True)
    # i150_sample2 = fields.Float(string="I150",compute="_compute_i150_sample2",store=True)
    # i150_sample3 = fields.Float(string="I150",compute="_compute_i150_sample3",store=True)
    # i180_sample1 = fields.Float(string="I180",compute="_compute_i180_sample1",store=True)
    # i180_sample2 = fields.Float(string="I180",compute="_compute_i180_sample2",store=True)
    # i180_sample3 = fields.Float(string="I180",compute="_compute_i180_sample3",store=True)
    # i210_sample1 = fields.Float(string="I210",compute="_compute_i210_sample1",store=True)
    # i210_sample2 = fields.Float(string="I210",compute="_compute_i210_sample2",store=True)
    # i210_sample3 = fields.Float(string="I210",compute="_compute_i210_sample3",store=True)
    # i240_sample1 = fields.Float(string="I240",compute="_compute_i240_sample1",store=True)
    # i240_sample2 = fields.Float(string="I240",compute="_compute_i240_sample2",store=True)
    # i240_sample3 = fields.Float(string="I240",compute="_compute_i240_sample3",store=True)
    # i270_sample1 = fields.Float(string="I270",compute="_compute_i270_sample1",store=True)
    # i270_sample2 = fields.Float(string="I270",compute="_compute_i270_sample2",store=True)
    # i270_sample3 = fields.Float(string="I270",compute="_compute_i270_sample3",store=True)
    # i300_sample1 = fields.Float(string="I300",compute="_compute_i300_sample1",store=True)
    # i300_sample2 = fields.Float(string="I300",compute="_compute_i300_sample2",store=True)
    # i300_sample3 = fields.Float(string="I300",compute="_compute_i300_sample3",store=True)
    # sample1_i330 = fields.Float(string="I330",compute="_compute_sample1_i330",store=True)
    # sample2_i330 = fields.Float(string="I330",compute="_compute_sample2_i330",store=True)
    # sample3_i330 = fields.Float(string="I330",compute="_compute_sample3_i330",store=True)
    
    # i360_sample1 = fields.Float(string="I360",compute="_compute_i360_sample1",store=True)
    # i360_sample2 = fields.Float(string="I360",compute="_compute_i360_sample2",store=True)
    # i360_sample3 = fields.Float(string="I360",compute="_compute_i360_sample3",store=True)

    

    # @api.depends('child_lines.io')
    # def _compute_io_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 first_child_line = record.child_lines[0]
    #                 record.io_sample1 = first_child_line.io*1000
    #             else:
    #                 record.io_sample1 = 0.0
    #         else:
    #             record.io_sample1 = 0.0

    # @api.depends('child_lines.io')
    # def _compute_io_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 second_child_line = record.child_lines[1]
    #                 record.io_sample2 = second_child_line.io*1000
    #             else:
    #                 record.io_sample2 = 0.0
    #         else:
    #             record.io_sample2 = 0.0

    # @api.depends('child_lines.io')
    # def _compute_io_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 third_child_line = record.child_lines[2]
    #                 record.io_sample3 = third_child_line.io*1000
    #             else:
    #                 record.io_sample3 = 0.0
    #         else:
    #             record.io_sample3 = 0.0


    # @api.depends('child_lines.i30')
    # def _compute_i30_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i30_first_child_line = record.child_lines[0]
    #                 record.i30_sample1 = i30_first_child_line.i30*1000
    #             else:
    #                 record.i30_sample1 = 0.0
    #         else:
    #             record.i30_sample1 = 0.0

    # @api.depends('child_lines.i30')
    # def _compute_i30_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i30_second_child_line = record.child_lines[1]
    #                 record.i30_sample2 = i30_second_child_line.i30*1000
    #             else:
    #                 record.i30_sample2 = 0.0
    #         else:
    #             record.i30_sample2 = 0.0

    # @api.depends('child_lines.i30')
    # def _compute_i30_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i30_third_child_line = record.child_lines[2]
    #                 record.i30_sample3 = i30_third_child_line.i30*1000
    #             else:
    #                 record.i30_sample3 = 0.0
    #         else:
    #             record.i30_sample3 = 0.0

    # @api.depends('child_lines.i60')
    # def _compute_i60_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i60_first_child_line = record.child_lines[0]
    #                 record.i60_sample1 = i60_first_child_line.i60*1000
    #             else:
    #                 record.i60_sample1 = 0.0
    #         else:
    #             record.i60_sample1 = 0.0

    # @api.depends('child_lines.i60')
    # def _compute_i60_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i60_second_child_line = record.child_lines[1]
    #                 record.i60_sample2 = i60_second_child_line.i60*1000
    #             else:
    #                 record.i60_sample2 = 0.0
    #         else:
    #             record.i60_sample2 = 0.0

    # @api.depends('child_lines.i60')
    # def _compute_i60_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i60_third_child_line = record.child_lines[2]
    #                 record.i60_sample3 = i60_third_child_line.i60*1000
    #             else:
    #                 record.i60_sample3 = 0.0
    #         else:
    #             record.i60_sample3 = 0.0

    # @api.depends('child_lines.i90')
    # def _compute_i90_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i90_first_child_line = record.child_lines[0]
    #                 record.i90_sample1 = i90_first_child_line.i90*1000
    #             else:
    #                 record.i90_sample1 = 0.0
    #         else:
    #             record.i90_sample1 = 0.0

    # @api.depends('child_lines.i90')
    # def _compute_i90_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i90_second_child_line = record.child_lines[1]
    #                 record.i90_sample2 = i90_second_child_line.i90*1000
    #             else:
    #                 record.i90_sample2 = 0.0
    #         else:
    #             record.i90_sample2 = 0.0

    # @api.depends('child_lines.i90')
    # def _compute_i90_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i90_third_child_line = record.child_lines[2]
    #                 record.i90_sample3 = i90_third_child_line.i90*1000
    #             else:
    #                 record.i90_sample3 = 0.0
    #         else:
    #             record.i90_sample3 = 0.0

    # @api.depends('child_lines.i120')
    # def _compute_i120_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i120_first_child_line = record.child_lines[0]
    #                 record.i120_sample1 = i120_first_child_line.i120*1000
    #             else:
    #                 record.i120_sample1 = 0.0
    #         else:
    #             record.i120_sample1 = 0.0

    # @api.depends('child_lines.i120')
    # def _compute_i120_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i120_second_child_line = record.child_lines[1]
    #                 record.i120_sample2 = i120_second_child_line.i120*1000
    #             else:
    #                 record.i120_sample2 = 0.0
    #         else:
    #             record.i120_sample2 = 0.0

    # @api.depends('child_lines.i120')
    # def _compute_i120_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i120_third_child_line = record.child_lines[2]
    #                 record.i120_sample3 = i120_third_child_line.i120*1000
    #             else:
    #                 record.i120_sample3 = 0.0
    #         else:
    #             record.i120_sample3 = 0.0

    
    # @api.depends('child_lines.i150')
    # def _compute_i150_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i150_first_child_line = record.child_lines[0]
    #                 record.i150_sample1 = i150_first_child_line.i150*1000
    #             else:
    #                 record.i150_sample1 = 0.0
    #         else:
    #             record.i150_sample1 = 0.0

    # @api.depends('child_lines.i150')
    # def _compute_i150_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i150_second_child_line = record.child_lines[1]
    #                 record.i150_sample2 = i150_second_child_line.i150*1000
    #             else:
    #                 record.i150_sample2 = 0.0
    #         else:
    #             record.i150_sample2 = 0.0

    # @api.depends('child_lines.i150')
    # def _compute_i150_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i150_third_child_line = record.child_lines[2]
    #                 record.i150_sample3 = i150_third_child_line.i150*1000
    #             else:
    #                 record.i150_sample3 = 0.0
    #         else:
    #             record.i150_sample3 = 0.0

    # @api.depends('child_lines.i180')
    # def _compute_i180_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i180_first_child_line = record.child_lines[0]
    #                 record.i180_sample1 = i180_first_child_line.i180*1000
    #             else:
    #                 record.i180_sample1 = 0.0
    #         else:
    #             record.i180_sample1 = 0.0

    # @api.depends('child_lines.i180')
    # def _compute_i180_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i180_second_child_line = record.child_lines[1]
    #                 record.i180_sample2 = i180_second_child_line.i180*1000
    #             else:
    #                 record.i180_sample2 = 0.0
    #         else:
    #             record.i180_sample2 = 0.0

    # @api.depends('child_lines.i180')
    # def _compute_i180_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i180_third_child_line = record.child_lines[2]
    #                 record.i180_sample3 = i180_third_child_line.i180*1000
    #             else:
    #                 record.i180_sample3 = 0.0
    #         else:
    #             record.i180_sample3 = 0.0

    # @api.depends('child_lines.i210')
    # def _compute_i210_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i210_first_child_line = record.child_lines[0]
    #                 record.i210_sample1 = i210_first_child_line.i210*1000
    #             else:
    #                 record.i210_sample1 = 0.0
    #         else:
    #             record.i210_sample1 = 0.0

    # @api.depends('child_lines.i210')
    # def _compute_i210_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i210_second_child_line = record.child_lines[1]
    #                 record.i210_sample2 = i210_second_child_line.i210*1000
    #             else:
    #                 record.i210_sample2 = 0.0
    #         else:
    #             record.i210_sample2 = 0.0

    # @api.depends('child_lines.i210')
    # def _compute_i210_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i210_third_child_line = record.child_lines[2]
    #                 record.i210_sample3 = i210_third_child_line.i210*1000
    #             else:
    #                 record.i210_sample3 = 0.0
    #         else:
    #             record.i210_sample3 = 0.0


    # @api.depends('child_lines.i240')
    # def _compute_i240_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i240_first_child_line = record.child_lines[0]
    #                 record.i240_sample1 = i240_first_child_line.i240*1000
    #             else:
    #                 record.i240_sample1 = 0.0
    #         else:
    #             record.i240_sample1 = 0.0

    # @api.depends('child_lines.i240')
    # def _compute_i240_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i240_second_child_line = record.child_lines[1]
    #                 record.i240_sample2 = i240_second_child_line.i240*1000
    #             else:
    #                 record.i240_sample2 = 0.0
    #         else:
    #             record.i240_sample2 = 0.0

    # @api.depends('child_lines.i240')
    # def _compute_i240_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i240_third_child_line = record.child_lines[2]
    #                 record.i240_sample3 = i240_third_child_line.i240*1000
    #             else:
    #                 record.i240_sample3 = 0.0
    #         else:
    #             record.i240_sample3 = 0.0

    
    # @api.depends('child_lines.i270')
    # def _compute_i270_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i270_first_child_line = record.child_lines[0]
    #                 record.i270_sample1 = i270_first_child_line.i270*1000
    #             else:
    #                 record.i270_sample1 = 0.0
    #         else:
    #             record.i270_sample1 = 0.0

    # @api.depends('child_lines.i270')
    # def _compute_i270_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i270_second_child_line = record.child_lines[1]
    #                 record.i270_sample2 = i270_second_child_line.i270*1000
    #             else:
    #                 record.i270_sample2 = 0.0
    #         else:
    #             record.i270_sample2 = 0.0

    # @api.depends('child_lines.i270')
    # def _compute_i270_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i270_third_child_line = record.child_lines[2]
    #                 record.i270_sample3 = i270_third_child_line.i270*1000
    #             else:
    #                 record.i270_sample3 = 0.0
    #         else:
    #             record.i270_sample3 = 0.0

    # @api.depends('child_lines.i300')
    # def _compute_i300_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i300_first_child_line = record.child_lines[0]
    #                 record.i300_sample1 = i300_first_child_line.i300*1000
    #             else:
    #                 record.i300_sample1 = 0.0
    #         else:
    #             record.i300_sample1 = 0.0

    # @api.depends('child_lines.i300')
    # def _compute_i300_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i300_second_child_line = record.child_lines[1]
    #                 record.i300_sample2 = i300_second_child_line.i300*1000
    #             else:
    #                 record.i300_sample2 = 0.0
    #         else:
    #             record.i300_sample2 = 0.0

    # @api.depends('child_lines.i300')
    # def _compute_i300_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i300_third_child_line = record.child_lines[2]
    #                 record.i300_sample3 = i300_third_child_line.i300*1000
    #             else:
    #                 record.i300_sample3 = 0.0
    #         else:
    #             record.i300_sample3 = 0.0

   
    
    # @api.depends('child_lines.i330')
    # def _compute_sample1_i330(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 sample1_i330_first_child_line = record.child_lines[0]
    #                 record.sample1_i330 = sample1_i330_first_child_line.i330*1000
    #             else:
    #                 record.sample1_i330 = 0.0
    #         else:
    #             record.sample1_i330 = 0.0

    # @api.depends('child_lines.i330')
    # def _compute_sample2_i330(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 sample2_i330_sec_child_line = record.child_lines[1]
    #                 record.sample2_i330 = sample2_i330_sec_child_line.i330*1000
    #             else:
    #                 record.sample2_i330 = 0.0
    #         else:
    #             record.sample2_i330 = 0.0

    # @api.depends('child_lines.i330')
    # def _compute_sample3_i330(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 sample3_i330_third_child_line = record.child_lines[2]
    #                 record.sample3_i330 = sample3_i330_third_child_line.i330*1000
    #             else:
    #                 record.sample3_i330 = 0.0
    #         else:
    #             record.sample3_i330 = 0.0


    # @api.depends('child_lines.i360')
    # def _compute_i360_sample1(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 0:
    #                 i360_first_child_line = record.child_lines[0]
    #                 record.i360_sample1 = i360_first_child_line.i360*1000
    #             else:
    #                 record.i360_sample1 = 0.0
    #         else:
    #             record.i360_sample1 = 0.0

    # @api.depends('child_lines.i360')
    # def _compute_i360_sample2(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 1:
    #                 i360_second_child_line = record.child_lines[1]
    #                 record.i360_sample2 = i360_second_child_line.i360*1000
    #             else:
    #                 record.i360_sample2 = 0.0
    #         else:
    #             record.i360_sample2 = 0.0

    # @api.depends('child_lines.i360')
    # def _compute_i360_sample3(self):
    #     for record in self:
    #         if record.child_lines:
    #             if len(record.child_lines) > 2:
    #                 i360_third_child_line = record.child_lines[2]
    #                 record.i360_sample3 = i360_third_child_line.i360*1000
    #             else:
    #                 record.i360_sample3 = 0.0
    #         else:
    #             record.i360_sample3 = 0.0

    


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
        record = super(RcptConcreteCube, self).create(vals)
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
        record = self.env['mechanical.rcpt.concrete.cube'].browse(self.ids[0])
        field_values = {}
        for field_name, field in record._fields.items():
            field_value = record[field_name]
            field_values[field_name] = field_value

        return field_values
    


   

    
class RcptConcreteCubeLine(models.Model):
    _name = "mechanical.rcpt.concrete.cube.line"
    parent_id = fields.Many2one('mechanical.rcpt.concrete.cube',string="Parent Id")
   
    sr_no = fields.Integer(string="Sample No", readonly=True, copy=False, default=1)
    # undefined=fields.Float(string="Undefined")
    height=fields.Float(string="Height")
    dia_core = fields.Float(string="Dia Of Core")
    identification_mark = fields.Char(string="Sample ID Mark",compute="_compute_sample_id")
    io = fields.Float(string="Io", digits=(16,1))
    i30 = fields.Float(string="I30", digits=(16,1))
    i60 = fields.Float(string="I60", digits=(16,1))
    i90 = fields.Float(string="I90", digits=(16,1))
    i120 = fields.Float(string="I120", digits=(16,1))
    i150 = fields.Float(string="I150", digits=(16,1))
    i180 = fields.Float(string="I180", digits=(16,1))
    i210 = fields.Float(string="I210", digits=(16,1))
    i240 = fields.Float(string="I240", digits=(16,1))
    i270 = fields.Float(string="I270", digits=(16,1))
    i300 = fields.Float(string="I300", digits=(16,1))
    i330 = fields.Float(string="I330", digits=(16,1))
    i360 = fields.Float(string="I360", digits=(16,1))
    qx = fields.Float(string="Qxy", compute="_compute_qx",digits=(16,2), store=True)
    qs = fields.Integer(string="Qs", compute="_compute_qs", digits=(16, 2), store=True)


    @api.depends('parent_id')
    def _compute_sample_id(self):
        for record in self:
            try:
                record.identification_mark = record.parent_id.eln_ref.sample_id.client_sample_id
            except:
                record.identification_mark = None
    

    @api.depends("qx", "dia_core", "height")
    def _compute_qs(self):
        for record in self:
            if record.dia_core != 0:
                raw_qs = record.qx * (95 / record.dia_core) ** 2 * (record.height / 50)
                record.qs = round(raw_qs)
            else:
                # Handle the case where dia_core is zero (to avoid division by zero)
                record.qs = 0  # You can adjust this based on your requirements




    @api.depends(
    "io", "i30", "i60", "i90", "i120", "i150", "i180", "i210", "i240",
    "i270", "i300", "i330", "i360"
    )
    def _compute_qx(self):
        for record in self:
            qx = 900 * (
                record.io
                + 2 * record.i30
                + 2 * record.i60
                + 2 * record.i90
                + 2 * record.i120
                + 2 * record.i150
                + 2 * record.i180
                + 2 * record.i210
                + 2 * record.i240
                + 2 * record.i270
                + 2 * record.i300
                + 2 * record.i330
                + record.i360
            ) / 1000
            # Assign the calculated float value to the field
            record.qx = qx

    




   

    


    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(RcptConcreteCubeLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1