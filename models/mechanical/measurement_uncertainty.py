from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
import math



class MEASUREMENTUNCERTAINTY(models.Model):
    _name = "mechanical.measurement.uncertainty"
    _inherit = "lerm.eln"
    _rec_name = "name"

    name = fields.Char("Name",default="MEASUREMENT UNCERTAINTY")
    parameter_id = fields.Many2one('eln.parameters.result',string="Parameter")
    sample_parameters = fields.Many2many('lerm.parameter.master',string="Parameters",compute="_compute_sample_parameters",store=True)
    eln_ref = fields.Many2one('lerm.eln',string="Eln")

    
    # Parameter Name = 1) Density Trial Mix
   
    weighing_balance_1 = fields.Float(string="Weighing Balance (gm)") 
    concrete_rod_1 = fields.Float(string="Concrete Tamping rod (mm)",digits=(16, 3))
    density_cylinder_1 = fields.Float(string="Density cylinder (litre)",digits=(16, 3))
    density_trial_mix = fields.Char("Name",default="Density Trial Mix")
    equipment_visible = fields.Boolean("USC Visible",compute="_compute_visible")



    weighing_balance_2 = fields.Float(string="Weighing Balance (gm)") 
    concrete_rod_2 = fields.Float(string="Concrete Tamping rod (mm)",digits=(16, 3))
    density_cylinder_2 = fields.Float(string="Density cylinder (litre)",digits=(16, 3))
    

    weighing_balance_3 = fields.Float(string="Weighing Balance (gm)") 
    concrete_rod_3 = fields.Float(string="Concrete Tamping rod (mm)",digits=(16, 3))
    density_cylinder_3 = fields.Float(string="Density cylinder (litre)",digits=(16, 3))



     # Type-A Uncertainty (Repeatability)

    sieve_analysis_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    uncertainty_rep_child_lines = fields.One2many('mechanical.equipment.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_uncertainty_rep_child_lines())
  
    mean_result_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_mean_result_avg",digits=(12 , 4))

    line1_sum = fields.Float(string="(X! - X)",compute="_compute_line_sums",digits=(12,4))
    line2_sum = fields.Float(string="(X! - X)2",compute="_compute_line_sums",digits=(12,4))

    standard_devition = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_deviation")
    std_uncertainty = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty")
    relative_std = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std")
    nos_reading= fields.Float(string="Nos of Reading = n")
    degree_freedom = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('uncertainty_rep_child_lines.mean_result')
    def _compute_mean_result_avg(self):
        for record in self:
            results = record.uncertainty_rep_child_lines.mapped('mean_result')
            if results:
                record.mean_result_avg = sum(results) / len(results)
            else:
                record.mean_result_avg = 0.0

    @api.depends('uncertainty_rep_child_lines.line2', 'degree_freedom')
    def _compute_standard_deviation(self):
        for record in self:
            if record.degree_freedom != 0:
                sum_line2 = sum(line.line2 for line in record.uncertainty_rep_child_lines)
                record.standard_devition = math.sqrt(sum_line2 / record.degree_freedom)
            else:
                record.standard_devition = 0

    @api.depends('standard_devition', 'nos_reading')
    def _compute_std_uncertainty(self):
        for record in self:
            if record.nos_reading != 0:
                record.std_uncertainty = record.standard_devition / math.sqrt(record.nos_reading)
            else:
                record.std_uncertainty = 0

    @api.depends('std_uncertainty', 'mean_result_avg')
    def _compute_relative_std(self):
        for record in self:
            if record.mean_result_avg != 0:
                record.relative_std = record.std_uncertainty / record.mean_result_avg
            else:
                record.relative_std = 0
                
                
    @api.depends('uncertainty_rep_child_lines.line1', 'uncertainty_rep_child_lines.line2')
    def _compute_line_sums(self):
        for record in self:
            record.line1_sum = sum(line.line1 for line in record.uncertainty_rep_child_lines)
            record.line2_sum = sum(line.line2 for line in record.uncertainty_rep_child_lines)






    @api.model
    def _default_uncertainty_rep_child_lines(self):
        default_lines = [
            (0, 0, {'sr_no': 'X1'}),
            (0, 0, {'sr_no': 'X2'}),
            (0, 0, {'sr_no': 'X3'}),
            (0, 0, {'sr_no': 'X4'}),
            (0, 0, {'sr_no': 'X5'}),
            
        ]
        return default_lines



      # Type-B Uncertainty



    #   Ub1 (Uncertainty of Weighing Balance (gm))


    type_b_uncertainty_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty", digits=(12, 2), store=True)
    coverage_factor = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor", store=True)
    mean = fields.Float(string="Mean",compute="_compute_mean")
    standard_uncertainty = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty", digits=(12, 2), store=True)
    degree_of_freedom = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds",
        store=True
    )
    # , default=float('inf')

    @api.depends('weighing_balance_1')
    def _compute_expanded_uncertainty(self):
        for record in self:
            record.expanded_uncertainty = record.weighing_balance_1

    @api.depends('concrete_rod_1')
    def _compute_coverage_factor(self):
        for record in self:
            record.coverage_factor = record.concrete_rod_1

    @api.depends('density_cylinder_1')
    def _compute_mean(self):
        for record in self:
            record.mean = record.density_cylinder_1

    @api.depends('expanded_uncertainty', 'coverage_factor')
    def _compute_standard_uncertainty(self):
        for record in self:
            if record.coverage_factor != 0:
                record.standard_uncertainty = record.expanded_uncertainty / record.coverage_factor
            else:
                record.standard_uncertainty = 0


    @api.depends('standard_uncertainty', 'mean')
    def _compute_relative_stds(self):
        for record in self:
            if record.mean != 0:
                record.relative_std_uncertainty = record.standard_uncertainty / record.mean
            else:
                record.relative_std_uncertainty = 0


    # Ub2 (Uncertainty of Concrete Tamping Rod (mm))


    # type_b_uncertainty_name2 = fields.Char("Name",default="Type-B Uncertainty")
    # type_b_uncertainty_visible2 = fields.Boolean("Type-B Uncertainty Visible",compute="_compute_visible")



    expanded_uncertainty2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty2", digits=(12, 2), store=True)
    coverage_factor2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor2", store=True)
    mean2 = fields.Float(string="Mean",compute="_compute_mean2")
    standard_uncertainty2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty2", digits=(12, 2), store=True)
    degree_of_freedom2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,7),
        compute="_compute_relative_stds2",
        store=True
    )
    # , default=float('inf')

    @api.depends('weighing_balance_2')
    def _compute_expanded_uncertainty2(self):
        for record in self:
            record.expanded_uncertainty2 = record.weighing_balance_2

    @api.depends('concrete_rod_2')
    def _compute_coverage_factor2(self):
        for record in self:
            record.coverage_factor2 = record.concrete_rod_2

    @api.depends('density_cylinder_2')
    def _compute_mean2(self):
        for record in self:
            record.mean2 = record.density_cylinder_2

    @api.depends('expanded_uncertainty2', 'coverage_factor2')
    def _compute_standard_uncertainty2(self):
        for record in self:
            if record.coverage_factor2 != 0:
                record.standard_uncertainty2 = record.expanded_uncertainty2 / record.coverage_factor2
            else:
                record.standard_uncertainty2 = 0


    @api.depends('standard_uncertainty2', 'mean2')
    def _compute_relative_stds2(self):
        for record in self:
            if record.mean2 != 0:
                record.relative_std_uncertainty2 = record.standard_uncertainty2 / record.mean2
            else:
                record.relative_std_uncertainty2 = 0




    # Ub3 (Uncertainty of Density Cylinder (Liter))


    # type_b_uncertainty_name2 = fields.Char("Name",default="Type-B Uncertainty")
    # type_b_uncertainty_visible2 = fields.Boolean("Type-B Uncertainty Visible",compute="_compute_visible")



    expanded_uncertainty3 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub3 ex)",compute="_compute_expanded_uncertainty3", digits=(12, 2), store=True)
    coverage_factor3 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor3", store=True)
    mean3 = fields.Float(string="Mean",compute="_compute_mean3")
    standard_uncertainty3 = fields.Float(string="Standard Uncertainty  Ub3 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty3", digits=(12, 2), store=True)
    degree_of_freedom3 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty3 = fields.Float(
        string="Relative Std. Uncertainty (Ub3/ Mean)",digits=(12,7),
        compute="_compute_relative_stds3",
        store=True
    )
    # , default=float('inf')

    @api.depends('weighing_balance_3')
    def _compute_expanded_uncertainty3(self):
        for record in self:
            record.expanded_uncertainty3 = record.weighing_balance_3

    @api.depends('concrete_rod_3')
    def _compute_coverage_factor3(self):
        for record in self:
            record.coverage_factor3 = record.concrete_rod_3

    @api.depends('density_cylinder_3')
    def _compute_mean3(self):
        for record in self:
            record.mean3 = record.density_cylinder_3

    @api.depends('expanded_uncertainty3', 'coverage_factor3')
    def _compute_standard_uncertainty3(self):
        for record in self:
            if record.coverage_factor3 != 0:
                record.standard_uncertainty3 = record.expanded_uncertainty3 / record.coverage_factor3
            else:
                record.standard_uncertainty3 = 0


    @api.depends('standard_uncertainty3', 'mean3')
    def _compute_relative_stds3(self):
        for record in self:
            if record.mean3 != 0:
                record.relative_std_uncertainty3 = record.standard_uncertainty3 / record.mean3
            else:
                record.relative_std_uncertainty3 = 0



    combined_standard_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_uc")

    @api.depends('relative_std', 'relative_std_uncertainty', 'relative_std_uncertainty2', 'relative_std_uncertainty3')
    def _compute_uc(self):
        for record in self:
            record.uc = math.sqrt(
                record.relative_std**2 + 
                record.relative_std_uncertainty**2 + 
                record.relative_std_uncertainty2**2 + 
                record.relative_std_uncertainty3**2
            )


    effective_freedom_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_verr")


    @api.depends('uc', 'relative_std', 'degree_freedom')
    def _compute_verr(self):
        for record in self:
            if record.degree_freedom and record.relative_std:
                try:
                    record.verr = (record.uc ** 4) / (record.relative_std ** 4 / record.degree_freedom)
                except ZeroDivisionError:
                    record.verr = 0  # Handle division by zero
            else:
                record.verr = 0  


    covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_relative_expanded")
    
    expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_expanded_uncertainty")

    @api.depends('uc', 'covrage_factor')
    def _compute_relative_expanded(self):
        for record in self:
            record.relative_expanded = record.uc * record.covrage_factor

    @api.depends('relative_expanded', 'mean_result_avg')
    def _compute_expanded_uncertainty(self):
        for record in self:
            record.expanded_uncertainty = record.relative_expanded * record.mean_result_avg

    

    # Parameter Name = 2) Density of hardened concrete

    density_hardened_concrete_name = fields.Char("Name",default="Density of hardened concrete")
    density_hardened_concrete_visible = fields.Boolean("Density of hardened concrete Visible",compute="_compute_visible")

    w_balance_1 = fields.Float(string="W .balance(gm)") 
    vernier_calliper_1 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 4))
    
   
     

    w_balance_2 = fields.Float(string="W .balance(gm)") 
    vernier_calliper_2 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 3))

    w_balance_3 = fields.Float(string="W .balance(gm)") 
    vernier_calliper_3 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 3))




    # Type-A Uncertainty (Repeatability)

    density_hardend_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    density_hardend_child_lines = fields.One2many('mechanical.density.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_density_hardend_child_lines())
  
    mean_result1_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_mean_result_avg1",digits=(12 , 4))

    density_line1_sum = fields.Float(string="(X! - X)",compute="_compute_line_sums1",digits=(12,4))
    density_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_line_sums1",digits=(12,4))

    standard_devition1 = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_deviation1")
    std_uncertainty1 = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1")
    relative_std1 = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std1")
    nos_reading1 = fields.Float(string="Nos of Reading = n")
    degree_freedom1 = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('density_hardend_child_lines.mean_result1')
    def _compute_mean_result_avg1(self):
        for record in self:
            results1 = record.density_hardend_child_lines.mapped('mean_result1')
            if results1:
                record.mean_result1_avg = sum(results1) / len(results1)
            else:
                record.mean_result1_avg = 0.0


    @api.depends('density_hardend_child_lines.density_line2', 'degree_freedom')
    def _compute_standard_deviation1(self):
        for record in self:
            if record.degree_freedom1 != 0:
                density_line2_sum = sum(line.density_line2 for line in record.density_hardend_child_lines)
                record.standard_devition1 = math.sqrt(density_line2_sum / record.degree_freedom1)
            else:
                record.standard_devition1 = 0

    @api.depends('standard_devition1', 'nos_reading1')
    def _compute_std_uncertainty1(self):
        for record in self:
            if record.nos_reading1 != 0:
                record.std_uncertainty1 = record.standard_devition1 / math.sqrt(record.nos_reading1)
            else:
                record.std_uncertainty1 = 0



    @api.depends('std_uncertainty1', 'mean_result1_avg')
    def _compute_relative_std1(self):
        for record in self:
            if record.mean_result1_avg != 0:
                record.relative_std1 = record.std_uncertainty1 / record.mean_result1_avg
            else:
                record.relative_std1 = 0
                
                
    @api.depends('density_hardend_child_lines.density_line1', 'density_hardend_child_lines.density_line2')
    def _compute_line_sums1(self):
        for record in self:
            record.density_line1_sum = sum(line.density_line1 for line in record.density_hardend_child_lines)
            record.density_line2_sum = sum(line.density_line2 for line in record.density_hardend_child_lines)




    
    @api.model
    def _default_density_hardend_child_lines(self):
        default_lines1 = [
            (0, 0, {'density_no': 'X1'}),
            (0, 0, {'density_no': 'X2'}),
            (0, 0, {'density_no': 'X3'}),
            (0, 0, {'density_no': 'X4'}),
            (0, 0, {'density_no': 'X5'}),
            
        ]
        return default_lines1




      # Type-B Uncertainty



    #   Ub2 (Uncertainty of Vernier Calliper (mm) 


    type_b_density_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_density = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_density", digits=(12, 2), store=True)
    coverage_factor_density = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_density", store=True)
    mean_density = fields.Float(string="Mean",compute="_compute_mean_density")
    standard_uncertainty_density = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_density", digits=(12, 2), store=True)
    degree_of_freedom_density = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_density = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_density",
        store=True
    )
    # , default=float('inf')

    @api.depends('w_balance_1')
    def _compute_expanded_uncertainty_density(self):
        for record in self:
            record.expanded_uncertainty_density = record.w_balance_1

    @api.depends('w_balance_2')
    def _compute_coverage_factor_density(self):
        for record in self:
            record.coverage_factor_density = record.w_balance_2

    
    @api.depends('expanded_uncertainty_density', 'coverage_factor_density')
    def _compute_standard_uncertainty_density(self):
        for record in self:
            if record.coverage_factor_density != 0:
                record.standard_uncertainty_density = record.expanded_uncertainty_density / record.coverage_factor_density
            else:
                record.standard_uncertainty_density = 0


    @api.depends('w_balance_3')
    def _compute_mean_density(self):
        for record in self:
            record.mean_density = record.w_balance_3


    @api.depends('standard_uncertainty_density', 'mean_density')
    def _compute_relative_stds_density(self):
        for record in self:
            if record.mean_density != 0:
                record.relative_std_uncertainty_density = record.standard_uncertainty_density / record.mean_density
            else:
                record.relative_std_uncertainty_density = 0



    # Ub2 (Uncertainty of Vernier Calliper (mm) )

    expanded_uncertainty_density1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_density1", digits=(12, 4), store=True)
    coverage_factor_density1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_density1", store=True)
    mean_density1 = fields.Float(string="Mean",compute="_compute_mean_density1")
    standard_uncertainty_density1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_density1", digits=(12, 4), store=True)
    degree_of_freedom_density1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_density1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_density1",
        store=True
    )
    # , default=float('inf')

    @api.depends('vernier_calliper_1')
    def _compute_expanded_uncertainty_density1(self):
        for record in self:
            record.expanded_uncertainty_density1 = record.vernier_calliper_1

    @api.depends('vernier_calliper_2')
    def _compute_coverage_factor_density1(self):
        for record in self:
            record.coverage_factor_density1 = record.vernier_calliper_2

    
    @api.depends('expanded_uncertainty_density1', 'coverage_factor_density1')
    def _compute_standard_uncertainty_density1(self):
        for record in self:
            if record.coverage_factor_density1 != 0:
                record.standard_uncertainty_density1 = record.expanded_uncertainty_density1 / record.coverage_factor_density1
            else:
                record.standard_uncertainty_density1 = 0


    @api.depends('vernier_calliper_3')
    def _compute_mean_density1(self):
        for record in self:
            record.mean_density1 = record.vernier_calliper_3


    @api.depends('standard_uncertainty_density1', 'mean_density1')
    def _compute_relative_stds_density1(self):
        for record in self:
            if record.mean_density1 != 0:
                record.relative_std_uncertainty_density1 = record.standard_uncertainty_density1 / record.mean_density1
            else:
                record.relative_std_uncertainty_density1 = 0


    combined_standard_density_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    density_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_density_uc")

    @api.depends('relative_std1', 'relative_std_uncertainty_density', 'relative_std_uncertainty_density1')
    def _compute_density_uc(self):
        for record in self:
            record.density_uc = math.sqrt(
                record.relative_std1**2 + 
                record.relative_std_uncertainty_density**2 + 
                record.relative_std_uncertainty_density1**2 
                 )


    effective_freedom_density_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    density_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_density_verr")


    @api.depends('density_uc', 'relative_std1', 'degree_freedom1')
    def _compute_density_verr(self):
        for record in self:
            if record.degree_freedom1 and record.relative_std1:
                try:
                    record.density_verr = (record.density_uc ** 4) / (record.relative_std1 ** 4 / record.degree_freedom1)
                except ZeroDivisionError:
                    record.density_verr = 0  # Handle division by zero
            else:
                record.density_verr = 0  


    density_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    density_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_density_relative_expanded")
    
    density_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_density_expanded_uncertainty")

    @api.depends('density_uc', 'density_covrage_factor')
    def _compute_density_relative_expanded(self):
        for record in self:
            record.density_relative_expanded = record.density_uc * record.density_covrage_factor

    @api.depends('density_relative_expanded', 'mean_result1_avg')
    def _compute_density_expanded_uncertainty(self):
        for record in self:
            record.density_expanded_uncertainty = record.density_relative_expanded * record.mean_result1_avg





    # 3) Cube Comp Strength  (M40)


    compressive_name = fields.Char("Name",default="Cube Compressive Strength  (M40)")
    compressive_visible = fields.Boolean("Cube Compressive Strength  Visible",compute="_compute_visible")

    compressive_w_balance_1 = fields.Float(string="W .balance(gm)") 
    compressive_vernier_calliper_1 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 4))
    compressive_ctm_1 = fields.Float(string="CTM Machine(Kn)") 

    
   
     

    compressive_w_balance_2 = fields.Float(string="W .balance(gm)") 
    compressive_vernier_calliper_2 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 3))
    compressive_ctm_2 = fields.Float(string="CTM Machine(Kn)") 


    compressive_w_balance_3 = fields.Float(string="W .balance(gm)") 
    compressive_vernier_calliper_3 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 3))
    compressive_ctm_3 = fields.Float(string="CTM Machine(Kn)") 


    # Type-A Uncertainty (Repeatability)

    compressive_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    compressive_child_lines = fields.One2many('mechanical.compressive.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_compressive_child_lines())
  
    compressive_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_compressive_mean_avg",digits=(12 , 4))

    compressive_line1_sum = fields.Float(string="(X! - X)",compute="_compute_compressive_line1_sum",digits=(12,4))
    compressive_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_compressive_line1_sum",digits=(12,4))

    standard_devition_compressive = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_compressive")
    std_uncertainty1_compressive = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_compressive")
    relative_std_compressive = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_compressive")
    nos_reading_compressive = fields.Float(string="Nos of Reading = n")
    degree_freedom_compressive = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('compressive_child_lines.compressive_mean_result')
    def _compute_compressive_mean_avg(self):
        for record in self:
            compressive = record.compressive_child_lines.mapped('compressive_mean_result')
            if compressive:
                record.compressive_mean_avg = sum(compressive) / len(compressive)
            else:
                record.compressive_mean_avg = 0.0


    @api.depends('compressive_child_lines.compressive_line2', 'degree_freedom')
    def _compute_standard_devition_compressive(self):
        for record in self:
            if record.degree_freedom_compressive != 0:
                compressive_line2_sum = sum(line.compressive_line2 for line in record.compressive_child_lines)
                record.standard_devition_compressive = math.sqrt(compressive_line2_sum / record.degree_freedom_compressive)
            else:
                record.standard_devition_compressive = 0

    @api.depends('standard_devition_compressive', 'nos_reading_compressive')
    def _compute_std_uncertainty1_compressive(self):
        for record in self:
            if record.nos_reading_compressive != 0:
                record.std_uncertainty1_compressive = record.standard_devition_compressive / math.sqrt(record.nos_reading_compressive)
            else:
                record.std_uncertainty1_compressive = 0



   
    @api.depends('std_uncertainty1_compressive', 'compressive_mean_avg')
    def _compute_relative_std_compressive(self):
        for record in self:
            if record.std_uncertainty1_compressive != 0:
                record.relative_std_compressive = record.std_uncertainty1_compressive / record.compressive_mean_avg
            else:
                record.relative_std_compressive = 0
                
                
    @api.depends('compressive_child_lines.compressive_line1', 'compressive_child_lines.compressive_line2')
    def _compute_compressive_line1_sum(self):
        for record in self:
            record.compressive_line1_sum = sum(line.compressive_line1 for line in record.compressive_child_lines)
            record.compressive_line2_sum = sum(line.compressive_line2 for line in record.compressive_child_lines)




    
    @api.model
    def _default_compressive_child_lines(self):
        default_compressive = [
            (0, 0, {'compressive': 'X1'}),
            (0, 0, {'compressive': 'X2'}),
            (0, 0, {'compressive': 'X3'}),
            (0, 0, {'compressive': 'X4'}),
            (0, 0, {'compressive': 'X5'}),
            
        ]
        return default_compressive


    # Type-B Uncertainty

    # (Ub1 (Uncertainty of  W. Balance (gm) 


    type_b_compressive_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_compressive = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_compressive", digits=(12, 2), store=True)
    coverage_factor_compressive = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_compressive", store=True)
    mean_compressive = fields.Float(string="Mean",compute="_compute_mean_compressive")
    standard_uncertainty_compressive = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_compressive", digits=(12, 2), store=True)
    degree_of_freedom_compressive = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_compressive = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_compressive",
        store=True
    )
    # , default=float('inf')

    @api.depends('compressive_w_balance_1')
    def _compute_expanded_uncertainty_compressive(self):
        for record in self:
            record.expanded_uncertainty_compressive = record.compressive_w_balance_1

    @api.depends('compressive_w_balance_2')
    def _compute_coverage_factor_compressive(self):
        for record in self:
            record.coverage_factor_compressive = record.compressive_w_balance_2

    
    @api.depends('expanded_uncertainty_compressive', 'coverage_factor_compressive')
    def _compute_standard_uncertainty_compressive(self):
        for record in self:
            if record.coverage_factor_compressive != 0:
                record.standard_uncertainty_compressive = record.expanded_uncertainty_compressive / record.coverage_factor_compressive
            else:
                record.standard_uncertainty_compressive = 0


    @api.depends('compressive_w_balance_3')
    def _compute_mean_compressive(self):
        for record in self:
            record.mean_compressive = record.compressive_w_balance_3


    @api.depends('standard_uncertainty_compressive', 'mean_compressive')
    def _compute_relative_stds_compressive(self):
        for record in self:
            if record.mean_compressive != 0:
                record.relative_std_uncertainty_compressive = record.standard_uncertainty_compressive / record.mean_compressive
            else:
                record.relative_std_uncertainty_compressive = 0


