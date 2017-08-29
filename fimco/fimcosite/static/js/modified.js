/** ********************************************** **
	@Author			Dorin Grigoras
	@Website		www.stepofweb.com
	@Last Update	Wednesday, March 8, 2017

	NOTE! 	Do not change anything here if you want to
			be able to update in the future! Please use
			your custom script (eg. custom.js).


	TABLE CONTENTS
	-------------------------------


	INLINE SCRIPTS
	-------------------------------
		COUNT TO
			https://github.com/mhuggins/jquery-countTo

		BROWSER DETECT

		Appear
			https://github.com/bas2k/jquery.appear/
			
		Parallax v1.1.3
			http://www.ianlunn.co.uk/plugins/jquery-parallax/

		jQuery Easing v1.3
			http://gsgd.co.uk/sandbox/jquery/easing/

		WOW - v1.0.3
			http://mynameismatthieu.com/WOW/

		Modernizr 3.3.1
			http://modernizr.com/download/#-csstransforms3d-csstransitions-video-touch-shiv-cssclasses-addtest-prefixed-teststyles-testprop-testallprops-hasevent-prefixes-domprefixes-load

		Tether 1.3.3 - required by bootstrap
		http://tether.io/
*************************************************** **/
	window.width 	= jQuery(window).width();
	window.height 	= jQuery(window).height();

	/* Init */
	jQuery(window).ready(function () {
		// jQuery 3.x do no support size() - should be replaceced with .legth
		// We use this hack to make old plugins working
		jQuery.fn.extend({
		  size: function() {
		    return this.length;
		  }
		});
		_loadTetherBS4();
		// Load Bootstrap JS
		loadScript('static/js/vendors/bootstrap.min.js', function() {
			// Init
			Init(false);
		});
	});


/** Init
	Ajax Reinit:		Init(true);
 **************************************************************** **/
	function Init(is_ajax) {

		// First Load Only
		if(is_ajax != true) {
		
			_afterResize();
			_slider_full();
			_topNav();
			_megaNavHorizontal();
			_stickyFooter();

		}

		// Reinit on Ajax

		_scrollTo(false, 0);
		_toggle();
		/** Bootstrap Tooltip **/ 
		jQuery("a[data-toggle=tooltip], button[data-toggle=tooltip], span[data-toggle=tooltip]").tooltip();
	}


/** After Resize
 **************************************************************** **/
	function _afterResize() {

		jQuery(window).on("load", function() {
			"use strict";

			// On Resize
			jQuery(window).resize(function() {

				if(window.afterResizeApp) {
					clearTimeout(window.afterResizeApp);
				}

				window.afterResizeApp = setTimeout(function() {

					/**
						After Resize Code
						.................
					**/

					_slider_full();

					window.width 	= jQuery(window).width();
					window.height 	= jQuery(window).height();

					// Resize Flex Slider if exists!
					if(jQuery('.flexslider').length > 0) {
						jQuery('.flexslider').resize();
					}
				}, 300);
			});
		});
	}



/** Load Script
 **************************************************************** **/
	var _arr 	= {};
	function loadScript(scriptName, callback) {

		if (!_arr[scriptName]) {
			_arr[scriptName] = true;

			var body 		= document.getElementsByTagName('body')[0];
			var script 		= document.createElement('script');
			script.type 	= 'text/javascript';
			script.src 		= scriptName;

			// then bind the event to the callback function
			// there are several events for cross browser compatibility
			// script.onreadystatechange = callback;
			script.onload = callback;

			// fire the loading
			body.appendChild(script);

		} else if (callback) {

			callback();
		}
	};


/** 00. Slider Full Height
 **************************************************************** **/
	function _slider_full() {
		_headerHeight = 0;

		if(jQuery("#header").hasClass('transparent') || jQuery("#header").hasClass('translucent')) {
			_headerHeight = 0;
		} else {
			_headerHeight = jQuery("#header").outerHeight() || 0;
			
			if(jQuery("#topBar").length > 0) {
				_topBarHeight = jQuery("#topBar").outerHeight() || 0;
				_headerHeight = _headerHeight + _topBarHeight;
			}
		}

		_screenHeight = jQuery(window).height() - _headerHeight;

		if(jQuery("#header").hasClass('static'))
			_screenHeight = jQuery(window).height();
	}


/** 01. Top Nav
 **************************************************************** **/
	function _topNav() {
		window.scrollTop 		= 0;
		window._cmScroll 		= 0;
		var _header_el 			= jQuery("#header");

		jQuery(window).scroll(function() {
			_toTop();
		});

		/* Scroll To Top */
		function _toTop() {
			_scrollTop = jQuery(document).scrollTop();
			
			if(_scrollTop > 100) {

				if(jQuery("#toTop").is(":hidden")) {
					jQuery("#toTop").show();
				}

			} else {

				if(jQuery("#toTop").is(":visible")) {
					jQuery("#toTop").hide();
				}
			}
		}


		// Mobile Submenu
		var addActiveClass 	= false;
		jQuery("#topMain a.dropdown-toggle").bind("click", function(e) {
			
			if(jQuery(this).attr('href') == "#") {
				e.preventDefault();
			}

			addActiveClass = jQuery(this).parent().hasClass("resp-active");
			jQuery("#topMain").find(".resp-active").removeClass("resp-active");

			if(!addActiveClass) {
				jQuery(this).parents("li").addClass("resp-active");
			}
			return;
		});


		// Srearch
		jQuery('li.search i.fa').click(function () {
			if(jQuery('#header .search-box').is(":visible")) {
				jQuery('#header .search-box').fadeOut(300);
			} else {
				jQuery('.search-box').fadeIn(300);
				jQuery('#header .search-box form input').focus();

				// hide quick cart if visible
				if (jQuery('#header li.quick-cart div.quick-cart-box').is(":visible")) {
					jQuery('#header li.quick-cart div.quick-cart-box').fadeOut(300);
				}
			}
		}); 

		// close search box on body click
		if(jQuery('#header li.search i.fa').size() != 0) {
			jQuery('#header .search-box, #header li.search i.fa').on('click', function(e){
				e.stopPropagation();
			});

			jQuery('body').on('click', function() {
				if(jQuery('#header li.search .search-box').is(":visible")) {
					jQuery('#header .search-box').fadeOut(300);
				}
			});
		}

		jQuery(document).bind("click", function() {
			if(jQuery('#header li.search .search-box').is(":visible")) {
				jQuery('#header .search-box').fadeOut(300);
			}
		});


		// Close Fullscreen Search
		jQuery("#closeSearch").bind("click", function(e) {
			e.preventDefault();

			jQuery('#header .search-box').fadeOut(300);
		});



		// Page Menu [mobile]
		jQuery("button#page-menu-mobile").bind("click", function() {
			jQuery(this).next('ul').slideToggle(150);
		});


		// Page Menu [scrollTo]
		jQuery("#page-menu ul.menu-scrollTo>li").bind("click", function(e) {

			// calculate padding-top for scroll offset
			var _href 	= jQuery('a', this).attr('href');
			
			if(!jQuery('a', this).hasClass('external')) {
				e.preventDefault();

				jQuery("#page-menu ul.menu-scrollTo>li").removeClass('active');
				jQuery(this).addClass('active');

				if(jQuery(_href).length > 0) {

					_padding_top = 0;

					if(jQuery("#header").hasClass('sticky')) {
						_padding_top = jQuery(_href).css('padding-top');
						_padding_top = _padding_top.replace('px', '');
					}

					jQuery('html,body').animate({scrollTop: jQuery(_href).offset().top - _padding_top}, 800, 'easeInOutExpo');
				}
			}
		});

		// MOBILE TOGGLE BUTTON
		window.currentScroll = 0;
		jQuery("button.btn-mobile").bind("click", function(e) {
			e.preventDefault();

			jQuery(this).toggleClass('btn-mobile-active');
			jQuery('html').removeClass('noscroll');
			jQuery('#menu-overlay').remove();
			jQuery("#topNav div.nav-main-collapse").hide(0);

			if(jQuery(this).hasClass('btn-mobile-active')) {
				jQuery("#topNav div.nav-main-collapse").show(0);
				jQuery('html').addClass('noscroll');
				jQuery('body').append('<div id="menu-overlay"></div>');
				 window.currentScroll = jQuery(window).scrollTop();
			} else {
				 jQuery('html,body').animate({scrollTop: currentScroll}, 300, 'easeInOutExpo');
			}
		});

		// STICKY
		if(_header_el.hasClass('sticky')) {

			_topBar_H 	= jQuery("#topBar").outerHeight() || 0;

			// Force fixed header on mobile to avoid "jump" effect.
			if(window.width <= 992 && _topBar_H < 1) {

				var _scrollTop 	= jQuery(document).scrollTop();
					_header_H 	= _header_el.outerHeight() || 0;

					_header_el.addClass('fixed');
					jQuery('body').css({"padding-top":_header_H+"px"});
			}

			jQuery(window).scroll(function() {

				if((window.width > 992 && _topBar_H < 1) || _topBar_H > 0) { // 992 to disable on mobile

					var _scrollTop 	= jQuery(document).scrollTop();

					if(_scrollTop > _topBar_H) {
						_header_el.addClass('fixed');

						_header_H = _header_el.outerHeight() || 0;

						if(!_header_el.hasClass('transparent') && !_header_el.hasClass('translucent')) {
							jQuery('body').css({"padding-top":_header_H+"px"});
						}

					} else {
						if(!_header_el.hasClass('transparent') && !_header_el.hasClass('translucent')) {
							jQuery('body').css({"padding-top":"0px"});
						}

						_header_el.removeClass('fixed');
					}

				}

				// SWITCH DROPDOWN MENU CLASS ON SCROLL
				if(_header_el.hasClass('transparent')) {

					var _el 					= jQuery("#topNav div.nav-main-collapse"),
						_data_switch_default 	= _el.attr('data-switch-default') 	|| '',
						_data_switch_scroll 	= _el.attr('data-switch-scroll') 	|| '';


					if(_data_switch_default != '' || _data_switch_scroll != '') {

						if(_scrollTop > 0) {

							if(window._cmScroll < 1) {

								_el.removeClass(_data_switch_default, _data_switch_scroll).addClass(_data_switch_scroll);

								// set to 1, we want to change classes once, not for each pixel on scroll
								window._cmScroll = 1;

							}

						} else
						if(_scrollTop < 1) {

							_el.removeClass(_data_switch_default, _data_switch_scroll).addClass(_data_switch_default);
							// Set back to 0
							window._cmScroll = 0;
						}
					}
				}
			});
		} else 
		// STATIC + TRANSPARENT
		if(_header_el.hasClass('static') && _header_el.hasClass('transparent')) {

			_topBar_H 	= jQuery("#topBar").outerHeight() || 0;

			// Force fixed header on mobile to avoid "jump" effect.
			if(window.width <= 992 && _topBar_H < 1) {

				var _scrollTop 	= jQuery(document).scrollTop();
					_header_H 	= _header_el.outerHeight() || 0;

					_header_el.addClass('fixed');

			}


			jQuery(window).scroll(function() {

				if((window.width > 992 && _topBar_H < 1) || _topBar_H > 0) { // 992 to disable on mobile

					var _scrollTop 	= jQuery(document).scrollTop();

					if(_scrollTop > _topBar_H) {
						_header_el.addClass('fixed');

						_header_H = _header_el.outerHeight() || 0;

					} else {


						_header_el.removeClass('fixed');
					}

				}

			});

		} else
		
		if(_header_el.hasClass('static')) {
			// _header_H = _header_el.outerHeight() + "px";
			// jQuery('body').css({"padding-top":_header_H});
		}

		/** OVERLAY MENU
		 *************************** **/
		if(jQuery("#menu_overlay_open").length > 0) {
			var is_ie9 = jQuery('html').hasClass('ie9') ? true : false;

			if(is_ie9 == true) {
				jQuery("#topMain").hide();
			}

			// open
			jQuery("#menu_overlay_open").bind("click", function(e) {
				e.preventDefault();
				
				jQuery('body').addClass('show-menu');

				if(is_ie9 == true) {
					jQuery("#topMain").show();
				}

			});

			// close
			jQuery("#menu_overlay_close").bind("click", function(e) {
				e.preventDefault();

				if(jQuery('body').hasClass('show-menu')) {
					jQuery('body').removeClass('show-menu');
				}

				if(is_ie9 == true) {
					jQuery("#topMain").hide();
				}

			});

			// 'esc' key
			jQuery(document).keyup(function(e) {
				if(e.keyCode == 27) {
					if(jQuery('body').hasClass('show-menu')) {
						jQuery('body').removeClass('show-menu');
					}

					if(is_ie9 == true) {
						jQuery("#topMain").hide();
					}
				}
			});

		}

		// quick cart & search for mobile - top calculate
		// Quick Cart & top Search Fix (if #topBar exists).
		if(jQuery("#topBar").length > 0) {
			jQuery("#topNav ul").addClass('has-topBar');
		}
		
		// Hide Cart & Search on Scroll
		jQuery(window).scroll(function() {
			if(window.width < 769) {
				// hide search if visible
				if(jQuery('#header li.search .search-box').is(":visible")) {
					jQuery('#header .search-box').fadeOut(0);
				}
			}
		});
	}


