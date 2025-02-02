$(".thumnail").click(function (){
    if($(".thumnail-active").length>0){
        $(".thumnail-active").removeClass("thumnail-active")
    }
    $(this).addClass("thumnail-active")
    $("#featured-image").attr("src",$(this).attr("src"))
})