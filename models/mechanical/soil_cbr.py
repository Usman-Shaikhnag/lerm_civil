from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class SoilCBR(models.Model):
    _name = "mechanical.soil.cbr"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="California Bearing Ratio")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.soils.cbr.line','parent_id',string="Parameter")

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(SoilCBR, self).create(vals)
        return record







class DENSITYRELATIONUSINGHEAVYCOMPACTION(models.Model):
    _name = "density.heavy.compaction"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="DETERMINATION OF WATER CONTENT")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('density.heavy.compaction.line','parent_id',string="Parameter")
    wt_of_modul = fields.Integer(string="Weight of Mould in gm")
    vl_of_modul = fields.Integer(string="Volume of Mould in cc")
    
    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(DENSITYRELATIONUSINGHEAVYCOMPACTION, self).create(vals)
        return record




class DENSITYRELATIONUSINGHEAVYCOMPACTIONLINE(models.Model):
    _name = "density.heavy.compaction.line"
    parent_id = fields.Many2one('density.heavy.compaction',string="Parent Id")

    determination_no = fields.Float(string="Determination No")
    wt_of_modul_compact = fields.Integer(string="Weight of Mould + Compacted sample in gm")
    wt_of_compact = fields.Integer(string="Weight of compacted sample in gm", compute="_compute_wt_of_compact")
    bulk_density = fields.Float(string="Bulk Density of sample in gm/cc", compute="_compute_bulk_density")
    container_no = fields.Integer(string="Container No")
    wt_of_container = fields.Float(string="Weight of Container in gm")
    wt_of_container_wet = fields.Float(string="Weight of Container + wet sample in gm")
    wt_of_container_dry = fields.Float(string="Weight of Container + dry sample in gm")
    wt_of_dry_sample = fields.Float(string="Weight of dry sample in gm", compute="_compute_wt_of_dry_sample")
    wt_of_moisture = fields.Float(string="Weight of moisture in gm", compute="_compute_wt_of_moisture")
    moisture = fields.Float(string="% Moisture", compute="_compute_moisture")
    dry_density = fields.Float(string="Dry density in gm/cc", compute="_compute_dry_density")


    @api.depends('wt_of_modul_compact', 'parent_id.wt_of_modul')
    def _compute_wt_of_compact(self):
        for line in self:
            line.wt_of_compact = line.wt_of_modul_compact - line.parent_id.wt_of_modul



    @api.depends('wt_of_compact', 'parent_id.vl_of_modul')
    def _compute_bulk_density(self):
        for line in self:
            if line.parent_id.vl_of_modul != 0:
                line.bulk_density = line.wt_of_compact / line.parent_id.vl_of_modul
            else:
                line.bulk_density = 0.0


    @api.depends('wt_of_container_dry', 'wt_of_container')
    def _compute_wt_of_dry_sample(self):
        for line in self:
            line.wt_of_dry_sample = line.wt_of_container_dry - line.wt_of_container


    @api.depends('wt_of_container_wet', 'wt_of_container_dry')
    def _compute_wt_of_moisture(self):
        for line in self:
            line.wt_of_moisture = line.wt_of_container_wet - line.wt_of_container_dry


    @api.depends('wt_of_moisture', 'wt_of_dry_sample')
    def _compute_moisture(self):
        for line in self:
            if line.wt_of_dry_sample != 0:
                line.moisture = line.wt_of_moisture / line.wt_of_dry_sample * 100
            else:
                line.moisture = 0.0


    @api.depends('bulk_density', 'moisture')
    def _compute_dry_density(self):
        for line in self:
            line.dry_density = (100 * line.bulk_density) / (100 + line.moisture)




class PLASTICLIMIT(models.Model):
    _name = "mechanical.plasticl.limit"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="PLASTIC LIMIT")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.plasticl.limit.line','parent_id',string="Parameter")

    plastic_limit = fields.Float(string="Average of % Moisture", compute="_compute_plastic_limit")
    plasticity_index = fields.Float(string="Plasticity Index", compute="_compute_plasticity_index")


    @api.depends('child_lines.moisture')
    def _compute_plastic_limit(self):
        for record in self:
            total_moisture = sum(record.child_lines.mapped('moisture'))
            record.plastic_limit = total_moisture / len(record.child_lines) if record.child_lines else 0.0

    @api.depends('plastic_limit')
    def _compute_plasticity_index(self):
        for record in self:
            record.plasticity_index = 46.14 - record.plastic_limit


  

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(PLASTICLIMIT, self).create(vals)
        return record



