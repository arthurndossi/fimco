/**
 * Created by Arthur on 9/6/2017.
 */

// jQuery(".rates a").click(function(){
//     var id = jQuery(this).attr("data-name");
//     if(id === "interests"){
//         jQuery(".content").load("interests #all");
//     }else{
//         jQuery(".content").load("interests #"+id+"Table");
//     }
// });
//
//
// jQuery('tr[data-href]').on("click", function() {
//     document.location = jQuery(this).data('href');
// });

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
                // window.location.href = response.url;
                _toastr(response.msg,"top-center","success",false);
            }else{
                // window.location.href = response.url;
                _toastr("Oops! something went wrong... try again!","top-center","error",false);
            }
            console.log(response);
        },
        error: function(xhr,errMsg,err) {
            console.log(errMsg+": "+err);
        }
    });
});