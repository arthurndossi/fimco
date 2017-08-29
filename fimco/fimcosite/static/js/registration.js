// var input = $('[type=tel]');
// input.mobilePhoneNumber({allowPhoneWithoutPrefix: '+255'});
// input.bind('country.mobilePhoneNumber', function(e, country) {
//   $('.country').text(country || '')
// });
$('#identity').hide();

$('input:radio[name="clientID"]')
  .change(function () {
      if($(this).is(':checked') && $(this).val() === 'driving'){
          $('#client').attr('pattern', '^\\d{10}$')
      }else if ($(this).is(':checked') && $(this).val() === 'passport'){
          $('#client').attr('pattern', '^[A-Z]{2}[0-9]{6}$')
      }else if ($(this).is(':checked') && $(this).val() === 'voting'){
          $('#client').attr('pattern', '^(T-)([a-zA-Z0-9]{4}(-)){2}([a-zA-Z0-9]){3}(-)[a-zA-Z0-9]$')
      }else if ($(this).is(':checked') && $(this).val() === 'national'){
          $('#client').attr('pattern', '^[A-Z0-9]{8}(-)([A-Z0-9]{5}(-)){2}[A-Z0-9]{2}$')
      }
      $('#identity').show();
  });
