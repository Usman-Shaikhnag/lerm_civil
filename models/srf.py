from odoo import api,fields,models

class LermSrf(models.Model):
    _name = "lerm.srf"
    _description = "Lerm SRF"

    name = fields.Char(string="Name")