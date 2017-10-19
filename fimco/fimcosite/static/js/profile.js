/**
 * Created by Arthur on 9/26/2017.
 */
var plugin_path = "/static/pochi/plugins/";

$('.radio, #mm, #ba').hide();

$('#add_account').click(function () {
    $('.radio').show();
});

$('input[name=radio-btn]').on('change', function() {
    if ($('input[name=radio-btn]:checked').val() === 'm_money'){
        $('#mm').show();
        $('#ba').hide();
    }
    else if ($('input[name=radio-btn]:checked').val() === 'bank_acc'){
        $('#ba').show();
        $('#mm').hide();
    }
});