/**
 * Created by Arthur on 10/30/2017.
 */
var groupModal = $('#groupModal');
var error = $('#error_div');
groupModal.submit(function(event) {
    event.preventDefault();
    var form = $('#login-form');
    $.ajax({
        data: form.serialize(),
        type: form.attr('method'),
        url: form.attr('action'),
        dataType: "json",
        success: function(response) {
            if(response.status === 'success'){
                //redirect
                window.location.href = response.url;
            }else{
                error.show();
                error.html("Wrong username or password!");
            }
            console.log(response);
        },
        error: function(xhr,errMsg,err) {
            console.log(errMsg+": "+err);
        }
    });
});

$( "#main" ).load( "", function() {
  $("#heading").html("");
});

$('.list-group-item a').click(function () {
  var id = $(this).attr('href');
  switch(id) {
    case 'mmSaveForm':
      // code
      break;
    case 'mmSaveAs':
      // code
      break;
    case 'mmSaveExit':
      // code
      break;
  }
});

function show_dropdown(id_name) {
    document.getElementById(id_name).classList.toggle("show");
}