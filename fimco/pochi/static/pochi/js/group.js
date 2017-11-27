/**
 * Created by Arthur on 9/29/2017.
 */
$(document).ready(function() {
    // The maximum number of options
    var MAX_OPTIONS = 5;
    var form = jQuery('.form-horizontal');

    if (form.find(':visible[name="option[]"]').length < 2) {
        form.find('#done').hide();
    }

    form.formValidation({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            'option[]': {
                validators: {
                    notEmpty: {
                        message: 'Add POCHI member ID, cannot be empty'
                    },
                    stringLength: {
                        max: 20,
                        message: 'The option must be less than 20 characters long'
                    },
                    callback: {
                        callback: function(value, validator, $field) {
                            var $options          = validator.getFieldElements('option[]'),
                                numOptions        = $options.length,
                                notEmptyCount    = 0,
                                obj              = {},
                                duplicateRemoved = [];

                            for (var i = 0; i < numOptions; i++) {
                                var v = $options.eq(i).val();
                                if (v !== '') {
                                    obj[v] = 0;
                                    notEmptyCount++;
                                }
                            }

                            for (i in obj) {
                                duplicateRemoved.push(obj[i]);
                            }

                            if (duplicateRemoved.length === 0) {
                                return {
                                    valid: false,
                                    message: 'You must fill at least one pochi member ID'
                                };
                            } else if (duplicateRemoved.length !== notEmptyCount) {
                                return {
                                    valid: false,
                                    message: 'The pochi member ID must be unique'
                                };
                            }

                            validator.updateStatus('option[]', validator.STATUS_VALID, 'callback');
                            return true;
                        }
                    }
                }
            }
        }
    })

    // Add button click handler
    .on('click', '.addButton', function() {
        var $template = $('#optionTemplate'),
            $clone    = $template
                            .clone()
                            .removeClass('hide')
                            .removeAttr('id')
                            .insertBefore($template),
            $option   = $clone.find('[name="option[]"]');

        // Add new field
        form.formValidation('addField', $option);
    })

    // Remove button click handler
    .on('click', '.removeButton', function() {
        var $row    = $(this).parents('.form-group'),
            $option = $row.find('[name="option[]"]');

        // Remove element containing the option
        $row.remove();

        // Remove field
        form.formValidation('removeField', $option);
    })

    // Called after adding new field
    .on('added.field.fv', function(e, data) {
        // data.field   --> The field name
        // data.element --> The new field element
        // data.options --> The new field options

        if (data.field === 'option[]') {
            if (form.find(':visible[name="option[]"]').length >= MAX_OPTIONS) {
                form.find('.addButton').attr('disabled', 'disabled');
            }
            if (form.find(':visible[name="option[]"]').length >= 2) {
                form.find('#done').show();
            }
        }
    })

    // Called after removing the field
    .on('removed.field.fv', function(e, data) {
       if (data.field === 'option[]') {
            if (form.find(':visible[name="option[]"]').length < MAX_OPTIONS) {
                form.find('.addButton').removeAttr('disabled');
            }
            if (form.find(':visible[name="option[]"]').length < 2) {
                form.find('#done').hide();
            }
        }
    });

    $('#done').click(function () {
        var inputs  = $("[name='option[]']"),
            admin   = $('#admin'),
            uniqueItems = [],
            options = [];

        if (admin.find('option').length !== inputs.length){
            for(var i = 0; i < inputs.length; i++){
                if ($(inputs[i]).val() !== ''){
                    options.push($(inputs[i]).val());
                    uniqueItems = Array.from(new Set(options));
                }
            }
            uniqueItems.forEach(function (opt) {
                admin.append($('<option>', {
                    value: opt,
                    text: opt
                }));
            });
        }

        $("#members").val(JSON.stringify(uniqueItems));

        $('#second-admin').show();
    });

    var member_input = $('#member');

    if(member_input.val()) $('.addButton').show(); else $('.addButton').hide();

    member_input.on('change', function () {
        console.log(member_input.val());
        if(member_input.val()) $('.addButton').show(); else $('.addButton').hide();
    })

});