/** Mega Horizontal Navigation
 **************************************************************** **/
	function _megaNavHorizontal() {

		// WRAPPER MAIN MENU
		if(jQuery("#wrapper nav.main-nav").length > 0) {

			var _sliderWidth 	= jQuery("#slider").width(),
				_sliderHeight 	= jQuery("#wrapper nav.main-nav").height();

			// Submenu widh & height
			jQuery("#wrapper nav.main-nav>div>ul>li>.main-nav-submenu").css({"min-height":_sliderHeight+"px"});
			jQuery("#wrapper nav.main-nav>div>ul>li.main-nav-expanded>.main-nav-submenu").css({"width":_sliderWidth+"px"});

			// SUBMENUS
			jQuery("#wrapper nav.main-nav>div>ul>li").bind("click", function(e) {
				var _this = jQuery(this);

				if(!jQuery('div', _this).hasClass('main-nav-open')) {
					jQuery("#wrapper nav.main-nav>div>ul>li>.main-nav-submenu").removeClass('main-nav-open');
				}

				jQuery('div', _this).toggleClass('main-nav-open');
			});

		}

		// HEADER MAIN MENU
		var _hsliderWidth 	= jQuery("#header>.container").width() - 278,
			_hsliderHeight 	= jQuery("#header nav.main-nav").height();

		// Submenu widh & height
		jQuery("#header nav.main-nav>div>ul>li>.main-nav-submenu").css({"min-height":_hsliderHeight+"px"});
		jQuery("#header nav.main-nav>div>ul>li.main-nav-expanded>.main-nav-submenu").css({"width":_hsliderWidth+"px"});

		// SUBMENUS
		jQuery("#header nav.main-nav>div>ul>li").bind("click", function(e) {
			var _this = jQuery(this);

			if(!jQuery('div', _this).hasClass('main-nav-open')) {
				jQuery("#header nav.main-nav>div>ul>li>.main-nav-submenu").removeClass('main-nav-open');
			}

			jQuery('div', _this).toggleClass('main-nav-open');
		});

		// HEADER MAIN MENU
		if(window.width > 767) { //  desktop|tablet

			jQuery("#header button.nav-toggle").mouseover(function(e) {
				e.preventDefault();

				_initMainNav();

			});


		} else { // mobile

			jQuery("#header button.nav-toggle").bind("click", function(e) {
				e.preventDefault();

				_initMainNav();

			});

		}

        jQuery('body').on('click', '#header button.nav-toggle, #header nav.main-nav', function (e) {
            e.stopPropagation();
        });

        jQuery("#header button.nav-toggle, #header nav.main-nav").mouseover(function(e) {
        	e.stopPropagation();
        });


		jQuery(document).bind("click", function() {

			_hideMainNav();

		});

		function _initMainNav() {

			// remove overlay first, no matter what
			jQuery("#main-nav-overlay").remove();
		
			// open menu
			jQuery("#header nav.main-nav").addClass('min-nav-active');

			// add overlay
			jQuery('body').append('<div id="main-nav-overlay"></div>');

			// Mobile menu open|close on click
			jQuery('#header button.nav-toggle-close').bind("click", function() {
				jQuery("#header nav.main-nav").removeClass('min-nav-active');
			});

			// Close menu on hover
	        jQuery("#main-nav-overlay, #header").mouseover(function() {

	        	_hideMainNav();

	        });

		}

		function _hideMainNav() {
			jQuery("#main-nav-overlay").remove();
			jQuery("#header nav.main-nav").removeClass('min-nav-active');
		}


		// Menu Click
		jQuery("nav.main-nav>div>ul>li a").bind("click", function(e) {
			var _href = jQuery(this).attr('href');

			if(_href == '#') {
				e.preventDefault();
			}
		});
	}


/** 06. ScrollTo
 **************************************************************** **/
	function _scrollTo(to, offset) {

		if(to == false) {

			jQuery("a.scrollTo").bind("click", function(e) {
				e.preventDefault();

				var href 	= jQuery(this).attr('href'),
					_offset	= jQuery(this).attr('data-offset') || 0;

				if(href != '#' && href != '#top') {
					jQuery('html,body').animate({scrollTop: jQuery(href).offset().top - parseInt(_offset)}, 800, 'easeInOutExpo');
				}

				if(href == '#top') {
					jQuery('html,body').animate({scrollTop: 0}, 800, 'easeInOutExpo');
				}
			});

			jQuery("#toTop").bind("click", function(e) {
				e.preventDefault();
				jQuery('html,body').animate({scrollTop: 0}, 800, 'easeInOutExpo');
			});
		
		} else {

			// USAGE: _scrollTo("#footer", 150);
			jQuery('html,body').animate({scrollTop: jQuery(to).offset().top - offset}, 800, 'easeInOutExpo');

		}
	}