class PLASTICLIMITLINE(models.Model):
    _name = "mechanical.plasticl.limit.line"
    parent_id = fields.Many2one('mechanical.plasticl.limit',string="Parent Id")



    container_no = fields.Integer(string="Container No")   
    mass_of_wet = fields.Float(string="Mass of wet sample+container (M1) in gms")
    mass_of_dry = fields.Float(string="Mass of dry sample+container (M2) in gms")
    mass_of_container = fields.Float(string="Mass of container (M3) in gms")
    mass_of_moisture = fields.Float(string="Mass of Moisture (M1-M2) in gms", compute="_compute_mass_of_moisture")
    mass_of_dry_sample = fields.Float(string="Mass of dry sample (M2-M3) in gms", compute="_compute_mass_of_dry_sample")
    moisture = fields.Float(string="% Moisture", compute="_compute_moisture")



    @api.depends('mass_of_wet', 'mass_of_dry')
    def _compute_mass_of_moisture(self):
        for line in self:
            line.mass_of_moisture = line.mass_of_wet - line.mass_of_dry


    @api.depends('mass_of_dry', 'mass_of_container')
    def _compute_mass_of_dry_sample(self):
        for line in self:
            line.mass_of_dry_sample = line.mass_of_dry - line.mass_of_container


    @api.depends('mass_of_moisture', 'mass_of_dry_sample')
    def _compute_moisture(self):
        for line in self:
            if line.mass_of_dry_sample != 0:
                line.moisture = line.mass_of_moisture / line.mass_of_dry_sample * 100
            else:
                line.moisture = 0.0



class LIQUIDLIMIT(models.Model):
    _name = "mechanical.liquid.limit"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="LIQUID LIMIT")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.liquid.limit.line','parent_id',string="Parameter")

    liquid_limit = fields.Float('Liquid Limit')

    # def calculate_result(self):

    are_child_lines_filled = fields.Boolean(compute='_compute_are_child_lines_filled',string='child lines',store=False)

    @api.depends('child_lines.moisture', 'child_lines.mass_of_dry_sample')  # Replace with actual field names
    def _compute_are_child_lines_filled(self):
        for record in self:
            all_lines_filled = all(line.moisture and line.mass_of_dry_sample for line in record.child_lines)
            record.are_child_lines_filled = all_lines_filled

       

    def liquid_calculation(self):
        print('<<<<<<<<<<<<')
        for record in self:
            data = self.child_lines
           
            result = 0  # Initialize result before the loop
            print(data, 'data')
            container2Moisture = data[1].moisture
            container1Moisture = data[0].moisture
            container3Moisture = data[2].moisture
            cont2blow = data[1].blwo_no
            cont3blow = data[2].blwo_no
            result = (container2Moisture * 100 - ((container2Moisture - container3Moisture) * 100 * (25 - cont2blow)) / (cont3blow - cont2blow)) / 100
            print(result, 'final result')
        self.write({'liquid_limit': result})

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(LIQUIDLIMIT, self).create(vals)
        return record

    # def liquid_calculation(self):
    #     print('<<<<<<<<<<<<')
    #     for record in self:
    #         data = self.child_lines  # Corrected the access to child_lines

    #         result = 0  # Initialize result before the loop
    #         print(data, 'data')

    #         if len(data) >= 3:  # Ensure there are at least 3 child records
    #             container2Moisture = data[1].moisture
    #             container3Moisture = data[2].moisture
    #             cont2blow = data[1].blow_no
    #             cont3blow = data[2].blow_no

    #             result = (container2Moisture * 100 - ((container2Moisture - container3Moisture) * 100 * (25 - cont2blow)) / (cont3blow - cont2blow)) / 100
    #             print(result, 'final result')

    #         # Update the 'liquid_limit' field for each record separately
    #         record.write({'liquid_limit': result})


   




class LIQUIDLIMITLINE(models.Model):
    _name = "mechanical.liquid.limit.line"
    parent_id = fields.Many2one('mechanical.liquid.limit',string="Parent Id")



    container_no = fields.Integer(string="Container No")   
    blwo_no = fields.Integer(string="No.of Blows")
    mass_of_wet = fields.Float(string="Mass of wet sample+container (M1) in gms")
    mass_of_dry = fields.Float(string="Mass of dry sample+container (M2) in gms")
    mass_of_container = fields.Float(string="Mass of container (M3) in gms")
    mass_of_moisture = fields.Float(string="Mass of Moisture (M1-M2) in gms", compute="_compute_mass_of_moisture")
    mass_of_dry_sample = fields.Float(string="Mass of dry sample (M2-M3) in gms", compute="_compute_mass_of_dry_sample")
    moisture = fields.Float(string="% Moisture", compute="_compute_moisture")

   


    @api.depends('mass_of_wet', 'mass_of_dry')
    def _compute_mass_of_moisture(self):
        for line in self:
            line.mass_of_moisture = line.mass_of_wet - line.mass_of_dry


    @api.depends('mass_of_dry', 'mass_of_container')
    def _compute_mass_of_dry_sample(self):
        for line in self:
            line.mass_of_dry_sample = line.mass_of_dry - line.mass_of_container


    @api.depends('mass_of_moisture', 'mass_of_dry_sample')
    def _compute_moisture(self):
        for line in self:
            if line.mass_of_dry_sample != 0:
                line.moisture = line.mass_of_moisture / line.mass_of_dry_sample * 100
            else:
                line.moisture = 0.0










   







  

   