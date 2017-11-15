/**
 * Created by Arthur on 11/11/2017.
 */

$('input[name="range"]').daterangepicker();

$('#sample_2').DataTable( {
    dom: 'B<"clear">lfrtip',
    buttons: [ 'copy', 'csv', 'excel' ]
} );