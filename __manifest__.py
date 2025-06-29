{'name':'LERM_CIVIL',
 'summary': "LERM_CIVIL",
 'author': "Usman Shaikhnag", 
 'website': "http://www.esehat.org", 
 'category': 'Uncategorized', 
 'version': '13.0.1', 
 'depends':['base' , 'contacts','stock','product' , 'mail','documents','documents_spreadsheet','lerm_civil_inv','attachment_indexation','maintenance','portal'],
 'data': [
  
    'security/security.xml',
    'data/sequence.xml',
    'views/enviroment_register.xml',
    'reports/wizard_reports/sample_report.xml',
    'reports/wizard_reports/ulr_report.xml',
    'views/wizards/sample_print_report_wizard.xml',
    'views/lerm.xml',
    'views/groups.xml',
    'views/res_company.xml',
    'views/material.xml',
    'views/srf.xml',
    'views/edit_srf_header_wizard.xml',
    'views/parameter_master.xml',
    'views/datasheet_master.xml',
    'views/sample.xml',
    'views/sample_range.xml',
    'views/eln.xml',
    'views/lab_master.xml',
    'views/contractor.xml',
    'views/employee.xml',
    'views/partner_document.xml',
    'views/customer_sample_request.xml',
    # 'views/mechanical/sieve_analysis.xml',
    'views/mechanical/free_swell_index.xml',
    'views/mechanical/soil_cbr.xml',
    'views/mechanical/heavy_ligth_compaction.xml',
    'views/mechanical/plastic_limit.xml',
    'views/mechanical/liquid_limit.xml',
    'views/mechanical/compressive_strength_solid.xml',
    'views/mechanical/block_density.xml',
    'views/mechanical/split_tensile_strength.xml',
    'views/mechanical/water_absorption_solid.xml',
    'views/mechanical/drying_shrinkage_solid.xml',
    'views/mechanical/moisture_movement_solid.xml',
    'views/mechanical/flexural_strength_concrete_beam.xml',
    'views/mechanical/precast_kerb_stone.xml',
    'views/mechanical/threaded_steel.xml',


    # 'views/mechanical/compressive_strength_concrete_cube.xml',
    'views/mechanical/splitting_tensile_strength_concrete.xml',
    'views/mechanical/act_compressive_concrete_cube.xml',
    # 'views/mechanical/crushing_value_coarse_aggregate.xml',
    # 'views/mechanical/impact_value_coarse_aggregate.xml',
    # 'views/mechanical/loose_bulk_density.xml',
    # 'views/mechanical/rodded_bulk_density.xml',
    # 'views/mechanical/abration_value_coarse_aggregate.xml',
    # 'views/mechanical/specific_gravity_and_water_absorption_coarce_aggregate.xml',
    'views/mechanical/compressive_strength_concrete_man_hole.xml',
    'views/mechanical/moisture_content_concrete_man_hole.xml',
    'views/mechanical/drying_shrinkage_concrete_man_hole.xml',
    'views/mechanical/dimentions_concrete_man_hole.xml',
    'views/mechanical/water_and_gravity_fine_aggregate.xml',
    'views/mechanical/steel_tmt_bar.xml',
    # 'views/mechanical/flakiness_elongated_index.xml',
    'views/mechanical/rock.xml',
    'views/mechanical/structural_steel.xml',
    'views/mechanical/bricks.xml',
    'views/mechanical/compressive_strength_brick.xml',
    'views/mechanical/dry_density_sand_replacement.xml',
    # added
    'views/mechanical/field_density_sand_replacement.xml', 
    'views/mechanical/cement_compatablity.xml',
    'views/mechanical/brick_2.xml',
    'views/chemical/fine_aggregate.xml',
    'views/mechanical/paver_block.xml',
    'views/ndt/crack_width.xml',
    'views/ndt/concrete_core.xml',
    'views/ndt/crack_depth.xml',
    'views/ndt/acil_crack_depth.xml',
    'views/ndt/cover_meter.xml',
    'views/ndt/carbonation_test.xml',
    'views/ndt/rebound_hammer.xml',
    'views/ndt/acil_upv.xml', 
    'views/ndt/upv.xml',
    
    'views/ndt/half_cell.xml',
    'views/mechanical/cement_normal_consistency.xml',
    'views/mechanical/cement_psc.xml',
    'views/mechanical/brick_2.xml',
    'views/mechanical/cement_ppc.xml',
    'views/mechanical/cement_setting_time.xml',
    'views/mechanical/ggbs.xml',
    'views/mechanical/wpt.xml',
    'views/mechanical/gypsum.xml',
    'views/mechanical/fly_ash.xml',
    'views/mechanical/microsilica.xml',
    'views/mechanical/pt_grout.xml',
    'views/mechanical/soil.xml',
    'views/mechanical/aac_block.xml',
    'views/mechanical/coarse_aggregate_mechanical.xml',
    'views/mechanical/aggregate_fine.xml',
    'views/mechanical/concrete_cube2.xml',
    'views/mechanical/wmm.xml',
    'views/mechanical/gsb.xml',
    'views/mechanical/wbm.xml',
    'views/mechanical/isat.xml',
    'views/mechanical/bricks_burnt_clay.xml',
    'views/chemical/crushed_sand.xml',
    



    'views/product_grade_wizard.xml',
    'views/wizards/sample_reports_wizard.xml',
    'views/wizards/ulr_reports_wizard.xml',

    'reports/eln_report_action.xml',
    'reports/eln_report_template.xml',
    'reports/sample_report_template.xml',
    'reports/srf_report_action.xml',
    'reports/srf_report_template.xml',
    'reports/cement/report_cement.xml',
    'reports/microsilica_datasheet.xml',
    'reports/gypsum_report.xml',
    'reports/wpt_report.xml',
    'reports/microsilica_report.xml',
    'reports/report_fly_ash.xml',
    'reports/ggbs_report.xml',
    'reports/pt_grout_report.xml',
    'reports/fine_aggregate_chemical_datasheet.xml',
    'reports/fine_aggregate_chemical_report.xml',
    # 'security/dump.sql',
    'security/ir.model.access.csv',
    'reports/sample_report_action.xml',
    'reports/datasheet_templates.xml',
    'reports/compatiblity_datasheet.xml',
    'reports/compatiblity_report.xml',
    'reports/general_template.xml',
    'reports/ggbs_datasheet.xml',
    'reports/gypsum_datasheet.xml',
    'reports/wpt_datasheet.xml',
    'reports/half_cell_datasheet.xml',
    'reports/half_cell_report.xml',
    'reports/general_report_template.xml',
    'reports/pt_grput_datasheet.xml',
    'reports/ptgrout_non_nabl_report.xml',
    'reports/cement/cement_psc_report.xml',
    'reports/cement/cement_ppc_report.xml',
    'reports/cement/cement_datasheet.xml',
    'reports/concrete_cube_print.xml',
    'reports/coarse_aggregate_mech_datasheet.xml',
    'reports/soil_print.xml',
    'reports/paver_block_report.xml',
    'reports/fine_aggregate_mech_datasheet.xml',
    'reports/bricks/bricks2_datasheet.xml',
    'reports/bricks/bricks2_report.xml',
    'reports/concrete_beam_datasheet.xml',
    'reports/coarse_aggregate_mech_report.xml',
    'views/mechanical/solid_concrete_block.xml',
    'reports/solid_concrete_block_datasheet.xml',
    'reports/concrete_beam_report.xml',
    'reports/steel_tmt_bar_report.xml',
    'reports/aac/aac_block_datasheet.xml',
    'reports/aac/aac_block_report.xml',
    'views/mechanical/concrete_splite_tensile_strength.xml',
    'reports/concrete_split_tensile_datasheet.xml',
    
    'reports/steel_tmt_bar_report.xml',
    'views/mechanical/admixture_mechanical.xml',
    'views/mechanical/rcmt_mechanical.xml',
    'reports/wmm_datasheet.xml',
    'reports/wmm_report.xml',
    'reports/gsb_datasheet.xml',
    'reports/gsb_report.xml',
    'reports/wbm_datasheet.xml',
    'reports/wbm_report.xml',

    'views/mechanical/fusion_bound_coated_steel.xml',
    'reports/fusion_bond_datasheet.xml',
    'reports/fusion_bond_report.xml',
    'reports/rock_print.xml',
    'views/mechanical/rcpt.xml',
    'views/miscellaneous.xml',
    'views/mechanical/ferrous_structural_steel.xml',
    'reports/ferrous_structural_steel_datasheet.xml',
    'reports/ferrous_structural_steel.xml',
    'reports/isat_datasheet.xml',
    'reports/isat_report.xml',
    'reports/admixture/admixture_datasheet.xml',
    'reports/admixture/admixture_report.xml',
    'reports/precast_kerb/precast_kerb_datasheet.xml',
    'reports/precast_kerb/precast_kerb_report.xml',

    'reports/flyash_chemical/flyash_report.xml',

    'reports/rcmt_datasheet.xml',
    'reports/rcmt_report.xml',
    'reports/rcpt/rcpt_datasheet.xml',
    'reports/rcpt/rcpt_report.xml',
    'views/chemical/flyash.xml',
    'reports/flyash_chemical/flyash_datasheet.xml',
    'reports/steel_tmt_bar_datasheet.xml',
    'reports/mechanical_general_template.xml',
    'reports/flyash_datasheet.xml',
    'views/mechanical/copler2.xml',
    'reports/coupler2/coupler_datasheet.xml',
    'reports/coupler2/coupler_report.xml',
    'views/chemical/gypsum.xml',
    'views/chemical/hardend_concrete.xml',
    'reports/hardend_concrete/harden_concrete_datasheet.xml',
    'reports/hardend_concrete/hardend_concrete_report.xml',
    'reports/crushed_sand_chemical/crushed_sand_repot.xml',
    'reports/crushed_sand_chemical/crushed_sand_dataheet.xml',
    'reports/gypsum_chem/gypsum_datasheet.xml',
    'reports/gypsum_chem/gypsum_report.xml',
    'views/sample_cancellation.xml',
    'views/reallocation_wizard.xml',
    'views/chemical/opc_cement_chemical.xml',
    'views/chemical/tmt_bar.xml',
    'views/mechanical/structural_steel_round.xml',
    'reports/structural_steel_round/datasheet.xml',
    'reports/structural_steel_round/report.xml',
    'reports/act/act_datasheet.xml',
    'reports/act/act_report.xml',
    'views/mechanical/drying_shrinkage.xml',
    'reports/drying_shrinkage/drying_datasheet.xml',
    'reports/drying_shrinkage/drying_report.xml',
    'views/mechanical/concrete_cube_water_absorption.xml',
    'reports/concrete_cube_water_absorption/concrete_datasheet.xml',
    'reports/concrete_cube_water_absorption/concrete_report.xml',
    'reports/threaded_steel/threaded_steel_report.xml',
    'reports/threaded_steel/threaded_steel_datasheet.xml',
    'reports/bricks_burnt_clay/bricks_burnt_clay_report.xml',
    'reports/bricks_burnt_clay/bricks_burnt_clay_datasheet.xml',
    'views/mechanical/concrete_mix_design.xml',
    'reports/concreate_design_mix/design_mix_datasheet.xml',
    'reports/concreate_design_mix/design_mix_report.xml',
    'views/mechanical/measurement_uncertainty.xml',
    'reports/measurment_uncertainty/datasheet.xml',
    'reports/measurment_uncertainty/report.xml',
    'views/mechanical/stainless_steel_tmt.xml',
    'reports/stainless_steel/stainless_steel_report.xml',
    'reports/stainless_steel/stainless_steel_datasheet.xml',
    'views/mechanical/tile.xml',
    'reports/tile/tile_datasheet.xml',
    'reports/tile/tile_report.xml',
    'views/ndt/pile_integrity.xml',
    'reports/pile_integrity_report.xml',
    'views/mechanical/gypsum_plaster_board.xml',
    'reports/gypsum_plaster/gypsum_datasheet.xml',
    'reports/gypsum_plaster/gypsum_plaster_report.xml',
    'views/mechanical/shuttering_plywood.xml',
    'reports/shuttering_plywood/shuttering_datasheet.xml',
    'reports/shuttering_plywood/shuttering_report.xml',
    'views/mechanical/particle_board.xml',
    'reports/particle_board/particle_datasheet.xml',
    'views/portal/lerm_portal.xml',
    'reports/particle_board/particle_report.xml',
    'views/mechanical/door.xml',
    'reports/door/door_datasheet.xml',
    'reports/door/door_report.xml',
    'views/sample_test_request.xml',
    'views/mechanical/natural_building_stone.xml',
    'reports/natural_stone/natural_datasheet.xml',
    'reports/natural_stone/natural_report.xml',
    'views/mechanical/tiles_chequered.xml',
    'reports/tile_chequered/tile_chequered_datasheet.xml',
    'reports/tile_chequered/tile_chequered_report.xml',
    'views/mechanical/cement_chequerd_tile.xml',
    'reports/cement_chequerd_tile/cement_tile_datasheet.xml',
    'reports/cement_chequerd_tile/cement_chequerd_report.xml',
    'views/mechanical/morter_cube.xml',
    'reports/mortar_cube/mortar_cube_datasheet.xml',
    'reports/mortar_cube/mortar_cube_report.xml',
    'reports/seperated_module_action.xml',
    'views/mechanical/plate_load.xml',
    'reports/plate_load/plate_load_datasheet.xml',
    'reports/plate_load/plate_load_report.xml',
    'views/mechanical/wood.xml',
    'reports/wood/wood_datasheet.xml',
    'reports/wood/wood_report.xml',
    'views/mechanical/temprature_monitoring.xml',
    'reports/temprature_monitoring/temprature_datasheet.xml',
    'reports/temprature_monitoring/temprature_monitoring_report.xml'
    # 'reports/demo_dsreport/datashet.xml'


    # 'views/portal_template.xml'
    


    
    
 



    
    ],
    'assets': {
    'web.assets_backend':[
        '/lerm_civil/static/src/js/spreadsheet.js'
    ],
    'web.assets_frontend': [
        'lerm_civil/static/src/js/portal_request.js',
    ],
    'web.report_assets_common': [
            '/lerm_civil/static/src/css/eln_report.scss',
            '/lerm_civil/static/src/css/data_sheet_styles.scss',

        ],
    'web.assets_qweb': [
        '/lerm_civil/static/src/xml/spreadsheet.xml'
    ],
        }
}