/** 09. Toggle
 **************************************************************** **/
	function _toggle() {

		var $_t = this,
			previewParClosedHeight = 25;

		jQuery("div.toggle.active > p").addClass("preview-active");
		jQuery("div.toggle.active > div.toggle-content").slideDown(400);
		jQuery("div.toggle > label").click(function(e) {

			var parentSection 	= jQuery(this).parent(),
				parentWrapper 	= jQuery(this).parents("div.toggle"),
				previewPar 		= false,
				isAccordion 	= parentWrapper.hasClass("toggle-accordion");

			if(isAccordion && typeof(e.originalEvent) != "undefined") {
				parentWrapper.find("div.toggle.active > label").trigger("click");
			}

			parentSection.toggleClass("active");

			if(parentSection.find("> p").get(0)) {

				previewPar 					= parentSection.find("> p");
				var previewParCurrentHeight = previewPar.css("height");
				var previewParAnimateHeight = previewPar.css("height");
				previewPar.css("height", "auto");
				previewPar.css("height", previewParCurrentHeight);

			}

			var toggleContent = parentSection.find("> div.toggle-content");

			if(parentSection.hasClass("active")) {

				jQuery(previewPar).animate({height: previewParAnimateHeight}, 350, function() {jQuery(this).addClass("preview-active");});
				toggleContent.slideDown(350);

			} else {

				jQuery(previewPar).animate({height: previewParClosedHeight}, 350, function() {jQuery(this).removeClass("preview-active");});
				toggleContent.slideUp(350);

			}

		});
	}


/** Sticky Footer
 **************************************************************** **/
	function _stickyFooter() {
		if(jQuery("#footer").hasClass('sticky')) {

			var footerHeight = 0,
				footerTop 	= 0,
				_footer 		= jQuery("#footer.sticky");

			positionFooter();

			function positionFooter() {
				footerHeight = _footer.height();
				footerTop = (jQuery(window).scrollTop()+jQuery(window).height()-footerHeight)+"px";

				if((jQuery(document.body).height()+footerHeight) > jQuery(window).height()) {
					_footer.css({
						position: "absolute"
					}).stop().animate({
						top: footerTop
					},0);
				} else {
					_footer.css({position: "static"});
				}

			}

			jQuery(window).scroll(positionFooter).resize(positionFooter);

		}
	}


	function relative_time(time_value) {
		var values 		= time_value.split(" "),
			parsed_date = Date.parse(time_value),
			relative_to = (arguments.length > 1) ? arguments[1] : new Date(),
			delta 		= parseInt((relative_to.getTime() - parsed_date) / 1000);

		time_value 		= values[1] + " " + values[2] + ", " + values[5] + " " + values[3];
		delta 			= delta + (relative_to.getTimezoneOffset() * 60);

		if (delta < 60) {
			return 'less than a minute ago';
		} else if(delta < 120) {
			return 'about a minute ago';
		} else if(delta < (60*60)) {
			return (parseInt(delta / 60)).toString() + ' minutes ago';
		} else if(delta < (120*60)) {
			return 'about an hour ago';
		} else if(delta < (24*60*60)) {
			return 'about ' + (parseInt(delta / 3600)).toString() + ' hours ago';
		} else if(delta < (48*60*60)) {
			return '1 day ago';
		} else {
			return (parseInt(delta / 86400)).toString() + ' days ago';
		}
	}

/** **************************************************************************************************************** **/
/** **************************************************************************************************************** **/
/** **************************************************************************************************************** **/
/** **************************************************************************************************************** **/


	/* 
		Mobile Check

		if( isMobile.any() ) alert('Mobile');
		if( isMobile.iOS() ) alert('iOS');
	*/

	var isMobile = {
	    iOS: function() {
	        return navigator.userAgent.match(/iPhone|iPad|iPod/i);
	    },
	    Android: function() {
	        return navigator.userAgent.match(/Android/i);
	    },
	    BlackBerry: function() {
	        return navigator.userAgent.match(/BlackBerry/i);
	    },
	    Opera: function() {
	        return navigator.userAgent.match(/Opera Mini/i);
	    },
	    Windows: function() {
	        return navigator.userAgent.match(/IEMobile/i) || navigator.userAgent.match(/WPDesktop/i);
	    },
	    any: function() {
	        return (isMobile.iOS() || isMobile.Android() || isMobile.BlackBerry() || isMobile.Opera() || isMobile.Windows());
	    }
	};




 	// Number Format
	Number.prototype.formatMoney = function(c, d, t){
	var n = this, 
	    c = isNaN(c = Math.abs(c)) ? 2 : c, 
	    d = d == undefined ? "." : d, 
	    t = t == undefined ? "," : t, 
	    s = n < 0 ? "-" : "", 
	    i = String(parseInt(n = Math.abs(Number(n) || 0).toFixed(c))), 
	    j = (j = i.length) > 3 ? j % 3 : 0;
	   return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
	};


	// scroll 
	function wheel(e) {
	  e.preventDefault();
	}

	function disable_scroll() {
	  if (window.addEventListener) {
		  window.addEventListener('DOMMouseScroll', wheel, false);
	  }
	  window.onmousewheel = document.onmousewheel = wheel;
	}

	function enable_scroll() {
		if (window.removeEventListener) {
			window.removeEventListener('DOMMouseScroll', wheel, false);
		}
		window.onmousewheel = document.onmousewheel = document.onkeydown = null;  
	}

	// overlay
	function enable_overlay() {
		jQuery("span.global-overlay").remove(); // remove first!
		jQuery('body').append('<span class="global-overlay"></span>');
	}
	function disable_overlay() {
		jQuery("span.global-overlay").remove();
	}


/** jQuery Easing v1.3
	http://gsgd.co.uk/sandbox/jquery/easing/
 **************************************************************** **/
jQuery.easing.jswing=jQuery.easing.swing;jQuery.extend(jQuery.easing,{def:"easeOutQuad",swing:function(e,f,a,h,g){return jQuery.easing[jQuery.easing.def](e,f,a,h,g)},easeInQuad:function(e,f,a,h,g){return h*(f/=g)*f+a},easeOutQuad:function(e,f,a,h,g){return -h*(f/=g)*(f-2)+a},easeInOutQuad:function(e,f,a,h,g){if((f/=g/2)<1){return h/2*f*f+a}return -h/2*((--f)*(f-2)-1)+a},easeInCubic:function(e,f,a,h,g){return h*(f/=g)*f*f+a},easeOutCubic:function(e,f,a,h,g){return h*((f=f/g-1)*f*f+1)+a},easeInOutCubic:function(e,f,a,h,g){if((f/=g/2)<1){return h/2*f*f*f+a}return h/2*((f-=2)*f*f+2)+a},easeInQuart:function(e,f,a,h,g){return h*(f/=g)*f*f*f+a},easeOutQuart:function(e,f,a,h,g){return -h*((f=f/g-1)*f*f*f-1)+a},easeInOutQuart:function(e,f,a,h,g){if((f/=g/2)<1){return h/2*f*f*f*f+a}return -h/2*((f-=2)*f*f*f-2)+a},easeInQuint:function(e,f,a,h,g){return h*(f/=g)*f*f*f*f+a},easeOutQuint:function(e,f,a,h,g){return h*((f=f/g-1)*f*f*f*f+1)+a},easeInOutQuint:function(e,f,a,h,g){if((f/=g/2)<1){return h/2*f*f*f*f*f+a}return h/2*((f-=2)*f*f*f*f+2)+a},easeInSine:function(e,f,a,h,g){return -h*Math.cos(f/g*(Math.PI/2))+h+a},easeOutSine:function(e,f,a,h,g){return h*Math.sin(f/g*(Math.PI/2))+a},easeInOutSine:function(e,f,a,h,g){return -h/2*(Math.cos(Math.PI*f/g)-1)+a},easeInExpo:function(e,f,a,h,g){return(f==0)?a:h*Math.pow(2,10*(f/g-1))+a},easeOutExpo:function(e,f,a,h,g){return(f==g)?a+h:h*(-Math.pow(2,-10*f/g)+1)+a},easeInOutExpo:function(e,f,a,h,g){if(f==0){return a}if(f==g){return a+h}if((f/=g/2)<1){return h/2*Math.pow(2,10*(f-1))+a}return h/2*(-Math.pow(2,-10*--f)+2)+a},easeInCirc:function(e,f,a,h,g){return -h*(Math.sqrt(1-(f/=g)*f)-1)+a},easeOutCirc:function(e,f,a,h,g){return h*Math.sqrt(1-(f=f/g-1)*f)+a},easeInOutCirc:function(e,f,a,h,g){if((f/=g/2)<1){return -h/2*(Math.sqrt(1-f*f)-1)+a}return h/2*(Math.sqrt(1-(f-=2)*f)+1)+a},easeInElastic:function(f,h,e,l,k){var i=1.70158;var j=0;var g=l;if(h==0){return e}if((h/=k)==1){return e+l}if(!j){j=k*0.3}if(g<Math.abs(l)){g=l;var i=j/4}else{var i=j/(2*Math.PI)*Math.asin(l/g)}return -(g*Math.pow(2,10*(h-=1))*Math.sin((h*k-i)*(2*Math.PI)/j))+e},easeOutElastic:function(f,h,e,l,k){var i=1.70158;var j=0;var g=l;if(h==0){return e}if((h/=k)==1){return e+l}if(!j){j=k*0.3}if(g<Math.abs(l)){g=l;var i=j/4}else{var i=j/(2*Math.PI)*Math.asin(l/g)}return g*Math.pow(2,-10*h)*Math.sin((h*k-i)*(2*Math.PI)/j)+l+e},easeInOutElastic:function(f,h,e,l,k){var i=1.70158;var j=0;var g=l;if(h==0){return e}if((h/=k/2)==2){return e+l}if(!j){j=k*(0.3*1.5)}if(g<Math.abs(l)){g=l;var i=j/4}else{var i=j/(2*Math.PI)*Math.asin(l/g)}if(h<1){return -0.5*(g*Math.pow(2,10*(h-=1))*Math.sin((h*k-i)*(2*Math.PI)/j))+e}return g*Math.pow(2,-10*(h-=1))*Math.sin((h*k-i)*(2*Math.PI)/j)*0.5+l+e},easeInBack:function(e,f,a,i,h,g){if(g==undefined){g=1.70158}return i*(f/=h)*f*((g+1)*f-g)+a},easeOutBack:function(e,f,a,i,h,g){if(g==undefined){g=1.70158}return i*((f=f/h-1)*f*((g+1)*f+g)+1)+a},easeInOutBack:function(e,f,a,i,h,g){if(g==undefined){g=1.70158}if((f/=h/2)<1){return i/2*(f*f*(((g*=(1.525))+1)*f-g))+a}return i/2*((f-=2)*f*(((g*=(1.525))+1)*f+g)+2)+a},easeInBounce:function(e,f,a,h,g){return h-jQuery.easing.easeOutBounce(e,g-f,0,h,g)+a},easeOutBounce:function(e,f,a,h,g){if((f/=g)<(1/2.75)){return h*(7.5625*f*f)+a}else{if(f<(2/2.75)){return h*(7.5625*(f-=(1.5/2.75))*f+0.75)+a}else{if(f<(2.5/2.75)){return h*(7.5625*(f-=(2.25/2.75))*f+0.9375)+a}else{return h*(7.5625*(f-=(2.625/2.75))*f+0.984375)+a}}}},easeInOutBounce:function(e,f,a,h,g){if(f<g/2){return jQuery.easing.easeInBounce(e,f*2,0,h,g)*0.5+a}return jQuery.easing.easeOutBounce(e,f*2-g,0,h,g)*0.5+h*0.5+a}});


