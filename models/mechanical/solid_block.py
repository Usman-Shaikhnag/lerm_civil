from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math

class CompressiveStrength(models.Model):
    _name = "mechanical.compressive.strength"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Compressive Strength")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.compressives.strength.line','parent_id',string="Parameter")
    average_strength = fields.Float(string="Average", compute="_compute_average_strength")


    @api.depends('child_lines.compressive_strength')
    def _compute_average_strength(self):
        for record in self:
            total_strength = sum(line.compressive_strength for line in record.child_lines)
            record.average_strength = total_strength / len(record.child_lines) if len(record.child_lines) > 0 else 0.0



    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(CompressiveStrength, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

class CompressiveStrengthLine(models.Model):
    _name = "mechanical.compressives.strength.line"
    parent_id = fields.Many2one('mechanical.compressive.strength',string="Parent Id")

    sr_no = fields.Integer(string="Sr.No.")
    length = fields.Integer(string="Length (mm)")
    width = fields.Integer(string="Width (mm)")
    thickness = fields.Integer(string="Thickness (mm)")
    area = fields.Integer(string="Area (mm²)", compute="_compute_area")
    load = fields.Float(string="Load (N)")
    compressive_strength = fields.Float(string="Compressive Strength N/mm²", compute="_compute_compressive_strength")
   


    @api.depends('width', 'thickness')
    def _compute_area(self):
        for record in self:
            record.area = record.width * record.thickness


    @api.depends('load', 'area')
    def _compute_compressive_strength(self):
        for record in self:
            if record.area != 0:
                record.compressive_strength = record.load / record.area * 1000
            else:
                record.compressive_strength = 0.0


class BlockDensity(models.Model):
    _name = "mechanical.block.density"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Block Density")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.block.density.line','parent_id',string="Parameter")
    average_block = fields.Float(string="Average", compute="_compute_average_block")


    @api.depends('child_lines.block_density')
    def _compute_average_block(self):
        for record in self:
            block_densities = record.child_lines.mapped('block_density')
            if block_densities:
                record.average_block = sum(block_densities) / len(block_densities)
            else:
                record.average_block = 0.0


  

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(BlockDensity, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record

class BlockDensityLine(models.Model):
    _name = "mechanical.block.density.line"
    parent_id = fields.Many2one('mechanical.block.density',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr.No.", readonly=True, copy=False, default=1)
    length = fields.Float(string="Length (mm)")
    heigth = fields.Float(string="Height (mm)")
    thickness = fields.Float(string="Thickness (mm)")
    volume = fields.Float(string="Volume (Cm3)", compute="_compute_volume")
    intial_wt = fields.Float(string="Initial Weight of the Specimen (kg)")
    final_wt = fields.Float(string="Final Weight of the Specimen after Oven Dry (kg) (Constant)")
    block_density = fields.Float(string="Block Density (kg/M³)", compute="_compute_block_density")



    @api.depends('length','heigth','thickness')
    def _compute_volume(self):
        for record in self:
            record.volume = record.length * record.heigth * record.thickness


    @api.depends('final_wt','volume')
    def _compute_block_density(self):
        for record in self:
            if record.volume != 0:
                record.block_density = record.final_wt / record.volume * 1000000
            else:
                record.block_density = 0.0

    

    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(BlockDensityLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1


class WaterAbsorptionSoil(models.Model):
    _name = "mechanical.water.absorption.solid"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Water Absorption")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.water.absorption.solid.line','parent_id',string="Parameter")
    average_water_absorption = fields.Float(string="Average", compute="_compute_average_water_absorption")


    @api.depends('child_lines.water_absorption')
    def _compute_average_water_absorption(self):
        for record in self:
            total_water_absorption = 0.0
            count_lines = len(record.child_lines)
            for line in record.child_lines:
                total_water_absorption += line.water_absorption
            record.average_water_absorption = total_water_absorption / count_lines if count_lines else 0.0


    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(WaterAbsorptionSoil, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record


class WaterAbsorptionSoilLine(models.Model):
    _name = "mechanical.water.absorption.solid.line"
    parent_id = fields.Many2one('mechanical.water.absorption.solid',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr.No.", readonly=True, copy=False, default=1)
    wet_mass = fields.Float(string="Wet Mass of the Block (kg)")
    dry_mass = fields.Float(string="Dry Mass of the Block (kg)")
    water_absorption = fields.Float(string="Water Absorption %", compute="_compute_water_absorption")


    @api.depends('wet_mass', 'dry_mass')
    def _compute_water_absorption(self):
        for record in self:
            if record.dry_mass != 0:
                record.water_absorption = (record.wet_mass - record.dry_mass) / record.dry_mass * 100
            else:
                record.water_absorption = 0.0



    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(WaterAbsorptionSoilLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1


class DryingShrinkage(models.Model):
    _name = "mechanical.drying.shrinkage.solid"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Drying Shrinkage")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.drying.shrinkage.solid.line','parent_id',string="Parameter")
    average_drying_shrinkage = fields.Float(string="Average", compute="_compute_average_drying_shrinkage")


    @api.depends('child_lines.drying_shrinkage')
    def _compute_average_drying_shrinkage(self):
        for record in self:
            total_drying_shrinkage = sum(record.child_lines.mapped('drying_shrinkage'))
            count_lines = len(record.child_lines)
            record.average_drying_shrinkage = total_drying_shrinkage / count_lines if count_lines else 0.0


   

  

    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(DryingShrinkage, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record


class DryingShrinkageLine(models.Model):
    _name = "mechanical.drying.shrinkage.solid.line"
    parent_id = fields.Many2one('mechanical.drying.shrinkage.solid',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr.No.", readonly=True, copy=False, default=1)
    wet_measurment = fields.Float(string="Wet measuremet of the Block",digits=(12, 3))
    dry_measurment = fields.Float(string="Dry Measurement of the Block",digits=(12, 3))
    dry_length = fields.Integer(string="Dry Lenth")
    drying_shrinkage = fields.Float(string="Drying Shrinkage %", compute="_compute_drying_shrinkage")



    @api.depends('wet_measurment', 'dry_measurment', 'dry_length')
    def _compute_drying_shrinkage(self):
        for record in self:
            if record.dry_length != 0:
                record.drying_shrinkage = (record.dry_measurment - record.wet_measurment) / record.dry_length * 100
            else:
                record.drying_shrinkage = 0.0


    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(DryingShrinkageLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1



class MoistureMovement(models.Model):
    _name = "mechanical.moisture.movement.solid"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="Drying Shrinkage")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    child_lines = fields.One2many('mechanical.moisture.movement.solid.line','parent_id',string="Parameter")
    average_moisture_movment = fields.Float(string="Average",compute="_compute_average_moisture_movment", digits=(12, 9))


    @api.depends('child_lines.moisture_movment')
    def _compute_average_moisture_movment(self):
        for record in self:
            total_moisture_movment = sum(record.child_lines.mapped('moisture_movment'))
            count_lines = len(record.child_lines)
            record.average_moisture_movment = total_moisture_movment / count_lines if count_lines else 0.0



    
    @api.model
    def create(self, vals):
        # import wdb;wdb.set_trace()
        record = super(MoistureMovement, self).create(vals)
        record.parameter_id.write({'model_id':record.id})
        return record



class MoistureMovementLine(models.Model):
    _name = "mechanical.moisture.movement.solid.line"
    parent_id = fields.Many2one('mechanical.moisture.movement.solid',string="Parent Id")
   
    sr_no = fields.Integer(string="Sr.No.", readonly=True, copy=False, default=1)
    dry_length = fields.Integer(string="Dry Length of the Block")
    wet_length = fields.Integer(string="Wet Length of the Block")
    moisture_movment = fields.Float(string="Moisture Movement %", compute="_compute_moisture_movement", digits=(12, 9))



    @api.depends('dry_length', 'wet_length')
    def _compute_moisture_movement(self):
        for record in self:
            if record.wet_length != 0:
                record.moisture_movment = (record.wet_length - record.dry_length) / record.wet_length * 100
            else:
                record.moisture_movment = 0.0


    @api.model
    def create(self, vals):
        # Set the serial_no based on the existing records for the same parent
        if vals.get('parent_id'):
            existing_records = self.search([('parent_id', '=', vals['parent_id'])])
            if existing_records:
                max_serial_no = max(existing_records.mapped('sr_no'))
                vals['sr_no'] = max_serial_no + 1

        return super(MoistureMovementLine, self).create(vals)

    def _reorder_serial_numbers(self):
        # Reorder the serial numbers based on the positions of the records in child_lines
        records = self.sorted('id')
        for index, record in enumerate(records):
            record.sr_no = index + 1




   




   



   




