/**
 * Created by Arthur on 9/29/2017.
 */
$(document).ready(function() {
    // The maximum number of options
    var MAX_OPTIONS = 100,
        inputIndex = 1,
        form = jQuery('.form-horizontal, .add-member');

    FormValidation.Validator.validMSISDN = {
        validate: function (validator, $field, options) {
            var value = $field.val();
            if (value.length > 1){
                var name = validate_phone_no(value);
                if (name === null){
                    return {
                        valid: false,
                        message: 'Please provide a phone number that is registered in POCHI'
                    }
                }else if ($.inArray(name, existingMembers) !== -1){
                    return {
                        valid: false,
                        message: 'This member is already in the group, please enter a new member!'
                    }
                }
                else{
                    return {
                        valid: true,
                        fullName: name
                    };
                }
            }else {
                return false
            }
        }
    };

    form.formValidation({
        framework: 'bootstrap',
        icon: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            'option[]': {
                enabled: false,
                validators: {
                    // notEmpty: {
                    //     message: 'Add POCHI member ID, cannot be empty'
                    // },
                    validMSISDN: {
                        message: 'Please enter a valid POCHI phone number!'
                    },
                    stringLength: {
                        max: 12,
                        message: 'The option must be less than 12 characters long'
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

                            // if (duplicateRemoved.length === 0) {
                            //     return {
                            //         valid: false,
                            //         message: 'You must fill at least one pochi member ID'
                            //     };
                            // } else if (duplicateRemoved.length !== notEmptyCount) {
                            //     return {
                            //         valid: false,
                            //         message: 'This Mobile Number is already selected, please enter another number!'
                            //     };
                            // }

                            if (duplicateRemoved.length !== notEmptyCount) {
                                return {
                                    valid: false,
                                    message: 'This Mobile Number is already selected, please enter another number!'
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

    .on('keyup', '[name="option[]"]', function() {
        var value = $(this).val();
        form.formValidation('enableFieldValidators', 'option[]', value.length >= 9)
    })

    .on('click', '#done', function() {
        $(this).attr("disabled", true);

        var inputs  = $("[name='option[]']"),
            uniqueItems = [],
            options = [];

        for(var i = 0; i < inputs.length; i++){
            if ($(inputs[i]).val() !== ''){
                options.push($(inputs[i]).val());
                uniqueItems = Array.from(new Set(options));
            }
        }

        var members = $("#members");
        members.val(JSON.stringify(uniqueItems));
        members.after("<button type='submit' class='btn btn-primary'>Submit</button>");
    })

    .on('click', '#add-button', function(e) {
        e.preventDefault();
        var inputs  = $("[name='option[]']"),
            uniqueItems = [],
            options = [];

        for(var i = 0; i < inputs.length; i++){
            if ($(inputs[i]).val() !== ''){
                options.push($(inputs[i]).val());
                uniqueItems = Array.from(new Set(options));
            }
        }

        var members = JSON.stringify(uniqueItems);
        addMoreMembers(members)
    })

    // Add button click handler
    .on('click', '.addButton', function() {
        inputIndex++;
        var $template = $('#optionTemplate'),
            $clone    = $template
                            .clone()
                            .removeClass('hide')
                            .removeAttr('id')
                            .insertBefore($template),
            $option   = $clone.find('[name="option[]"]').attr('autocomplete', 'off');

        $('#add-button').addClass('hide');
        $clone.find('.control-label').html('Member '+inputIndex);
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

    .on('err.field.fv', function(e, data) {
        // data.field   --> The field name
        // data.element --> The new field element
        // data.options --> The new field options

        var $row    = data.element.parents('.form-group'),
            $informer = $row.find('.hint');

        $informer.addClass('hide').html("")
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
                form.find('#done').removeClass("hide");
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
                form.find('#done').addClass("hide");
            }
        }
    })

    // This event is triggered when the field passes any validator
    .on('success.validator.fv', function(e, data) {

        var $row    = data.element.parents('.form-group'),
            $informer = $row.find('.hint');

        if (data.validator === 'validMSISDN') {
            $informer.removeClass('hide').html(data.result.fullName);
            $row.find('.extras').removeClass('hide');
            $('#add-button').removeClass('hide');
        }
    })

    .on('status.field.fv', function(e, data) {
        // data.field is the field name
        // data.status is the current status of validator
        // data.element is the field element

        var $row    = $(this).parents('.form-group'),
            $loader = $row.find('.loader');
        $loader.removeClass('hide');

        (data.status === 'VALIDATING') ? $loader.removeClass('hide') : $loader.addClass('hide');
    });
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function validate_phone_no(value) {
    var name = null;
    $.ajax({
        async: false,
        url : "/pochi/check/user",
        type : "POST",
        data : { username : value, csrftoken: $("[name=csrfmiddlewaretoken]").val() },
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        // handle a successful response
        success : function(response) {
            name = response.result
        },
        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + err + ": " + xhr.responseText);
        }
    });
    return name
}

// group settings

function addMoreMembers(values) {
    var form = $('#add').find('form');
    $.ajax({
        data: {'members': values, csrftoken: $("[name=csrfmiddlewaretoken]").val() },
        type: form.attr('method'),
        url: form.attr('action'),
        dataType: "json",
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        error: function(xhr,errMsg,err) {
            _toastr("Something went wrong... Please try again!","top-center","error",false);
            console.log(errMsg+": "+err);
        }
    });
}

if($(":checkbox:checked").length > 2){
    $('#remove').attr('disabled', true)
}else{
    $('#remove').attr('disabled', false)
}