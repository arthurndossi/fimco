/**
 * Created by Arthur on 2/2/2018.
 */
$(document).ready(function() {
    $('#addNew').on('click', function (e) {
        e.preventDefault();
        var form = $('#corporate').find('form');
        $.post( form.attr('action'), form.serialize() );
    })
});