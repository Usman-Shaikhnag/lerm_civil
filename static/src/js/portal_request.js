odoo.define('lerm_civil.portal_request', function(require) {
    "use strict";
    
    var $ = require('jquery');
    var ajax = require('web.ajax');
    
    $(document).ready(function() {
        // Discipline change handler
        $('#discipline_select').on('change', function() {
            var disciplineId = $(this).val();
            var $groupSelect = $('#group_select');
            var $productSelect = $('#product_select');
            
            $groupSelect.empty().append($('<option>', {
                value: '',
                text: '-- Select Group --'
            })).prop('disabled', true);
            
            $productSelect.empty().append($('<option>', {
                value: '',
                text: '-- Select Product --'
            })).prop('disabled', true);
            
            if (disciplineId) {
                // Show loading
                $groupSelect.empty().append($('<option>', {
                    value: '',
                    text: 'Loading...'
                }));
                
                ajax.jsonRpc('/lerm/get_groups', 'call', {
                    'discipline_id': disciplineId
                }).then(function(data) {
                    if (data.groups && data.groups.length > 0) {
                        $groupSelect.empty().append($('<option>', {
                            value: '',
                            text: '-- Select Group --'
                        }));
                        
                        $.each(data.groups, function(index, group) {
                            $groupSelect.append($('<option>', {
                                value: group.id,
                                text: group.name
                            }));
                        });
                        
                        $groupSelect.prop('disabled', false);
                    } else {
                        $groupSelect.empty().append($('<option>', {
                            value: '',
                            text: 'No groups found'
                        }));
                    }
                }).fail(function(error) {
                    console.error("Error:", error);
                    $groupSelect.empty().append($('<option>', {
                        value: '',
                        text: 'Error loading groups'
                    }));
                });
            }
        });
        
        // Group change handler
        $('#group_select').on('change', function() {
            var groupId = $(this).val();
            var $productSelect = $('#product_select');
            
            $productSelect.empty().append($('<option>', {
                value: '',
                text: '-- Select Product --'
            }));
            
            if (groupId) {
                $productSelect.empty().append($('<option>', {
                    value: '',
                    text: 'Loading...'
                }));
                
                ajax.jsonRpc('/lerm/get_products', 'call', {
                    'group_id': groupId
                }).then(function(data) {
                    if (data.products && data.products.length > 0) {
                        $productSelect.empty().append($('<option>', {
                            value: '',
                            text: '-- Select Product --'
                        }));
                        
                        $.each(data.products, function(index, product) {
                            $productSelect.append($('<option>', {
                                value: product.id,
                                text: product.name
                            }));
                        });
                        
                        $productSelect.prop('disabled', false);
                    } else {
                        $productSelect.empty().append($('<option>', {
                            value: '',
                            text: 'No products found'
                        }));
                    }
                }).fail(function(error) {
                    console.error("Error:", error);
                    $productSelect.empty().append($('<option>', {
                        value: '',
                        text: 'Error loading products'
                    }));
                });
            } else {
                $productSelect.prop('disabled', true);
            }
        });
    });
});