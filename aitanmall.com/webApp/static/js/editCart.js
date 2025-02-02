$(document).on("click", ".editCartPrdBtn", function(){
    var thisCartItem = $(this).closest(".cart-item");
    var editPrdCartAction = $(this).data("action");
    var editPrdCartPrdId = $(this).data("prdid");
    var editPrdCartPrdVarId = $(this).data("prdvarid");
    //check if ther's request already
    if(thisCartItem.data("requestRunning")){
        return false;
    }
    //set it to true
    thisCartItem.data("requestRunning", true);
    
    if(editPrdCartAction === "delete" || editPrdCartAction === "increment" || editPrdCartAction === "decrement"){
        var fd = new FormData();
        fd.append("submit", "editCart");
        fd.append("action", editPrdCartAction);
        fd.append("prdId", editPrdCartPrdId);
        fd.append("prdVarId", editPrdCartPrdVarId);
        
        
        var deleteCartPrdBtn = $(this);
        deleteCartPrdBtn.attr("disabled", true);
        deleteCartPrdBtn.css({"opacity":"0.5", "pointer-events":"none"});
        
        $.ajax({
            contentType:false,
            processData:false,
            type:"POST",
            url:"/assets/under_developing_tools/edit-cart.php",
            data:fd,
            success:function(data){
                thisCartItem.data("requestRunning", false);
                var result = JSON.parse(data);
                if(result.passcheck==1){
                    $(result.reload).load(location.href+" "+result.reload+">*");
                    $("#cartBody .cart-end #cart-summary").load(location.href+" #cartBody .cart-end #cart-summary>*");
                    if(result.msg!="NONE"){
                        swal(result.msg,{
                            icon:"success",
                        }).then(function(){
                            deleteCartPrdBtn.attr("disabled", false);
                            deleteCartPrdBtn.css({"opacity":"1", "pointer-events":"initial"});
                        })
                    }else{
                        deleteCartPrdBtn.attr("disabled", false);
                        deleteCartPrdBtn.css({"opacity":"1", "pointer-events":"initial"});
                    }
                }else{
                    swal("ERROR",{
                        icon:"warning",
                    }).then(function(){
                        deleteCartPrdBtn.attr("disabled", false);
                        deleteCartPrdBtn.css({"opacity":"1", "pointer-events":"initial"});
                    })
                }
            },
            error: function(){
                thisCartItem.data("requestRunning", false);
                deleteCartPrdBtn.attr("disabled", false);
                deleteCartPrdBtn.css({"opacity":"1", "pointer-events":"initial"});
            }
        })
    }else{
        thisCartItem.data("requestRunning", false);
    }
})