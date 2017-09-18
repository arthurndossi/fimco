// $("#vision").css("position", "relative");
$( document ).ready(function() {
    hipster_cards.fitBackgroundForCards();

    $('#fullpage').fullpage({
        anchors: ['mission', 'vision', 'values', 'people', 'investment'],
        sectionsColor: ['#003366', '#002952', '#001f3d', '#001429', '#000a14'],
        navigation: true,
        navigationPosition: 'right',
        navigationTooltips: ['Mission', 'Vision', 'Values', 'People', 'Investment'],
        scrollBar: true
    });
    
    $('.single-item').slick();
    
    $('.multiple-items').slick({
        infinite: true,
        slidesToShow: 4,
        slidesToScroll: 4,
        centerPadding: '60px',
        responsive: [
            {
              breakpoint: 1024,
              settings: {
                slidesToShow: 3,
                slidesToScroll: 3,
                infinite: true,
                dots: true
              }
            },
            {
              breakpoint: 600,
              settings: {
                slidesToShow: 2,
                slidesToScroll: 2
              }
            },
            {
              breakpoint: 480,
              settings: {
                slidesToShow: 1,
                slidesToScroll: 1
              }
            }
        ]
    });
});

hipster_cards = {
    misc:{
        navbar_menu_visible: 0
    },
    
    fitBackgroundForCards: function(){
        $('[data-background="image"]').each(function(){
            $this = $(this);
                        
            background_src = $this.data("src");                                
            
            if(background_src != "undefined"){                
                new_css = {
                    "background-image": "url('" + background_src + "')",
                    "background-position": "center center",
                    "background-size": "cover"
                };
                
                $this.css(new_css);                
            }              
        });
        
        $('.card .header img').each(function(){
            $card = $(this).parent().parent();
            $header = $(this).parent();
                        
            background_src = $(this).attr("src");                                
            
            if(background_src != "undefined"){                
                new_css = {
                    "background-image": "url('" + background_src + "')",
                    "background-position": "center center",
                    "background-size": "cover"
                };
                
                $header.css(new_css);                
            }              
        });
        
    },   
}