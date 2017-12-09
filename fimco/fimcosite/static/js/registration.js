var id = $('#id_client_id'), choice = $("#id_id_choice");

$('#next, #prev').click(function (e) {
    e.preventDefault();
   $('#one, #two, #next, #prev').toggle()
});

$(":checkbox").change(function() {
    if(this.checked) {
        $("#finish").show()
    }else{
        $("#finish").hide()
    }
});

choice.on('change', function() {
    var id_choice = choice.find(":selected").val();
    if (id_choice === 'national'){
        // id.attr('pattern', '^[A-Z0-9]{8}(-)([A-Z0-9]{5}(-)){2}[A-Z0-9]{2}$');
        id.attr('data-format', '********-*****-*****-**')
    }else if (id_choice === 'voting'){
        // id.attr('pattern', '^(T-)([a-zA-Z0-9]{4}(-)){2}([a-zA-Z0-9]){3}(-)[a-zA-Z0-9]$');
        id.attr('data-format', 'T-9999-9999-999-9')
    }else if (id_choice === 'passport'){
        // id.attr('pattern', '^[A-Z]{2}[0-9]{6}$');
        id.attr('data-format', 'aa999999')
    }else if (id_choice === 'driving'){
        // id.attr('pattern', '^\\d{10}$');
        id.attr('data-format', '9999999999')
    }
});

// Prepare the preview for profile picture
$("#picture, #file").change(function(){
    if (this.id === 'picture') {
        readURL(this, 'wizardPicturePreview');
    }
    else if (this.id === 'file') {
        readURL(this, 'wizardFilePreview');
    }
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

var uploadField = $("#file");

uploadField.onchange = function() {
    if(this.files[0].size > 5242880){
       alert("File is too big!");
       this.value = "";
    }
};

var password = $("#id_password"),
		msg = $("#pass-message"),
    confirm_password = $("#id_verify");

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