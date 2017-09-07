/**
 * Created by Arthur on 9/6/2017.
 */
var currencyModal = '';

$(".currencyModal").on( "shown.bs.modal", function() {
    currencyModal = $('#'+$(this).attr("id"));
    var str = $(this).attr("id");
    currencyModal.submit(function(e) {
        e.preventDefault();
        var curr = str.split("viewModal");
        $('#'+curr+'Exchange').load('/pochi/'+curr)
    });
});