#    Ub2 (Uncertainty of Vernier Calliper (mm))


    expanded_uncertainty_compressive1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_compressive1", digits=(12, 4), store=True)
    coverage_factor_compressive1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_compressive1", store=True)
    mean_compressive1 = fields.Float(string="Mean",compute="_compute_mean_compressive1")
    standard_uncertainty_compressive1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_compressive1", digits=(12, 4), store=True)
    degree_of_freedom_compressive1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_compressive1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,7),
        compute="_compute_relative_stds_compressive1",
        store=True
    )
    # , default=float('inf')

    @api.depends('compressive_vernier_calliper_1')
    def _compute_expanded_uncertainty_compressive1(self):
        for record in self:
            record.expanded_uncertainty_compressive1 = record.compressive_vernier_calliper_1

    @api.depends('compressive_vernier_calliper_2')
    def _compute_coverage_factor_compressive1(self):
        for record in self:
            record.coverage_factor_compressive1 = record.compressive_vernier_calliper_2

    
    @api.depends('expanded_uncertainty_compressive1', 'coverage_factor_compressive1')
    def _compute_standard_uncertainty_compressive1(self):
        for record in self:
            if record.coverage_factor_compressive1 != 0:
                record.standard_uncertainty_compressive1 = record.expanded_uncertainty_compressive1 / record.coverage_factor_compressive1
            else:
                record.standard_uncertainty_compressive1 = 0

    @api.depends('standard_uncertainty_compressive1', 'mean_compressive1')
    def _compute_relative_stds_compressive1(self):
        for record in self:
            if record.mean_compressive1 != 0:
                record.relative_std_uncertainty_compressive1 = record.standard_uncertainty_compressive1 / record.mean_compressive1
            else:
                record.relative_std_uncertainty_compressive1 = 0




    @api.depends('compressive_vernier_calliper_3')
    def _compute_mean_compressive1(self):
        for record in self:
            record.mean_compressive1 = record.compressive_vernier_calliper_3



    
    #    Ub3 (Uncertainty of CMT Machine (Kn))


    expanded_uncertainty_compressive2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_compressive2", digits=(12, 4), store=True)
    coverage_factor_compressive2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_compressive2", store=True)
    mean_compressive2 = fields.Float(string="Mean",compute="_compute_mean_compressive2")
    standard_uncertainty_compressive2 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_compressive2", digits=(12, 4), store=True)
    degree_of_freedom_compressive2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_compressive2 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,7),
        compute="_compute_relative_stds_compressive2",
        store=True
    )
    # , default=float('inf')

    @api.depends('compressive_ctm_1')
    def _compute_expanded_uncertainty_compressive2(self):
        for record in self:
            record.expanded_uncertainty_compressive2 = record.compressive_ctm_1

    @api.depends('compressive_ctm_2')
    def _compute_coverage_factor_compressive2(self):
        for record in self:
            record.coverage_factor_compressive2 = record.compressive_ctm_2

    
    @api.depends('expanded_uncertainty_compressive2', 'coverage_factor_compressive2')
    def _compute_standard_uncertainty_compressive2(self):
        for record in self:
            if record.coverage_factor_compressive2 != 0:
                record.standard_uncertainty_compressive2 = record.expanded_uncertainty_compressive2 / record.coverage_factor_compressive2
            else:
                record.standard_uncertainty_compressive2 = 0

    @api.depends('standard_uncertainty_compressive2', 'mean_compressive2')
    def _compute_relative_stds_compressive2(self):
        for record in self:
            if record.mean_compressive2 != 0:
                record.relative_std_uncertainty_compressive2 = record.standard_uncertainty_compressive2 / record.mean_compressive2
            else:
                record.relative_std_uncertainty_compressive2 = 0




    @api.depends('compressive_ctm_3')
    def _compute_mean_compressive2(self):
        for record in self:
            record.mean_compressive2 = record.compressive_ctm_3



    combined_standard_compressive_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    compressive_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_compressive_uc")

    @api.depends('relative_std_compressive', 'relative_std_uncertainty_compressive', 'relative_std_uncertainty_compressive1','relative_std_uncertainty_compressive1')
    def _compute_compressive_uc(self):
        for record in self:
            record.compressive_uc = math.sqrt(
                record.relative_std_compressive**2 + 
                record.relative_std_uncertainty_compressive**2 + 
                record.relative_std_uncertainty_compressive1**2 +
                record.relative_std_uncertainty_compressive1
                 )


    effective_freedom_compressive_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    compressive_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_compressive_verr")


    @api.depends('compressive_uc', 'relative_std_compressive', 'degree_freedom_compressive')
    def _compute_compressive_verr(self):
        for record in self:
            if record.degree_freedom_compressive and record.relative_std_compressive:
                try:
                    record.compressive_verr = (record.compressive_uc ** 4) / (record.relative_std_compressive ** 4 / record.degree_freedom_compressive)
                except ZeroDivisionError:
                    record.compressive_verr = 0  # Handle division by zero
            else:
                record.compressive_verr = 0  


    compressive_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    compressive_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_compressive_verr_relative_expanded")
    
    compressive_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_compressive_verr_expanded_uncertainty")

    @api.depends('compressive_uc', 'compressive_verr_covrage_factor')
    def _compute_compressive_verr_relative_expanded(self):
        for record in self:
            record.compressive_verr_relative_expanded = record.compressive_uc * record.compressive_verr_covrage_factor

    @api.depends('compressive_verr_relative_expanded', 'compressive_mean_avg')
    def _compute_compressive_verr_expanded_uncertainty(self):
        for record in self:
            record.compressive_verr_expanded_uncertainty = record.compressive_verr_relative_expanded * record.compressive_mean_avg





    # 4) Accelerated Cube Comp Strength  (M40)



    act_name = fields.Char("Name",default="Accelerated Cube Compressive Strength  (M40)")
    act_visible = fields.Boolean("Accelerated Cube Comp Strength  (M40)  Visible",compute="_compute_visible")

    act_w_balance_1 = fields.Float(string="W .balance(gm)") 
    act_vernier_calliper_1 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 4))
    act_curing_tank_1 = fields.Float(string="Curing Tank(°C)")
    act_ctm_1 = fields.Float(string="CTM Machine(Kn)") 

    
   
     

    act_w_balance_2 = fields.Float(string="W .balance(gm)") 
    act_vernier_calliper_2 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 3))
    act_curing_tank_2 = fields.Float(string="Curing Tank(°C)")
    act_ctm_2 = fields.Float(string="CTM Machine(Kn)") 


    act_w_balance_3 = fields.Float(string="W .balance(gm)") 
    act_vernier_calliper_3 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 3))
    act_curing_tank_3 = fields.Float(string="Curing Tank(°C)")
    act_ctm_3 = fields.Float(string="CTM Machine(Kn)") 

    act_w_balance_4 = fields.Float(string="W .balance(gm)") 
    act_vernier_calliper_4 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 4))
    act_curing_tank_4 = fields.Float(string="Curing Tank(°C)")
    act_ctm_4 = fields.Float(string="CTM Machine(Kn)") 


     # Type-A Uncertainty (Repeatability)

    act_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    act_child_lines = fields.One2many('mechanical.act.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_act_child_lines())
  
    act_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_act_mean_avg",digits=(12 , 4))

    act_line1_sum = fields.Float(string="(X! - X)",compute="_compute_act_line1_sum",digits=(12,4))
    act_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_act_line1_sum",digits=(12,4))

    standard_devition_act = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_act")
    std_uncertainty1_act = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_act")
    relative_std_act = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_act")
    nos_reading_act = fields.Float(string="Nos of Reading = n")
    degree_freedom_act = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('act_child_lines.act_mean_result')
    def _compute_act_mean_avg(self):
        for record in self:
            act = record.act_child_lines.mapped('act_mean_result')
            if act:
                record.act_mean_avg = sum(act) / len(act)
            else:
                record.act_mean_avg = 0.0


    @api.depends('act_child_lines.act_line2', 'degree_freedom')
    def _compute_standard_devition_act(self):
        for record in self:
            if record.degree_freedom_act != 0:
                act_line2_sum = sum(line.act_line2 for line in record.act_child_lines)
                record.standard_devition_act = math.sqrt(act_line2_sum / record.degree_freedom_act)
            else:
                record.standard_devition_act = 0

    @api.depends('standard_devition_act', 'nos_reading_act')
    def _compute_std_uncertainty1_act(self):
        for record in self:
            if record.nos_reading_act != 0:
                record.std_uncertainty1_act = record.standard_devition_act / math.sqrt(record.nos_reading_act)
            else:
                record.std_uncertainty1_act = 0



   
    @api.depends('std_uncertainty1_act', 'act_mean_avg')
    def _compute_relative_std_act(self):
        for record in self:
            if record.std_uncertainty1_act != 0:
                record.relative_std_act = record.std_uncertainty1_act / record.act_mean_avg
            else:
                record.relative_std_act = 0
                
                
    @api.depends('act_child_lines.act_line1', 'act_child_lines.act_line2')
    def _compute_act_line1_sum(self):
        for record in self:
            record.act_line1_sum = sum(line.act_line1 for line in record.act_child_lines)
            record.act_line2_sum = sum(line.act_line2 for line in record.act_child_lines)




    
    @api.model
    def _default_act_child_lines(self):
        default_act = [
            (0, 0, {'act': 'X1'}),
            (0, 0, {'act': 'X2'}),
            (0, 0, {'act': 'X3'}),
            (0, 0, {'act': 'X4'}),
            (0, 0, {'act': 'X5'}),
            
        ]
        return default_act


     # Type-B Uncertainty

    # (Ub1 (Uncertainty of  W. Balance (gm) 


    type_b_act1_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_act1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_act1", digits=(12, 2), store=True)
    coverage_factor_act1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_act1", store=True)
    mean_act1 = fields.Float(string="Mean",compute="_compute_mean_act1")
    standard_uncertainty_act1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_act1", digits=(12, 2), store=True)
    degree_of_freedom_act1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_act1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_act1",
        store=True
    )
    # , default=float('inf')

    @api.depends('act_w_balance_1')
    def _compute_expanded_uncertainty_act1(self):
        for record in self:
            record.expanded_uncertainty_act1 = record.act_w_balance_1

    @api.depends('act_w_balance_2')
    def _compute_coverage_factor_act1(self):
        for record in self:
            record.coverage_factor_act1 = record.act_w_balance_2

    
    @api.depends('expanded_uncertainty_act1', 'coverage_factor_act1')
    def _compute_standard_uncertainty_act1(self):
        for record in self:
            if record.coverage_factor_act1 != 0:
                record.standard_uncertainty_act1 = record.expanded_uncertainty_act1 / record.coverage_factor_act1
            else:
                record.standard_uncertainty_act1 = 0


    @api.depends('act_w_balance_3')
    def _compute_mean_act1(self):
        for record in self:
            record.mean_act1 = record.act_w_balance_3


    @api.depends('standard_uncertainty_act1', 'mean_act1')
    def _compute_relative_stds_act1(self):
        for record in self:
            if record.mean_act1 != 0:
                record.relative_std_uncertainty_act1 = record.standard_uncertainty_act1 / record.mean_act1
            else:
                record.relative_std_uncertainty_act1 = 0

    #  Ub2 (Uncertainty of Vernier Calliper (mm))
    expanded_uncertainty_act2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_act2", digits=(12, 4), store=True)
    coverage_factor_act2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_act2", store=True)
    mean_act2 = fields.Float(string="Mean",compute="_compute_mean_act2")
    standard_uncertainty_act2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_act2", digits=(12, 4), store=True)
    degree_of_freedom_act2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_act2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_act2",
        store=True
    )
    # , default=float('inf')

    @api.depends('act_vernier_calliper_1')
    def _compute_expanded_uncertainty_act2(self):
        for record in self:
            record.expanded_uncertainty_act2 = record.act_vernier_calliper_1

    @api.depends('act_vernier_calliper_2')
    def _compute_coverage_factor_act2(self):
        for record in self:
            record.coverage_factor_act2 = record.act_vernier_calliper_2

    
    @api.depends('expanded_uncertainty_act2', 'coverage_factor_act2')
    def _compute_standard_uncertainty_act2(self):
        for record in self:
            if record.coverage_factor_act2 != 0:
                record.standard_uncertainty_act2 = record.expanded_uncertainty_act2 / record.coverage_factor_act2
            else:
                record.standard_uncertainty_act2 = 0


    @api.depends('act_vernier_calliper_3')
    def _compute_mean_act2(self):
        for record in self:
            record.mean_act2 = record.act_vernier_calliper_3


    @api.depends('standard_uncertainty_act2', 'mean_act2')
    def _compute_relative_stds_act2(self):
        for record in self:
            if record.mean_act2 != 0:
                record.relative_std_uncertainty_act2 = record.standard_uncertainty_act2 / record.mean_act2
            else:
                record.relative_std_uncertainty_act2 = 0


     #  Ub3 (Uncertainty of Accelerated Curing Tank)
    expanded_uncertainty_act3 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub3 ex)",compute="_compute_expanded_uncertainty_act3", digits=(12, 4), store=True)
    coverage_factor_act3 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_act3", store=True)
    mean_act3 = fields.Float(string="Mean",compute="_compute_mean_act3")
    standard_uncertainty_act3 = fields.Float(string="Standard Uncertainty  Ub3 = [Ub3 ex/ k]",compute="_compute_standard_uncertainty_act3", digits=(12, 4), store=True)
    degree_of_freedom_act3 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_act3 = fields.Float(
        string="Relative Std. Uncertainty (Ub3/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_act3",
        store=True
    )
    # , default=float('inf')

    @api.depends('act_curing_tank_1')
    def _compute_expanded_uncertainty_act3(self):
        for record in self:
            record.expanded_uncertainty_act3 = record.act_curing_tank_1

    @api.depends('act_curing_tank_2')
    def _compute_coverage_factor_act3(self):
        for record in self:
            record.coverage_factor_act3 = record.act_curing_tank_2

    
    @api.depends('expanded_uncertainty_act3', 'coverage_factor_act3')
    def _compute_standard_uncertainty_act3(self):
        for record in self:
            if record.coverage_factor_act3 != 0:
                record.standard_uncertainty_act3 = record.expanded_uncertainty_act3 / record.coverage_factor_act3
            else:
                record.standard_uncertainty_act3 = 0


    @api.depends('act_curing_tank_3')
    def _compute_mean_act3(self):
        for record in self:
            record.mean_act3 = record.act_curing_tank_3


    @api.depends('standard_uncertainty_act3', 'mean_act3')
    def _compute_relative_stds_act3(self):
        for record in self:
            if record.mean_act3 != 0:
                record.relative_std_uncertainty_act3 = record.standard_uncertainty_act3 / record.mean_act3
            else:
                record.relative_std_uncertainty_act3 = 0



    #  Ub4 (Uncertainty of CMT Machine (Kn))
    expanded_uncertainty_act4 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub4 ex)",compute="_compute_expanded_uncertainty_act4", digits=(12, 4), store=True)
    coverage_factor_act4 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_act4", store=True)
    mean_act4 = fields.Float(string="Mean",compute="_compute_mean_act4")
    standard_uncertainty_act4 = fields.Float(string="Standard Uncertainty  Ub4 = [Ub4 ex/ k]",compute="_compute_standard_uncertainty_act4", digits=(12, 4), store=True)
    degree_of_freedom_act4 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_act4 = fields.Float(
        string="Relative Std. Uncertainty (Ub4/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_act4",
        store=True
    )
    # , default=float('inf')

    @api.depends('act_ctm_1')
    def _compute_expanded_uncertainty_act4(self):
        for record in self:
            record.expanded_uncertainty_act4 = record.act_ctm_1

    @api.depends('act_ctm_2')
    def _compute_coverage_factor_act4(self):
        for record in self:
            record.coverage_factor_act4 = record.act_ctm_2

    
    @api.depends('expanded_uncertainty_act4', 'coverage_factor_act4')
    def _compute_standard_uncertainty_act4(self):
        for record in self:
            if record.coverage_factor_act4 != 0:
                record.standard_uncertainty_act4 = record.expanded_uncertainty_act4 / record.coverage_factor_act4
            else:
                record.standard_uncertainty_act4 = 0


    @api.depends('act_ctm_3')
    def _compute_mean_act4(self):
        for record in self:
            record.mean_act4 = record.act_ctm_3


    @api.depends('standard_uncertainty_act4', 'mean_act4')
    def _compute_relative_stds_act4(self):
        for record in self:
            if record.mean_act4 != 0:
                record.relative_std_uncertainty_act4 = record.standard_uncertainty_act4 / record.mean_act4
            else:
                record.relative_std_uncertainty_act4 = 0


    combined_standard_act_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    act_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_act_uc")

    @api.depends('relative_std_act', 'relative_std_uncertainty_act1', 'relative_std_uncertainty_act1','relative_std_uncertainty_act3','relative_std_uncertainty_act4')
    def _compute_act_uc(self):
        for record in self:
            record.act_uc = math.sqrt(
                record.relative_std_act**2 + 
                record.relative_std_uncertainty_act1**2 + 
                record.relative_std_uncertainty_act2**2 +
                record.relative_std_uncertainty_act3**2 +
                record.relative_std_uncertainty_act4**2 
                 )


    effective_freedom_act_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    act_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_act_verr")


    @api.depends('act_uc', 'relative_std_act', 'degree_freedom_act')
    def _compute_act_verr(self):
        for record in self:
            if record.degree_freedom_act and record.relative_std_act:
                try:
                    record.act_verr = (record.act_uc ** 4) / (record.relative_std_act ** 4 / record.degree_freedom_act)
                except ZeroDivisionError:
                    record.act_verr = 0  # Handle division by zero
            else:
                record.act_verr = 0  


    act_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    act_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_act_verr_relative_expanded")
    
    act_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_act_verr_expanded_uncertainty")

    @api.depends('act_uc', 'act_verr_covrage_factor')
    def _compute_act_verr_relative_expanded(self):
        for record in self:
            record.act_verr_relative_expanded = record.act_uc * record.act_verr_covrage_factor

    @api.depends('act_verr_relative_expanded', 'act_mean_avg')
    def _compute_act_verr_expanded_uncertainty(self):
        for record in self:
            record.act_verr_expanded_uncertainty = record.act_verr_relative_expanded * record.act_mean_avg


     # 5) flexural beam Comp Strength (M40)



    flexural_name = fields.Char("Name",default="Flexural beam Comp Strength (M40)")
    flexural_visible = fields.Boolean("Flexural beam Comp Strength (M40)  Visible",compute="_compute_visible")

    flexural_w_balance_1 = fields.Float(string="W .balance(gm)") 
    flexural_vernier_calliper_1 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 4))
    flexural_utm_1 = fields.Float(string="UTM Machine(KN)")
    flexural_measuring_1 = fields.Float(string="Measuring tape(mm)") 

    
   
     

    flexural_w_balance_2 = fields.Float(string="W .balance(gm)") 
    flexural_vernier_calliper_2 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 3))
    flexural_utm_2 = fields.Float(string="UTM Machine(KN)")
    flexural_measuring_2 = fields.Float(string="Measuring tape(mm)") 


    flexural_w_balance_3 = fields.Float(string="W .balance(gm)") 
    flexural_vernier_calliper_3 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 3))
    flexural_utm_3 = fields.Float(string="UTM Machine(KN)")
    flexural_measuring_3 = fields.Float(string="Measuring tape(mm)") 

    flexural_w_balance_4 = fields.Float(string="W .balance(gm)") 
    flexural_vernier_calliper_4 = fields.Float(string="Vernier Calliper(mm)",digits=(16, 4))
    flexural_utm_4 = fields.Float(string="UTM Machine(KN)")
    flexural_measuring_4 = fields.Float(string="Measuring tape(mm)") 


     # Type-A Uncertainty (Repeatability)

    flexural_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    flexural_child_lines = fields.One2many('mechanical.flexural.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_flexural_child_lines())
  
    flexural_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_flexural_mean_avg",digits=(12 , 4))

    flexural_line1_sum = fields.Float(string="(X! - X)",compute="_compute_flexural_line1_sum",digits=(12,4))
    flexural_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_flexural_line1_sum",digits=(12,4))

    standard_devition_flexural = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_flexural")
    std_uncertainty1_flexural = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_flexural")
    relative_std_flexural = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_flexural")
    nos_reading_flexural = fields.Float(string="Nos of Reading = n")
    degree_freedom_flexural = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('flexural_child_lines.flexural_mean_result')
    def _compute_flexural_mean_avg(self):
        for record in self:
            flexural = record.flexural_child_lines.mapped('flexural_mean_result')
            if flexural:
                record.flexural_mean_avg = sum(flexural) / len(flexural)
            else:
                record.flexural_mean_avg = 0.0


    @api.depends('flexural_child_lines.flexural_line2', 'degree_freedom')
    def _compute_standard_devition_flexural(self):
        for record in self:
            if record.degree_freedom_flexural != 0:
                flexural_line2_sum = sum(line.flexural_line2 for line in record.flexural_child_lines)
                record.standard_devition_flexural = math.sqrt(flexural_line2_sum / record.degree_freedom_flexural)
            else:
                record.standard_devition_flexural = 0

    @api.depends('standard_devition_flexural', 'nos_reading_flexural')
    def _compute_std_uncertainty1_flexural(self):
        for record in self:
            if record.nos_reading_flexural != 0:
                record.std_uncertainty1_flexural = record.standard_devition_flexural / math.sqrt(record.nos_reading_flexural)
            else:
                record.std_uncertainty1_flexural = 0



   
    @api.depends('std_uncertainty1_flexural', 'flexural_mean_avg')
    def _compute_relative_std_flexural(self):
        for record in self:
            if record.std_uncertainty1_flexural != 0:
                record.relative_std_flexural = record.std_uncertainty1_flexural / record.flexural_mean_avg
            else:
                record.relative_std_flexural = 0
                
                
    @api.depends('flexural_child_lines.flexural_line1', 'flexural_child_lines.flexural_line2')
    def _compute_flexural_line1_sum(self):
        for record in self:
            record.flexural_line1_sum = sum(line.flexural_line1 for line in record.flexural_child_lines)
            record.flexural_line2_sum = sum(line.flexural_line2 for line in record.flexural_child_lines)




    
    @api.model
    def _default_flexural_child_lines(self):
        default_flexural = [
            (0, 0, {'flexural': 'X1'}),
            (0, 0, {'flexural': 'X2'}),
            (0, 0, {'flexural': 'X3'}),
            (0, 0, {'flexural': 'X4'}),
            (0, 0, {'flexural': 'X5'}),
            
        ]
        return default_flexural



     # Type-B Uncertainty

    # (Ub1 (Uncertainty of  W. Balance (gm) 


    type_b_flexural1_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_flexural1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_flexural1", digits=(12, 2), store=True)
    coverage_factor_flexural1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_flexural1", store=True)
    mean_flexural1 = fields.Float(string="Mean",compute="_compute_mean_flexural1")
    standard_uncertainty_flexural1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_flexural1", digits=(12, 2), store=True)
    degree_of_freedom_flexural1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_flexural1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_flexural1",
        store=True
    )
    # , default=float('inf')

    @api.depends('flexural_w_balance_1')
    def _compute_expanded_uncertainty_flexural1(self):
        for record in self:
            record.expanded_uncertainty_flexural1 = record.flexural_w_balance_1

    @api.depends('flexural_w_balance_2')
    def _compute_coverage_factor_flexural1(self):
        for record in self:
            record.coverage_factor_flexural1 = record.flexural_w_balance_2

    
    @api.depends('expanded_uncertainty_flexural1', 'coverage_factor_flexural1')
    def _compute_standard_uncertainty_flexural1(self):
        for record in self:
            if record.coverage_factor_flexural1 != 0:
                record.standard_uncertainty_flexural1 = record.expanded_uncertainty_flexural1 / record.coverage_factor_flexural1
            else:
                record.standard_uncertainty_flexural1 = 0


    @api.depends('flexural_w_balance_3')
    def _compute_mean_flexural1(self):
        for record in self:
            record.mean_flexural1 = record.flexural_w_balance_3


    @api.depends('standard_uncertainty_flexural1', 'mean_flexural1')
    def _compute_relative_stds_flexural1(self):
        for record in self:
            if record.mean_flexural1 != 0:
                record.relative_std_uncertainty_flexural1 = record.standard_uncertainty_flexural1 / record.mean_flexural1
            else:
                record.relative_std_uncertainty_flexural1 = 0

    #  Ub2 (Uncertainty of Vernier Calliper (mm))
    expanded_uncertainty_flexural2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_flexural2", digits=(12, 4), store=True)
    coverage_factor_flexural2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_flexural2", store=True)
    mean_flexural2 = fields.Float(string="Mean",compute="_compute_mean_flexural2")
    standard_uncertainty_flexural2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_flexural2", digits=(12, 4), store=True)
    degree_of_freedom_flexural2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_flexural2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_flexural2",
        store=True
    )
    # , default=float('inf')

    @api.depends('flexural_vernier_calliper_1')
    def _compute_expanded_uncertainty_flexural2(self):
        for record in self:
            record.expanded_uncertainty_flexural2 = record.flexural_vernier_calliper_1

    @api.depends('flexural_vernier_calliper_2')
    def _compute_coverage_factor_flexural2(self):
        for record in self:
            record.coverage_factor_flexural2 = record.flexural_vernier_calliper_2

    
    @api.depends('expanded_uncertainty_flexural2', 'coverage_factor_flexural2')
    def _compute_standard_uncertainty_flexural2(self):
        for record in self:
            if record.coverage_factor_flexural2 != 0:
                record.standard_uncertainty_flexural2 = record.expanded_uncertainty_flexural2 / record.coverage_factor_flexural2
            else:
                record.standard_uncertainty_flexural2 = 0


    @api.depends('flexural_vernier_calliper_3')
    def _compute_mean_flexural2(self):
        for record in self:
            record.mean_flexural2 = record.flexural_vernier_calliper_3


    @api.depends('standard_uncertainty_flexural2', 'mean_flexural2')
    def _compute_relative_stds_flexural2(self):
        for record in self:
            if record.mean_flexural2 != 0:
                record.relative_std_uncertainty_flexural2 = record.standard_uncertainty_flexural2 / record.mean_flexural2
            else:
                record.relative_std_uncertainty_flexural2 = 0

    
     #  Ub3 (Uncertainty of UTM Machine (Kn))
    expanded_uncertainty_flexural3 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub3 ex)",compute="_compute_expanded_uncertainty_flexural3", digits=(13, 4), store=True)
    coverage_factor_flexural3 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_flexural3", store=True)
    mean_flexural3 = fields.Float(string="Mean",compute="_compute_mean_flexural3")
    standard_uncertainty_flexural3 = fields.Float(string="Standard Uncertainty  Ub3 = [Ub3 ex/ k]",compute="_compute_standard_uncertainty_flexural3", digits=(13, 4), store=True)
    degree_of_freedom_flexural3 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_flexural3 = fields.Float(
        string="Relative Std. Uncertainty (Ub3/ Mean)",digits=(13,5),
        compute="_compute_relative_stds_flexural3",
        store=True
    )
    # , default=float('inf')

    @api.depends('flexural_utm_1')
    def _compute_expanded_uncertainty_flexural3(self):
        for record in self:
            record.expanded_uncertainty_flexural3 = record.flexural_utm_1

    @api.depends('flexural_utm_2')
    def _compute_coverage_factor_flexural3(self):
        for record in self:
            record.coverage_factor_flexural3 = record.flexural_utm_2

    
    @api.depends('expanded_uncertainty_flexural3', 'coverage_factor_flexural3')
    def _compute_standard_uncertainty_flexural3(self):
        for record in self:
            if record.coverage_factor_flexural3 != 0:
                record.standard_uncertainty_flexural3 = record.expanded_uncertainty_flexural3 / record.coverage_factor_flexural3
            else:
                record.standard_uncertainty_flexural3 = 0


    @api.depends('flexural_utm_3')
    def _compute_mean_flexural3(self):
        for record in self:
            record.mean_flexural3 = record.flexural_utm_3


    @api.depends('standard_uncertainty_flexural3', 'mean_flexural3')
    def _compute_relative_stds_flexural3(self):
        for record in self:
            if record.mean_flexural3 != 0:
                record.relative_std_uncertainty_flexural3 = record.standard_uncertainty_flexural3 / record.mean_flexural3
            else:
                record.relative_std_uncertainty_flexural3 = 0


     #  Ub4 (Uncertainty of Measuring Tape (mm))
    expanded_uncertainty_flexural4 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub4 ex)",compute="_compute_expanded_uncertainty_flexural4", digits=(14, 4), store=True)
    coverage_factor_flexural4 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_flexural4", store=True)
    mean_flexural4 = fields.Float(string="Mean",compute="_compute_mean_flexural4")
    standard_uncertainty_flexural4 = fields.Float(string="Standard Uncertainty  Ub4 = [Ub4 ex/ k]",compute="_compute_standard_uncertainty_flexural4", digits=(14, 4), store=True)
    degree_of_freedom_flexural4 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_flexural4 = fields.Float(
        string="Relative Std. Uncertainty (Ub4/ Mean)",digits=(14,5),
        compute="_compute_relative_stds_flexural4",
        store=True
    )
    # , default=float('inf')

    @api.depends('flexural_measuring_1')
    def _compute_expanded_uncertainty_flexural4(self):
        for record in self:
            record.expanded_uncertainty_flexural4 = record.flexural_measuring_1

    @api.depends('flexural_measuring_2')
    def _compute_coverage_factor_flexural4(self):
        for record in self:
            record.coverage_factor_flexural4 = record.flexural_measuring_2

    
    @api.depends('expanded_uncertainty_flexural4', 'coverage_factor_flexural4')
    def _compute_standard_uncertainty_flexural4(self):
        for record in self:
            if record.coverage_factor_flexural4 != 0:
                record.standard_uncertainty_flexural4 = record.expanded_uncertainty_flexural4 / record.coverage_factor_flexural4
            else:
                record.standard_uncertainty_flexural4 = 0


    @api.depends('flexural_measuring_3')
    def _compute_mean_flexural4(self):
        for record in self:
            record.mean_flexural4 = record.flexural_measuring_3


    @api.depends('standard_uncertainty_flexural4', 'mean_flexural4')
    def _compute_relative_stds_flexural4(self):
        for record in self:
            if record.mean_flexural4 != 0:
                record.relative_std_uncertainty_flexural4 = record.standard_uncertainty_flexural4 / record.mean_flexural4
            else:
                record.relative_std_uncertainty_flexural4 = 0



    combined_standard_flexural_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    flexural_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_flexural_uc")

    @api.depends('relative_std_flexural', 'relative_std_uncertainty_flexural1', 'relative_std_uncertainty_flexural2','relative_std_uncertainty_flexural3','relative_std_uncertainty_flexural4')
    def _compute_flexural_uc(self):
        for record in self:
            record.flexural_uc = math.sqrt(
                record.relative_std_flexural**2 + 
                record.relative_std_uncertainty_flexural1**2 + 
                record.relative_std_uncertainty_flexural2**2 +
                record.relative_std_uncertainty_flexural3**2 +
                record.relative_std_uncertainty_flexural4**2 
                 )


    effective_freedom_flexural_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    flexural_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_flexural_verr")


    @api.depends('flexural_uc', 'relative_std_flexural', 'degree_freedom_flexural')
    def _compute_flexural_verr(self):
        for record in self:
            if record.degree_freedom_flexural and record.relative_std_flexural:
                try:
                    record.flexural_verr = (record.flexural_uc ** 4) / (record.relative_std_flexural ** 4 / record.degree_freedom_flexural)
                except ZeroDivisionError:
                    record.flexural_verr = 0  # Handle division by zero
            else:
                record.flexural_verr = 0  


    flexural_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    flexural_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_flexural_verr_relative_expanded")
    
    flexural_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_flexural_verr_expanded_uncertainty")

    @api.depends('flexural_uc', 'flexural_verr_covrage_factor')
    def _compute_flexural_verr_relative_expanded(self):
        for record in self:
            record.flexural_verr_relative_expanded = record.flexural_uc * record.flexural_verr_covrage_factor

    @api.depends('flexural_verr_relative_expanded', 'flexural_mean_avg')
    def _compute_flexural_verr_expanded_uncertainty(self):
        for record in self:
            record.flexural_verr_expanded_uncertainty = record.flexural_verr_relative_expanded * record.flexural_mean_avg



    # 6) concrete Water Absorption



    water_name = fields.Char("Name",default="concrete Water Absorption")
    water_visible = fields.Boolean("concrete Water Absorption  Visible",compute="_compute_visible")

    water_w_balance_1 = fields.Float(string="W .balance(gm)") 
    water_hotair_1 = fields.Float(string="Hot Air Oven(°C)",digits=(16, 4))
    

    water_w_balance_2 = fields.Float(string="W .balance(gm)") 
    water_hotair_2 = fields.Float(string="Hot Air Oven(°C)",digits=(16, 3))
   

    water_w_balance_3 = fields.Float(string="W .balance(gm)") 
    water_hotair_3 = fields.Float(string="Hot Air Oven(°C)",digits=(16, 3))
    

    water_w_balance_4 = fields.Float(string="W .balance(gm)") 
    water_hotair_4 = fields.Float(string="Hot Air Oven(°C)",digits=(16, 4))
   


     # Type-A Uncertainty (Repeatability)

    water_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    water_child_lines = fields.One2many('mechanical.water.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_water_child_lines())
  
    water_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_water_mean_avg",digits=(12 , 4))

    water_line1_sum = fields.Float(string="(X! - X)",compute="_compute_water_line1_sum",digits=(12,4))
    water_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_water_line1_sum",digits=(12,4))

    standard_devition_water = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_water")
    std_uncertainty1_water = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_water")
    relative_std_water = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_water")
    nos_reading_water = fields.Float(string="Nos of Reading = n")
    degree_freedom_water = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('water_child_lines.water_mean_result')
    def _compute_water_mean_avg(self):
        for record in self:
            water = record.water_child_lines.mapped('water_mean_result')
            if water:
                record.water_mean_avg = sum(water) / len(water)
            else:
                record.water_mean_avg = 0.0


    @api.depends('water_child_lines.water_line2', 'degree_freedom')
    def _compute_standard_devition_water(self):
        for record in self:
            if record.degree_freedom_water != 0:
                water_line2_sum = sum(line.water_line2 for line in record.water_child_lines)
                record.standard_devition_water = math.sqrt(water_line2_sum / record.degree_freedom_water)
            else:
                record.standard_devition_water = 0

    @api.depends('standard_devition_water', 'nos_reading_water')
    def _compute_std_uncertainty1_water(self):
        for record in self:
            if record.nos_reading_water != 0:
                record.std_uncertainty1_water = record.standard_devition_water / math.sqrt(record.nos_reading_water)
            else:
                record.std_uncertainty1_water = 0



   
    @api.depends('std_uncertainty1_water', 'water_mean_avg')
    def _compute_relative_std_water(self):
        for record in self:
            if record.std_uncertainty1_water != 0:
                record.relative_std_water = record.std_uncertainty1_water / record.water_mean_avg
            else:
                record.relative_std_water = 0
                
                
    @api.depends('water_child_lines.water_line1', 'water_child_lines.water_line2')
    def _compute_water_line1_sum(self):
        for record in self:
            record.water_line1_sum = sum(line.water_line1 for line in record.water_child_lines)
            record.water_line2_sum = sum(line.water_line2 for line in record.water_child_lines)




    
    @api.model
    def _default_water_child_lines(self):
        default_water = [
            (0, 0, {'water': 'X1'}),
            (0, 0, {'water': 'X2'}),
            (0, 0, {'water': 'X3'}),
            (0, 0, {'water': 'X4'}),
            (0, 0, {'water': 'X5'}),
            
        ]
        return default_water


     # Type-B Uncertainty

    # (Ub1 (Uncertainty of  W. Balance (gm) 


    type_b_water1_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_water1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_water1", digits=(12, 2), store=True)
    coverage_factor_water1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_water1", store=True)
    mean_water1 = fields.Float(string="Mean",compute="_compute_mean_water1")
    standard_uncertainty_water1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_water1", digits=(12, 2), store=True)
    degree_of_freedom_water1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_water1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_water1",
        store=True
    )
    # , default=float('inf')

    @api.depends('water_w_balance_1')
    def _compute_expanded_uncertainty_water1(self):
        for record in self:
            record.expanded_uncertainty_water1 = record.water_w_balance_1

    @api.depends('water_w_balance_2')
    def _compute_coverage_factor_water1(self):
        for record in self:
            record.coverage_factor_water1 = record.water_w_balance_2

    
    @api.depends('expanded_uncertainty_water1', 'coverage_factor_water1')
    def _compute_standard_uncertainty_water1(self):
        for record in self:
            if record.coverage_factor_water1 != 0:
                record.standard_uncertainty_water1 = record.expanded_uncertainty_water1 / record.coverage_factor_water1
            else:
                record.standard_uncertainty_water1 = 0


    @api.depends('water_w_balance_3')
    def _compute_mean_water1(self):
        for record in self:
            record.mean_water1 = record.water_w_balance_3


    @api.depends('standard_uncertainty_water1', 'mean_water1')
    def _compute_relative_stds_water1(self):
        for record in self:
            if record.mean_water1 != 0:
                record.relative_std_uncertainty_water1 = record.standard_uncertainty_water1 / record.mean_water1
            else:
                record.relative_std_uncertainty_water1 = 0

    #  Ub2 (Uncertainty of Hot Air Oven (°C))
    expanded_uncertainty_water2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_water2", digits=(12, 4), store=True)
    coverage_factor_water2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_water2", store=True)
    mean_water2 = fields.Float(string="Mean",compute="_compute_mean_water2")
    standard_uncertainty_water2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_water2", digits=(12, 4), store=True)
    degree_of_freedom_water2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_water2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_water2",
        store=True
    )
    # , default=float('inf')

    @api.depends('water_hotair_1')
    def _compute_expanded_uncertainty_water2(self):
        for record in self:
            record.expanded_uncertainty_water2 = record.water_hotair_1

    @api.depends('water_hotair_2')
    def _compute_coverage_factor_water2(self):
        for record in self:
            record.coverage_factor_water2 = record.water_hotair_2

    
    @api.depends('expanded_uncertainty_water2', 'coverage_factor_water2')
    def _compute_standard_uncertainty_water2(self):
        for record in self:
            if record.coverage_factor_water2 != 0:
                record.standard_uncertainty_water2 = record.expanded_uncertainty_water2 / record.coverage_factor_water2
            else:
                record.standard_uncertainty_water2 = 0


    @api.depends('water_hotair_3')
    def _compute_mean_water2(self):
        for record in self:
            record.mean_water2 = record.water_hotair_3


    @api.depends('standard_uncertainty_water2', 'mean_water2')
    def _compute_relative_stds_water2(self):
        for record in self:
            if record.mean_water2 != 0:
                record.relative_std_uncertainty_water2 = record.standard_uncertainty_water2 / record.mean_water2
            else:
                record.relative_std_uncertainty_water2 = 0


    combined_standard_water_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    water_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_water_uc")

    @api.depends('relative_std_water', 'relative_std_uncertainty_water1','relative_std_uncertainty_water2')
    def _compute_water_uc(self):
        for record in self:
            record.water_uc = math.sqrt(
                record.relative_std_water**2 + 
                record.relative_std_uncertainty_water1**2 + 
                record.relative_std_uncertainty_water2**2 
                
                 )


    effective_freedom_water_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    water_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_water_verr")


    @api.depends('water_uc', 'relative_std_water', 'degree_freedom_water')
    def _compute_water_verr(self):
        for record in self:
            if record.degree_freedom_water and record.relative_std_water:
                try:
                    record.water_verr = (record.water_uc ** 4) / (record.relative_std_water ** 4 / record.degree_freedom_water)
                except ZeroDivisionError:
                    record.water_verr = 0  # Handle division by zero
            else:
                record.water_verr = 0  


    water_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    water_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_water_verr_relative_expanded")
    
    water_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_water_verr_expanded_uncertainty")

    @api.depends('water_uc', 'water_verr_covrage_factor')
    def _compute_water_verr_relative_expanded(self):
        for record in self:
            record.water_verr_relative_expanded = record.water_uc * record.water_verr_covrage_factor

    @api.depends('water_verr_relative_expanded', 'water_mean_avg')
    def _compute_water_verr_expanded_uncertainty(self):
        for record in self:
            record.water_verr_expanded_uncertainty = record.water_verr_relative_expanded * record.water_mean_avg



    
    # 7) split tensile Strength  (M40)



    split_name = fields.Char("Name",default="Split Tensile Strength  (M40)")
    split_visible = fields.Boolean("Split Tensile Strength  (M40)  Visible",compute="_compute_visible")

    split_w_balance_1 = fields.Float(string="W .balance(gm)") 
    split_measuring_1 = fields.Float(string="Measuring tape(mm)") 
    split_ctm_1 = fields.Float(string="CTM Machine(Kn)")

    
   
     

    split_w_balance_2 = fields.Float(string="W .balance(gm)") 
    split_measuring_2 = fields.Float(string="Measuring tape(mm)") 
    split_ctm_2 = fields.Float(string="CTM Machine(Kn)")


    split_w_balance_3 = fields.Float(string="W .balance(gm)") 
    split_measuring_3 = fields.Float(string="Measuring tape(mm)") 
    split_ctm_3 = fields.Float(string="CTM Machine(Kn)")

    split_w_balance_4 = fields.Float(string="W .balance(gm)") 
    split_measuring_4 = fields.Float(string="Measuring tape(mm)") 
    split_ctm_4 = fields.Float(string="CTM Machine(Kn)")



       # Type-A Uncertainty (Repeatability)

    split_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    split_child_lines = fields.One2many('mechanical.split.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_split_child_lines())
  
    split_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_split_mean_avg",digits=(12 , 4))

    split_line1_sum = fields.Float(string="(X! - X)",compute="_compute_split_line1_sum",digits=(12,4))
    split_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_split_line1_sum",digits=(12,4))

    standard_devition_split = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_split")
    std_uncertainty1_split = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_split")
    relative_std_split = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_split")
    nos_reading_split = fields.Float(string="Nos of Reading = n")
    degree_freedom_split = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('split_child_lines.split_mean_result')
    def _compute_split_mean_avg(self):
        for record in self:
            split = record.split_child_lines.mapped('split_mean_result')
            if split:
                record.split_mean_avg = sum(split) / len(split)
            else:
                record.split_mean_avg = 0.0


    @api.depends('split_child_lines.split_line2', 'degree_freedom')
    def _compute_standard_devition_split(self):
        for record in self:
            if record.degree_freedom_split != 0:
                split_line2_sum = sum(line.split_line2 for line in record.split_child_lines)
                record.standard_devition_split = math.sqrt(split_line2_sum / record.degree_freedom_split)
            else:
                record.standard_devition_split = 0

    @api.depends('standard_devition_split', 'nos_reading_split')
    def _compute_std_uncertainty1_split(self):
        for record in self:
            if record.nos_reading_split != 0:
                record.std_uncertainty1_split = record.standard_devition_split / math.sqrt(record.nos_reading_split)
            else:
                record.std_uncertainty1_split = 0



   
    @api.depends('std_uncertainty1_split', 'split_mean_avg')
    def _compute_relative_std_split(self):
        for record in self:
            if record.std_uncertainty1_split != 0:
                record.relative_std_split = record.std_uncertainty1_split / record.split_mean_avg
            else:
                record.relative_std_split = 0
                
                
    @api.depends('split_child_lines.split_line1', 'split_child_lines.split_line2')
    def _compute_split_line1_sum(self):
        for record in self:
            record.split_line1_sum = sum(line.split_line1 for line in record.split_child_lines)
            record.split_line2_sum = sum(line.split_line2 for line in record.split_child_lines)




    
    @api.model
    def _default_split_child_lines(self):
        default_split = [
            (0, 0, {'split': 'X1'}),
            (0, 0, {'split': 'X2'}),
            (0, 0, {'split': 'X3'}),
            (0, 0, {'split': 'X4'}),
            (0, 0, {'split': 'X5'}),
            
        ]
        return default_split



     # Type-B Uncertainty

    # (Ub1 (Uncertainty of  W. Balance (gm) 


    type_b_split1_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_split1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_split1", digits=(12, 2), store=True)
    coverage_factor_split1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_split1", store=True)
    mean_split1 = fields.Float(string="Mean",compute="_compute_mean_split1")
    standard_uncertainty_split1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_split1", digits=(12, 2), store=True)
    degree_of_freedom_split1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_split1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_split1",
        store=True
    )
    # , default=float('inf')

    @api.depends('split_w_balance_1')
    def _compute_expanded_uncertainty_split1(self):
        for record in self:
            record.expanded_uncertainty_split1 = record.split_w_balance_1

    @api.depends('split_w_balance_2')
    def _compute_coverage_factor_split1(self):
        for record in self:
            record.coverage_factor_split1 = record.split_w_balance_2

    
    @api.depends('expanded_uncertainty_split1', 'coverage_factor_split1')
    def _compute_standard_uncertainty_split1(self):
        for record in self:
            if record.coverage_factor_split1 != 0:
                record.standard_uncertainty_split1 = record.expanded_uncertainty_split1 / record.coverage_factor_split1
            else:
                record.standard_uncertainty_split1 = 0


    @api.depends('split_w_balance_3')
    def _compute_mean_split1(self):
        for record in self:
            record.mean_split1 = record.split_w_balance_3


    @api.depends('standard_uncertainty_split1', 'mean_split1')
    def _compute_relative_stds_split1(self):
        for record in self:
            if record.mean_split1 != 0:
                record.relative_std_uncertainty_split1 = record.standard_uncertainty_split1 / record.mean_split1
            else:
                record.relative_std_uncertainty_split1 = 0

    #  Ub2 (Uncertainty of Measuring tape (mm))
    expanded_uncertainty_split2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_split2", digits=(12, 4), store=True)
    coverage_factor_split2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_split2", store=True)
    mean_split2 = fields.Float(string="Mean",compute="_compute_mean_split2")
    standard_uncertainty_split2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_split2", digits=(12, 4), store=True)
    degree_of_freedom_split2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_split2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_split2",
        store=True
    )
    # , default=float('inf')

    @api.depends('split_measuring_1')
    def _compute_expanded_uncertainty_split2(self):
        for record in self:
            record.expanded_uncertainty_split2 = record.split_measuring_1

    @api.depends('split_measuring_2')
    def _compute_coverage_factor_split2(self):
        for record in self:
            record.coverage_factor_split2 = record.split_measuring_2

    
    @api.depends('expanded_uncertainty_split2', 'coverage_factor_split2')
    def _compute_standard_uncertainty_split2(self):
        for record in self:
            if record.coverage_factor_split2 != 0:
                record.standard_uncertainty_split2 = record.expanded_uncertainty_split2 / record.coverage_factor_split2
            else:
                record.standard_uncertainty_split2 = 0


    @api.depends('split_measuring_3')
    def _compute_mean_split2(self):
        for record in self:
            record.mean_split2 = record.split_measuring_3


    @api.depends('standard_uncertainty_split2', 'mean_split2')
    def _compute_relative_stds_split2(self):
        for record in self:
            if record.mean_split2 != 0:
                record.relative_std_uncertainty_split2 = record.standard_uncertainty_split2 / record.mean_split2
            else:
                record.relative_std_uncertainty_split2 = 0


    #  Ub3 (Uncertainty of CTM Machine(Kn))
    expanded_uncertainty_split3 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub3 ex)",compute="_compute_expanded_uncertainty_split3", digits=(13, 4), store=True)
    coverage_factor_split3 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_split3", store=True)
    mean_split3 = fields.Float(string="Mean",compute="_compute_mean_split3")
    standard_uncertainty_split3 = fields.Float(string="Standard Uncertainty  Ub3 = [Ub3 ex/ k]",compute="_compute_standard_uncertainty_split3", digits=(13, 4), store=True)
    degree_of_freedom_split3 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_split3 = fields.Float(
        string="Relative Std. Uncertainty (Ub3/ Mean)",digits=(13,5),
        compute="_compute_relative_stds_split3",
        store=True
    )
    # , default=float('inf')

    @api.depends('split_ctm_1')
    def _compute_expanded_uncertainty_split3(self):
        for record in self:
            record.expanded_uncertainty_split3 = record.split_ctm_1

    @api.depends('split_ctm_2')
    def _compute_coverage_factor_split3(self):
        for record in self:
            record.coverage_factor_split3 = record.split_ctm_2

    
    @api.depends('expanded_uncertainty_split3', 'coverage_factor_split3')
    def _compute_standard_uncertainty_split3(self):
        for record in self:
            if record.coverage_factor_split3 != 0:
                record.standard_uncertainty_split3 = record.expanded_uncertainty_split3 / record.coverage_factor_split3
            else:
                record.standard_uncertainty_split3 = 0


    @api.depends('split_ctm_3')
    def _compute_mean_split3(self):
        for record in self:
            record.mean_split3 = record.split_ctm_3


    @api.depends('standard_uncertainty_split3', 'mean_split3')
    def _compute_relative_stds_split3(self):
        for record in self:
            if record.mean_split3 != 0:
                record.relative_std_uncertainty_split3 = record.standard_uncertainty_split3 / record.mean_split3
            else:
                record.relative_std_uncertainty_split3 = 0


    combined_standard_split_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    split_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_split_uc")

    @api.depends('relative_std_split', 'relative_std_uncertainty_split1','relative_std_uncertainty_split2','relative_std_uncertainty_split3')
    def _compute_split_uc(self):
        for record in self:
            record.split_uc = math.sqrt(
                record.relative_std_split**2 + 
                record.relative_std_uncertainty_split1**2 + 
                record.relative_std_uncertainty_split2**2 +
                record.relative_std_uncertainty_split3**2 
                
                 )


    effective_freedom_split_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    split_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_split_verr")


    @api.depends('split_uc', 'relative_std_split', 'degree_freedom_split')
    def _compute_split_verr(self):
        for record in self:
            if record.degree_freedom_split and record.relative_std_split:
                try:
                    record.split_verr = (record.split_uc ** 4) / (record.relative_std_split ** 4 / record.degree_freedom_split)
                except ZeroDivisionError:
                    record.split_verr = 0  # Handle division by zero
            else:
                record.split_verr = 0  


    split_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    split_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_split_verr_relative_expanded")
    
    split_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_split_verr_expanded_uncertainty")

    @api.depends('split_uc', 'split_verr_covrage_factor')
    def _compute_split_verr_relative_expanded(self):
        for record in self:
            record.split_verr_relative_expanded = record.split_uc * record.split_verr_covrage_factor

    @api.depends('split_verr_relative_expanded', 'split_mean_avg')
    def _compute_split_verr_expanded_uncertainty(self):
        for record in self:
            record.split_verr_expanded_uncertainty = record.split_verr_relative_expanded * record.split_mean_avg


     # 8) drying Shrinkage Of Concrete



    drying_name = fields.Char("Name",default="Drying Shrinkage Of Concrete")
    drying_visible = fields.Boolean("Drying Shrinkage Of Concrete  Visible",compute="_compute_visible")

    drying_vernier_1 = fields.Float(string="Vernier Caliper (mm)",digits=(12,4)) 
    drying_hot_1 = fields.Float(string="Hot air oven  (°c)") 
    drying_dial_1 = fields.Float(string="Dial Guage (mm)",digits=(12,4))

    
   
     

    drying_vernier_2 = fields.Float(string="Vernier Caliper (mm)") 
    drying_hot_2 = fields.Float(string="Hot air oven  (°c)") 
    drying_dial_2 = fields.Float(string="Dial Guage (mm)")


    drying_vernier_3 = fields.Float(string="Vernier Caliper (mm)") 
    drying_hot_3 = fields.Float(string="Hot air oven  (°c)") 
    drying_dial_3 = fields.Float(string="Dial Guage (mm)")

     # Type-A Uncertainty (Repeatability)

    drying_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    drying_child_lines = fields.One2many('mechanical.drying.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_drying_child_lines())
  
    drying_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_drying_mean_avg",digits=(12 , 4))

    drying_line1_sum = fields.Float(string="(X! - X)",compute="_compute_drying_line1_sum",digits=(12,7))
    drying_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_drying_line1_sum",digits=(12,6))

    standard_devition_drying = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_drying")
    std_uncertainty1_drying = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_drying")
    relative_std_drying = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_drying")
    nos_reading_drying = fields.Float(string="Nos of Reading = n")
    degree_freedom_drying = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('drying_child_lines.drying_mean_result')
    def _compute_drying_mean_avg(self):
        for record in self:
            drying = record.drying_child_lines.mapped('drying_mean_result')
            if drying:
                record.drying_mean_avg = sum(drying) / len(drying)
            else:
                record.drying_mean_avg = 0.0


    @api.depends('drying_child_lines.drying_line2', 'degree_freedom')
    def _compute_standard_devition_drying(self):
        for record in self:
            if record.degree_freedom_drying != 0:
                drying_line2_sum = sum(line.drying_line2 for line in record.drying_child_lines)
                record.standard_devition_drying = math.sqrt(drying_line2_sum / record.degree_freedom_drying)
            else:
                record.standard_devition_drying = 0

    @api.depends('standard_devition_drying', 'nos_reading_drying')
    def _compute_std_uncertainty1_drying(self):
        for record in self:
            if record.nos_reading_drying != 0:
                record.std_uncertainty1_drying = record.standard_devition_drying / math.sqrt(record.nos_reading_drying)
            else:
                record.std_uncertainty1_drying = 0



   
    @api.depends('std_uncertainty1_drying', 'drying_mean_avg')
    def _compute_relative_std_drying(self):
        for record in self:
            if record.std_uncertainty1_drying != 0:
                record.relative_std_drying = record.std_uncertainty1_drying / record.drying_mean_avg
            else:
                record.relative_std_drying = 0
                
                
    @api.depends('drying_child_lines.drying_line1', 'drying_child_lines.drying_line2')
    def _compute_drying_line1_sum(self):
        for record in self:
            record.drying_line1_sum = sum(line.drying_line1 for line in record.drying_child_lines)
            record.drying_line2_sum = sum(line.drying_line2 for line in record.drying_child_lines)




    
    @api.model
    def _default_drying_child_lines(self):
        default_drying = [
            (0, 0, {'drying': 'X1'}),
            (0, 0, {'drying': 'X2'}),
            (0, 0, {'drying': 'X3'}),
            (0, 0, {'drying': 'X4'}),
            (0, 0, {'drying': 'X5'}),
            
        ]
        return default_drying

     # Type-B Uncertainty

    # Ub1 (Uncertainty of  Vernier Caliper (mm) 


    type_b_drying1_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_drying1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_drying1", digits=(12, 4), store=True)
    coverage_factor_drying1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_drying1", store=True)
    mean_drying1 = fields.Float(string="Mean",compute="_compute_mean_drying1")
    standard_uncertainty_drying1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_drying1", digits=(12, 2), store=True)
    degree_of_freedom_drying1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_drying1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_drying1",
        store=True
    )
    # , default=float('inf')

    @api.depends('drying_vernier_1')
    def _compute_expanded_uncertainty_drying1(self):
        for record in self:
            record.expanded_uncertainty_drying1 = record.drying_vernier_1

    @api.depends('drying_vernier_2')
    def _compute_coverage_factor_drying1(self):
        for record in self:
            record.coverage_factor_drying1 = record.drying_vernier_2

    
    @api.depends('expanded_uncertainty_drying1', 'coverage_factor_drying1')
    def _compute_standard_uncertainty_drying1(self):
        for record in self:
            if record.coverage_factor_drying1 != 0:
                record.standard_uncertainty_drying1 = record.expanded_uncertainty_drying1 / record.coverage_factor_drying1
            else:
                record.standard_uncertainty_drying1 = 0


    @api.depends('drying_vernier_3')
    def _compute_mean_drying1(self):
        for record in self:
            record.mean_drying1 = record.drying_vernier_3


    @api.depends('standard_uncertainty_drying1', 'mean_drying1')
    def _compute_relative_stds_drying1(self):
        for record in self:
            if record.mean_drying1 != 0:
                record.relative_std_uncertainty_drying1 = record.standard_uncertainty_drying1 / record.mean_drying1
            else:
                record.relative_std_uncertainty_drying1 = 0

    #  Ub2 (Uncertainty of Hot air oven (°c))
    expanded_uncertainty_drying2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_drying2", digits=(12, 4), store=True)
    coverage_factor_drying2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_drying2", store=True)
    mean_drying2 = fields.Float(string="Mean",compute="_compute_mean_drying2")
    standard_uncertainty_drying2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_drying2", digits=(12, 4), store=True)
    degree_of_freedom_drying2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_drying2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_drying2",
        store=True
    )
    # , default=float('inf')

    @api.depends('drying_hot_1')
    def _compute_expanded_uncertainty_drying2(self):
        for record in self:
            record.expanded_uncertainty_drying2 = record.drying_hot_1

    @api.depends('drying_hot_2')
    def _compute_coverage_factor_drying2(self):
        for record in self:
            record.coverage_factor_drying2 = record.drying_hot_2

    
    @api.depends('expanded_uncertainty_drying2', 'coverage_factor_drying2')
    def _compute_standard_uncertainty_drying2(self):
        for record in self:
            if record.coverage_factor_drying2 != 0:
                record.standard_uncertainty_drying2 = record.expanded_uncertainty_drying2 / record.coverage_factor_drying2
            else:
                record.standard_uncertainty_drying2 = 0


    @api.depends('drying_hot_3')
    def _compute_mean_drying2(self):
        for record in self:
            record.mean_drying2 = record.drying_hot_3


    @api.depends('standard_uncertainty_drying2', 'mean_drying2')
    def _compute_relative_stds_drying2(self):
        for record in self:
            if record.mean_drying2 != 0:
                record.relative_std_uncertainty_drying2 = record.standard_uncertainty_drying2 / record.mean_drying2
            else:
                record.relative_std_uncertainty_drying2 = 0


    #  Ub3 (Uncertainty of Dial Guage (mm))
    expanded_uncertainty_drying3 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub3 ex)",compute="_compute_expanded_uncertainty_drying3", digits=(13, 4), store=True)
    coverage_factor_drying3 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_drying3", store=True)
    mean_drying3 = fields.Float(string="Mean",compute="_compute_mean_drying3")
    standard_uncertainty_drying3 = fields.Float(string="Standard Uncertainty  Ub3 = [Ub3 ex/ k]",compute="_compute_standard_uncertainty_drying3", digits=(13, 4), store=True)
    degree_of_freedom_drying3 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_drying3 = fields.Float(
        string="Relative Std. Uncertainty (Ub3/ Mean)",digits=(13,5),
        compute="_compute_relative_stds_drying3",
        store=True
    )
    # , default=float('inf')

    @api.depends('drying_dial_1')
    def _compute_expanded_uncertainty_drying3(self):
        for record in self:
            record.expanded_uncertainty_drying3 = record.drying_dial_1

    @api.depends('drying_dial_2')
    def _compute_coverage_factor_drying3(self):
        for record in self:
            record.coverage_factor_drying3 = record.drying_dial_2

    
    @api.depends('expanded_uncertainty_drying3', 'coverage_factor_drying3')
    def _compute_standard_uncertainty_drying3(self):
        for record in self:
            if record.coverage_factor_drying3 != 0:
                record.standard_uncertainty_drying3 = record.expanded_uncertainty_drying3 / record.coverage_factor_drying3
            else:
                record.standard_uncertainty_drying3 = 0


    @api.depends('drying_dial_3')
    def _compute_mean_drying3(self):
        for record in self:
            record.mean_drying3 = record.drying_dial_3


    @api.depends('standard_uncertainty_drying3', 'mean_drying3')
    def _compute_relative_stds_drying3(self):
        for record in self:
            if record.mean_drying3 != 0:
                record.relative_std_uncertainty_drying3 = record.standard_uncertainty_drying3 / record.mean_drying3
            else:
                record.relative_std_uncertainty_drying3 = 0

    
    combined_standard_drying_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    drying_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_drying_uc")

    @api.depends('relative_std_drying', 'relative_std_uncertainty_drying1','relative_std_uncertainty_drying2','relative_std_uncertainty_drying3')
    def _compute_drying_uc(self):
        for record in self:
            record.drying_uc = math.sqrt(
                record.relative_std_drying**2 + 
                record.relative_std_uncertainty_drying1**2 + 
                record.relative_std_uncertainty_drying2**2 +
                record.relative_std_uncertainty_drying3**2 
                
                 )


    effective_freedom_drying_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    drying_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_drying_verr")


    @api.depends('drying_uc', 'relative_std_drying', 'degree_freedom_drying')
    def _compute_drying_verr(self):
        for record in self:
            if record.degree_freedom_drying and record.relative_std_drying:
                try:
                    record.drying_verr = (record.drying_uc ** 4) / (record.relative_std_drying ** 4 / record.degree_freedom_drying)
                except ZeroDivisionError:
                    record.drying_verr = 0  # Handle division by zero
            else:
                record.drying_verr = 0  


    drying_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    drying_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_drying_verr_relative_expanded")
    
    drying_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_drying_verr_expanded_uncertainty")

    @api.depends('drying_uc', 'drying_verr_covrage_factor')
    def _compute_drying_verr_relative_expanded(self):
        for record in self:
            record.drying_verr_relative_expanded = record.drying_uc * record.drying_verr_covrage_factor

    @api.depends('drying_verr_relative_expanded', 'drying_mean_avg')
    def _compute_drying_verr_expanded_uncertainty(self):
        for record in self:
            record.drying_verr_expanded_uncertainty = record.drying_verr_relative_expanded * record.drying_mean_avg


    # 9) moisture Movement Of Concrete



    moisture_name = fields.Char("Name",default="Moisture Movement Of Concrete")
    moisture_visible = fields.Boolean("Moisture Movement Of Concrete  Visible",compute="_compute_visible")

    moisture_vernier_1 = fields.Float(string="Vernier Caliper (mm)",digits=(12,4)) 
    moisture_hot_1 = fields.Float(string="Hot air oven  (°c)") 
    moisture_dial_1 = fields.Float(string="Dial Guage (mm)",digits=(12,4))

    
   
     

    moisture_vernier_2 = fields.Float(string="Vernier Caliper (mm)") 
    moisture_hot_2 = fields.Float(string="Hot air oven  (°c)") 
    moisture_dial_2 = fields.Float(string="Dial Guage (mm)")


    moisture_vernier_3 = fields.Float(string="Vernier Caliper (mm)") 
    moisture_hot_3 = fields.Float(string="Hot air oven  (°c)") 
    moisture_dial_3 = fields.Float(string="Dial Guage (mm)")

     # Type-A Uncertainty (Repeatability)

    moisture_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    moisture_child_lines = fields.One2many('mechanical.moisture.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_moisture_child_lines())
  
    moisture_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_moisture_mean_avg",digits=(12 , 4))

    moisture_line1_sum = fields.Float(string="(X! - X)",compute="_compute_moisture_line1_sum",digits=(12,7))
    moisture_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_moisture_line1_sum",digits=(12,6))

    standard_devition_moisture = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_moisture")
    std_uncertainty1_moisture = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_moisture")
    relative_std_moisture = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_moisture")
    nos_reading_moisture = fields.Float(string="Nos of Reading = n")
    degree_freedom_moisture = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('moisture_child_lines.moisture_mean_result')
    def _compute_moisture_mean_avg(self):
        for record in self:
            moisture = record.moisture_child_lines.mapped('moisture_mean_result')
            if moisture:
                record.moisture_mean_avg = sum(moisture) / len(moisture)
            else:
                record.moisture_mean_avg = 0.0


    @api.depends('moisture_child_lines.moisture_line2', 'degree_freedom')
    def _compute_standard_devition_moisture(self):
        for record in self:
            if record.degree_freedom_moisture != 0:
                moisture_line2_sum = sum(line.moisture_line2 for line in record.moisture_child_lines)
                record.standard_devition_moisture = math.sqrt(moisture_line2_sum / record.degree_freedom_moisture)
            else:
                record.standard_devition_moisture = 0

    @api.depends('standard_devition_moisture', 'nos_reading_moisture')
    def _compute_std_uncertainty1_moisture(self):
        for record in self:
            if record.nos_reading_moisture != 0:
                record.std_uncertainty1_moisture = record.standard_devition_moisture / math.sqrt(record.nos_reading_moisture)
            else:
                record.std_uncertainty1_moisture = 0



   
    @api.depends('std_uncertainty1_moisture', 'moisture_mean_avg')
    def _compute_relative_std_moisture(self):
        for record in self:
            if record.std_uncertainty1_moisture != 0:
                record.relative_std_moisture = record.std_uncertainty1_moisture / record.moisture_mean_avg
            else:
                record.relative_std_moisture = 0
                
                
    @api.depends('moisture_child_lines.moisture_line1', 'moisture_child_lines.moisture_line2')
    def _compute_moisture_line1_sum(self):
        for record in self:
            record.moisture_line1_sum = sum(line.moisture_line1 for line in record.moisture_child_lines)
            record.moisture_line2_sum = sum(line.moisture_line2 for line in record.moisture_child_lines)




    
    @api.model
    def _default_moisture_child_lines(self):
        default_moisture = [
            (0, 0, {'moisture': 'X1'}),
            (0, 0, {'moisture': 'X2'}),
            (0, 0, {'moisture': 'X3'}),
            (0, 0, {'moisture': 'X4'}),
            (0, 0, {'moisture': 'X5'}),
            
        ]
        return default_moisture

      # Type-B Uncertainty

    # Ub1 (Uncertainty of  Vernier Caliper (mm) 


    type_b_moisture1_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_moisture1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_moisture1", digits=(12, 4), store=True)
    coverage_factor_moisture1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_moisture1", store=True)
    mean_moisture1 = fields.Float(string="Mean",compute="_compute_mean_moisture1")
    standard_uncertainty_moisture1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_moisture1", digits=(12, 2), store=True)
    degree_of_freedom_moisture1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_moisture1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_moisture1",
        store=True
    )
    # , default=float('inf')

    @api.depends('moisture_vernier_1')
    def _compute_expanded_uncertainty_moisture1(self):
        for record in self:
            record.expanded_uncertainty_moisture1 = record.moisture_vernier_1

    @api.depends('moisture_vernier_2')
    def _compute_coverage_factor_moisture1(self):
        for record in self:
            record.coverage_factor_moisture1 = record.moisture_vernier_2

    
    @api.depends('expanded_uncertainty_moisture1', 'coverage_factor_moisture1')
    def _compute_standard_uncertainty_moisture1(self):
        for record in self:
            if record.coverage_factor_moisture1 != 0:
                record.standard_uncertainty_moisture1 = record.expanded_uncertainty_moisture1 / record.coverage_factor_moisture1
            else:
                record.standard_uncertainty_moisture1 = 0


    @api.depends('moisture_vernier_3')
    def _compute_mean_moisture1(self):
        for record in self:
            record.mean_moisture1 = record.moisture_vernier_3


    @api.depends('standard_uncertainty_moisture1', 'mean_moisture1')
    def _compute_relative_stds_moisture1(self):
        for record in self:
            if record.mean_moisture1 != 0:
                record.relative_std_uncertainty_moisture1 = record.standard_uncertainty_moisture1 / record.mean_moisture1
            else:
                record.relative_std_uncertainty_moisture1 = 0

    #  Ub2 (Uncertainty of Hot air oven (°c))
    expanded_uncertainty_moisture2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_moisture2", digits=(12, 4), store=True)
    coverage_factor_moisture2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_moisture2", store=True)
    mean_moisture2 = fields.Float(string="Mean",compute="_compute_mean_moisture2")
    standard_uncertainty_moisture2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_moisture2", digits=(12, 4), store=True)
    degree_of_freedom_moisture2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_moisture2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_moisture2",
        store=True
    )
    # , default=float('inf')

    @api.depends('moisture_hot_1')
    def _compute_expanded_uncertainty_moisture2(self):
        for record in self:
            record.expanded_uncertainty_moisture2 = record.moisture_hot_1

    @api.depends('moisture_hot_2')
    def _compute_coverage_factor_moisture2(self):
        for record in self:
            record.coverage_factor_moisture2 = record.moisture_hot_2

    
    @api.depends('expanded_uncertainty_moisture2', 'coverage_factor_moisture2')
    def _compute_standard_uncertainty_moisture2(self):
        for record in self:
            if record.coverage_factor_moisture2 != 0:
                record.standard_uncertainty_moisture2 = record.expanded_uncertainty_moisture2 / record.coverage_factor_moisture2
            else:
                record.standard_uncertainty_moisture2 = 0


    @api.depends('moisture_hot_3')
    def _compute_mean_moisture2(self):
        for record in self:
            record.mean_moisture2 = record.moisture_hot_3


    @api.depends('standard_uncertainty_moisture2', 'mean_moisture2')
    def _compute_relative_stds_moisture2(self):
        for record in self:
            if record.mean_moisture2 != 0:
                record.relative_std_uncertainty_moisture2 = record.standard_uncertainty_moisture2 / record.mean_moisture2
            else:
                record.relative_std_uncertainty_moisture2 = 0


    #  Ub3 (Uncertainty of Dial Guage (mm))
    expanded_uncertainty_moisture3 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub3 ex)",compute="_compute_expanded_uncertainty_moisture3", digits=(13, 4), store=True)
    coverage_factor_moisture3 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_moisture3", store=True)
    mean_moisture3 = fields.Float(string="Mean",compute="_compute_mean_moisture3")
    standard_uncertainty_moisture3 = fields.Float(string="Standard Uncertainty  Ub3 = [Ub3 ex/ k]",compute="_compute_standard_uncertainty_moisture3", digits=(13, 4), store=True)
    degree_of_freedom_moisture3 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_moisture3 = fields.Float(
        string="Relative Std. Uncertainty (Ub3/ Mean)",digits=(13,5),
        compute="_compute_relative_stds_moisture3",
        store=True
    )
    # , default=float('inf')

    @api.depends('moisture_dial_1')
    def _compute_expanded_uncertainty_moisture3(self):
        for record in self:
            record.expanded_uncertainty_moisture3 = record.moisture_dial_1

    @api.depends('moisture_dial_2')
    def _compute_coverage_factor_moisture3(self):
        for record in self:
            record.coverage_factor_moisture3 = record.moisture_dial_2

    
    @api.depends('expanded_uncertainty_moisture3', 'coverage_factor_moisture3')
    def _compute_standard_uncertainty_moisture3(self):
        for record in self:
            if record.coverage_factor_moisture3 != 0:
                record.standard_uncertainty_moisture3 = record.expanded_uncertainty_moisture3 / record.coverage_factor_moisture3
            else:
                record.standard_uncertainty_moisture3 = 0


    @api.depends('moisture_dial_3')
    def _compute_mean_moisture3(self):
        for record in self:
            record.mean_moisture3 = record.moisture_dial_3


    @api.depends('standard_uncertainty_moisture3', 'mean_moisture3')
    def _compute_relative_stds_moisture3(self):
        for record in self:
            if record.mean_moisture3 != 0:
                record.relative_std_uncertainty_moisture3 = record.standard_uncertainty_moisture3 / record.mean_moisture3
            else:
                record.relative_std_uncertainty_moisture3 = 0

    
    combined_standard_moisture_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    moisture_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_moisture_uc")

    @api.depends('relative_std_moisture', 'relative_std_uncertainty_moisture1','relative_std_uncertainty_moisture2','relative_std_uncertainty_moisture3')
    def _compute_moisture_uc(self):
        for record in self:
            record.moisture_uc = math.sqrt(
                record.relative_std_moisture**2 + 
                record.relative_std_uncertainty_moisture1**2 + 
                record.relative_std_uncertainty_moisture2**2 +
                record.relative_std_uncertainty_moisture3**2 
                
                 )


    effective_freedom_moisture_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    moisture_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_moisture_verr")


    @api.depends('moisture_uc', 'relative_std_moisture', 'degree_freedom_moisture')
    def _compute_moisture_verr(self):
        for record in self:
            if record.degree_freedom_moisture and record.relative_std_moisture:
                try:
                    record.moisture_verr = (record.moisture_uc ** 4) / (record.relative_std_moisture ** 4 / record.degree_freedom_moisture)
                except ZeroDivisionError:
                    record.moisture_verr = 0  # Handle division by zero
            else:
                record.moisture_verr = 0  


    moisture_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    moisture_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_moisture_verr_relative_expanded")
    
    moisture_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_moisture_verr_expanded_uncertainty")

    @api.depends('moisture_uc', 'moisture_verr_covrage_factor')
    def _compute_moisture_verr_relative_expanded(self):
        for record in self:
            record.moisture_verr_relative_expanded = record.moisture_uc * record.moisture_verr_covrage_factor

    @api.depends('moisture_verr_relative_expanded', 'moisture_mean_avg')
    def _compute_moisture_verr_expanded_uncertainty(self):
        for record in self:
            record.moisture_verr_expanded_uncertainty = record.moisture_verr_relative_expanded * record.moisture_mean_avg

     # 10) slump0  Slump 0 min

    slump0_name = fields.Char("Name",default="Slump 0 min")
    slump0_visible = fields.Boolean("Slump 0 min  Visible",compute="_compute_visible")

    slump0_cone_1 = fields.Float(string="Slump cone(mm)",digits=(12,4)) 
    slump0_taping_1 = fields.Float(string="Concrete Tamping rod(mm)") 
    
    slump0_cone_2 = fields.Float(string="Slump cone(mm)") 
    slump0_taping_2 = fields.Float(string="Concrete Tamping rod(mm)") 

    slump0_cone_3 = fields.Float(string="Slump cone(mm)") 
    slump0_taping_3 = fields.Float(string="Concrete Tamping rod(mm)") 
   

    
     # Type-A Uncertainty (Repeatability)

    slump0_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    slump0_child_lines = fields.One2many('mechanical.slump0.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_slump0_child_lines())
  
    slump0_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_slump0_mean_avg",digits=(12 , 4))

    slump0_line1_sum = fields.Float(string="(X! - X)",compute="_compute_slump0_line1_sum",digits=(12,4))
    slump0_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_slump0_line1_sum",digits=(12,4))

    standard_devition_slump0 = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_slump0")
    std_uncertainty1_slump0 = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_slump0")
    relative_std_slump0 = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_slump0")
    nos_reading_slump0 = fields.Float(string="Nos of Reading = n")
    degree_freedom_slump0 = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('slump0_child_lines.slump0_mean_result')
    def _compute_slump0_mean_avg(self):
        for record in self:
            slump0 = record.slump0_child_lines.mapped('slump0_mean_result')
            if slump0:
                record.slump0_mean_avg = sum(slump0) / len(slump0)
            else:
                record.slump0_mean_avg = 0.0


    @api.depends('slump0_child_lines.slump0_line2', 'degree_freedom')
    def _compute_standard_devition_slump0(self):
        for record in self:
            if record.degree_freedom_slump0 != 0:
                slump0_line2_sum = sum(line.slump0_line2 for line in record.slump0_child_lines)
                record.standard_devition_slump0 = math.sqrt(slump0_line2_sum / record.degree_freedom_slump0)
            else:
                record.standard_devition_slump0 = 0

    @api.depends('standard_devition_slump0', 'nos_reading_slump0')
    def _compute_std_uncertainty1_slump0(self):
        for record in self:
            if record.nos_reading_slump0 != 0:
                record.std_uncertainty1_slump0 = record.standard_devition_slump0 / math.sqrt(record.nos_reading_slump0)
            else:
                record.std_uncertainty1_slump0 = 0



   
    @api.depends('std_uncertainty1_slump0', 'slump0_mean_avg')
    def _compute_relative_std_slump0(self):
        for record in self:
            if record.std_uncertainty1_slump0 != 0:
                record.relative_std_slump0 = record.std_uncertainty1_slump0 / record.slump0_mean_avg
            else:
                record.relative_std_slump0 = 0
                
                
    @api.depends('slump0_child_lines.slump0_line1', 'slump0_child_lines.slump0_line2')
    def _compute_slump0_line1_sum(self):
        for record in self:
            record.slump0_line1_sum = sum(line.slump0_line1 for line in record.slump0_child_lines)
            record.slump0_line2_sum = sum(line.slump0_line2 for line in record.slump0_child_lines)




    
    @api.model
    def _default_slump0_child_lines(self):
        default_slump0 = [
            (0, 0, {'slump0': 'X1'}),
            (0, 0, {'slump0': 'X2'}),
            (0, 0, {'slump0': 'X3'}),
            (0, 0, {'slump0': 'X4'}),
            (0, 0, {'slump0': 'X5'}),
            
        ]
        return default_slump0


       # Type-B Uncertainty

    # Ub1 (Uncertainty of  Slump cone(mm)) 


    type_b_slump01_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_slump01 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_slump01", digits=(12, 4), store=True)
    coverage_factor_slump01 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump01", store=True)
    mean_slump01 = fields.Float(string="Mean",compute="_compute_mean_slump01")
    standard_uncertainty_slump01 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_slump01", digits=(12, 2), store=True)
    degree_of_freedom_slump01 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump01 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump01",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump0_cone_1')
    def _compute_expanded_uncertainty_slump01(self):
        for record in self:
            record.expanded_uncertainty_slump01 = record.slump0_cone_1

    @api.depends('slump0_cone_2')
    def _compute_coverage_factor_slump01(self):
        for record in self:
            record.coverage_factor_slump01 = record.slump0_cone_2

    
    @api.depends('expanded_uncertainty_slump01', 'coverage_factor_slump01')
    def _compute_standard_uncertainty_slump01(self):
        for record in self:
            if record.coverage_factor_slump01 != 0:
                record.standard_uncertainty_slump01 = record.expanded_uncertainty_slump01 / record.coverage_factor_slump01
            else:
                record.standard_uncertainty_slump01 = 0


    @api.depends('slump0_cone_3')
    def _compute_mean_slump01(self):
        for record in self:
            record.mean_slump01 = record.slump0_cone_3


    @api.depends('standard_uncertainty_slump01', 'mean_slump01')
    def _compute_relative_stds_slump01(self):
        for record in self:
            if record.mean_slump01 != 0:
                record.relative_std_uncertainty_slump01 = record.standard_uncertainty_slump01 / record.mean_slump01
            else:
                record.relative_std_uncertainty_slump01 = 0

    #  Ub2 (Uncertainty of Concrete Tamping rod(mm))
    expanded_uncertainty_slump02 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_slump02", digits=(12, 4), store=True)
    coverage_factor_slump02 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump02", store=True)
    mean_slump02 = fields.Float(string="Mean",compute="_compute_mean_slump02")
    standard_uncertainty_slump02 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_slump02", digits=(12, 4), store=True)
    degree_of_freedom_slump02 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump02 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump02",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump0_taping_1')
    def _compute_expanded_uncertainty_slump02(self):
        for record in self:
            record.expanded_uncertainty_slump02 = record.slump0_taping_1

    @api.depends('slump0_taping_2')
    def _compute_coverage_factor_slump02(self):
        for record in self:
            record.coverage_factor_slump02 = record.slump0_taping_2

    
    @api.depends('expanded_uncertainty_slump02', 'coverage_factor_slump02')
    def _compute_standard_uncertainty_slump02(self):
        for record in self:
            if record.coverage_factor_slump02 != 0:
                record.standard_uncertainty_slump02 = record.expanded_uncertainty_slump02 / record.coverage_factor_slump02
            else:
                record.standard_uncertainty_slump02 = 0


    @api.depends('slump0_taping_3')
    def _compute_mean_slump02(self):
        for record in self:
            record.mean_slump02 = record.slump0_taping_3


    @api.depends('standard_uncertainty_slump02', 'mean_slump02')
    def _compute_relative_stds_slump02(self):
        for record in self:
            if record.mean_slump02 != 0:
                record.relative_std_uncertainty_slump02 = record.standard_uncertainty_slump02 / record.mean_slump02
            else:
                record.relative_std_uncertainty_slump02 = 0

     
    combined_standard_slump02_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    slump02_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_slump02_uc")

    @api.depends('relative_std_slump0', 'relative_std_uncertainty_slump01','relative_std_uncertainty_slump02')
    def _compute_slump02_uc(self):
        for record in self:
            record.slump02_uc = math.sqrt(
                record.relative_std_slump0**2 + 
                record.relative_std_uncertainty_slump01**2 + 
                record.relative_std_uncertainty_slump02**2 
                
                 )


    effective_freedom_slump02_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    slump02_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_slump02_verr")


    @api.depends('slump02_uc', 'relative_std_slump0', 'degree_freedom_slump0')
    def _compute_slump02_verr(self):
        for record in self:
            if record.degree_freedom_slump0 and record.relative_std_slump0:
                try:
                    record.slump02_verr = (record.slump02_uc ** 4) / (record.relative_std_slump0 ** 4 / record.degree_freedom_slump0)
                except ZeroDivisionError:
                    record.slump02_verr = 0  # Handle division by zero
            else:
                record.slump02_verr = 0  


    slump02_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    slump02_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_slump02_verr_relative_expanded")
    
    slump02_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_slump02_verr_expanded_uncertainty")

    @api.depends('slump02_uc', 'slump02_verr_covrage_factor')
    def _compute_slump02_verr_relative_expanded(self):
        for record in self:
            record.slump02_verr_relative_expanded = record.slump02_uc * record.slump02_verr_covrage_factor

    @api.depends('slump02_verr_relative_expanded', 'slump0_mean_avg')
    def _compute_slump02_verr_expanded_uncertainty(self):
        for record in self:
            record.slump02_verr_expanded_uncertainty = record.slump02_verr_relative_expanded * record.slump0_mean_avg

    

     # 11) slump0  Slump 30 min

    slump30_name = fields.Char("Name",default="Slump 30 min")
    slump30_visible = fields.Boolean("Slump 30 min  Visible",compute="_compute_visible")

    slump30_cone_1 = fields.Float(string="Slump cone(mm)",digits=(12,4)) 
    slump30_taping_1 = fields.Float(string="Concrete Tamping rod(mm)") 
    
    slump30_cone_2 = fields.Float(string="Slump cone(mm)") 
    slump30_taping_2 = fields.Float(string="Concrete Tamping rod(mm)") 

    slump30_cone_3 = fields.Float(string="Slump cone(mm)") 
    slump30_taping_3 = fields.Float(string="Concrete Tamping rod(mm)") 
   

    
     # Type-A Uncertainty (Repeatability)

    slump30_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    slump30_child_lines = fields.One2many('mechanical.slump30.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_slump30_child_lines())
  
    slump30_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_slump30_mean_avg",digits=(12 , 4))

    slump30_line1_sum = fields.Float(string="(X! - X)",compute="_compute_slump30_line1_sum",digits=(12,4))
    slump30_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_slump30_line1_sum",digits=(12,4))

    standard_devition_slump30 = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_slump30")
    std_uncertainty1_slump30 = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_slump30")
    relative_std_slump30 = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_slump30")
    nos_reading_slump30 = fields.Float(string="Nos of Reading = n")
    degree_freedom_slump30 = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('slump30_child_lines.slump30_mean_result')
    def _compute_slump30_mean_avg(self):
        for record in self:
            slump30 = record.slump30_child_lines.mapped('slump30_mean_result')
            if slump30:
                record.slump30_mean_avg = sum(slump30) / len(slump30)
            else:
                record.slump30_mean_avg = 0.0


    @api.depends('slump30_child_lines.slump30_line2', 'degree_freedom')
    def _compute_standard_devition_slump30(self):
        for record in self:
            if record.degree_freedom_slump30 != 0:
                slump30_line2_sum = sum(line.slump30_line2 for line in record.slump30_child_lines)
                record.standard_devition_slump30 = math.sqrt(slump30_line2_sum / record.degree_freedom_slump30)
            else:
                record.standard_devition_slump30 = 0

    @api.depends('standard_devition_slump30', 'nos_reading_slump30')
    def _compute_std_uncertainty1_slump30(self):
        for record in self:
            if record.nos_reading_slump30 != 0:
                record.std_uncertainty1_slump30 = record.standard_devition_slump30 / math.sqrt(record.nos_reading_slump30)
            else:
                record.std_uncertainty1_slump30 = 0



   
    @api.depends('std_uncertainty1_slump30', 'slump30_mean_avg')
    def _compute_relative_std_slump30(self):
        for record in self:
            if record.std_uncertainty1_slump30 != 0:
                record.relative_std_slump30 = record.std_uncertainty1_slump30 / record.slump30_mean_avg
            else:
                record.relative_std_slump30 = 0
                
                
    @api.depends('slump30_child_lines.slump30_line1', 'slump30_child_lines.slump30_line2')
    def _compute_slump30_line1_sum(self):
        for record in self:
            record.slump30_line1_sum = sum(line.slump30_line1 for line in record.slump30_child_lines)
            record.slump30_line2_sum = sum(line.slump30_line2 for line in record.slump30_child_lines)




    
    @api.model
    def _default_slump30_child_lines(self):
        default_slump30 = [
            (0, 0, {'slump30': 'X1'}),
            (0, 0, {'slump30': 'X2'}),
            (0, 0, {'slump30': 'X3'}),
            (0, 0, {'slump30': 'X4'}),
            (0, 0, {'slump30': 'X5'}),
            
        ]
        return default_slump30



     # Type-B Uncertainty

    # Ub1 (Uncertainty of  Slump cone(mm)) 


    type_b_slump30_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_slump30_1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_slump30_1", digits=(12, 4), store=True)
    coverage_factor_slump30_1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump30_1", store=True)
    mean_slump30_1 = fields.Float(string="Mean",compute="_compute_mean_slump30_1")
    standard_uncertainty_slump30_1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_slump30_1", digits=(12, 2), store=True)
    degree_of_freedom_slump30_1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump30_1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump30_1",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump30_cone_1')
    def _compute_expanded_uncertainty_slump30_1(self):
        for record in self:
            record.expanded_uncertainty_slump30_1 = record.slump30_cone_1

    @api.depends('slump30_cone_2')
    def _compute_coverage_factor_slump30_1(self):
        for record in self:
            record.coverage_factor_slump30_1 = record.slump30_cone_2

    
    @api.depends('expanded_uncertainty_slump30_1', 'coverage_factor_slump30_1')
    def _compute_standard_uncertainty_slump30_1(self):
        for record in self:
            if record.coverage_factor_slump30_1 != 0:
                record.standard_uncertainty_slump30_1 = record.expanded_uncertainty_slump30_1 / record.coverage_factor_slump30_1
            else:
                record.standard_uncertainty_slump30_1 = 0


    @api.depends('slump30_cone_3')
    def _compute_mean_slump30_1(self):
        for record in self:
            record.mean_slump30_1 = record.slump30_cone_3


    @api.depends('standard_uncertainty_slump30_1', 'mean_slump30_1')
    def _compute_relative_stds_slump30_1(self):
        for record in self:
            if record.mean_slump30_1 != 0:
                record.relative_std_uncertainty_slump30_1 = record.standard_uncertainty_slump30_1 / record.mean_slump30_1
            else:
                record.relative_std_uncertainty_slump30_1 = 0

    #  Ub2 (Uncertainty of Concrete Tamping rod(mm))
    expanded_uncertainty_slump30_2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_slump30_2", digits=(12, 4), store=True)
    coverage_factor_slump30_2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump30_2", store=True)
    mean_slump30_2 = fields.Float(string="Mean",compute="_compute_mean_slump30_2")
    standard_uncertainty_slump30_2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_slump30_2", digits=(12, 4), store=True)
    degree_of_freedom_slump30_2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump30_2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump30_2",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump30_taping_1')
    def _compute_expanded_uncertainty_slump30_2(self):
        for record in self:
            record.expanded_uncertainty_slump30_2 = record.slump30_taping_1

    @api.depends('slump30_taping_2')
    def _compute_coverage_factor_slump30_2(self):
        for record in self:
            record.coverage_factor_slump30_2 = record.slump30_taping_2

    
    @api.depends('expanded_uncertainty_slump30_2', 'coverage_factor_slump30_2')
    def _compute_standard_uncertainty_slump30_2(self):
        for record in self:
            if record.coverage_factor_slump30_2 != 0:
                record.standard_uncertainty_slump30_2 = record.expanded_uncertainty_slump30_2 / record.coverage_factor_slump30_2
            else:
                record.standard_uncertainty_slump30_2 = 0


    @api.depends('slump30_taping_3')
    def _compute_mean_slump30_2(self):
        for record in self:
            record.mean_slump30_2 = record.slump30_taping_3


    @api.depends('standard_uncertainty_slump30_2', 'mean_slump30_2')
    def _compute_relative_stds_slump30_2(self):
        for record in self:
            if record.mean_slump30_2 != 0:
                record.relative_std_uncertainty_slump30_2 = record.standard_uncertainty_slump30_2 / record.mean_slump30_2
            else:
                record.relative_std_uncertainty_slump30_2 = 0

     
    combined_standard_slump30_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    slump30_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_slump30_uc")

    @api.depends('relative_std_slump30', 'relative_std_uncertainty_slump30_1','relative_std_uncertainty_slump30_2')
    def _compute_slump30_uc(self):
        for record in self:
            record.slump30_uc = math.sqrt(
                record.relative_std_slump30**2 + 
                record.relative_std_uncertainty_slump30_1**2 + 
                record.relative_std_uncertainty_slump30_2**2 
                
                 )


    effective_freedom_slump30_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    slump30_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_slump30_verr")


    @api.depends('slump30_uc', 'relative_std_slump30', 'degree_freedom_slump30')
    def _compute_slump30_verr(self):
        for record in self:
            if record.degree_freedom_slump30 and record.relative_std_slump30:
                try:
                    record.slump30_verr = (record.slump30_uc ** 4) / (record.relative_std_slump30 ** 4 / record.degree_freedom_slump30)
                except ZeroDivisionError:
                    record.slump30_verr = 0  # Handle division by zero
            else:
                record.slump30_verr = 0  


    slump30_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    slump30_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_slump30_verr_relative_expanded")
    
    slump30_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_slump30_verr_expanded_uncertainty")

    @api.depends('slump30_uc', 'slump30_verr_covrage_factor')
    def _compute_slump30_verr_relative_expanded(self):
        for record in self:
            record.slump30_verr_relative_expanded = record.slump30_uc * record.slump30_verr_covrage_factor

    @api.depends('slump30_verr_relative_expanded', 'slump30_mean_avg')
    def _compute_slump30_verr_expanded_uncertainty(self):
        for record in self:
            record.slump30_verr_expanded_uncertainty = record.slump30_verr_relative_expanded * record.slump30_mean_avg

    

     # 12) slump60  Slump 60 min

    slump60_name = fields.Char("Name",default="Slump 60 min")
    slump60_visible = fields.Boolean("Slump 60 min  Visible",compute="_compute_visible")

    slump60_cone_1 = fields.Float(string="Slump cone(mm)",digits=(12,4)) 
    slump60_taping_1 = fields.Float(string="Concrete Tamping rod(mm)") 
    
    slump60_cone_2 = fields.Float(string="Slump cone(mm)") 
    slump60_taping_2 = fields.Float(string="Concrete Tamping rod(mm)") 

    slump60_cone_3 = fields.Float(string="Slump cone(mm)") 
    slump60_taping_3 = fields.Float(string="Concrete Tamping rod(mm)") 
   

    
     # Type-A Uncertainty (Repeatability)

    slump60_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    slump60_child_lines = fields.One2many('mechanical.slump60.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_slump60_child_lines())
  
    slump60_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_slump60_mean_avg",digits=(12 , 4))

    slump60_line1_sum = fields.Float(string="(X! - X)",compute="_compute_slump60_line1_sum",digits=(12,4))
    slump60_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_slump60_line1_sum",digits=(12,4))

    standard_devition_slump60 = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_slump60")
    std_uncertainty1_slump60 = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_slump60")
    relative_std_slump60 = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_slump60")
    nos_reading_slump60 = fields.Float(string="Nos of Reading = n")
    degree_freedom_slump60 = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('slump60_child_lines.slump60_mean_result')
    def _compute_slump60_mean_avg(self):
        for record in self:
            slump60 = record.slump60_child_lines.mapped('slump60_mean_result')
            if slump60:
                record.slump60_mean_avg = sum(slump60) / len(slump60)
            else:
                record.slump60_mean_avg = 0.0


    @api.depends('slump60_child_lines.slump60_line2', 'degree_freedom')
    def _compute_standard_devition_slump60(self):
        for record in self:
            if record.degree_freedom_slump60 != 0:
                slump60_line2_sum = sum(line.slump60_line2 for line in record.slump60_child_lines)
                record.standard_devition_slump60 = math.sqrt(slump60_line2_sum / record.degree_freedom_slump60)
            else:
                record.standard_devition_slump60 = 0

    @api.depends('standard_devition_slump60', 'nos_reading_slump60')
    def _compute_std_uncertainty1_slump60(self):
        for record in self:
            if record.nos_reading_slump60 != 0:
                record.std_uncertainty1_slump60 = record.standard_devition_slump60 / math.sqrt(record.nos_reading_slump60)
            else:
                record.std_uncertainty1_slump60 = 0



   
    @api.depends('std_uncertainty1_slump60', 'slump60_mean_avg')
    def _compute_relative_std_slump60(self):
        for record in self:
            if record.std_uncertainty1_slump60 != 0:
                record.relative_std_slump60 = record.std_uncertainty1_slump60 / record.slump60_mean_avg
            else:
                record.relative_std_slump60 = 0
                
                
    @api.depends('slump60_child_lines.slump60_line1', 'slump60_child_lines.slump60_line2')
    def _compute_slump60_line1_sum(self):
        for record in self:
            record.slump60_line1_sum = sum(line.slump60_line1 for line in record.slump60_child_lines)
            record.slump60_line2_sum = sum(line.slump60_line2 for line in record.slump60_child_lines)




    
    @api.model
    def _default_slump60_child_lines(self):
        default_slump60 = [
            (0, 0, {'slump60': 'X1'}),
            (0, 0, {'slump60': 'X2'}),
            (0, 0, {'slump60': 'X3'}),
            (0, 0, {'slump60': 'X4'}),
            (0, 0, {'slump60': 'X5'}),
            
        ]
        return default_slump60



      # Type-B Uncertainty

    # Ub1 (Uncertainty of  Slump cone(mm)) 


    type_b_slump60_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_slump60_1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_slump60_1", digits=(12, 4), store=True)
    coverage_factor_slump60_1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump60_1", store=True)
    mean_slump60_1 = fields.Float(string="Mean",compute="_compute_mean_slump60_1")
    standard_uncertainty_slump60_1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_slump60_1", digits=(12, 2), store=True)
    degree_of_freedom_slump60_1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump60_1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump60_1",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump60_cone_1')
    def _compute_expanded_uncertainty_slump60_1(self):
        for record in self:
            record.expanded_uncertainty_slump60_1 = record.slump60_cone_1

    @api.depends('slump60_cone_2')
    def _compute_coverage_factor_slump60_1(self):
        for record in self:
            record.coverage_factor_slump60_1 = record.slump60_cone_2

    
    @api.depends('expanded_uncertainty_slump60_1', 'coverage_factor_slump60_1')
    def _compute_standard_uncertainty_slump60_1(self):
        for record in self:
            if record.coverage_factor_slump60_1 != 0:
                record.standard_uncertainty_slump60_1 = record.expanded_uncertainty_slump60_1 / record.coverage_factor_slump60_1
            else:
                record.standard_uncertainty_slump60_1 = 0


    @api.depends('slump60_cone_3')
    def _compute_mean_slump60_1(self):
        for record in self:
            record.mean_slump60_1 = record.slump60_cone_3


    @api.depends('standard_uncertainty_slump60_1', 'mean_slump60_1')
    def _compute_relative_stds_slump60_1(self):
        for record in self:
            if record.mean_slump60_1 != 0:
                record.relative_std_uncertainty_slump60_1 = record.standard_uncertainty_slump60_1 / record.mean_slump60_1
            else:
                record.relative_std_uncertainty_slump60_1 = 0

    #  Ub2 (Uncertainty of Concrete Tamping rod(mm))
    expanded_uncertainty_slump60_2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_slump60_2", digits=(12, 4), store=True)
    coverage_factor_slump60_2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump60_2", store=True)
    mean_slump60_2 = fields.Float(string="Mean",compute="_compute_mean_slump60_2")
    standard_uncertainty_slump60_2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_slump60_2", digits=(12, 4), store=True)
    degree_of_freedom_slump60_2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump60_2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump60_2",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump60_taping_1')
    def _compute_expanded_uncertainty_slump60_2(self):
        for record in self:
            record.expanded_uncertainty_slump60_2 = record.slump60_taping_1

    @api.depends('slump60_taping_2')
    def _compute_coverage_factor_slump60_2(self):
        for record in self:
            record.coverage_factor_slump60_2 = record.slump60_taping_2

    
    @api.depends('expanded_uncertainty_slump60_2', 'coverage_factor_slump60_2')
    def _compute_standard_uncertainty_slump60_2(self):
        for record in self:
            if record.coverage_factor_slump60_2 != 0:
                record.standard_uncertainty_slump60_2 = record.expanded_uncertainty_slump60_2 / record.coverage_factor_slump60_2
            else:
                record.standard_uncertainty_slump60_2 = 0


    @api.depends('slump60_taping_3')
    def _compute_mean_slump60_2(self):
        for record in self:
            record.mean_slump60_2 = record.slump60_taping_3


    @api.depends('standard_uncertainty_slump60_2', 'mean_slump60_2')
    def _compute_relative_stds_slump60_2(self):
        for record in self:
            if record.mean_slump60_2 != 0:
                record.relative_std_uncertainty_slump60_2 = record.standard_uncertainty_slump60_2 / record.mean_slump60_2
            else:
                record.relative_std_uncertainty_slump60_2 = 0

     
    combined_standard_slump60_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    slump60_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_slump60_uc")

    @api.depends('relative_std_slump60', 'relative_std_uncertainty_slump60_1','relative_std_uncertainty_slump60_2')
    def _compute_slump60_uc(self):
        for record in self:
            record.slump60_uc = math.sqrt(
                record.relative_std_slump60**2 + 
                record.relative_std_uncertainty_slump60_1**2 + 
                record.relative_std_uncertainty_slump60_2**2 
                
                 )


    effective_freedom_slump60_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    slump60_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_slump60_verr")


    @api.depends('slump60_uc', 'relative_std_slump60', 'degree_freedom_slump60')
    def _compute_slump60_verr(self):
        for record in self:
            if record.degree_freedom_slump60 and record.relative_std_slump60:
                try:
                    record.slump60_verr = (record.slump60_uc ** 4) / (record.relative_std_slump60 ** 4 / record.degree_freedom_slump60)
                except ZeroDivisionError:
                    record.slump60_verr = 0  # Handle division by zero
            else:
                record.slump60_verr = 0  


    slump60_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    slump60_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_slump60_verr_relative_expanded")
    
    slump60_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_slump60_verr_expanded_uncertainty")

    @api.depends('slump60_uc', 'slump60_verr_covrage_factor')
    def _compute_slump60_verr_relative_expanded(self):
        for record in self:
            record.slump60_verr_relative_expanded = record.slump60_uc * record.slump60_verr_covrage_factor

    @api.depends('slump60_verr_relative_expanded', 'slump60_mean_avg')
    def _compute_slump60_verr_expanded_uncertainty(self):
        for record in self:
            record.slump60_verr_expanded_uncertainty = record.slump60_verr_relative_expanded * record.slump60_mean_avg

    


    # 13) slump90  Slump 90 min

    slump90_name = fields.Char("Name",default="Slump 90 min")
    slump90_visible = fields.Boolean("Slump 90 min  Visible",compute="_compute_visible")

    slump90_cone_1 = fields.Float(string="Slump cone(mm)",digits=(12,4)) 
    slump90_taping_1 = fields.Float(string="Concrete Tamping rod(mm)") 
    
    slump90_cone_2 = fields.Float(string="Slump cone(mm)") 
    slump90_taping_2 = fields.Float(string="Concrete Tamping rod(mm)") 

    slump90_cone_3 = fields.Float(string="Slump cone(mm)") 
    slump90_taping_3 = fields.Float(string="Concrete Tamping rod(mm)") 
   

    
     # Type-A Uncertainty (Repeatability)

    slump90_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    slump90_child_lines = fields.One2many('mechanical.slump90.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_slump90_child_lines())
  
    slump90_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_slump90_mean_avg",digits=(12 , 4))

    slump90_line1_sum = fields.Float(string="(X! - X)",compute="_compute_slump90_line1_sum",digits=(12,4))
    slump90_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_slump90_line1_sum",digits=(12,4))

    standard_devition_slump90 = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_slump90")
    std_uncertainty1_slump90 = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_slump90")
    relative_std_slump90 = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_slump90")
    nos_reading_slump90 = fields.Float(string="Nos of Reading = n")
    degree_freedom_slump90 = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('slump90_child_lines.slump90_mean_result')
    def _compute_slump90_mean_avg(self):
        for record in self:
            slump90 = record.slump90_child_lines.mapped('slump90_mean_result')
            if slump90:
                record.slump90_mean_avg = sum(slump90) / len(slump90)
            else:
                record.slump90_mean_avg = 0.0


    @api.depends('slump90_child_lines.slump90_line2', 'degree_freedom')
    def _compute_standard_devition_slump90(self):
        for record in self:
            if record.degree_freedom_slump90 != 0:
                slump90_line2_sum = sum(line.slump90_line2 for line in record.slump90_child_lines)
                record.standard_devition_slump90 = math.sqrt(slump90_line2_sum / record.degree_freedom_slump90)
            else:
                record.standard_devition_slump90 = 0

    @api.depends('standard_devition_slump90', 'nos_reading_slump90')
    def _compute_std_uncertainty1_slump90(self):
        for record in self:
            if record.nos_reading_slump90 != 0:
                record.std_uncertainty1_slump90 = record.standard_devition_slump90 / math.sqrt(record.nos_reading_slump90)
            else:
                record.std_uncertainty1_slump90 = 0



   
    @api.depends('std_uncertainty1_slump90', 'slump90_mean_avg')
    def _compute_relative_std_slump90(self):
        for record in self:
            if record.std_uncertainty1_slump90 != 0:
                record.relative_std_slump90 = record.std_uncertainty1_slump90 / record.slump90_mean_avg
            else:
                record.relative_std_slump90 = 0
                
                
    @api.depends('slump90_child_lines.slump90_line1', 'slump90_child_lines.slump90_line2')
    def _compute_slump90_line1_sum(self):
        for record in self:
            record.slump90_line1_sum = sum(line.slump90_line1 for line in record.slump90_child_lines)
            record.slump90_line2_sum = sum(line.slump90_line2 for line in record.slump90_child_lines)




    
    @api.model
    def _default_slump90_child_lines(self):
        default_slump90 = [
            (0, 0, {'slump90': 'X1'}),
            (0, 0, {'slump90': 'X2'}),
            (0, 0, {'slump90': 'X3'}),
            (0, 0, {'slump90': 'X4'}),
            (0, 0, {'slump90': 'X5'}),
            
        ]
        return default_slump90


       # Type-B Uncertainty

    # Ub1 (Uncertainty of  Slump cone(mm)) 


    type_b_slump90_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_slump90_1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_slump90_1", digits=(12, 4), store=True)
    coverage_factor_slump90_1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump90_1", store=True)
    mean_slump90_1 = fields.Float(string="Mean",compute="_compute_mean_slump90_1")
    standard_uncertainty_slump90_1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_slump90_1", digits=(12, 2), store=True)
    degree_of_freedom_slump90_1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump90_1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump90_1",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump90_cone_1')
    def _compute_expanded_uncertainty_slump90_1(self):
        for record in self:
            record.expanded_uncertainty_slump90_1 = record.slump90_cone_1

    @api.depends('slump90_cone_2')
    def _compute_coverage_factor_slump90_1(self):
        for record in self:
            record.coverage_factor_slump90_1 = record.slump90_cone_2

    
    @api.depends('expanded_uncertainty_slump90_1', 'coverage_factor_slump90_1')
    def _compute_standard_uncertainty_slump90_1(self):
        for record in self:
            if record.coverage_factor_slump90_1 != 0:
                record.standard_uncertainty_slump90_1 = record.expanded_uncertainty_slump90_1 / record.coverage_factor_slump90_1
            else:
                record.standard_uncertainty_slump90_1 = 0


    @api.depends('slump90_cone_3')
    def _compute_mean_slump90_1(self):
        for record in self:
            record.mean_slump90_1 = record.slump90_cone_3


    @api.depends('standard_uncertainty_slump90_1', 'mean_slump90_1')
    def _compute_relative_stds_slump90_1(self):
        for record in self:
            if record.mean_slump90_1 != 0:
                record.relative_std_uncertainty_slump90_1 = record.standard_uncertainty_slump90_1 / record.mean_slump90_1
            else:
                record.relative_std_uncertainty_slump90_1 = 0

    #  Ub2 (Uncertainty of Concrete Tamping rod(mm))
    expanded_uncertainty_slump90_2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_slump90_2", digits=(12, 4), store=True)
    coverage_factor_slump90_2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump90_2", store=True)
    mean_slump90_2 = fields.Float(string="Mean",compute="_compute_mean_slump90_2")
    standard_uncertainty_slump90_2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_slump90_2", digits=(12, 4), store=True)
    degree_of_freedom_slump90_2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump90_2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump90_2",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump90_taping_1')
    def _compute_expanded_uncertainty_slump90_2(self):
        for record in self:
            record.expanded_uncertainty_slump90_2 = record.slump90_taping_1

    @api.depends('slump90_taping_2')
    def _compute_coverage_factor_slump90_2(self):
        for record in self:
            record.coverage_factor_slump90_2 = record.slump90_taping_2

    
    @api.depends('expanded_uncertainty_slump90_2', 'coverage_factor_slump90_2')
    def _compute_standard_uncertainty_slump90_2(self):
        for record in self:
            if record.coverage_factor_slump90_2 != 0:
                record.standard_uncertainty_slump90_2 = record.expanded_uncertainty_slump90_2 / record.coverage_factor_slump90_2
            else:
                record.standard_uncertainty_slump90_2 = 0


    @api.depends('slump90_taping_3')
    def _compute_mean_slump90_2(self):
        for record in self:
            record.mean_slump90_2 = record.slump90_taping_3


    @api.depends('standard_uncertainty_slump90_2', 'mean_slump90_2')
    def _compute_relative_stds_slump90_2(self):
        for record in self:
            if record.mean_slump90_2 != 0:
                record.relative_std_uncertainty_slump90_2 = record.standard_uncertainty_slump90_2 / record.mean_slump90_2
            else:
                record.relative_std_uncertainty_slump90_2 = 0

     
    combined_standard_slump90_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    slump90_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_slump90_uc")

    @api.depends('relative_std_slump90', 'relative_std_uncertainty_slump90_1','relative_std_uncertainty_slump90_2')
    def _compute_slump90_uc(self):
        for record in self:
            record.slump90_uc = math.sqrt(
                record.relative_std_slump90**2 + 
                record.relative_std_uncertainty_slump90_1**2 + 
                record.relative_std_uncertainty_slump90_2**2 
                
                 )


    effective_freedom_slump90_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    slump90_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_slump90_verr")


    @api.depends('slump90_uc', 'relative_std_slump90', 'degree_freedom_slump90')
    def _compute_slump90_verr(self):
        for record in self:
            if record.degree_freedom_slump90 and record.relative_std_slump90:
                try:
                    record.slump90_verr = (record.slump90_uc ** 4) / (record.relative_std_slump90 ** 4 / record.degree_freedom_slump90)
                except ZeroDivisionError:
                    record.slump90_verr = 0  # Handle division by zero
            else:
                record.slump90_verr = 0  


    slump90_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    slump90_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_slump90_verr_relative_expanded")
    
    slump90_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_slump90_verr_expanded_uncertainty")

    @api.depends('slump90_uc', 'slump90_verr_covrage_factor')
    def _compute_slump90_verr_relative_expanded(self):
        for record in self:
            record.slump90_verr_relative_expanded = record.slump90_uc * record.slump90_verr_covrage_factor

    @api.depends('slump90_verr_relative_expanded', 'slump90_mean_avg')
    def _compute_slump90_verr_expanded_uncertainty(self):
        for record in self:
            record.slump90_verr_expanded_uncertainty = record.slump90_verr_relative_expanded * record.slump90_mean_avg

    

    # 14) slump120  Slump 120 min

    slump120_name = fields.Char("Name",default="Slump 120 min")
    slump120_visible = fields.Boolean("Slump 120 min  Visible",compute="_compute_visible")

    slump120_cone_1 = fields.Float(string="Slump cone(mm)",digits=(12,4)) 
    slump120_taping_1 = fields.Float(string="Concrete Tamping rod(mm)") 
    
    slump120_cone_2 = fields.Float(string="Slump cone(mm)") 
    slump120_taping_2 = fields.Float(string="Concrete Tamping rod(mm)") 

    slump120_cone_3 = fields.Float(string="Slump cone(mm)") 
    slump120_taping_3 = fields.Float(string="Concrete Tamping rod(mm)") 
   

    
     # Type-A Uncertainty (Repeatability)

    slump120_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    slump120_child_lines = fields.One2many('mechanical.slump120.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_slump120_child_lines())
  
    slump120_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_slump120_mean_avg",digits=(12 , 4))

    slump120_line1_sum = fields.Float(string="(X! - X)",compute="_compute_slump120_line1_sum",digits=(12,4))
    slump120_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_slump120_line1_sum",digits=(12,4))

    standard_devition_slump120 = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_slump120")
    std_uncertainty1_slump120 = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_slump120")
    relative_std_slump120 = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_slump120")
    nos_reading_slump120 = fields.Float(string="Nos of Reading = n")
    degree_freedom_slump120 = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('slump120_child_lines.slump120_mean_result')
    def _compute_slump120_mean_avg(self):
        for record in self:
            slump120 = record.slump120_child_lines.mapped('slump120_mean_result')
            if slump120:
                record.slump120_mean_avg = sum(slump120) / len(slump120)
            else:
                record.slump120_mean_avg = 0.0


    @api.depends('slump120_child_lines.slump120_line2', 'degree_freedom')
    def _compute_standard_devition_slump120(self):
        for record in self:
            if record.degree_freedom_slump120 != 0:
                slump120_line2_sum = sum(line.slump120_line2 for line in record.slump120_child_lines)
                record.standard_devition_slump120 = math.sqrt(slump120_line2_sum / record.degree_freedom_slump120)
            else:
                record.standard_devition_slump120 = 0

    @api.depends('standard_devition_slump120', 'nos_reading_slump120')
    def _compute_std_uncertainty1_slump120(self):
        for record in self:
            if record.nos_reading_slump120 != 0:
                record.std_uncertainty1_slump120 = record.standard_devition_slump120 / math.sqrt(record.nos_reading_slump120)
            else:
                record.std_uncertainty1_slump120 = 0



   
    @api.depends('std_uncertainty1_slump120', 'slump120_mean_avg')
    def _compute_relative_std_slump120(self):
        for record in self:
            if record.std_uncertainty1_slump120 != 0:
                record.relative_std_slump120 = record.std_uncertainty1_slump120 / record.slump120_mean_avg
            else:
                record.relative_std_slump120 = 0
                
                
    @api.depends('slump120_child_lines.slump120_line1', 'slump120_child_lines.slump120_line2')
    def _compute_slump120_line1_sum(self):
        for record in self:
            record.slump120_line1_sum = sum(line.slump120_line1 for line in record.slump120_child_lines)
            record.slump120_line2_sum = sum(line.slump120_line2 for line in record.slump120_child_lines)




    
    @api.model
    def _default_slump120_child_lines(self):
        default_slump120 = [
            (0, 0, {'slump120': 'X1'}),
            (0, 0, {'slump120': 'X2'}),
            (0, 0, {'slump120': 'X3'}),
            (0, 0, {'slump120': 'X4'}),
            (0, 0, {'slump120': 'X5'}),
            
        ]
        return default_slump120


       # Type-B Uncertainty

    # Ub1 (Uncertainty of  Slump cone(mm)) 


    type_b_slump120_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_slump120_1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_slump120_1", digits=(12, 4), store=True)
    coverage_factor_slump120_1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump120_1", store=True)
    mean_slump120_1 = fields.Float(string="Mean",compute="_compute_mean_slump120_1")
    standard_uncertainty_slump120_1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_slump120_1", digits=(12, 2), store=True)
    degree_of_freedom_slump120_1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump120_1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump120_1",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump120_cone_1')
    def _compute_expanded_uncertainty_slump120_1(self):
        for record in self:
            record.expanded_uncertainty_slump120_1 = record.slump120_cone_1

    @api.depends('slump120_cone_2')
    def _compute_coverage_factor_slump120_1(self):
        for record in self:
            record.coverage_factor_slump120_1 = record.slump120_cone_2

    
    @api.depends('expanded_uncertainty_slump120_1', 'coverage_factor_slump120_1')
    def _compute_standard_uncertainty_slump120_1(self):
        for record in self:
            if record.coverage_factor_slump120_1 != 0:
                record.standard_uncertainty_slump120_1 = record.expanded_uncertainty_slump120_1 / record.coverage_factor_slump120_1
            else:
                record.standard_uncertainty_slump120_1 = 0


    @api.depends('slump120_cone_3')
    def _compute_mean_slump120_1(self):
        for record in self:
            record.mean_slump120_1 = record.slump120_cone_3


    @api.depends('standard_uncertainty_slump120_1', 'mean_slump120_1')
    def _compute_relative_stds_slump120_1(self):
        for record in self:
            if record.mean_slump120_1 != 0:
                record.relative_std_uncertainty_slump120_1 = record.standard_uncertainty_slump120_1 / record.mean_slump120_1
            else:
                record.relative_std_uncertainty_slump120_1 = 0

    #  Ub2 (Uncertainty of Concrete Tamping rod(mm))
    expanded_uncertainty_slump120_2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_slump120_2", digits=(12, 4), store=True)
    coverage_factor_slump120_2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump120_2", store=True)
    mean_slump120_2 = fields.Float(string="Mean",compute="_compute_mean_slump120_2")
    standard_uncertainty_slump120_2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_slump120_2", digits=(12, 4), store=True)
    degree_of_freedom_slump120_2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump120_2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump120_2",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump120_taping_1')
    def _compute_expanded_uncertainty_slump120_2(self):
        for record in self:
            record.expanded_uncertainty_slump120_2 = record.slump120_taping_1

    @api.depends('slump120_taping_2')
    def _compute_coverage_factor_slump120_2(self):
        for record in self:
            record.coverage_factor_slump120_2 = record.slump120_taping_2

    
    @api.depends('expanded_uncertainty_slump120_2', 'coverage_factor_slump120_2')
    def _compute_standard_uncertainty_slump120_2(self):
        for record in self:
            if record.coverage_factor_slump120_2 != 0:
                record.standard_uncertainty_slump120_2 = record.expanded_uncertainty_slump120_2 / record.coverage_factor_slump120_2
            else:
                record.standard_uncertainty_slump120_2 = 0


    @api.depends('slump120_taping_3')
    def _compute_mean_slump120_2(self):
        for record in self:
            record.mean_slump120_2 = record.slump120_taping_3


    @api.depends('standard_uncertainty_slump120_2', 'mean_slump120_2')
    def _compute_relative_stds_slump120_2(self):
        for record in self:
            if record.mean_slump120_2 != 0:
                record.relative_std_uncertainty_slump120_2 = record.standard_uncertainty_slump120_2 / record.mean_slump120_2
            else:
                record.relative_std_uncertainty_slump120_2 = 0

     
    combined_standard_slump120_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    slump120_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_slump120_uc")

    @api.depends('relative_std_slump120', 'relative_std_uncertainty_slump120_1','relative_std_uncertainty_slump120_2')
    def _compute_slump120_uc(self):
        for record in self:
            record.slump120_uc = math.sqrt(
                record.relative_std_slump120**2 + 
                record.relative_std_uncertainty_slump120_1**2 + 
                record.relative_std_uncertainty_slump120_2**2 
                
                 )


    effective_freedom_slump120_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    slump120_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_slump120_verr")


    @api.depends('slump120_uc', 'relative_std_slump120', 'degree_freedom_slump120')
    def _compute_slump120_verr(self):
        for record in self:
            if record.degree_freedom_slump120 and record.relative_std_slump120:
                try:
                    record.slump120_verr = (record.slump120_uc ** 4) / (record.relative_std_slump120 ** 4 / record.degree_freedom_slump120)
                except ZeroDivisionError:
                    record.slump120_verr = 0  # Handle division by zero
            else:
                record.slump120_verr = 0  


    slump120_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    slump120_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_slump120_verr_relative_expanded")
    
    slump120_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_slump120_verr_expanded_uncertainty")

    @api.depends('slump120_uc', 'slump120_verr_covrage_factor')
    def _compute_slump120_verr_relative_expanded(self):
        for record in self:
            record.slump120_verr_relative_expanded = record.slump120_uc * record.slump120_verr_covrage_factor

    @api.depends('slump120_verr_relative_expanded', 'slump120_mean_avg')
    def _compute_slump120_verr_expanded_uncertainty(self):
        for record in self:
            record.slump120_verr_expanded_uncertainty = record.slump120_verr_relative_expanded * record.slump120_mean_avg

    

     # 15) slump150  Slump 150 min

    slump150_name = fields.Char("Name",default="Slump 150 min")
    slump150_visible = fields.Boolean("Slump 150 min  Visible",compute="_compute_visible")

    slump150_cone_1 = fields.Float(string="Slump cone(mm)",digits=(12,4)) 
    slump150_taping_1 = fields.Float(string="Concrete Tamping rod(mm)") 
    
    slump150_cone_2 = fields.Float(string="Slump cone(mm)") 
    slump150_taping_2 = fields.Float(string="Concrete Tamping rod(mm)") 

    slump150_cone_3 = fields.Float(string="Slump cone(mm)") 
    slump150_taping_3 = fields.Float(string="Concrete Tamping rod(mm)") 
   

    
     # Type-A Uncertainty (Repeatability)

    slump150_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    slump150_child_lines = fields.One2many('mechanical.slump150.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_slump150_child_lines())
  
    slump150_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_slump150_mean_avg",digits=(12 , 4))

    slump150_line1_sum = fields.Float(string="(X! - X)",compute="_compute_slump150_line1_sum",digits=(12,4))
    slump150_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_slump150_line1_sum",digits=(12,4))

    standard_devition_slump150 = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_slump150")
    std_uncertainty1_slump150 = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_slump150")
    relative_std_slump150 = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_slump150")
    nos_reading_slump150 = fields.Float(string="Nos of Reading = n")
    degree_freedom_slump150 = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('slump150_child_lines.slump150_mean_result')
    def _compute_slump150_mean_avg(self):
        for record in self:
            slump150 = record.slump150_child_lines.mapped('slump150_mean_result')
            if slump150:
                record.slump150_mean_avg = sum(slump150) / len(slump150)
            else:
                record.slump150_mean_avg = 0.0


    @api.depends('slump150_child_lines.slump150_line2', 'degree_freedom')
    def _compute_standard_devition_slump150(self):
        for record in self:
            if record.degree_freedom_slump150 != 0:
                slump150_line2_sum = sum(line.slump150_line2 for line in record.slump150_child_lines)
                record.standard_devition_slump150 = math.sqrt(slump150_line2_sum / record.degree_freedom_slump150)
            else:
                record.standard_devition_slump150 = 0

    @api.depends('standard_devition_slump150', 'nos_reading_slump150')
    def _compute_std_uncertainty1_slump150(self):
        for record in self:
            if record.nos_reading_slump150 != 0:
                record.std_uncertainty1_slump150 = record.standard_devition_slump150 / math.sqrt(record.nos_reading_slump150)
            else:
                record.std_uncertainty1_slump150 = 0



   
    @api.depends('std_uncertainty1_slump150', 'slump150_mean_avg')
    def _compute_relative_std_slump150(self):
        for record in self:
            if record.std_uncertainty1_slump150 != 0:
                record.relative_std_slump150 = record.std_uncertainty1_slump150 / record.slump150_mean_avg
            else:
                record.relative_std_slump150 = 0
                
                
    @api.depends('slump150_child_lines.slump150_line1', 'slump150_child_lines.slump150_line2')
    def _compute_slump150_line1_sum(self):
        for record in self:
            record.slump150_line1_sum = sum(line.slump150_line1 for line in record.slump150_child_lines)
            record.slump150_line2_sum = sum(line.slump150_line2 for line in record.slump150_child_lines)




    
    @api.model
    def _default_slump150_child_lines(self):
        default_slump150 = [
            (0, 0, {'slump150': 'X1'}),
            (0, 0, {'slump150': 'X2'}),
            (0, 0, {'slump150': 'X3'}),
            (0, 0, {'slump150': 'X4'}),
            (0, 0, {'slump150': 'X5'}),
            
        ]
        return default_slump150


       # Type-B Uncertainty

    # Ub1 (Uncertainty of  Slump cone(mm)) 


    type_b_slump150_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_slump150_1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_slump150_1", digits=(12, 4), store=True)
    coverage_factor_slump150_1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump150_1", store=True)
    mean_slump150_1 = fields.Float(string="Mean",compute="_compute_mean_slump150_1")
    standard_uncertainty_slump150_1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_slump150_1", digits=(12, 2), store=True)
    degree_of_freedom_slump150_1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump150_1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump150_1",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump150_cone_1')
    def _compute_expanded_uncertainty_slump150_1(self):
        for record in self:
            record.expanded_uncertainty_slump150_1 = record.slump150_cone_1

    @api.depends('slump150_cone_2')
    def _compute_coverage_factor_slump150_1(self):
        for record in self:
            record.coverage_factor_slump150_1 = record.slump150_cone_2

    
    @api.depends('expanded_uncertainty_slump150_1', 'coverage_factor_slump150_1')
    def _compute_standard_uncertainty_slump150_1(self):
        for record in self:
            if record.coverage_factor_slump150_1 != 0:
                record.standard_uncertainty_slump150_1 = record.expanded_uncertainty_slump150_1 / record.coverage_factor_slump150_1
            else:
                record.standard_uncertainty_slump150_1 = 0


    @api.depends('slump150_cone_3')
    def _compute_mean_slump150_1(self):
        for record in self:
            record.mean_slump150_1 = record.slump150_cone_3


    @api.depends('standard_uncertainty_slump150_1', 'mean_slump150_1')
    def _compute_relative_stds_slump150_1(self):
        for record in self:
            if record.mean_slump150_1 != 0:
                record.relative_std_uncertainty_slump150_1 = record.standard_uncertainty_slump150_1 / record.mean_slump150_1
            else:
                record.relative_std_uncertainty_slump150_1 = 0

    #  Ub2 (Uncertainty of Concrete Tamping rod(mm))
    expanded_uncertainty_slump150_2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_slump150_2", digits=(12, 4), store=True)
    coverage_factor_slump150_2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump150_2", store=True)
    mean_slump150_2 = fields.Float(string="Mean",compute="_compute_mean_slump150_2")
    standard_uncertainty_slump150_2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_slump150_2", digits=(12, 4), store=True)
    degree_of_freedom_slump150_2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump150_2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump150_2",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump150_taping_1')
    def _compute_expanded_uncertainty_slump150_2(self):
        for record in self:
            record.expanded_uncertainty_slump150_2 = record.slump150_taping_1

    @api.depends('slump150_taping_2')
    def _compute_coverage_factor_slump150_2(self):
        for record in self:
            record.coverage_factor_slump150_2 = record.slump150_taping_2

    
    @api.depends('expanded_uncertainty_slump150_2', 'coverage_factor_slump150_2')
    def _compute_standard_uncertainty_slump150_2(self):
        for record in self:
            if record.coverage_factor_slump150_2 != 0:
                record.standard_uncertainty_slump150_2 = record.expanded_uncertainty_slump150_2 / record.coverage_factor_slump150_2
            else:
                record.standard_uncertainty_slump150_2 = 0


    @api.depends('slump150_taping_3')
    def _compute_mean_slump150_2(self):
        for record in self:
            record.mean_slump150_2 = record.slump150_taping_3


    @api.depends('standard_uncertainty_slump150_2', 'mean_slump150_2')
    def _compute_relative_stds_slump150_2(self):
        for record in self:
            if record.mean_slump150_2 != 0:
                record.relative_std_uncertainty_slump150_2 = record.standard_uncertainty_slump150_2 / record.mean_slump150_2
            else:
                record.relative_std_uncertainty_slump150_2 = 0

     
    combined_standard_slump150_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    slump150_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_slump150_uc")

    @api.depends('relative_std_slump150', 'relative_std_uncertainty_slump150_1','relative_std_uncertainty_slump150_2')
    def _compute_slump150_uc(self):
        for record in self:
            record.slump150_uc = math.sqrt(
                record.relative_std_slump150**2 + 
                record.relative_std_uncertainty_slump150_1**2 + 
                record.relative_std_uncertainty_slump150_2**2 
                
                 )


    effective_freedom_slump150_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    slump150_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_slump150_verr")


    @api.depends('slump150_uc', 'relative_std_slump150', 'degree_freedom_slump150')
    def _compute_slump150_verr(self):
        for record in self:
            if record.degree_freedom_slump150 and record.relative_std_slump150:
                try:
                    record.slump150_verr = (record.slump150_uc ** 4) / (record.relative_std_slump150 ** 4 / record.degree_freedom_slump150)
                except ZeroDivisionError:
                    record.slump150_verr = 0  # Handle division by zero
            else:
                record.slump150_verr = 0  


    slump150_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    slump150_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_slump150_verr_relative_expanded")
    
    slump150_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_slump150_verr_expanded_uncertainty")

    @api.depends('slump150_uc', 'slump150_verr_covrage_factor')
    def _compute_slump150_verr_relative_expanded(self):
        for record in self:
            record.slump150_verr_relative_expanded = record.slump150_uc * record.slump150_verr_covrage_factor

    @api.depends('slump150_verr_relative_expanded', 'slump150_mean_avg')
    def _compute_slump150_verr_expanded_uncertainty(self):
        for record in self:
            record.slump150_verr_expanded_uncertainty = record.slump150_verr_relative_expanded * record.slump150_mean_avg
    

     # 16) slump180  Slump 180 min

    slump180_name = fields.Char("Name",default="Slump 180 min")
    slump180_visible = fields.Boolean("Slump 180 min  Visible",compute="_compute_visible")

    slump180_cone_1 = fields.Float(string="Slump cone(mm)",digits=(12,4)) 
    slump180_taping_1 = fields.Float(string="Concrete Tamping rod(mm)") 
    
    slump180_cone_2 = fields.Float(string="Slump cone(mm)") 
    slump180_taping_2 = fields.Float(string="Concrete Tamping rod(mm)") 

    slump180_cone_3 = fields.Float(string="Slump cone(mm)") 
    slump180_taping_3 = fields.Float(string="Concrete Tamping rod(mm)") 
   

    
     # Type-A Uncertainty (Repeatability)

    slump180_type_name = fields.Char("Name",default="Type-A Uncertainty (Repeatability)")
  
    slump180_child_lines = fields.One2many('mechanical.slump180.line','parent_id',string="Parameter",
                                                  default=lambda self: self._default_slump180_child_lines())
  
    slump180_mean_avg = fields.Float(string="Mean =   Measure Results",compute="_compute_slump180_mean_avg",digits=(12 , 4))

    slump180_line1_sum = fields.Float(string="(X! - X)",compute="_compute_slump180_line1_sum",digits=(12,4))
    slump180_line2_sum = fields.Float(string="(X! - X)2",compute="_compute_slump180_line1_sum",digits=(12,4))

    standard_devition_slump180 = fields.Float(string="Standard Deviation",digits=(12 , 4),compute="_compute_standard_devition_slump180")
    std_uncertainty1_slump180 = fields.Float(string="Std Uncertainty Ua =(S/√n) =",digits=(12 , 4),compute="_compute_std_uncertainty1_slump180")
    relative_std_slump180 = fields.Float(string="Relative Std. Uncertainty (Ua/ Mean)",digits=(12 , 5),compute="_compute_relative_std_slump180")
    nos_reading_slump180 = fields.Float(string="Nos of Reading = n")
    degree_freedom_slump180 = fields.Float(string="Degree of Freedom V1= (n-1)")


    @api.depends('slump180_child_lines.slump180_mean_result')
    def _compute_slump180_mean_avg(self):
        for record in self:
            slump180 = record.slump180_child_lines.mapped('slump180_mean_result')
            if slump180:
                record.slump180_mean_avg = sum(slump180) / len(slump180)
            else:
                record.slump180_mean_avg = 0.0


    @api.depends('slump180_child_lines.slump180_line2', 'degree_freedom')
    def _compute_standard_devition_slump180(self):
        for record in self:
            if record.degree_freedom_slump180 != 0:
                slump180_line2_sum = sum(line.slump180_line2 for line in record.slump180_child_lines)
                record.standard_devition_slump180 = math.sqrt(slump180_line2_sum / record.degree_freedom_slump180)
            else:
                record.standard_devition_slump180 = 0

    @api.depends('standard_devition_slump180', 'nos_reading_slump180')
    def _compute_std_uncertainty1_slump180(self):
        for record in self:
            if record.nos_reading_slump180 != 0:
                record.std_uncertainty1_slump180 = record.standard_devition_slump180 / math.sqrt(record.nos_reading_slump180)
            else:
                record.std_uncertainty1_slump180 = 0



   
    @api.depends('std_uncertainty1_slump180', 'slump180_mean_avg')
    def _compute_relative_std_slump180(self):
        for record in self:
            if record.std_uncertainty1_slump180 != 0:
                record.relative_std_slump180 = record.std_uncertainty1_slump180 / record.slump180_mean_avg
            else:
                record.relative_std_slump180 = 0
                
                
    @api.depends('slump180_child_lines.slump180_line1', 'slump180_child_lines.slump180_line2')
    def _compute_slump180_line1_sum(self):
        for record in self:
            record.slump180_line1_sum = sum(line.slump180_line1 for line in record.slump180_child_lines)
            record.slump180_line2_sum = sum(line.slump180_line2 for line in record.slump180_child_lines)




    
    @api.model
    def _default_slump180_child_lines(self):
        default_slump180 = [
            (0, 0, {'slump180': 'X1'}),
            (0, 0, {'slump180': 'X2'}),
            (0, 0, {'slump180': 'X3'}),
            (0, 0, {'slump180': 'X4'}),
            (0, 0, {'slump180': 'X5'}),
            
        ]
        return default_slump180


       # Type-B Uncertainty

    # Ub1 (Uncertainty of  Slump cone(mm)) 


    type_b_slump180_name = fields.Char("Name",default="Type-B Uncertainty")
   
   
    expanded_uncertainty_slump180_1 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub1 ex)",compute="_compute_expanded_uncertainty_slump180_1", digits=(12, 4), store=True)
    coverage_factor_slump180_1 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump180_1", store=True)
    mean_slump180_1 = fields.Float(string="Mean",compute="_compute_mean_slump180_1")
    standard_uncertainty_slump180_1 = fields.Float(string="Standard Uncertainty  Ub1 = [Ub1 ex/ k]",compute="_compute_standard_uncertainty_slump180_1", digits=(12, 2), store=True)
    degree_of_freedom_slump180_1 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump180_1 = fields.Float(
        string="Relative Std. Uncertainty (Ub1/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump180_1",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump180_cone_1')
    def _compute_expanded_uncertainty_slump180_1(self):
        for record in self:
            record.expanded_uncertainty_slump180_1 = record.slump180_cone_1

    @api.depends('slump180_cone_2')
    def _compute_coverage_factor_slump180_1(self):
        for record in self:
            record.coverage_factor_slump180_1 = record.slump180_cone_2

    
    @api.depends('expanded_uncertainty_slump180_1', 'coverage_factor_slump180_1')
    def _compute_standard_uncertainty_slump180_1(self):
        for record in self:
            if record.coverage_factor_slump180_1 != 0:
                record.standard_uncertainty_slump180_1 = record.expanded_uncertainty_slump180_1 / record.coverage_factor_slump180_1
            else:
                record.standard_uncertainty_slump180_1 = 0


    @api.depends('slump180_cone_3')
    def _compute_mean_slump180_1(self):
        for record in self:
            record.mean_slump180_1 = record.slump180_cone_3


    @api.depends('standard_uncertainty_slump180_1', 'mean_slump180_1')
    def _compute_relative_stds_slump180_1(self):
        for record in self:
            if record.mean_slump180_1 != 0:
                record.relative_std_uncertainty_slump180_1 = record.standard_uncertainty_slump180_1 / record.mean_slump180_1
            else:
                record.relative_std_uncertainty_slump180_1 = 0

    #  Ub2 (Uncertainty of Concrete Tamping rod(mm))
    expanded_uncertainty_slump180_2 = fields.Float(string="Expanded Uncertainty of Master in Cert. (Ub2 ex)",compute="_compute_expanded_uncertainty_slump180_2", digits=(12, 4), store=True)
    coverage_factor_slump180_2 = fields.Float(string="Coverage factor (k) =",compute="_compute_coverage_factor_slump180_2", store=True)
    mean_slump180_2 = fields.Float(string="Mean",compute="_compute_mean_slump180_2")
    standard_uncertainty_slump180_2 = fields.Float(string="Standard Uncertainty  Ub2 = [Ub2 ex/ k]",compute="_compute_standard_uncertainty_slump180_2", digits=(12, 4), store=True)
    degree_of_freedom_slump180_2 = fields.Char(string="Degree of freedom =",default="∞")
    relative_std_uncertainty_slump180_2 = fields.Float(
        string="Relative Std. Uncertainty (Ub2/ Mean)",digits=(12,5),
        compute="_compute_relative_stds_slump180_2",
        store=True
    )
    # , default=float('inf')

    @api.depends('slump180_taping_1')
    def _compute_expanded_uncertainty_slump180_2(self):
        for record in self:
            record.expanded_uncertainty_slump180_2 = record.slump180_taping_1

    @api.depends('slump180_taping_2')
    def _compute_coverage_factor_slump180_2(self):
        for record in self:
            record.coverage_factor_slump180_2 = record.slump180_taping_2

    
    @api.depends('expanded_uncertainty_slump180_2', 'coverage_factor_slump180_2')
    def _compute_standard_uncertainty_slump180_2(self):
        for record in self:
            if record.coverage_factor_slump180_2 != 0:
                record.standard_uncertainty_slump180_2 = record.expanded_uncertainty_slump180_2 / record.coverage_factor_slump180_2
            else:
                record.standard_uncertainty_slump180_2 = 0


    @api.depends('slump180_taping_3')
    def _compute_mean_slump180_2(self):
        for record in self:
            record.mean_slump180_2 = record.slump180_taping_3


    @api.depends('standard_uncertainty_slump180_2', 'mean_slump180_2')
    def _compute_relative_stds_slump180_2(self):
        for record in self:
            if record.mean_slump180_2 != 0:
                record.relative_std_uncertainty_slump180_2 = record.standard_uncertainty_slump180_2 / record.mean_slump180_2
            else:
                record.relative_std_uncertainty_slump180_2 = 0

     
    combined_standard_slump180_name = fields.Char("Name",default="Combined Standard Uncertainty (Relative)")
 
    slump180_uc = fields.Float(string="UC = ",digits=(12,5), compute="_compute_slump180_uc")

    @api.depends('relative_std_slump180', 'relative_std_uncertainty_slump180_1','relative_std_uncertainty_slump180_2')
    def _compute_slump180_uc(self):
        for record in self:
            record.slump180_uc = math.sqrt(
                record.relative_std_slump180**2 + 
                record.relative_std_uncertainty_slump180_1**2 + 
                record.relative_std_uncertainty_slump180_2**2 
                
                 )


    effective_freedom_slump180_name = fields.Char("Name",default="Effective Degrees of Freedom")
 
    slump180_verr = fields.Float(string="Verr = ",digits=(12,5),compute="_compute_slump180_verr")


    @api.depends('slump180_uc', 'relative_std_slump180', 'degree_freedom_slump180')
    def _compute_slump180_verr(self):
        for record in self:
            if record.degree_freedom_slump180 and record.relative_std_slump180:
                try:
                    record.slump180_verr = (record.slump180_uc ** 4) / (record.relative_std_slump180 ** 4 / record.degree_freedom_slump180)
                except ZeroDivisionError:
                    record.slump180_verr = 0  # Handle division by zero
            else:
                record.slump180_verr = 0  


    slump180_verr_covrage_factor = fields.Float(string="Covrage Factor (k)- (as per Student t distribution)",digits=(12,3))
    slump180_verr_relative_expanded = fields.Float(string="Relative Expanded Uncertainty U=  k X uc",digits=(12,5),compute="_compute_slump180_verr_relative_expanded")
    
    slump180_verr_expanded_uncertainty = fields.Float(string="Expanded Uncertainty (U X Mean) ±",digits=(12,3),compute="_compute_slump180_verr_expanded_uncertainty")

    @api.depends('slump180_uc', 'slump180_verr_covrage_factor')
    def _compute_slump180_verr_relative_expanded(self):
        for record in self:
            record.slump180_verr_relative_expanded = record.slump180_uc * record.slump180_verr_covrage_factor

    @api.depends('slump180_verr_relative_expanded', 'slump180_mean_avg')
    def _compute_slump180_verr_expanded_uncertainty(self):
        for record in self:
            record.slump180_verr_expanded_uncertainty = record.slump180_verr_relative_expanded * record.slump180_mean_avg



    ### Compute Visible
    @api.depends('sample_parameters')
    def _compute_visible(self):
        
        for record in self:
            record.equipment_visible = False
            record.density_hardened_concrete_visible = False
            record.compressive_visible = False
            record.act_visible = False
            record.flexural_visible = False
            record.water_visible = False
            record.split_visible = False
            record.drying_visible = False
            record.moisture_visible = False
            record.slump0_visible = False
            record.slump30_visible = False
            record.slump60_visible = False
            record.slump90_visible = False
            record.slump120_visible = False
            record.slump150_visible = False
            record.slump180_visible = False




           
          
            
            for sample in record.sample_parameters:
                print("Internal Ids",sample.internal_id)

                if sample.internal_id == "028824e1-462f-4304-a0fd-757daa6484a1":
                    record.equipment_visible = True

                if sample.internal_id == "e0477542-8c51-4906-9570-33adb0428dca":
                    record.density_hardened_concrete_visible = True

                if sample.internal_id == "0936f653-a382-4a98-9061-d8034672b552":
                    record.compressive_visible = True

                if sample.internal_id == "14f3d3b3-fb6a-4379-8556-4d537787b1f7":
                    record.act_visible = True

                if sample.internal_id == "23b04acd-dd1e-4b1b-baae-4a7ca9faa7aa":
                    record.flexural_visible = True

                if sample.internal_id == "1a08f663-f08f-4adb-9728-431f3f2b4282":
                    record.water_visible = True

                if sample.internal_id == "277f9b62-7ad8-4971-b36f-93bce104376e":
                    record.split_visible = True
                
                if sample.internal_id == "483aeff7-21ee-4c5d-8b5c-b98860865123":
                    record.drying_visible = True

                if sample.internal_id == "c8c7e1b4-cc70-456e-b00c-2c37b3503482":
                    record.moisture_visible = True

                if sample.internal_id == "6047e30f-174e-4455-a6b9-d8598f3178dd":
                    record.slump0_visible = True

                if sample.internal_id == "ea32c7eb-8dba-4007-b2f4-10cdf3252ef1":
                    record.slump30_visible = True

                if sample.internal_id == "ab079b28-145d-4348-8ca1-c3c0e62d09f1":
                    record.slump60_visible = True

                if sample.internal_id == "2277e940-724c-4e99-a819-e9219d55fb2a":
                    record.slump90_visible = True
                
                if sample.internal_id == "640e482e-3702-4448-a9c3-5bec14823e28":
                    record.slump120_visible = True
                
                if sample.internal_id == "07b5efb4-0fd0-4507-ae8d-7c8ed3c8af77":
                    record.slump150_visible = True
                
                if sample.internal_id == "6a0fc840-70a5-4fd1-ae6f-77c377523841":
                    record.slump180_visible = True




   
            
           

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
        record = super(MEASUREMENTUNCERTAINTY, self).create(vals)
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
        record = self.env['measurement.uncertainty'].browse(self.ids[0])
        field_values = {}
        for field_name, field in record._fields.items():
            field_value = record[field_name]
            field_values[field_name] = field_value

        return field_values


class MEASUREMENTUNCERTAINTYLINE(models.Model):
    _name = "mechanical.equipment.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    sr_no = fields.Char(string="No. of. Obs.")
    mean_result = fields.Float(string=" Measure Results",digits=(12,2)) 
    line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute_line1")
    line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_line2")



    @api.depends('mean_result', 'parent_id.mean_result_avg')
    def _compute_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.mean_result_avg:
                record.line1 = record.parent_id.mean_result_avg - record.mean_result
            else:
                record.line1 = 0.0


    @api.depends('line1')
    def _compute_line2(self):
        for record in self:
            record.line2 = record.line1 ** 2



# Parameter 2

class DENSITYHRDENDLINE(models.Model):
    _name = "mechanical.density.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    density_no = fields.Char(string="No. of. Obs.")
    mean_result1 = fields.Float(string=" Measure Results",digits=(12,2)) 
    density_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__density_line1")
    density_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_density_line2")



    @api.depends('mean_result1', 'parent_id.mean_result1_avg')
    def _compute__density_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.mean_result1_avg:
                record.density_line1 = record.mean_result1 - record.parent_id.mean_result1_avg
            else:
                record.density_line1 = 0.0


    @api.depends('density_line1')
    def _compute_density_line2(self):
        for record in self:
            record.density_line2 = record.density_line1 ** 2



# Parameter 3) cube compressive strength

class CompressiveLINE(models.Model):
    _name = "mechanical.compressive.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    compressive = fields.Char(string="No. of. Obs.")
    compressive_mean_result = fields.Float(string=" Measure Results",digits=(12,2)) 
    compressive_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__compressive_line1")
    compressive_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_compressive_line2")



    @api.depends('compressive_mean_result', 'parent_id.compressive_mean_avg')
    def _compute__compressive_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.compressive_mean_avg:
                record.compressive_line1 = record.compressive_mean_result - record.parent_id.compressive_mean_avg
            else:
                record.compressive_line1 = 0.0


    @api.depends('compressive_line1')
    def _compute_compressive_line2(self):
        for record in self:
            record.compressive_line2 = record.compressive_line1 ** 2



# Parameter 4) Accelerated Cube Comp Strength  (M40)

class ACTLINE(models.Model):
    _name = "mechanical.act.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    act = fields.Char(string="No. of. Obs.")
    act_mean_result = fields.Float(string=" Measure Results",digits=(12,2)) 
    act_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__act_line1")
    act_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_act_line2")



    @api.depends('act_mean_result', 'parent_id.act_mean_avg')
    def _compute__act_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.act_mean_avg:
                record.act_line1 = record.act_mean_result - record.parent_id.act_mean_avg
            else:
                record.act_line1 = 0.0

    @api.depends('act_line1')
    def _compute_act_line2(self):
        for record in self:
            record.act_line2 = record.act_line1 ** 2



# Parameter 5) Flexural beam Comp Strength (M40)

class FlexuralLINE(models.Model): 
    _name = "mechanical.flexural.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    flexural = fields.Char(string="No. of. Obs.")
    flexural_mean_result = fields.Float(string=" Measure Results",digits=(12,2)) 
    flexural_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__flexural_line1")
    flexural_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_flexural_line2")



    @api.depends('flexural_mean_result', 'parent_id.flexural_mean_avg')
    def _compute__flexural_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.flexural_mean_avg:
                record.flexural_line1 = record.flexural_mean_result - record.parent_id.flexural_mean_avg
            else:
                record.flexural_line1 = 0.0



    @api.depends('flexural_line1')
    def _compute_flexural_line2(self):
        for record in self:
            record.flexural_line2 = record.flexural_line1 ** 2


# Parameter 6) concrete water Absorption

class WaterLINE(models.Model): 
    _name = "mechanical.water.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    water = fields.Char(string="No. of. Obs.")
    water_mean_result = fields.Float(string=" Measure Results",digits=(12,2)) 
    water_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__water_line1")
    water_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_water_line2")



    @api.depends('water_mean_result', 'parent_id.water_mean_avg')
    def _compute__water_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.water_mean_avg:
                record.water_line1 = record.water_mean_result - record.parent_id.water_mean_avg
            else:
                record.water_line1 = 0.0



    @api.depends('water_line1')
    def _compute_water_line2(self):
        for record in self:
            record.water_line2 = record.water_line1 ** 2



# Parameter 7 concrete water Absorption

class SplitLINE(models.Model): 
    _name = "mechanical.split.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    split = fields.Char(string="No. of. Obs.")
    split_mean_result = fields.Float(string=" Measure Results",digits=(12,2)) 
    split_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__split_line1")
    split_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_split_line2")



    @api.depends('split_mean_result', 'parent_id.split_mean_avg')
    def _compute__split_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.split_mean_avg:
                record.split_line1 = record.split_mean_result - record.parent_id.split_mean_avg
            else:
                record.split_line1 = 0.0



    @api.depends('split_line1')
    def _compute_split_line2(self):
        for record in self:
            record.split_line2 = record.split_line1 ** 2


# Parameter 8) Drying Shrinkage Of Concrete

class DryingLINE(models.Model): 
    _name = "mechanical.drying.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    drying = fields.Char(string="No. of. Obs.")
    drying_mean_result = fields.Float(string=" Measure Results",digits=(12,4)) 
    drying_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__drying_line1")
    drying_line2 = fields.Float(string="(X! - X)2",digits=(12,6),compute="_compute_drying_line2")



    @api.depends('drying_mean_result', 'parent_id.drying_mean_avg')
    def _compute__drying_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.drying_mean_avg:
                record.drying_line1 = record.drying_mean_result - record.parent_id.drying_mean_avg
            else:
                record.drying_line1 = 0.0



    @api.depends('drying_line1')
    def _compute_drying_line2(self):
        for record in self:
            record.drying_line2 = record.drying_line1 ** 2

# Parameter 9) moisture Movement Of Concrete

class MoistureLINE(models.Model): 
    _name = "mechanical.moisture.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    moisture = fields.Char(string="No. of. Obs.")
    moisture_mean_result = fields.Float(string=" Measure Results",digits=(12,4)) 
    moisture_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__moisture_line1")
    moisture_line2 = fields.Float(string="(X! - X)2",digits=(12,6),compute="_compute_moisture_line2")



    @api.depends('moisture_mean_result', 'parent_id.moisture_mean_avg')
    def _compute__moisture_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.moisture_mean_avg:
                record.moisture_line1 = record.moisture_mean_result - record.parent_id.moisture_mean_avg
            else:
                record.moisture_line1 = 0.0



    @api.depends('moisture_line1')
    def _compute_moisture_line2(self):
        for record in self:
            record.moisture_line2 = record.moisture_line1 ** 2


# Parameter 10) slump0 0 min

class SlumpLINE(models.Model): 
    _name = "mechanical.slump0.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    slump0 = fields.Char(string="No. of. Obs.")
    slump0_mean_result = fields.Float(string=" Measure Results",digits=(12,4)) 
    slump0_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__slump0_line1")
    slump0_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_slump0_line2")



    @api.depends('slump0_mean_result', 'parent_id.slump0_mean_avg')
    def _compute__slump0_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.slump0_mean_avg:
                record.slump0_line1 =  record.parent_id.slump0_mean_avg - record.slump0_mean_result
            else:
                record.slump0_line1 = 0.0



    @api.depends('slump0_line1')
    def _compute_slump0_line2(self):
        for record in self:
            record.slump0_line2 = record.slump0_line1 ** 2



# Parameter 11) slump0 30 min

class Slump30LINE(models.Model): 
    _name = "mechanical.slump30.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    slump30 = fields.Char(string="No. of. Obs.")
    slump30_mean_result = fields.Float(string=" Measure Results",digits=(12,4)) 
    slump30_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__slump30_line1")
    slump30_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_slump30_line2")



    @api.depends('slump30_mean_result', 'parent_id.slump30_mean_avg')
    def _compute__slump30_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.slump30_mean_avg:
                record.slump30_line1 =  record.parent_id.slump30_mean_avg - record.slump30_mean_result
            else:
                record.slump30_line1 = 0.0



    @api.depends('slump30_line1')
    def _compute_slump30_line2(self):
        for record in self:
            record.slump30_line2 = record.slump30_line1 ** 2


# Parameter 12) slump60 360 min

class Slump60LINE(models.Model): 
    _name = "mechanical.slump60.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    slump60 = fields.Char(string="No. of. Obs.")
    slump60_mean_result = fields.Float(string=" Measure Results",digits=(12,4)) 
    slump60_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__slump60_line1")
    slump60_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_slump60_line2")



    @api.depends('slump60_mean_result', 'parent_id.slump60_mean_avg')
    def _compute__slump60_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.slump60_mean_avg:
                record.slump60_line1 =  record.parent_id.slump60_mean_avg - record.slump60_mean_result
            else:
                record.slump60_line1 = 0.0



    @api.depends('slump60_line1')
    def _compute_slump60_line2(self):
        for record in self:
            record.slump60_line2 = record.slump60_line1 ** 2


# Parameter 13) slump90 90 min

class Slump90LINE(models.Model): 
    _name = "mechanical.slump90.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    slump90 = fields.Char(string="No. of. Obs.")
    slump90_mean_result = fields.Float(string=" Measure Results",digits=(12,4)) 
    slump90_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__slump90_line1")
    slump90_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_slump90_line2")



    @api.depends('slump90_mean_result', 'parent_id.slump90_mean_avg')
    def _compute__slump90_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.slump90_mean_avg:
                record.slump90_line1 =  record.parent_id.slump90_mean_avg - record.slump90_mean_result
            else:
                record.slump90_line1 = 0.0



    @api.depends('slump90_line1')
    def _compute_slump90_line2(self):
        for record in self:
            record.slump90_line2 = record.slump90_line1 ** 2


# Parameter 14) slump120 120 min

class Slump120LINE(models.Model): 
    _name = "mechanical.slump120.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    slump120 = fields.Char(string="No. of. Obs.")
    slump120_mean_result = fields.Float(string=" Measure Results",digits=(12,4)) 
    slump120_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__slump120_line1")
    slump120_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_slump120_line2")



    @api.depends('slump120_mean_result', 'parent_id.slump120_mean_avg')
    def _compute__slump120_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.slump120_mean_avg:
                record.slump120_line1 =  record.parent_id.slump120_mean_avg - record.slump120_mean_result
            else:
                record.slump120_line1 = 0.0



    @api.depends('slump120_line1')
    def _compute_slump120_line2(self):
        for record in self:
            record.slump120_line2 = record.slump120_line1 ** 2


# Parameter 15) slump150 150 min

class Slump150LINE(models.Model): 
    _name = "mechanical.slump150.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    slump150 = fields.Char(string="No. of. Obs.")
    slump150_mean_result = fields.Float(string=" Measure Results",digits=(12,4)) 
    slump150_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__slump150_line1")
    slump150_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_slump150_line2")



    @api.depends('slump150_mean_result', 'parent_id.slump150_mean_avg')
    def _compute__slump150_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.slump150_mean_avg:
                record.slump150_line1 =  record.parent_id.slump150_mean_avg - record.slump150_mean_result
            else:
                record.slump150_line1 = 0.0



    @api.depends('slump150_line1')
    def _compute_slump150_line2(self):
        for record in self:
            record.slump150_line2 = record.slump150_line1 ** 2


# Parameter 16) slump180 180 min

class Slump180LINE(models.Model): 
    _name = "mechanical.slump180.line"
    parent_id = fields.Many2one('mechanical.measurement.uncertainty',string="Parent Id")
   
    slump180 = fields.Char(string="No. of. Obs.")
    slump180_mean_result = fields.Float(string=" Measure Results",digits=(12,4)) 
    slump180_line1 = fields.Float(string="(X! - X)",digits=(12,4),compute="_compute__slump180_line1")
    slump180_line2 = fields.Float(string="(X! - X)2",digits=(12,4),compute="_compute_slump180_line2")



    @api.depends('slump180_mean_result', 'parent_id.slump180_mean_avg')
    def _compute__slump180_line1(self):
        for record in self:
            if record.parent_id and record.parent_id.slump180_mean_avg:
                record.slump180_line1 =  record.parent_id.slump180_mean_avg - record.slump180_mean_result
            else:
                record.slump180_line1 = 0.0



    @api.depends('slump180_line1')
    def _compute_slump180_line2(self):
        for record in self:
            record.slump180_line2 = record.slump180_line1 ** 2




















    
