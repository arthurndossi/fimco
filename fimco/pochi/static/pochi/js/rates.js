/**
 * Created by Arthur on 9/8/2017.
 */
$(document).ready(function () {
   // Table Carousel

    $('button.next-table').click( function(){
        var currentone = $('.responsive-tables .active');
        var currenttwo = $('.responsive-tables .activetwo');
        var next = $('.responsive-tables .activetwo + [class*="little"]');
        var last = $('.responsive-tables .last');
        next.addClass('activetwo');
        currentone.removeClass('active').addClass('last');
        currenttwo.removeClass('activetwo').addClass('active');
        last.removeClass('last');

        var echonext = next.attr('class');


        if( echonext === undefined ){
            $('.little1').addClass('activetwo');
        }

    });

    $('button.prev-table').click( function(){
        var currentone = $('.responsive-tables .active');
        var currenttwo = $('.responsive-tables .activetwo');
        var prev = $('.responsive-tables .last').prev('[class*="little"]');
        var last = $('.responsive-tables .last');
        prev.addClass('last');
        currentone.removeClass('active').addClass('activetwo');
        last.removeClass('last').addClass('active');
        currenttwo.removeClass('activetwo');

        //alert(prev.attr('class'));

        if( prev.attr('class') === undefined ){
            $('.responsive-tables .little9').addClass('last');
        }

    });
});