/** Modernizr 3.3.1
	http://modernizr.com/download/#-csstransforms3d-csstransitions-video-touch-shiv-cssclasses-addtest-prefixed-teststyles-testprop-testallprops-hasevent-prefixes-domprefixes-load
 **************************************************************** **/
!function(e,t,n){function r(e,t){return typeof e===t}function o(){var e,t,n,o,i,a,s;for(var l in b)if(b.hasOwnProperty(l)){if(e=[],t=b[l],t.name&&(e.push(t.name.toLowerCase()),t.options&&t.options.aliases&&t.options.aliases.length))for(n=0;n<t.options.aliases.length;n++)e.push(t.options.aliases[n].toLowerCase());for(o=r(t.fn,"function")?t.fn():t.fn,i=0;i<e.length;i++)a=e[i],s=a.split("."),1===s.length?Modernizr[s[0]]=o:(!Modernizr[s[0]]||Modernizr[s[0]]instanceof Boolean||(Modernizr[s[0]]=new Boolean(Modernizr[s[0]])),Modernizr[s[0]][s[1]]=o),C.push((o?"":"no-")+s.join("-"))}}function i(e){var t=w.className,n=Modernizr._config.classPrefix||"";if(S&&(t=t.baseVal),Modernizr._config.enableJSClass){var r=new RegExp("(^|\\s)"+n+"no-js(\\s|$)");t=t.replace(r,"$1"+n+"js$2")}Modernizr._config.enableClasses&&(t+=" "+n+e.join(" "+n),S?w.className.baseVal=t:w.className=t)}function a(){return"function"!=typeof t.createElement?t.createElement(arguments[0]):S?t.createElementNS.call(t,"http://www.w3.org/2000/svg",arguments[0]):t.createElement.apply(t,arguments)}function s(e,t){if("object"==typeof e)for(var n in e)N(e,n)&&s(n,e[n]);else{e=e.toLowerCase();var r=e.split("."),o=Modernizr[r[0]];if(2==r.length&&(o=o[r[1]]),"undefined"!=typeof o)return Modernizr;t="function"==typeof t?t():t,1==r.length?Modernizr[r[0]]=t:(!Modernizr[r[0]]||Modernizr[r[0]]instanceof Boolean||(Modernizr[r[0]]=new Boolean(Modernizr[r[0]])),Modernizr[r[0]][r[1]]=t),i([(t&&0!=t?"":"no-")+r.join("-")]),Modernizr._trigger(e,t)}return Modernizr}function l(e){return e.replace(/([a-z])-([a-z])/g,function(e,t,n){return t+n.toUpperCase()}).replace(/^-/,"")}function c(e,t){return!!~(""+e).indexOf(t)}function u(){var e=t.body;return e||(e=a(S?"svg":"body"),e.fake=!0),e}function f(e,n,r,o){var i,s,l,c,f="modernizr",d=a("div"),p=u();if(parseInt(r,10))for(;r--;)l=a("div"),l.id=o?o[r]:f+(r+1),d.appendChild(l);return i=a("style"),i.type="text/css",i.id="s"+f,(p.fake?p:d).appendChild(i),p.appendChild(d),i.styleSheet?i.styleSheet.cssText=e:i.appendChild(t.createTextNode(e)),d.id=f,p.fake&&(p.style.background="",p.style.overflow="hidden",c=w.style.overflow,w.style.overflow="hidden",w.appendChild(p)),s=n(d,e),p.fake?(p.parentNode.removeChild(p),w.style.overflow=c,w.offsetHeight):d.parentNode.removeChild(d),!!s}function d(e,t){return function(){return e.apply(t,arguments)}}function p(e,t,n){var o;for(var i in e)if(e[i]in t)return n===!1?e[i]:(o=t[e[i]],r(o,"function")?d(o,n||t):o);return!1}function m(e){return e.replace(/([A-Z])/g,function(e,t){return"-"+t.toLowerCase()}).replace(/^ms-/,"-ms-")}function h(t,r){var o=t.length;if("CSS"in e&&"supports"in e.CSS){for(;o--;)if(e.CSS.supports(m(t[o]),r))return!0;return!1}if("CSSSupportsRule"in e){for(var i=[];o--;)i.push("("+m(t[o])+":"+r+")");return i=i.join(" or "),f("@supports ("+i+") { #modernizr { position: absolute; } }",function(e){return"absolute"==getComputedStyle(e,null).position})}return n}function v(e,t,o,i){function s(){f&&(delete A.style,delete A.modElem)}if(i=r(i,"undefined")?!1:i,!r(o,"undefined")){var u=h(e,o);if(!r(u,"undefined"))return u}for(var f,d,p,m,v,g=["modernizr","tspan","samp"];!A.style&&g.length;)f=!0,A.modElem=a(g.shift()),A.style=A.modElem.style;for(p=e.length,d=0;p>d;d++)if(m=e[d],v=A.style[m],c(m,"-")&&(m=l(m)),A.style[m]!==n){if(i||r(o,"undefined"))return s(),"pfx"==t?m:!0;try{A.style[m]=o}catch(y){}if(A.style[m]!=v)return s(),"pfx"==t?m:!0}return s(),!1}function g(e,t,n,o,i){var a=e.charAt(0).toUpperCase()+e.slice(1),s=(e+" "+z.join(a+" ")+a).split(" ");return r(t,"string")||r(t,"undefined")?v(s,t,o,i):(s=(e+" "+T.join(a+" ")+a).split(" "),p(s,t,n))}function y(e,t,r){return g(e,n,n,t,r)}var C=[],b=[],E={_version:"3.3.1",_config:{classPrefix:"",enableClasses:!0,enableJSClass:!0,usePrefixes:!0},_q:[],on:function(e,t){var n=this;setTimeout(function(){t(n[e])},0)},addTest:function(e,t,n){b.push({name:e,fn:t,options:n})},addAsyncTest:function(e){b.push({name:null,fn:e})}},Modernizr=function(){};Modernizr.prototype=E,Modernizr=new Modernizr;var _=E._config.usePrefixes?" -webkit- -moz- -o- -ms- ".split(" "):["",""];E._prefixes=_;var w=t.documentElement,S="svg"===w.nodeName.toLowerCase();S||!function(e,t){function n(e,t){var n=e.createElement("p"),r=e.getElementsByTagName("head")[0]||e.documentElement;return n.innerHTML="x<style>"+t+"</style>",r.insertBefore(n.lastChild,r.firstChild)}function r(){var e=C.elements;return"string"==typeof e?e.split(" "):e}function o(e,t){var n=C.elements;"string"!=typeof n&&(n=n.join(" ")),"string"!=typeof e&&(e=e.join(" ")),C.elements=n+" "+e,c(t)}function i(e){var t=y[e[v]];return t||(t={},g++,e[v]=g,y[g]=t),t}function a(e,n,r){if(n||(n=t),f)return n.createElement(e);r||(r=i(n));var o;return o=r.cache[e]?r.cache[e].cloneNode():h.test(e)?(r.cache[e]=r.createElem(e)).cloneNode():r.createElem(e),!o.canHaveChildren||m.test(e)||o.tagUrn?o:r.frag.appendChild(o)}function s(e,n){if(e||(e=t),f)return e.createDocumentFragment();n=n||i(e);for(var o=n.frag.cloneNode(),a=0,s=r(),l=s.length;l>a;a++)o.createElement(s[a]);return o}function l(e,t){t.cache||(t.cache={},t.createElem=e.createElement,t.createFrag=e.createDocumentFragment,t.frag=t.createFrag()),e.createElement=function(n){return C.shivMethods?a(n,e,t):t.createElem(n)},e.createDocumentFragment=Function("h,f","return function(){var n=f.cloneNode(),c=n.createElement;h.shivMethods&&("+r().join().replace(/[\w\-:]+/g,function(e){return t.createElem(e),t.frag.createElement(e),'c("'+e+'")'})+");return n}")(C,t.frag)}function c(e){e||(e=t);var r=i(e);return!C.shivCSS||u||r.hasCSS||(r.hasCSS=!!n(e,"article,aside,dialog,figcaption,figure,footer,header,hgroup,main,nav,section{display:block}mark{background:#FF0;color:#000}template{display:none}")),f||l(e,r),e}var u,f,d="3.7.3",p=e.html5||{},m=/^<|^(?:button|map|select|textarea|object|iframe|option|optgroup)$/i,h=/^(?:a|b|code|div|fieldset|h1|h2|h3|h4|h5|h6|i|label|li|ol|p|q|span|strong|style|table|tbody|td|th|tr|ul)$/i,v="_html5shiv",g=0,y={};!function(){try{var e=t.createElement("a");e.innerHTML="<xyz></xyz>",u="hidden"in e,f=1==e.childNodes.length||function(){t.createElement("a");var e=t.createDocumentFragment();return"undefined"==typeof e.cloneNode||"undefined"==typeof e.createDocumentFragment||"undefined"==typeof e.createElement}()}catch(n){u=!0,f=!0}}();var C={elements:p.elements||"abbr article aside audio bdi canvas data datalist details dialog figcaption figure footer header hgroup main mark meter nav output picture progress section summary template time video",version:d,shivCSS:p.shivCSS!==!1,supportsUnknownElements:f,shivMethods:p.shivMethods!==!1,type:"default",shivDocument:c,createElement:a,createDocumentFragment:s,addElements:o};e.html5=C,c(t),"object"==typeof module&&module.exports&&(module.exports=C)}("undefined"!=typeof e?e:this,t);var x="Moz O ms Webkit",T=E._config.usePrefixes?x.toLowerCase().split(" "):[];E._domPrefixes=T;var P=function(){function e(e,t){var o;return e?(t&&"string"!=typeof t||(t=a(t||"div")),e="on"+e,o=e in t,!o&&r&&(t.setAttribute||(t=a("div")),t.setAttribute(e,""),o="function"==typeof t[e],t[e]!==n&&(t[e]=n),t.removeAttribute(e)),o):!1}var r=!("onblur"in t.documentElement);return e}();E.hasEvent=P,Modernizr.addTest("video",function(){var e=a("video"),t=!1;try{(t=!!e.canPlayType)&&(t=new Boolean(t),t.ogg=e.canPlayType('video/ogg; codecs="theora"').replace(/^no$/,""),t.h264=e.canPlayType('video/mp4; codecs="avc1.42E01E"').replace(/^no$/,""),t.webm=e.canPlayType('video/webm; codecs="vp8, vorbis"').replace(/^no$/,""),t.vp9=e.canPlayType('video/webm; codecs="vp9"').replace(/^no$/,""),t.hls=e.canPlayType('application/x-mpegURL; codecs="avc1.42E01E"').replace(/^no$/,""))}catch(n){}return t});var N;!function(){var e={}.hasOwnProperty;N=r(e,"undefined")||r(e.call,"undefined")?function(e,t){return t in e&&r(e.constructor.prototype[t],"undefined")}:function(t,n){return e.call(t,n)}}(),E._l={},E.on=function(e,t){this._l[e]||(this._l[e]=[]),this._l[e].push(t),Modernizr.hasOwnProperty(e)&&setTimeout(function(){Modernizr._trigger(e,Modernizr[e])},0)},E._trigger=function(e,t){if(this._l[e]){var n=this._l[e];setTimeout(function(){var e,r;for(e=0;e<n.length;e++)(r=n[e])(t)},0),delete this._l[e]}},Modernizr._q.push(function(){E.addTest=s});var j="CSS"in e&&"supports"in e.CSS,k="supportsCSS"in e;Modernizr.addTest("supports",j||k);var z=E._config.usePrefixes?x.split(" "):[];E._cssomPrefixes=z;var F=function(t){var r,o=_.length,i=e.CSSRule;if("undefined"==typeof i)return n;if(!t)return!1;if(t=t.replace(/^@/,""),r=t.replace(/-/g,"_").toUpperCase()+"_RULE",r in i)return"@"+t;for(var a=0;o>a;a++){var s=_[a],l=s.toUpperCase()+"_"+r;if(l in i)return"@-"+s.toLowerCase()+"-"+t}return!1};E.atRule=F;var L=E.testStyles=f,$={elem:a("modernizr")};Modernizr._q.push(function(){delete $.elem});var A={style:$.elem.style};Modernizr._q.unshift(function(){delete A.style});E.testProp=function(e,t,r){return v([e],n,t,r)};E.testAllProps=g;E.prefixed=function(e,t,n){return 0===e.indexOf("@")?F(e):(-1!=e.indexOf("-")&&(e=l(e)),t?g(e,t,n):g(e,"pfx"))};E.testAllProps=y,Modernizr.addTest("csstransitions",y("transition","all",!0)),Modernizr.addTest("csstransforms3d",function(){var e=!!y("perspective","1px",!0),t=Modernizr._config.usePrefixes;if(e&&(!t||"webkitPerspective"in w.style)){var n,r="#modernizr{width:0;height:0}";Modernizr.supports?n="@supports (perspective: 1px)":(n="@media (transform-3d)",t&&(n+=",(-webkit-transform-3d)")),n+="{#modernizr{width:7px;height:18px;margin:0;padding:0;border:0}}",L(r+n,function(t){e=7===t.offsetWidth&&18===t.offsetHeight})}return e}),o(),i(C),delete E.addTest,delete E.addAsyncTest;for(var M=0;M<Modernizr._q.length;M++)Modernizr._q[M]();e.Modernizr=Modernizr}(window,document);

