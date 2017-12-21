/**
 * Created by Arthur on 12/15/2017.
 */
$(document).ready(function () {
    var co = $('#co'),
        step = $('.process-steps .nav-link'),
        id = $('#id_id_type'),
        choice = $("#id_id_number"),
        uploadField = $("#license, #certificate, #id_user_id, #ad-id_user_id");

    // co.hide();

    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {

        var $target = $(e.target);

        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    // if(step.first().hasClass('active')){
    //     $('#prev').hide();
    //     co.parent().addClass('text-right')
    // }

    // $(".next-step").click(function (e) {
    //     e.preventDefault();
    //     var $active = $('#company').find('.nav li a.active');
    //     $active.parent().next().removeClass('disabled');
    //     nextTab($active);
    //
    //     co.parent().removeClass('text-right');
    //     co.parent().addClass('justify');
    //     if(step.last().hasClass('active')){
    //         $('#next').hide();
    //         co.show();
    //     }else{
    //         $('#next').show();
    //         $('#prev').show();
    //         co.hide();
    //     }
    // });

    // $(".prev-step").click(function (e) {
    //     e.preventDefault();
    //     var $active = $('#company').find('.nav li a.active');
    //     prevTab($active);
    //
    //     co.hide();
    //     if(step.first().hasClass('active')){
    //         $('#prev').hide();
    //         co.parent().removeClass('justify');
    //         co.parent().addClass('text-right')
    //     }else{
    //         $('#next').show();
    //         $('#prev').show();
    //     }
    // });

    $("#id_password, #id_verify, #ad-id_password, #ad-id_verify").keyup(validatePassword);

    uploadField.onchange = function() {
        if(this.files[0].size > 5242880){
           alert("File is too big!");
           this.value = "";
        }
    };

    choice.on('change', function() {
        var id_choice = id.find(":selected").val();
        if (id_choice === 'national'){
            choice.attr('pattern', '^[A-Z\d]{8}(-)([A-Z\d]{5}(-)){2}[A-Z\d]{2}$');
        }else if (id_choice === 'voting'){
            choice.attr('pattern', '^(T-)([a-zA-Z\d]{4}(-)){2}([a-zA-Z\d]){3}(-)[a-zA-Z\d]$');
        }else if (id_choice === 'passport'){
            choice.attr('pattern', '^[A-Z]{2}[\\d]{6}$');
        }else if (id_choice === 'driving'){
            choice.attr('pattern', '^\d{10}$');
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
    var password = $("#id_password, #ad-id_password"),
        confirm_password = $("#id_verify, #ad-id_verify"),
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
