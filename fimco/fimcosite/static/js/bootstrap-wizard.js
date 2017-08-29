$(document).ready(function () {
    //Initialize tooltips
    // $('.nav-tabs > li a[title]').tooltip();
    
    //Wizard
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {

        var $target = $(e.target);
    
        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    $(".next-step").click(function (e) {
        var $valid = $('#wizard').valid();
        if(!$valid) {
            $validator.focusInvalid();
            return false;
        }
        else{
            var $active = $('.bootstrapWizard li.active');
            $active.next().removeClass('disabled');
            nextTab($active);
        }
        
    });
    $(".prev-step").click(function (e) {

        var $active = $('.bootstrapWizard li.active');
        prevTab($active);

    });

    // Prepare the preview for profile picture
    $("#picture, #file").change(function(){
        if (this.id == 'picture') {
            readURL(this, 'wizardPicturePreview');
        }
        else if (this.id == 'file') {
            readURL(this, 'wizardFilePreview');
        }
    });

    $('[data-toggle="wizard-radio"]').click(function(){
        wizard = $(this).closest('.wizard-card');
        wizard.find('[data-toggle="wizard-radio"]').removeClass('active');
        $(this).addClass('active');
        $(wizard).find('[type="radio"]').removeAttr('checked');
        $(this).find('[type="radio"]').attr('checked','true');
    });

    $('[data-toggle="wizard-checkbox"]').click(function(){
        if( $(this).hasClass('active')){
            $(this).removeClass('active');
            $(this).find('[type="checkbox"]').removeAttr('checked');
        } else {
            $(this).addClass('active');
            $(this).find('[type="checkbox"]').attr('checked','true');
        }
    });

    // Code for the Validator
    var $validator = $('#wizard').validate({
          rules: {
            firstname: {
              required: true,
              minlength: 3
            },
            lastname: {
              required: true,
              minlength: 3
            },
            dob: {
              required: true
            },
            gender: {
              required: true
            },
            mobile: {
              required: true
            },
            pass: {
              required: true
            },
            repass: {
              required: true
            },
            idtype: {
              required: true
            },
            identity: {
              required: true
            },
            picture: {
              required: true
            },
            file: {
              required: true
            }
        },
    });
});

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}

function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}

//Function to show image before upload
function readURL(input, id) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#'+id).attr('src', e.target.result).fadeIn('slow');
        }
        reader.readAsDataURL(input.files[0]);
    }
}