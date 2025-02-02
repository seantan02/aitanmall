var variationModalShowing = false;
function showVariationModal(){
    $("#variation-modal-wrapper").addClass("active");
    $("#mask-overlay").addClass("mask_opened");
    variationModalShowing = true;
}
function hideVariationModal(){
    $("#variation-modal-wrapper").removeClass("active");
    $("#mask-overlay").removeClass("mask_opened");
    variationModalShowing = false;
}
function updateVariationOptionImg(imgSrc){
    $(".variation-modal .preview .image").find("img").data("src", imgSrc);
    $(".variation-modal .preview .image").find("img").attr("src", imgSrc);
    $(".variation-modal .preview .image").css({"background-color":"black"});
    $(".variation-modal .preview .image").find("img").hide();
}
function updateVariationOptionPrice(displayPriceValue, priceValue){
    $(".variation-modal .preview .display-price").find("span").text(displayPriceValue);
    $(".variation-modal .preview .price").find("span").text(priceValue);
}
function updateVariationFormInputValue(inputValue){
    $("#addToCartForm").find("input[name='prd_var_id']").val(inputValue);
}

$(document).ready(function(){
    if(variationModalShowing=true){
        $("#mask-overlay").on("click", function(){
            hideVariationModal();
        })
    }
    $(document).on("click", "#close-variation-modal-button", function(){
        hideVariationModal();
    })
    $(".show-variation-modal-btn").on("click", function(){
        showVariationModal();
    })
    const variationOption = $(".variation-modal").find(".option");
    
    variationOption.on("click", function(){
        var variationModalReminder = $(this).closest(".variation-modal").find(".variation-modal-reminder");
        if(!variationModalReminder.hasClass("hide")){
            variationModalReminder.addClass("scaleToZero");
        }
        
        variationOption.removeClass("selected");
        variationOption.removeClass("redlight");
        $(this).addClass("selected");
        var variationOptionImgSrc = $(this).data("src");
        var variationOptionDisplayPrice = $(this).data("display-price");
        var variationOptionPrice = $(this).data("price");
        var variationOptionId = $(this).data("id");
        updateVariationOptionImg(variationOptionImgSrc);
        updateVariationOptionPrice(variationOptionDisplayPrice,variationOptionPrice);
        updateVariationFormInputValue(variationOptionId);
    })
    $(document).on("click", "#variation-modal-wrapper .add-to-cart button", function(){
        var thisAddToCartBtn = $(this);
        var variationModalHeader = thisAddToCartBtn.closest(".variation-modal").find(".variation-modal-reminder");
        var variationInput = thisAddToCartBtn.closest(".variation-modal").find("#addToCartForm input[name='prd_var_id']");
        var variationChoices = thisAddToCartBtn.closest(".variation-modal").find(".content .option");
        
        if(variationInput.val()==""){
            variationChoices.addClass("redlight");
            variationModalHeader.removeClass("scaleToZero");
        }else{
            return true;
        }
    })
    $(".variation-modal .preview .image").find("img").on("load", function(){
        $(".variation-modal .preview .image").css({"background-color":"none"});
        $(".variation-modal .preview .image").find("img").show();
    });
})