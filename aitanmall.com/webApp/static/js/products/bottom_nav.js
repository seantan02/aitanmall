$(window).on("scroll", function(e){
    if($(window).scrollTop() > 100){
        $("#bottom-nav").removeClass("masked");
    }else{
        $("#bottom-nav").addClass("masked");
    }
})