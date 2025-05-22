from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError


class CementSettingTime(models.Model):
    _name = "mechanical.cement.setting.time"
    _inherit = "lerm.eln"
    _rec_name = "name"


    setting_time_name = fields.Char("Name",default="Setting Time")
    parameter_id = fields.Many2one('eln.parameters.result', string="Parameter")

    temp_percent = fields.Float("Temperature %")
    humidity_percent = fields.Float("Humidity %")

    wt_of_cement = fields.Float("Wt. of Cement(g)",default=400)
    wt_of_water_required = fields.Float("Wt.of water required (g) (0.85*P%)")

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(CementSettingTime, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record
