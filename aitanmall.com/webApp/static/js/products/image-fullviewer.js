function imageFullViewerShow(imageScr){
    $(".image-fullview-wrapper .image-fullview .image").find("img").attr("src", imageScr);
    $(".image-fullview-wrapper").removeClass("masked");
    imageFullViewerShowing = true;
}
function imageFullViewerHide(){
    $(".image-fullview-wrapper .image-fullview .image").find("img").attr("src", false);
    $(".image-fullview-wrapper").addClass("masked");
    imageFullViewerShowing = false;
}
$(document).on("click", ".imgClickToView", function(){
    var imgToViewSrc = $(this).data("src");
    var imageFullViewerShowing = false;
    imageFullViewerShow(imgToViewSrc);
})
if(imageFullViewerShowing=true){
    $("#close-image-fullview-btn").on("click", function(){
        imageFullViewerHide();
    })
}