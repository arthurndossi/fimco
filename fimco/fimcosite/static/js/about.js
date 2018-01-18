$( document ).ready(function() {
    // $('.more-content').addClass('hide');
    // $('.read-more-show').removeClass('hide');

    // Set up the toggle effect:
    $('.read-more-show').on('click', function(e) {
      $('.more-content').removeClass('hide');
      $(this).addClass('hide');
      e.preventDefault();
    });
    window.addEventListener("hashchange", function () {
        window.scrollTo(window.scrollX, window.scrollY - 90);
    });

    jQuery("#topMain.nav-main").find("li ul li a").bind("click", function() {
        location.href = $(this).attr("href");

		jQuery("button.btn-mobile").toggleClass('btn-mobile-active');
		jQuery('html').removeClass('noscroll');
		jQuery('#menu-overlay').remove();
		jQuery("#topNav").find("div.nav-main-collapse").hide(0);
	});
});