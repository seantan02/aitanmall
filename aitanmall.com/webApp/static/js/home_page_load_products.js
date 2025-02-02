$(document).ready(function(){
    $(document).on("click", ".load-more-button", function(){
        var thisBtn = $(this);
        var thisBtnTarget = thisBtn.data("target");
        var thisBtnType = thisBtn.data("type")
        var thisBtnLastId = thisBtn.attr('data-lastid');

        var fd = new FormData();
        
        fd.append("action", "load_more_product")
        fd.append("last_product_index_id", thisBtnLastId)

        if(thisBtn.data("requestRunning")){
            return false;
        }
        thisBtn.data("requestRunning", true);
        $.ajax({
            url: '/api/load_more_'+thisBtnType,
            type: 'POST',
            data: fd,
            processData: false,  // Important!
            contentType: false,  // Important!
            dataType: "json",
            success: function(result) {
              if (Array.isArray(result)) { // check if products is an array
                for (var i = 0; i < result.length; i++) {
                  if (typeof result[i] === 'object' && result[i] !== null && !Array.isArray(result[i])) { // check if each item is an object
                    var product = result[i];
                    //Handle the product
                    //Clone the html
                    var cloneHTML = thisBtn.closest(".product-container").find(".product:eq(0)").clone();
                    cloneHTML.find("a").attr("href", 'products/'+product.merchant_id+'/'+product.prd_id);
                    cloneHTML.find("img").attr("src", 'https://tmpmc.aitanmall.com/static/assets/merchant/'+product.merchant_id+'/product/'+product.prd_id+'/'+product.prd_image);
                    //Update price if there's price
                    if(cloneHTML.find(".product-price").length > 0){
                      cloneHTML.find(".product-price").text("Rm"+product.prd_offer_price)
                    }
                    if(cloneHTML.find(".product-name").length > 0){
                      cloneHTML.find(".product-name").text(product.prd_name)
                    }
                    //Update price if there's price
                    if(cloneHTML.find(".product-discount-percentage").length > 0){
                      var productDiscountPercentage = 0.00;
                      var productOriPrice = parseFloat(product.prd_price);
                      var productOfferPrice = parseFloat(product.prd_offer_price);
                      productDiscountPercentage = (productOriPrice-productOfferPrice)/productOriPrice * 100
                      var productDiscountPercentage = Math.round(productDiscountPercentage);
                      cloneHTML.find(".product-discount-percentage").text("Discount "+productDiscountPercentage+"% !")
                    }
                    $(thisBtnTarget).find(".products").append(cloneHTML);

                    if (i == result.length - 1) {
                      thisBtn.attr('data-lastid', product.id);
                    }
                  } else {
                    thisBtn.remove();
                  }
                }
                //Remove show more button if there's no more
                if(result.length == 0){
                  thisBtn.remove();
                }
              } else {
                alert(result.msg);
              }
            },
            error: function(error) {
                alert(error);
            }
        }).then(function(){
          thisBtn.data("requestRunning", false);
        });
    })
})