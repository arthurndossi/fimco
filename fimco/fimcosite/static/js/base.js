/**
 * Created by Arthur on 9/25/2017.
 */
jQuery(document).ready(function() {
    if(jQuery("#rev_slider_72_1").revolution == undefined){
        revslider_showDoubleJqueryError("#rev_slider_72_1");
    }else{
        revapi66 = jQuery("#rev_slider_72_1").show().revolution({
            sliderType:"standard",
            jsFileLocation:plugin_path + "slider.revolution.v5/js/",
            sliderLayout:"auto",
            dottedOverlay:"none",
            delay:3000,
            navigation: {
                keyboardNavigation:"on",
                keyboard_direction: "horizontal",
                mouseScrollNavigation:"on",
                onHoverStop:"off",
                arrows: {
                    enable: true,
                    hide_onmobile: true
                },
                touch:{
                    touchenabled:"on",
                    touchOnDesktop:"on",
                    swipe_threshold: 75,
                    swipe_min_touches: 1,
                    swipe_direction: "horizontal",
                    drag_block_vertical: false
                },
                bullets: {
                    enable:true,
                    hide_onmobile:true,
                    // hide_under:1024,
                    // style:"hephaistos",
                    hide_onleave:false,
                    direction:"horizontal",
                    h_align:"center",
                    v_align:"bottom",
                    h_offset:0,
                    v_offset:20,
                    space:5,
                    tmp:''
                }
            },

            responsiveLevels:[1240,1024,778,480],
            gridwidth:[1400,1240,778,480],
            gridheight:[868,768,960,720],
            lazyType:"none",
            shadow:0,
            spinner:"off",
            stopLoop:"on",
            stopAfterLoops:0,
            stopAtSlide:1,
            shuffle:"off",
            autoHeight:"off",
            fullScreenAlignForce:"off",
            fullScreenOffsetContainer: jQuery("#header").hasClass('transparent') || jQuery("#header").hasClass('translucent') ? null : "#header",
            fullScreenOffset: "",
            disableProgressBar:"on",
            hideThumbsOnMobile:"off",
            hideSliderAtLimit:0,
            hideCaptionAtLimit:0,
            hideAllCaptionAtLilmit:0,
            debugMode:false,
            fallbacks: {
                simplifyAll:"off",
                nextSlideOnWindowFocus:"off",
                disableFocusListener:false,
            }
        });
    }
});