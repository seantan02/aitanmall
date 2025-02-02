$('.prd-des-sign').click(function () {
    var prdSignAction = $(this).data("action");
    var prdSignActionSubs = $(this).data("subs");
    var prdSignActionTarget = $(this).data("target");
    const currentSign = $(this);
    signActionTriggered(prdSignAction,prdSignActionSubs,currentSign,prdSignActionTarget);
    console.log(currentSign);
});
function signActionTriggered(action,prdSignActionSubs,currentSign,prdSignActionTarget) {
    if(action == "show"){
        showPrdDes(prdSignActionTarget);
        $(currentSign).addClass("masked");
        $(".prd-des-"+prdSignActionSubs+prdSignActionTarget).removeClass("masked");
    }
    if(action == "hide"){
        hidePrdDes(prdSignActionTarget);
        $(currentSign).addClass("masked");
        $(".prd-des-"+prdSignActionSubs+prdSignActionTarget).removeClass("masked");
    }
}
function hidePrdDes(target){
    $("#prd-des-body"+target).addClass('masked');
}
function showPrdDes(target){
    $("#prd-des-body"+target).removeClass('masked');
}