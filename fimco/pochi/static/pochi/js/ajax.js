/**
 * Created by Arthur on 9/6/2017.
 */

$(".rates a").click(function(){
    var id = $(this).attr("data-name");
    if(id === "interests"){
        $(".content").load("interests #all");
    }else{
        $(".content").load("interests #"+id+"Table");
    }
});

$('tr[data-href]').on("click", function() {
    document.location = $(this).data('href');
});