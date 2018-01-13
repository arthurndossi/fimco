/**
 * Created by Arthur on 11/30/2017.
 */
$(document).ready(function() {
    $('input[name="exchangerange"]').daterangepicker();

    $('#exchange_table').DataTable( {
        dom: 'B<"clear">lfrtip',
        buttons: [ 'copy', 'csv', 'excel' ]
    } );

    // {% for exchange in data %}
    //     var currency = "{{ exchange.counter_currency }}";
    //     if (currency === 'GBP'){
    //         $("#counter_rate").val({{ exchange.current_rate }});
    //     }
    // {% endfor %}

    $( "#counter" ).change(function() {
        // var current_label = $.trim($("#counter").find("option:selected").text());
        // {% for exchange in data %}
        //     var currency = "{{ exchange.counter_currency }}";
        //     if (currency === current_label){
        //         $("#counter_rate").val({{ exchange.current_rate }})
        //     }
        // {% endfor %}
    });

    $( "#base_rate" ).on('input', function() {
        // var new_val = $( "#base_rate" ).val();
        // var current_label = $.trim($("#counter").find("option:selected").text());
        // {% for exchange in data %}
        //     var currency = "{{ exchange.counter_currency }}";
        //     if (currency === current_label){
        //         $("#counter_rate").val(new_val * {{ exchange.current_rate }});
        //     }
        // {% endfor %}
    });

    $('#exchange').click(function(e) {
        e.preventDefault();
    });

    // var base_currency, counter_currency;
    var baseInput = $('#base_input');
    var counterInput = $('#counter_input');
    $('#base_select, #counter_select').change(function(){
        // var selected_counter_option = $("#counter_select").find("option:selected").text();
        // var selected_base_option = $("#base_select").find("option:selected").text();
        // var default_rate = {{ exchange.current_rate }};
        var default_rate = '';
        var default_inverse_rate = 1/default_rate;
        var base_input = baseInput.val();
        var counter_input = counterInput.val();
        var conversion_value;

        if (base_input){
            conversion_value = base_input * default_rate;
            $('#counter_input').val(conversion_value)
        }
        else if (counter_input){
            conversion_value = counter_input * default_inverse_rate;
            $('#base_input').val(conversion_value)
        }
    })

    $('.HSselectBox').removeClass('HSselectBox').addClass('form-control form-control-sm');
    // $('.HStextarea').addClass('form-control');
});