/**
 * Created by Arthur on 12/15/2017.
 */
$(document).ready(function () {
    //Wizard
    var co = $('#co');
    var step = $('.process-steps .nav-link');
    co.hide();

    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {

        var $target = $(e.target);

        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    if(step.first().hasClass('active')){
        $('#prev').hide();
        co.parent().addClass('text-right')
    }

    $(".next-step").click(function (e) {
        e.preventDefault();
        var $active = $('#company').find('.nav li a.active');
        $active.parent().next().removeClass('disabled');
        nextTab($active);

        co.parent().removeClass('text-right');
        co.parent().addClass('justify');
        if(step.last().hasClass('active')){
            $('#next').hide();
            co.show();
        }else{
            $('#next').show();
            $('#prev').show();
            co.hide();
        }
    });
    $(".prev-step").click(function (e) {
        e.preventDefault();
        var $active = $('#company').find('.nav li a.active');
        prevTab($active);

        co.hide();
        if(step.first().hasClass('active')){
            $('#prev').hide();
            co.parent().removeClass('justify');
            co.parent().addClass('text-right')
        }else{
            $('#next').show();
            $('#prev').show();
        }
    });
});

function nextTab(elem) {
    $(elem).parent().next().find('a[data-toggle="tab"]').click();
}
function prevTab(elem) {
    $(elem).parent().prev().find('a[data-toggle="tab"]').click();
}

var uploadField = $("#license, #certificate, #userID");

uploadField.onchange = function() {
    if(this.files[0].size > 5242880){
       alert("File is too big!");
       this.value = "";
    }
};

var password = $("#repPass"),
		msg = $("#passMessage"),
    confirm_password = $("#repVerify");

function validatePassword(){
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
$("#id_password, #id_verify").keyup(validatePassword);

var id = $('#id_id_type'), choice = $("#id_id_number");

choice.on('change', function() {
    var id_choice = choice.find(":selected").val();
    if (id_choice === 'national'){
        id.attr('pattern', '^[A-Z0-9]{8}(-)([A-Z0-9]{5}(-)){2}[A-Z0-9]{2}$');
    }else if (id_choice === 'voting'){
        id.attr('pattern', '^(T-)([a-zA-Z0-9]{4}(-)){2}([a-zA-Z0-9]){3}(-)[a-zA-Z0-9]$');
    }else if (id_choice === 'passport'){
        id.attr('pattern', '^[A-Z]{2}[0-9]{6}$');
        id.attr('data-format', 'aa999999')
    }else if (id_choice === 'driving'){
        id.attr('pattern', '^\\d{10}$');
    }
});