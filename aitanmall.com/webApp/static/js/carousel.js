//carousel script
//Set carousel image source depending on window size
$(document).ready(function(){
    carousel = $(".carousel")
    carouselItems = carousel.find(".carousel-item")
    windowScreenWidth = $(window).width()
    if(windowScreenWidth>599 && windowScreenWidth <=899){
        carouselItems.each(function(){
        thisCarousel = $(this)
        thisCarouselImg = $(this).find("img")
        carouselMidSizeImgSrc = thisCarouselImg.data("srcmid")
        if(thisCarousel.hasClass("active")){
          thisCarouselImg.attr("src",carouselMidSizeImgSrc)
        }else{
          thisCarouselImg.attr("data-src",carouselMidSizeImgSrc)
        }
        })
    }else{
        if(windowScreenWidth>899){
            carouselItems.each(function(){
                thisCarousel = $(this)
                thisCarouselImg = $(this).find("img")
                carouselLargeSizeImgSrc = thisCarouselImg.data("scrlarge")
                if(thisCarousel.hasClass("active")){
                    thisCarouselImg.attr("src",carouselLargeSizeImgSrc)
                }else{
                    thisCarouselImg.attr("data-src",carouselLargeSizeImgSrc)
                }
            })
        }
    }
})
//lazyloading carousel images
$(document).ready(function() {     
    $('#promotionsCarousel').on('slide.bs.carousel', function (e) {
        carouselImage = $(e.relatedTarget).find("img")
        var url = carouselImage.data("src"); 
        carouselImage.attr("src", url);
    });
});