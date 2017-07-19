/**
 * Created by Arthur on 6/15/2017.
 */
"use strict";

var can = $("#canvas")[0];
var scaleImage = function scaleImage(aspect, img) {
  var ctx = can.getContext("2d");
  var height = parseInt(can.width / aspect);
  can.height = height;
  ctx.drawImage(img, 0, 0, can.width, height);
};

var saveImage = function saveImage() {
  document.location = can.toDataURL();
};

var readImage = function readImage(file) {
  var fileReader = new FileReader();
  fileReader.addEventListener("load", function () {
    var img = new Image();
    img.onload = function () {
      var aspect = img.width / img.height;
      scaleImage(aspect, img);
    };
    img.src = fileReader.result;
  });
  fileReader.readAsDataURL(file);
};

var fileChangeHandler = function fileChangeHandler($e) {
  var files = $e.target.files;
  var file = files[0];
  // var type = file.type;
  $e.target.value = "";
  readImage(file);
};
$(".upload-file-btn input").change(fileChangeHandler);
$('.save-btn').click(saveImage);

var input = $('[type=tel]');
input.mobilePhoneNumber({allowPhoneWithoutPrefix: '+255'});
input.bind('country.mobilePhoneNumber', function(e, country) {
  $('.country').text(country || '')
});

$("select #rf-id-type")
  .change(function () {
    var str = '';
    $( "select option:selected" ).each(function() {
      str = $( this ).text();
      $( "select #rf-id" ).attr('pattern', setPattern(str));
    });
  })
  .change();

function setPattern(choice){
  if(choice==='Driver\'s licence'){
    return '/^[a-zA-Z0-9]{10}$/'
  }else if(choice==='Passport') {
    return '/^[A-Z]{2}[0-9]{6}$/'
  }else if(choice==='Voter\'s ID'){
    return '/^(T-)([a-zA-Z0-9]{4}(-)){2}([a-zA-Z0-9]){3}(-)[a-zA-Z0-9]$/'
  }else if(choice==='National ID'){
    return '/^[A-Z0-9]{8}(-)([A-Z0-9]{5}(-)){2}[A-Z0-9]{2}$/'
  }
}