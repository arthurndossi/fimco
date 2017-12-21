$(document).ready(function () {
    var id = $('#id_client_id'), choice = $("#id_id_choice"),
        uploadField = $("#file"), checkbox = $('#checker'),
        empty = false, form_element = $('#one').find('.required');

    id.attr('pattern', '^[A-Z\\d]{8}(-)([A-Z\\d]{5}(-)){2}[A-Z\\d]{2}$');

    choice.on('change', function() {
        var id_choice = choice.find(":selected").val();
        if (id_choice === 'national'){
            id.attr('pattern', '^[A-Z\\d]{8}(-)([A-Z\\d]{5}(-)){2}[A-Z\\d]{2}$');
        }else if (id_choice === 'voting'){
            id.attr('pattern', '^(T-)([a-zA-Z\\d]{4}(-)){2}([a-zA-Z\\d]){3}(-)[a-zA-Z\\d]$');
        }else if (id_choice === 'passport'){
            id.attr('pattern', '^[A-Z]{2}[\\d]{6}$');
        }else if (id_choice === 'driving'){
            id.attr('pattern', '^\\d{10}$');
        }
    });

    form_element.each(function() {
        if ($(this).val() === '') {
            empty = true;
        }
    });
    if (empty) {
        $('#next').attr('disabled', 'disabled');
    } else {
        $('#next').removeAttr('disabled');
    }

    form_element.keyup(function() {
        var empty = false, alert = $(".alert");
        form_element.each(function() {
            if ($(this).val() === '') {
                empty = true;
            }
            if (alert.length > 0){
                alert.hide();
            }
        });

        if (empty) {
            $('#next').attr('disabled', 'disabled');
        } else {
            $('#next').removeAttr('disabled');
        }
    });

    if (checkbox.is(':checked')){
        if (uploadField.val() !== '' && id.val() !== '') {
            $('#finish').removeAttr('disabled')
        } else {
            $('#finish').attr('disabled', 'disabled');
        }
    }

    checkbox.change(function(){
        if (uploadField.val() !== '' && id.val() !== '' && checkbox.is(':checked')) {
            $('#finish').removeAttr('disabled');
        } else {
            $('#finish').attr('disabled', 'disabled');
        }
    });

    $("#id_password, #id_verify").keyup(validatePassword);

    uploadField.change(function(){
        readURL(this, 'wizardFilePreview');
        if(this.files[0].size > 5242880){
           alert("File is too big!");
           this.value = "";
        }
        if (alert.length > 0){
            alert.hide();
        }
    });
});

//Function to show image before upload
function readURL(input, id) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#'+id).attr('src', e.target.result).fadeIn('slow');
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function validatePassword(){
    var password = $("#id_password"),
		msg = $("#pass-message"),
        confirm_password = $("#id_verify");
    if(password.val() !== '' && confirm_password.val() !== ''){
        if(password.val() !== confirm_password.val()) {
            if(msg.hasClass("alert-success")){
                msg.removeClass("alert-success");
            }
            msg.addClass("alert-danger").html("Passwords Don't Match").show();
        } else {
            if(msg.hasClass("alert-danger")){
                msg.removeClass("alert-danger");
            }
            msg.addClass("alert-success").html("Passwords Match").show();
        }
    }
}
