/**
 * Created by Arthur on 12/6/2017.
 */
$(document).ready(function() {
    $('input[name="interestrange"]').daterangepicker();

    $('#interest_table, #overnight_table, #bill_table #bond_table, #libor_table').DataTable( {
        dom: 'B<"clear">lfrtip',
        buttons: [ 'copy', 'csv', 'excel' ]
    } );

});