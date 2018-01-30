/**
 * Created by Arthur on 12/15/2017.
 */
$(document).ready(function () {
    var choice = $('#id_3-id_type, #id_id_type'),
        hint = $("#hint"),
        id = $("#id_3-id_number, #id_id_number"),
        uploadField = $("#license, #certificate, #id_3-user_id, #id_user_id");

    // co.hide();

    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {

        var $target = $(e.target);

        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    $("#id_2-password, #id_2-verify, #id_password, #id_verify").keyup(validatePassword);

    uploadField.onchange = function() {
        if(this.files[0].size > 5242880){
           alert("File is too big!");
           this.value = "";
        }
    };

    choice.on('change', function() {
        var id_choice = choice.find(":selected").val();
        if (id_choice === 'national'){
            id.attr('pattern', '^[A-Z\d]{8}(-)([A-Z\d]{5}(-)){2}[A-Z\d]{2}$');
            hint.html("Format should be (XXXXXXXX-XXXXX-XXXXX-XX)")
        }else if (id_choice === 'voting'){
            id.attr('pattern', '^(T-)([a-zA-Z\d]{4}(-)){2}([a-zA-Z\d]){3}(-)[a-zA-Z\d]$');
            hint.html("Format should be (T-XXXX-XXXX-XXX-X)")
        }else if (id_choice === 'passport'){
            id.attr('pattern', '^[A-Z]{2}[\\d]{6}$');
            hint.html("Format should be (ABXXXXXX)")
        }else if (id_choice === 'driving'){
            id.attr('pattern', '^\d{10}$');
            hint.html("Format should be (XXXXXXXXXX)")
        }
    });
});

// function nextTab(elem) {
//     $(elem).parent().next().find('a[data-toggle="tab"]').click();
// }
//
// function prevTab(elem) {
//     $(elem).parent().prev().find('a[data-toggle="tab"]').click();
// }

function validatePassword(){
    var password = $("#id_2-password, #id_password"),
        confirm_password = $("#id_2-verify, #id_verify"),
        msg = $("#passMessage");
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
