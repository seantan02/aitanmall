$(document).on("click", ".customBtnToTriggerBtn", function(e){
  var realBtnForTrigger=$(this).data("target");
  $(realBtnForTrigger).click();
})
function onlyNumber(evt){
  var input=String.fromCharCode(evt.which);
  if(!(/[0-9]/.test(input))){
      evt.preventDefault();
  }
}
function selectProductOption(element){
  var thisOptionBox = $(element)
  var thisOptionData = thisOptionBox.data("data")
  var optionBoxWrapper = thisOptionBox.closest(".option-box-wrapper")
  var thisOptionTarget = thisOptionBox.data("target")
  optionBoxWrapper.find(".option-box").removeClass('selected');
  thisOptionBox.addClass('selected');
  
  if(thisOptionTarget != ""){
    $(thisOptionTarget).val(thisOptionData)
  }else{
    optionBoxWrapper.find("input").val(thisOptionData)
  }
  
}
/*script for mask overlay*/
function maskOverlayOpened(){
var maskOverlay = $("#mask-overlay")
if(maskOverlay.hasClass("hide")){
  return false;
}
return true;
}

function openMaskOverlay(){
var returnStatus = true
var maskOverlay = $("#mask-overlay")
maskOverlay.removeClass("hide");
return returnStatus
}

function closeMaskOverlay(){
var returnStatus = true
var maskOverlay = $("#mask-overlay")
maskOverlay.addClass("hide");
return returnStatus
}

/* Script for loader */
function showLoader(){
lodaerHTML = '<div class="loader-wrapper pre-loader" id="loader-wrapper">\
<div class="loader">Loading...</div>\
<div class="loader-sub"><span>Our Webpage Workers Are Working Hard...</span></div>\
</div>'
$("body .display").prepend(lodaerHTML)
if(!$("#pagebody").hasClass("hide")){
    $("#pagebody").addClass("hide");
}
if(!maskOverlayOpened()){
  openMaskOverlay();
}
}

function hideLoader(){
$("#loader-wrapper").remove()
if($("#pagebody").hasClass("hide")){
    $("#pagebody").removeClass("hide");
}
if(maskOverlayOpened()){
  closeMaskOverlay();
}

}
$(document).ready(function(){
hideLoader();
//Adjust margin top for perfect display
  navbar = $("#nav-wrapper")
  navbarTotalHeight = navbar.outerHeight(true)
  $(".after-nav").css({"margin-top":navbarTotalHeight+"px"})
  //Script to direct user to #
  var hash = window.location.hash;
  var navbarHeight = $("#nav-wrapper").height()
  if (hash) {
    var element = $(hash);
    if (element.length) {
      $('html, body').animate({
      scrollTop: element.offset().top-navbarHeight-20
      }, 800, function(){
      window.location.hash = hash;
      $(hash).addClass('red-border');
      });
    }
}
})