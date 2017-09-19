$(document).ready(function(){
  _topNav();
});

if($("#topBar").length > 0) {
  $("#topNav ul").addClass('has-topBar');
}
/** 01. Top Nav
 **************************************************************** **/
  function _topNav() {
    window.scrollTop    = 0;
    window._cmScroll    = 0;
    var _header_el      = $("#header");

    $(window).scroll(function() {
      _toTop();
    });

    /* Scroll To Top */
    function _toTop() {
      _scrollTop = $(document).scrollTop();
      if(_scrollTop > 100) {
        if($("#toTop").is(":hidden")) {
          $("#toTop").show();
        }
      } else {
        if($("#toTop").is(":visible")) {
          $("#toTop").hide();
        }
      }
    }


    // Mobile Submenu
    var addActiveClass  = false;
    $("#topMain a.dropdown-toggle").bind("click", function(e) {
      
      if($(this).attr('href') == "#") {
        e.preventDefault();
      }

      addActiveClass = $(this).parent().hasClass("resp-active");
      $("#topMain").find(".resp-active").removeClass("resp-active");
      if(!addActiveClass) {
        $(this).parents("li").addClass("resp-active");
      }
      return;
    });


    // Search
    $('li.search i.fa').click(function () {
      if($('#header .search-box').is(":visible")) {
        $('#header .search-box').fadeOut(300);
      } else {
        $('.search-box').fadeIn(300);
        $('#header .search-box form input').focus();
      }
    }); 

    // close search box on body click
    if($('#header li.search i.fa').length != 0) {
      $('#header .search-box, #header li.search i.fa').on('click', function(e){
        e.stopPropagation();
      });

      $('body').on('click', function() {
        if($('#header li.search .search-box').is(":visible")) {
          $('#header .search-box').fadeOut(300);
        }
      });
    }

    $(document).bind("click", function() {
      if($('#header li.search .search-box').is(":visible")) {
        $('#header .search-box').fadeOut(300);
      }
    });

    // Close Fullscreen Search
    $("#closeSearch").bind("click", function(e) {
      e.preventDefault();

      $('#header .search-box').fadeOut(300);
    });


    // MOBILE TOGGLE BUTTON
    window.currentScroll = 0;
    $("button.btn-mobile").bind("click", function(e) {
      e.preventDefault();
      $(this).toggleClass('btn-mobile-active');
      $('#menu-overlay').remove();
      $("#topNav div.nav-main-collapse").hide(0);

      if($(this).hasClass('btn-mobile-active')) {
        $("#topNav div.nav-main-collapse").show(0);
        $('body').append('<div id="menu-overlay"></div>');
        window.currentScroll = $(window).scrollTop();
      } else {
        $('html,body').animate({scrollTop: currentScroll}, 300, 'easeInOutExpo');
      }
    });

    // STICKY
    if(_header_el.hasClass('sticky')) {
      _topBar_H   = $("#topBar").outerHeight() || 0;

      // Force fixed header on mobile to avoid "jump" effect.
      if(window.width <= 992 && _topBar_H < 1) {
        var _scrollTop  = $(document).scrollTop();
        _header_H   = _header_el.outerHeight() || 0;
        _header_el.addClass('fixed');
        $('body').css({"padding-top":_header_H+"px"});
      }

      $(window).scroll(function() {
        if((window.width > 992 && _topBar_H < 1) || _topBar_H > 0) { // 992 to disable on mobile
          var _scrollTop  = $(document).scrollTop();
          if(_scrollTop > _topBar_H) {
            _header_el.addClass('fixed');
            _header_H = _header_el.outerHeight() || 0;
            if(!_header_el.hasClass('transparent') && !_header_el.hasClass('translucent')) {
              $('body').css({"padding-top":_header_H+"px"});
            }
          } else {
            if(!_header_el.hasClass('transparent') && !_header_el.hasClass('translucent')) {
              $('body').css({"padding-top":"0px"});
            }
            _header_el.removeClass('fixed');
          }
        }
      });
    } else
    // STATIC + TRANSPARENT
    if(_header_el.hasClass('static') && _header_el.hasClass('transparent')) {
      _topBar_H   = $("#topBar").outerHeight() || 0;
      // Force fixed header on mobile to avoid "jump" effect.
      if(window.width <= 992 && _topBar_H < 1) {
        var _scrollTop  = $(document).scrollTop();
          _header_H   = _header_el.outerHeight() || 0;
          _header_el.addClass('fixed');
      }
      $(window).scroll(function() {
        if((window.width > 992 && _topBar_H < 1) || _topBar_H > 0) { // 992 to disable on mobile
          var _scrollTop  = $(document).scrollTop();
          if(_scrollTop > _topBar_H) {
            _header_el.addClass('fixed');
            _header_H = _header_el.outerHeight() || 0;
          } else {
            _header_el.removeClass('fixed');
          }
        }
      });
    }
  }