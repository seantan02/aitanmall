function openCart(){
    $('#cart').addClass('open');
    openMaskOverlay();
}
function closeCart(){
    $('#cart').removeClass('open');
    closeMaskOverlay();
}
$(document).ready(function() {
    $(document).on("click", ".cartBtn", function() {
        openCart();
    });

    $(document).on("click", ".cartCloseBtn", function() {
        closeCart()
    });
});
$(document).ready(function(){
    $(document).on("click", ".add-to-cart", function() {
        var thisBtn = $(this)
        var targetId = thisBtn.data('target');
        var targetType = thisBtn.data('targettype');
        
        var isValid = true;
        $(targetId + " input").each(function(){
            var thisInputDataName = $(this).data("name");
            var thisInputDataClass = $(this).data("classname");
            var thisInputDataType = $(this).data("type");
            if(typeof thisInputDataClass !== 'undefined' & thisInputDataClass != ""){
                var thisInputWrapper = $(targetId + " ."+thisInputDataClass);
                if(thisInputDataType == "modal"){
                    //nothing
                }else{
                    thisInputWrapper.removeClass("red-border");
                    thisInputWrapper.find(".reminder").remove();
                }
            }
            if($(this).val() == ""){
                inValidReasonMessage = thisInputDataName+" was not choosen.";
                alert(inValidReasonMessage);
                var thisInputWrapper = $(targetId + " ."+thisInputDataClass);
                if(thisInputDataType == "modal"){
                    thisInputWrapper.closest("modal").modal("show");
                    isValid = false;
                }else{
                    $('html, body').animate({
                        scrollTop: thisInputWrapper.offset().top
                    }, 1000);
                    thisInputWrapper.addClass("red-border");
                    thisInputWrapper.prepend("<span class='reminder'>"+inValidReasonMessage+"</span>");
                    isValid = false;
                }
                
                return false;
            }
        });
        $(targetId + " select").each(function(){
            var thisInputDataName = $(this).data("name");
            var thisInputDataClass = $(this).data("classname");
            if(typeof thisInputDataClass !== 'undefined' & thisInputDataClass != ""){
                var thisInputWrapper = $(targetId + " ."+thisInputDataClass);
                thisInputWrapper.removeClass("red-border");
                thisInputWrapper.find(".reminder").remove();
            }
            if($(this).find("option:selected").val() == ""){
                inValidReasonMessage = thisInputDataName+" was not choosen.";
                alert(inValidReasonMessage);
                $('html, body').animate({
                    scrollTop: thisInputWrapper.offset().top
                }, 1000);
                thisInputWrapper.addClass("red-border");
                thisInputWrapper.prepend("<span class='reminder'>"+inValidReasonMessage+"</span>");
                isValid = false;
                return false;
            }
        });

        var formData = new FormData($(targetId)[0]);
        if(thisBtn.data("requestRunning")){
            inValidReasonMessage = "Request is being processed";
            alert(inValidReasonMessage);
            isValid = false;
        }

        if(isValid != true){
            return false;
        }

        thisBtn.data("requestRunning", true);
        showLoader();
        $.ajax({
            url: '/api/user_add_to_cart',
            type: 'POST',
            data: formData,
            processData: false,  // Important!
            contentType: false,  // Important!
            dataType: "json",
            success: function(result) {
                if(result.passcheck == 1){
                    $('#cart').load(location.href+" #cart>*");
                    closeCart();
                    openCart();
                }else if(result.passcheck == 4){
                    alert(result.msg);
                    window.location.href = result.redirect;
                }
            },
            error: function(error) {
                console.log(error);
                // handle error logic here
            },
            complete: function () {
                thisBtn.data("requestRunning", false);
                hideLoader();
            }
        }).then(function(){
            fbq('track', 'AddToCart');
            ttq.track('AddToCart');
            if(targetType=="recommendedModal"){
                $('#productRecommendModal').modal("hide");
            }else{
                if ($('#productRecommendModal').length) {
                    $('#productRecommendModal').modal('show');
                }
            }
        });
    });

    $(document).on("click", ".increase-cart-quantity-btn", function() {
        var thisBtn = $(this);
        var cartItemId = thisBtn.data('id');
        var cartItemDiv = thisBtn.closest(".cart-content")
        var thisCartItemId = cartItemDiv.attr("id")
        var fd = new FormData();
        
        fd.append("cart_item_id", cartItemId)
        fd.append("quantity", 1)
        fd.append("action", "increaseCartItemQuantity")

        if(thisBtn.data("requestRunning")){
            isValid = false;
            inValidReasonMessage = "Request is being processed";
        }
        showLoader();
        thisBtn.data("requestRunning", true);
        $.ajax({
            url: '/api/user_update_cart_item',
            type: 'POST',
            data: fd,
            processData: false,  // Important!
            contentType: false,  // Important!
            dataType: "json",
            success: function(result) {
                if(result.passcheck == 1){
                    $('#'+thisCartItemId).load(location.href+" #"+thisCartItemId+">*");
                }else if(result.passcheck == 4){
                    alert(result.msg);
                    window.location.href = result.redirect;
                }
            },
            error: function(error) {
                alert(error);
            },
            complete: function () {
                fbq('track', 'Increase Cart Item');
                thisBtn.data("requestRunning", false);
                hideLoader();
            }
        });
    });
    $(document).on("click", ".decrease-cart-quantity-btn", function() {
        var thisBtn = $(this);
        var cartItemId = thisBtn.data('id');
        var cartItemDiv = thisBtn.closest(".cart-content")
        var thisCartItemId = cartItemDiv.attr("id")
        var fd = new FormData();
        
        fd.append("cart_item_id", cartItemId)
        fd.append("quantity", 1)
        fd.append("action", "decreaseCartItemQuantity")

        if(thisBtn.data("requestRunning")){
            isValid = false;
            inValidReasonMessage = "Request is being processed";
        }
        showLoader();
        thisBtn.data("requestRunning", true);
        $.ajax({
            url: '/api/user_update_cart_item',
            type: 'POST',
            data: fd,
            processData: false,  // Important!
            contentType: false,  // Important!
            dataType: "json",
            success: function(result) {
                if(result.passcheck == 1){
                    $('#'+thisCartItemId).load(location.href+" #"+thisCartItemId+">*");
                }else if(result.passcheck == 4){
                    alert(result.msg);
                    window.location.href = result.redirect;
                }
            },
            error: function(error) {
                alert(error);
            },
            complete: function () {
                fbq('track', 'Decrease Cart Item');
                thisBtn.data("requestRunning", false);
                hideLoader();
            }
        });
    });

    $(document).on("click", ".remove-cart-quantity-btn", function() {
        var thisBtn = $(this);
        var cartItemId = thisBtn.data('id');
        var cartItemDiv = thisBtn.closest(".cart-content")
        var thisCartItemId = cartItemDiv.attr("id")
        var thisCartItemBody = thisBtn.closest(".cart-item-body")
        var quantity = thisCartItemBody.find(".cart-item-quantity").val()
        var fd = new FormData();
        
        fd.append("cart_item_id", cartItemId)
        fd.append("quantity", quantity)
        fd.append("action", "decreaseCartItemQuantity")

        if(thisBtn.data("requestRunning")){
            isValid = false;
            inValidReasonMessage = "Request is being processed";
        }
        showLoader();
        thisBtn.data("requestRunning", true);
        $.ajax({
            url: '/api/user_update_cart_item',
            type: 'POST',
            data: fd,
            processData: false,  // Important!
            contentType: false,  // Important!
            dataType: "json",
            success: function(result) {
                if(result.passcheck == 1){
                    $('#'+thisCartItemId).load(location.href+" #"+thisCartItemId+">*");
                }else if(result.passcheck == 4){
                    alert(result.msg);
                    window.location.href = result.redirect;
                }
            },
            error: function(error) {
                alert(error);
            },
            complete: function () {
                thisBtn.data("requestRunning", false);
                hideLoader();
            }
        });
    });
})