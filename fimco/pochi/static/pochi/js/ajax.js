/**
 * Created by Arthur on 9/6/2017.
 */

var form = jQuery('form.payment');

form.submit(function(event) {
    event.preventDefault();
    jQuery.ajax({
        data: form.serialize(),
        type: form.attr('method'),
        url: form.attr('action'),
        dataType: "json",
        success: function(response) {
            if(response.status === 'success'){
                _toastr(response.msg,"top-center","success",false);
            }else{
                _toastr("Oops! something went wrong... Try again!","top-center","error",false);
            }
            console.log(response);
        },
        error: function(xhr,errMsg,err) {
            console.log(errMsg+": "+err);
        }
    });
});