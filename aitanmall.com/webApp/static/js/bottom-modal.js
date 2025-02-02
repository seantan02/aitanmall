function showBtmModal(targetElement,maskElement){
    $(targetElement).addClass("active");
    if(!$(maskElement).hasClass("mask_opened")){
        $(maskElement).addClass("mask_opened");
        $(maskElement).addClass("btmModalMask");
    }
}
function hideBtmModal(targetElement,maskElement){
    $(targetElement).removeClass("active");
    if($(maskElement).hasClass("btmModalMask")){
        $(maskElement).removeClass("mask_opened");
        $(maskElement).removeClass("btmModalMask");
    }
}
$(document).on("click", ".triggerBtmModal", function(){
    var thisTriggerTarget = $(this).data("target");
    var maskId="#mask-overlay";
    if(!$(thisTriggerTarget).hasClass("active")){
        showBtmModal(thisTriggerTarget,maskId);
    }
})
$(document).on("click", ".btmModalMask", function(){
    var thisTriggerTarget = ".bottom-modal-wrapper.active";
    hideBtmModal(thisTriggerTarget,this);
})
$(document).on("click", ".btmModalCloseBtn", function(){
    var thisTriggerTarget = $(this).closest(".bottom-modal-wrapper");
    if($(thisTriggerTarget).hasClass("active")){
        hideBtmModal(thisTriggerTarget,".btmModalMask")
    }
})