/** TETHER - used by bootstrap
	http://tether.io/
 **************************************************************** **/
function _loadTetherBS4() {
	!function(t,e){"function"==typeof define&&define.amd?define(e):"object"==typeof exports?module.exports=e(require,exports,module):t.Tether=e()}(this,function(t,e,o){"use strict";function n(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}function i(t){var e=t.getBoundingClientRect(),o={};for(var n in e)o[n]=e[n];if(t.ownerDocument!==document){var r=t.ownerDocument.defaultView.frameElement;if(r){var s=i(r);o.top+=s.top,o.bottom+=s.top,o.left+=s.left,o.right+=s.left}}return o}function r(t){var e=getComputedStyle(t)||{},o=e.position,n=[];if("fixed"===o)return[t];for(var i=t;(i=i.parentNode)&&i&&1===i.nodeType;){var r=void 0;try{r=getComputedStyle(i)}catch(s){}if("undefined"==typeof r||null===r)return n.push(i),n;var a=r,f=a.overflow,l=a.overflowX,h=a.overflowY;/(auto|scroll)/.test(f+h+l)&&("absolute"!==o||["relative","absolute","fixed"].indexOf(r.position)>=0)&&n.push(i)}return n.push(t.ownerDocument.body),t.ownerDocument!==document&&n.push(t.ownerDocument.defaultView),n}function s(){A&&document.body.removeChild(A),A=null}function a(t){var e=void 0;t===document?(e=document,t=document.documentElement):e=t.ownerDocument;var o=e.documentElement,n=i(t),r=P();return n.top-=r.top,n.left-=r.left,"undefined"==typeof n.width&&(n.width=document.body.scrollWidth-n.left-n.right),"undefined"==typeof n.height&&(n.height=document.body.scrollHeight-n.top-n.bottom),n.top=n.top-o.clientTop,n.left=n.left-o.clientLeft,n.right=e.body.clientWidth-n.width-n.left,n.bottom=e.body.clientHeight-n.height-n.top,n}function f(t){return t.offsetParent||document.documentElement}function l(){var t=document.createElement("div");t.style.width="100%",t.style.height="200px";var e=document.createElement("div");h(e.style,{position:"absolute",top:0,left:0,pointerEvents:"none",visibility:"hidden",width:"200px",height:"150px",overflow:"hidden"}),e.appendChild(t),document.body.appendChild(e);var o=t.offsetWidth;e.style.overflow="scroll";var n=t.offsetWidth;o===n&&(n=e.clientWidth),document.body.removeChild(e);var i=o-n;return{width:i,height:i}}function h(){var t=arguments.length<=0||void 0===arguments[0]?{}:arguments[0],e=[];return Array.prototype.push.apply(e,arguments),e.slice(1).forEach(function(e){if(e)for(var o in e)({}).hasOwnProperty.call(e,o)&&(t[o]=e[o])}),t}function u(t,e){if("undefined"!=typeof t.classList)e.split(" ").forEach(function(e){e.trim()&&t.classList.remove(e)});else{var o=new RegExp("(^| )"+e.split(" ").join("|")+"( |$)","gi"),n=c(t).replace(o," ");g(t,n)}}function d(t,e){if("undefined"!=typeof t.classList)e.split(" ").forEach(function(e){e.trim()&&t.classList.add(e)});else{u(t,e);var o=c(t)+(" "+e);g(t,o)}}function p(t,e){if("undefined"!=typeof t.classList)return t.classList.contains(e);var o=c(t);return new RegExp("(^| )"+e+"( |$)","gi").test(o)}function c(t){return t.className instanceof t.ownerDocument.defaultView.SVGAnimatedString?t.className.baseVal:t.className}function g(t,e){t.setAttribute("class",e)}function m(t,e,o){o.forEach(function(o){-1===e.indexOf(o)&&p(t,o)&&u(t,o)}),e.forEach(function(e){p(t,e)||d(t,e)})}function n(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}function v(t,e){if("function"!=typeof e&&null!==e)throw new TypeError("Super expression must either be null or a function, not "+typeof e);t.prototype=Object.create(e&&e.prototype,{constructor:{value:t,enumerable:!1,writable:!0,configurable:!0}}),e&&(Object.setPrototypeOf?Object.setPrototypeOf(t,e):t.__proto__=e)}function y(t,e){var o=arguments.length<=2||void 0===arguments[2]?1:arguments[2];return t+o>=e&&e>=t-o}function b(){return"undefined"!=typeof performance&&"undefined"!=typeof performance.now?performance.now():+new Date}function w(){for(var t={top:0,left:0},e=arguments.length,o=Array(e),n=0;e>n;n++)o[n]=arguments[n];return o.forEach(function(e){var o=e.top,n=e.left;"string"==typeof o&&(o=parseFloat(o,10)),"string"==typeof n&&(n=parseFloat(n,10)),t.top+=o,t.left+=n}),t}function C(t,e){return"string"==typeof t.left&&-1!==t.left.indexOf("%")&&(t.left=parseFloat(t.left,10)/100*e.width),"string"==typeof t.top&&-1!==t.top.indexOf("%")&&(t.top=parseFloat(t.top,10)/100*e.height),t}function O(t,e){return"scrollParent"===e?e=t.scrollParents[0]:"window"===e&&(e=[pageXOffset,pageYOffset,innerWidth+pageXOffset,innerHeight+pageYOffset]),e===document&&(e=e.documentElement),"undefined"!=typeof e.nodeType&&!function(){var t=e,o=a(e),n=o,i=getComputedStyle(e);if(e=[n.left,n.top,o.width+n.left,o.height+n.top],t.ownerDocument!==document){var r=t.ownerDocument.defaultView;e[0]+=r.pageXOffset,e[1]+=r.pageYOffset,e[2]+=r.pageXOffset,e[3]+=r.pageYOffset}$.forEach(function(t,o){t=t[0].toUpperCase()+t.substr(1),"Top"===t||"Left"===t?e[o]+=parseFloat(i["border"+t+"Width"]):e[o]-=parseFloat(i["border"+t+"Width"])})}(),e}var E=function(){function t(t,e){for(var o=0;o<e.length;o++){var n=e[o];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,n.key,n)}}return function(e,o,n){return o&&t(e.prototype,o),n&&t(e,n),e}}(),x=void 0;"undefined"==typeof x&&(x={modules:[]});var A=null,T=function(){var t=0;return function(){return++t}}(),S={},P=function(){var t=A;t||(t=document.createElement("div"),t.setAttribute("data-tether-id",T()),h(t.style,{top:0,left:0,position:"absolute"}),document.body.appendChild(t),A=t);var e=t.getAttribute("data-tether-id");return"undefined"==typeof S[e]&&(S[e]=i(t),M(function(){delete S[e]})),S[e]},W=[],M=function(t){W.push(t)},_=function(){for(var t=void 0;t=W.pop();)t()},k=function(){function t(){n(this,t)}return E(t,[{key:"on",value:function(t,e,o){var n=arguments.length<=3||void 0===arguments[3]?!1:arguments[3];"undefined"==typeof this.bindings&&(this.bindings={}),"undefined"==typeof this.bindings[t]&&(this.bindings[t]=[]),this.bindings[t].push({handler:e,ctx:o,once:n})}},{key:"once",value:function(t,e,o){this.on(t,e,o,!0)}},{key:"off",value:function(t,e){if("undefined"!=typeof this.bindings&&"undefined"!=typeof this.bindings[t])if("undefined"==typeof e)delete this.bindings[t];else for(var o=0;o<this.bindings[t].length;)this.bindings[t][o].handler===e?this.bindings[t].splice(o,1):++o}},{key:"trigger",value:function(t){if("undefined"!=typeof this.bindings&&this.bindings[t]){for(var e=0,o=arguments.length,n=Array(o>1?o-1:0),i=1;o>i;i++)n[i-1]=arguments[i];for(;e<this.bindings[t].length;){var r=this.bindings[t][e],s=r.handler,a=r.ctx,f=r.once,l=a;"undefined"==typeof l&&(l=this),s.apply(l,n),f?this.bindings[t].splice(e,1):++e}}}}]),t}();x.Utils={getActualBoundingClientRect:i,getScrollParents:r,getBounds:a,getOffsetParent:f,extend:h,addClass:d,removeClass:u,hasClass:p,updateClasses:m,defer:M,flush:_,uniqueId:T,Evented:k,getScrollBarSize:l,removeUtilElements:s};var B=function(){function t(t,e){var o=[],n=!0,i=!1,r=void 0;try{for(var s,a=t[Symbol.iterator]();!(n=(s=a.next()).done)&&(o.push(s.value),!e||o.length!==e);n=!0);}catch(f){i=!0,r=f}finally{try{!n&&a["return"]&&a["return"]()}finally{if(i)throw r}}return o}return function(e,o){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,o);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),E=function(){function t(t,e){for(var o=0;o<e.length;o++){var n=e[o];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(t,n.key,n)}}return function(e,o,n){return o&&t(e.prototype,o),n&&t(e,n),e}}(),z=function(t,e,o){for(var n=!0;n;){var i=t,r=e,s=o;n=!1,null===i&&(i=Function.prototype);var a=Object.getOwnPropertyDescriptor(i,r);if(void 0!==a){if("value"in a)return a.value;var f=a.get;if(void 0===f)return;return f.call(s)}var l=Object.getPrototypeOf(i);if(null===l)return;t=l,e=r,o=s,n=!0,a=l=void 0}};if("undefined"==typeof x)throw new Error("You must include the utils.js file before tether.js");var j=x.Utils,r=j.getScrollParents,a=j.getBounds,f=j.getOffsetParent,h=j.extend,d=j.addClass,u=j.removeClass,m=j.updateClasses,M=j.defer,_=j.flush,l=j.getScrollBarSize,s=j.removeUtilElements,Y=function(){if("undefined"==typeof document)return"";for(var t=document.createElement("div"),e=["transform","WebkitTransform","OTransform","MozTransform","msTransform"],o=0;o<e.length;++o){var n=e[o];if(void 0!==t.style[n])return n}}(),L=[],D=function(){L.forEach(function(t){t.position(!1)}),_()};!function(){var t=null,e=null,o=null,n=function i(){return"undefined"!=typeof e&&e>16?(e=Math.min(e-16,250),void(o=setTimeout(i,250))):void("undefined"!=typeof t&&b()-t<10||(null!=o&&(clearTimeout(o),o=null),t=b(),D(),e=b()-t))};"undefined"!=typeof window&&"undefined"!=typeof window.addEventListener&&["resize","scroll","touchmove"].forEach(function(t){window.addEventListener(t,n)})}();var X={center:"center",left:"right",right:"left"},F={middle:"middle",top:"bottom",bottom:"top"},H={top:0,left:0,middle:"50%",center:"50%",bottom:"100%",right:"100%"},N=function(t,e){var o=t.left,n=t.top;return"auto"===o&&(o=X[e.left]),"auto"===n&&(n=F[e.top]),{left:o,top:n}},U=function(t){var e=t.left,o=t.top;return"undefined"!=typeof H[t.left]&&(e=H[t.left]),"undefined"!=typeof H[t.top]&&(o=H[t.top]),{left:e,top:o}},V=function(t){var e=t.split(" "),o=B(e,2),n=o[0],i=o[1];return{top:n,left:i}},R=V,q=function(t){function e(t){var o=this;n(this,e),z(Object.getPrototypeOf(e.prototype),"constructor",this).call(this),this.position=this.position.bind(this),L.push(this),this.history=[],this.setOptions(t,!1),x.modules.forEach(function(t){"undefined"!=typeof t.initialize&&t.initialize.call(o)}),this.position()}return v(e,t),E(e,[{key:"getClass",value:function(){var t=arguments.length<=0||void 0===arguments[0]?"":arguments[0],e=this.options.classes;return"undefined"!=typeof e&&e[t]?this.options.classes[t]:this.options.classPrefix?this.options.classPrefix+"-"+t:t}},{key:"setOptions",value:function(t){var e=this,o=arguments.length<=1||void 0===arguments[1]?!0:arguments[1],n={offset:"0 0",targetOffset:"0 0",targetAttachment:"auto auto",classPrefix:"tether"};this.options=h(n,t);var i=this.options,s=i.element,a=i.target,f=i.targetModifier;if(this.element=s,this.target=a,this.targetModifier=f,"viewport"===this.target?(this.target=document.body,this.targetModifier="visible"):"scroll-handle"===this.target&&(this.target=document.body,this.targetModifier="scroll-handle"),["element","target"].forEach(function(t){if("undefined"==typeof e[t])throw new Error("Tether Error: Both element and target must be defined");"undefined"!=typeof e[t].jquery?e[t]=e[t][0]:"string"==typeof e[t]&&(e[t]=document.querySelector(e[t]))}),d(this.element,this.getClass("element")),this.options.addTargetClasses!==!1&&d(this.target,this.getClass("target")),!this.options.attachment)throw new Error("Tether Error: You must provide an attachment");this.targetAttachment=R(this.options.targetAttachment),this.attachment=R(this.options.attachment),this.offset=V(this.options.offset),this.targetOffset=V(this.options.targetOffset),"undefined"!=typeof this.scrollParents&&this.disable(),"scroll-handle"===this.targetModifier?this.scrollParents=[this.target]:this.scrollParents=r(this.target),this.options.enabled!==!1&&this.enable(o)}},{key:"getTargetBounds",value:function(){if("undefined"==typeof this.targetModifier)return a(this.target);if("visible"===this.targetModifier){if(this.target===document.body)return{top:pageYOffset,left:pageXOffset,height:innerHeight,width:innerWidth};var t=a(this.target),e={height:t.height,width:t.width,top:t.top,left:t.left};return e.height=Math.min(e.height,t.height-(pageYOffset-t.top)),e.height=Math.min(e.height,t.height-(t.top+t.height-(pageYOffset+innerHeight))),e.height=Math.min(innerHeight,e.height),e.height-=2,e.width=Math.min(e.width,t.width-(pageXOffset-t.left)),e.width=Math.min(e.width,t.width-(t.left+t.width-(pageXOffset+innerWidth))),e.width=Math.min(innerWidth,e.width),e.width-=2,e.top<pageYOffset&&(e.top=pageYOffset),e.left<pageXOffset&&(e.left=pageXOffset),e}if("scroll-handle"===this.targetModifier){var t=void 0,o=this.target;o===document.body?(o=document.documentElement,t={left:pageXOffset,top:pageYOffset,height:innerHeight,width:innerWidth}):t=a(o);var n=getComputedStyle(o),i=o.scrollWidth>o.clientWidth||[n.overflow,n.overflowX].indexOf("scroll")>=0||this.target!==document.body,r=0;i&&(r=15);var s=t.height-parseFloat(n.borderTopWidth)-parseFloat(n.borderBottomWidth)-r,e={width:15,height:.975*s*(s/o.scrollHeight),left:t.left+t.width-parseFloat(n.borderLeftWidth)-15},f=0;408>s&&this.target===document.body&&(f=-11e-5*Math.pow(s,2)-.00727*s+22.58),this.target!==document.body&&(e.height=Math.max(e.height,24));var l=this.target.scrollTop/(o.scrollHeight-s);return e.top=l*(s-e.height-f)+t.top+parseFloat(n.borderTopWidth),this.target===document.body&&(e.height=Math.max(e.height,24)),e}}},{key:"clearCache",value:function(){this._cache={}}},{key:"cache",value:function(t,e){return"undefined"==typeof this._cache&&(this._cache={}),"undefined"==typeof this._cache[t]&&(this._cache[t]=e.call(this)),this._cache[t]}},{key:"enable",value:function(){var t=this,e=arguments.length<=0||void 0===arguments[0]?!0:arguments[0];this.options.addTargetClasses!==!1&&d(this.target,this.getClass("enabled")),d(this.element,this.getClass("enabled")),this.enabled=!0,this.scrollParents.forEach(function(e){e!==t.target.ownerDocument&&e.addEventListener("scroll",t.position)}),e&&this.position()}},{key:"disable",value:function(){var t=this;u(this.target,this.getClass("enabled")),u(this.element,this.getClass("enabled")),this.enabled=!1,"undefined"!=typeof this.scrollParents&&this.scrollParents.forEach(function(e){e.removeEventListener("scroll",t.position)})}},{key:"destroy",value:function(){var t=this;this.disable(),L.forEach(function(e,o){e===t&&L.splice(o,1)}),0===L.length&&s()}},{key:"updateAttachClasses",value:function(t,e){var o=this;t=t||this.attachment,e=e||this.targetAttachment;var n=["left","top","bottom","right","middle","center"];"undefined"!=typeof this._addAttachClasses&&this._addAttachClasses.length&&this._addAttachClasses.splice(0,this._addAttachClasses.length),"undefined"==typeof this._addAttachClasses&&(this._addAttachClasses=[]);var i=this._addAttachClasses;t.top&&i.push(this.getClass("element-attached")+"-"+t.top),t.left&&i.push(this.getClass("element-attached")+"-"+t.left),e.top&&i.push(this.getClass("target-attached")+"-"+e.top),e.left&&i.push(this.getClass("target-attached")+"-"+e.left);var r=[];n.forEach(function(t){r.push(o.getClass("element-attached")+"-"+t),r.push(o.getClass("target-attached")+"-"+t)}),M(function(){"undefined"!=typeof o._addAttachClasses&&(m(o.element,o._addAttachClasses,r),o.options.addTargetClasses!==!1&&m(o.target,o._addAttachClasses,r),delete o._addAttachClasses)})}},{key:"position",value:function(){var t=this,e=arguments.length<=0||void 0===arguments[0]?!0:arguments[0];if(this.enabled){this.clearCache();var o=N(this.targetAttachment,this.attachment);this.updateAttachClasses(this.attachment,o);var n=this.cache("element-bounds",function(){return a(t.element)}),i=n.width,r=n.height;if(0===i&&0===r&&"undefined"!=typeof this.lastSize){var s=this.lastSize;i=s.width,r=s.height}else this.lastSize={width:i,height:r};var h=this.cache("target-bounds",function(){return t.getTargetBounds()}),u=h,d=C(U(this.attachment),{width:i,height:r}),p=C(U(o),u),c=C(this.offset,{width:i,height:r}),g=C(this.targetOffset,u);d=w(d,c),p=w(p,g);for(var m=h.left+p.left-d.left,v=h.top+p.top-d.top,y=0;y<x.modules.length;++y){var b=x.modules[y],O=b.position.call(this,{left:m,top:v,targetAttachment:o,targetPos:h,elementPos:n,offset:d,targetOffset:p,manualOffset:c,manualTargetOffset:g,scrollbarSize:S,attachment:this.attachment});if(O===!1)return!1;"undefined"!=typeof O&&"object"==typeof O&&(v=O.top,m=O.left)}var E={page:{top:v,left:m},viewport:{top:v-pageYOffset,bottom:pageYOffset-v-r+innerHeight,left:m-pageXOffset,right:pageXOffset-m-i+innerWidth}},A=this.target.ownerDocument,T=A.defaultView,S=void 0;return A.body.scrollWidth>T.innerWidth&&(S=this.cache("scrollbar-size",l),E.viewport.bottom-=S.height),A.body.scrollHeight>T.innerHeight&&(S=this.cache("scrollbar-size",l),E.viewport.right-=S.width),(-1===["","static"].indexOf(A.body.style.position)||-1===["","static"].indexOf(A.body.parentElement.style.position))&&(E.page.bottom=A.body.scrollHeight-v-r,E.page.right=A.body.scrollWidth-m-i),"undefined"!=typeof this.options.optimizations&&this.options.optimizations.moveElement!==!1&&"undefined"==typeof this.targetModifier&&!function(){var e=t.cache("target-offsetparent",function(){return f(t.target)}),o=t.cache("target-offsetparent-bounds",function(){return a(e)}),n=getComputedStyle(e),i=o,r={};if(["Top","Left","Bottom","Right"].forEach(function(t){r[t.toLowerCase()]=parseFloat(n["border"+t+"Width"])}),o.right=A.body.scrollWidth-o.left-i.width+r.right,o.bottom=A.body.scrollHeight-o.top-i.height+r.bottom,E.page.top>=o.top+r.top&&E.page.bottom>=o.bottom&&E.page.left>=o.left+r.left&&E.page.right>=o.right){var s=e.scrollTop,l=e.scrollLeft;E.offset={top:E.page.top-o.top+s-r.top,left:E.page.left-o.left+l-r.left}}}(),this.move(E),this.history.unshift(E),this.history.length>3&&this.history.pop(),e&&_(),!0}}},{key:"move",value:function(t){var e=this;if("undefined"!=typeof this.element.parentNode){var o={};for(var n in t){o[n]={};for(var i in t[n]){for(var r=!1,s=0;s<this.history.length;++s){var a=this.history[s];if("undefined"!=typeof a[n]&&!y(a[n][i],t[n][i])){r=!0;break}}r||(o[n][i]=!0)}}var l={top:"",left:"",right:"",bottom:""},u=function(t,o){var n="undefined"!=typeof e.options.optimizations,i=n?e.options.optimizations.gpu:null;if(i!==!1){var r=void 0,s=void 0;t.top?(l.top=0,r=o.top):(l.bottom=0,r=-o.bottom),t.left?(l.left=0,s=o.left):(l.right=0,s=-o.right),l[Y]="translateX("+Math.round(s)+"px) translateY("+Math.round(r)+"px)","msTransform"!==Y&&(l[Y]+=" translateZ(0)")}else t.top?l.top=o.top+"px":l.bottom=o.bottom+"px",t.left?l.left=o.left+"px":l.right=o.right+"px"},d=!1;if((o.page.top||o.page.bottom)&&(o.page.left||o.page.right)?(l.position="absolute",u(o.page,t.page)):(o.viewport.top||o.viewport.bottom)&&(o.viewport.left||o.viewport.right)?(l.position="fixed",u(o.viewport,t.viewport)):"undefined"!=typeof o.offset&&o.offset.top&&o.offset.left?!function(){l.position="absolute";var n=e.cache("target-offsetparent",function(){return f(e.target)});f(e.element)!==n&&M(function(){e.element.parentNode.removeChild(e.element),n.appendChild(e.element)}),u(o.offset,t.offset),d=!0}():(l.position="absolute",u({top:!0,left:!0},t.page)),!d){for(var p=!0,c=this.element.parentNode;c&&1===c.nodeType&&"BODY"!==c.tagName;){if("static"!==getComputedStyle(c).position){p=!1;break}c=c.parentNode}p||(this.element.parentNode.removeChild(this.element),this.element.ownerDocument.body.appendChild(this.element))}var g={},m=!1;for(var i in l){var v=l[i],b=this.element.style[i];b!==v&&(m=!0,g[i]=v)}m&&M(function(){h(e.element.style,g)})}}}]),e}(k);q.modules=[],x.position=D;var I=h(q,x),B=function(){function t(t,e){var o=[],n=!0,i=!1,r=void 0;try{for(var s,a=t[Symbol.iterator]();!(n=(s=a.next()).done)&&(o.push(s.value),!e||o.length!==e);n=!0);}catch(f){i=!0,r=f}finally{try{!n&&a["return"]&&a["return"]()}finally{if(i)throw r}}return o}return function(e,o){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,o);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}(),j=x.Utils,a=j.getBounds,h=j.extend,m=j.updateClasses,M=j.defer,$=["left","top","right","bottom"];x.modules.push({position:function(t){var e=this,o=t.top,n=t.left,i=t.targetAttachment;if(!this.options.constraints)return!0;var r=this.cache("element-bounds",function(){return a(e.element)}),s=r.height,f=r.width;if(0===f&&0===s&&"undefined"!=typeof this.lastSize){var l=this.lastSize;f=l.width,s=l.height}var u=this.cache("target-bounds",function(){return e.getTargetBounds()}),d=u.height,p=u.width,c=[this.getClass("pinned"),this.getClass("out-of-bounds")];this.options.constraints.forEach(function(t){var e=t.outOfBoundsClass,o=t.pinnedClass;e&&c.push(e),o&&c.push(o)}),c.forEach(function(t){["left","top","right","bottom"].forEach(function(e){c.push(t+"-"+e)})});var g=[],v=h({},i),y=h({},this.attachment);return this.options.constraints.forEach(function(t){var r=t.to,a=t.attachment,l=t.pin;"undefined"==typeof a&&(a="");var h=void 0,u=void 0;if(a.indexOf(" ")>=0){var c=a.split(" "),m=B(c,2);u=m[0],h=m[1]}else h=u=a;var b=O(e,r);("target"===u||"both"===u)&&(o<b[1]&&"top"===v.top&&(o+=d,v.top="bottom"),o+s>b[3]&&"bottom"===v.top&&(o-=d,v.top="top")),"together"===u&&("top"===v.top&&("bottom"===y.top&&o<b[1]?(o+=d,v.top="bottom",o+=s,y.top="top"):"top"===y.top&&o+s>b[3]&&o-(s-d)>=b[1]&&(o-=s-d,v.top="bottom",y.top="bottom")),"bottom"===v.top&&("top"===y.top&&o+s>b[3]?(o-=d,v.top="top",o-=s,y.top="bottom"):"bottom"===y.top&&o<b[1]&&o+(2*s-d)<=b[3]&&(o+=s-d,v.top="top",y.top="top")),"middle"===v.top&&(o+s>b[3]&&"top"===y.top?(o-=s,y.top="bottom"):o<b[1]&&"bottom"===y.top&&(o+=s,y.top="top"))),("target"===h||"both"===h)&&(n<b[0]&&"left"===v.left&&(n+=p,v.left="right"),n+f>b[2]&&"right"===v.left&&(n-=p,v.left="left")),"together"===h&&(n<b[0]&&"left"===v.left?"right"===y.left?(n+=p,v.left="right",n+=f,y.left="left"):"left"===y.left&&(n+=p,v.left="right",n-=f,y.left="right"):n+f>b[2]&&"right"===v.left?"left"===y.left?(n-=p,v.left="left",n-=f,y.left="right"):"right"===y.left&&(n-=p,v.left="left",n+=f,y.left="left"):"center"===v.left&&(n+f>b[2]&&"left"===y.left?(n-=f,y.left="right"):n<b[0]&&"right"===y.left&&(n+=f,y.left="left"))),("element"===u||"both"===u)&&(o<b[1]&&"bottom"===y.top&&(o+=s,y.top="top"),o+s>b[3]&&"top"===y.top&&(o-=s,y.top="bottom")),("element"===h||"both"===h)&&(n<b[0]&&("right"===y.left?(n+=f,y.left="left"):"center"===y.left&&(n+=f/2,y.left="left")),n+f>b[2]&&("left"===y.left?(n-=f,y.left="right"):"center"===y.left&&(n-=f/2,y.left="right"))),"string"==typeof l?l=l.split(",").map(function(t){return t.trim()}):l===!0&&(l=["top","left","right","bottom"]),l=l||[];var w=[],C=[];o<b[1]&&(l.indexOf("top")>=0?(o=b[1],w.push("top")):C.push("top")),o+s>b[3]&&(l.indexOf("bottom")>=0?(o=b[3]-s,w.push("bottom")):C.push("bottom")),n<b[0]&&(l.indexOf("left")>=0?(n=b[0],w.push("left")):C.push("left")),n+f>b[2]&&(l.indexOf("right")>=0?(n=b[2]-f,w.push("right")):C.push("right")),w.length&&!function(){var t=void 0;t="undefined"!=typeof e.options.pinnedClass?e.options.pinnedClass:e.getClass("pinned"),g.push(t),w.forEach(function(e){g.push(t+"-"+e)})}(),C.length&&!function(){var t=void 0;t="undefined"!=typeof e.options.outOfBoundsClass?e.options.outOfBoundsClass:e.getClass("out-of-bounds"),g.push(t),C.forEach(function(e){g.push(t+"-"+e)})}(),(w.indexOf("left")>=0||w.indexOf("right")>=0)&&(y.left=v.left=!1),(w.indexOf("top")>=0||w.indexOf("bottom")>=0)&&(y.top=v.top=!1),(v.top!==i.top||v.left!==i.left||y.top!==e.attachment.top||y.left!==e.attachment.left)&&(e.updateAttachClasses(y,v),e.trigger("update",{attachment:y,targetAttachment:v}))}),M(function(){e.options.addTargetClasses!==!1&&m(e.target,g,c),m(e.element,g,c)}),{top:o,left:n}}});var j=x.Utils,a=j.getBounds,m=j.updateClasses,M=j.defer;x.modules.push({position:function(t){var e=this,o=t.top,n=t.left,i=this.cache("element-bounds",function(){return a(e.element)}),r=i.height,s=i.width,f=this.getTargetBounds(),l=o+r,h=n+s,u=[];o<=f.bottom&&l>=f.top&&["left","right"].forEach(function(t){var e=f[t];(e===n||e===h)&&u.push(t)}),n<=f.right&&h>=f.left&&["top","bottom"].forEach(function(t){var e=f[t];(e===o||e===l)&&u.push(t)});var d=[],p=[],c=["left","top","right","bottom"];return d.push(this.getClass("abutted")),c.forEach(function(t){d.push(e.getClass("abutted")+"-"+t)}),u.length&&p.push(this.getClass("abutted")),u.forEach(function(t){p.push(e.getClass("abutted")+"-"+t)}),M(function(){e.options.addTargetClasses!==!1&&m(e.target,p,d),m(e.element,p,d)}),!0}});var B=function(){function t(t,e){var o=[],n=!0,i=!1,r=void 0;try{for(var s,a=t[Symbol.iterator]();!(n=(s=a.next()).done)&&(o.push(s.value),!e||o.length!==e);n=!0);}catch(f){i=!0,r=f}finally{try{!n&&a["return"]&&a["return"]()}finally{if(i)throw r}}return o}return function(e,o){if(Array.isArray(e))return e;if(Symbol.iterator in Object(e))return t(e,o);throw new TypeError("Invalid attempt to destructure non-iterable instance")}}();return x.modules.push({position:function(t){var e=t.top,o=t.left;if(this.options.shift){var n=this.options.shift;"function"==typeof this.options.shift&&(n=this.options.shift.call(this,{top:e,left:o}));var i=void 0,r=void 0;if("string"==typeof n){n=n.split(" "),n[1]=n[1]||n[0];var s=n,a=B(s,2);i=a[0],r=a[1],i=parseFloat(i,10),r=parseFloat(r,10)}else i=n.top,r=n.left;return e+=i,o+=r,{top:e,left:o}}}}),I});
}
