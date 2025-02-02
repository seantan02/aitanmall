//script for the announcement bar
function closeAnnouncementBar(element){
    elementId = element.attr("id")
    if(elementId == "announcement-close-btn"){
      element.closest(".announement-wrapper").remove()
    }else{
      return("Element ID not announcement-close-btn")
    }
  }
$(document).ready(function(){
    announcementBar = $(".announement-wrapper")
    announcementBarCloseBtn = announcementBar.find("#announcement-close-btn")

    $(announcementBarCloseBtn).on("click",function(){
      closeAnnouncementBar($(this))
    })
})