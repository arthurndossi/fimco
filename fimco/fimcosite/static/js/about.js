$( document ).ready(function() {
    $('.more-content').addClass('hide');
    $('.read-more-show').removeClass('hide');

    // Set up the toggle effect:
    $('.read-more-show').on('click', function(e) {
      $('.more-content').removeClass('hide');
      $(this).addClass('hide');
      e.preventDefault();
    });
    window.addEventListener("hashchange", function () {
        window.scrollTo(window.scrollX, window.scrollY - 90);
    });
});