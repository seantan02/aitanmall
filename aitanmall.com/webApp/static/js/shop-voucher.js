function shopVoucherBtnInfoReady(voucherUnavailableMsg,voucherSelectReloadElement,voucherUseBtnText,voucherAppliedBtnText){
    $(document).on("click", ".voucherUnavailableBtn", function(){
        swal(voucherUnavailableMsg,{icon:"warning"});
    })
    
    $(document).on("click", ".voucherSelectBtn", function(){
        var allSelectBtn= $(this).closest(".shop-voucher-selection").find(".shop-voucher-select-button button");
        var thisSelectBtn = $(this);
        var thisModalWrapper = $(this).closest(".bottom-modal-wrapper");
        var thisSelectBtnOriText = $(this).text();
        var voucherBtmModalWrapper = $(this).closest(".bottom-modal-wrapper");
        var thisVoucherSelect = $(this).closest(".shop-voucher-select");
        var thisVoucherId = thisVoucherSelect.data("id");
        var thisVoucherCode = thisVoucherSelect.data("code");
        
        //check if request is running already
        if(voucherBtmModalWrapper.data("requestRunning")){
            return false;
        }
        thisSelectBtn.text("Loading...");
        //set to running if no request running
        voucherBtmModalWrapper.data("requestRunning", true);
        
        var fd = new FormData();
        fd.append("voucher_id", thisVoucherId);
        fd.append("voucher_code", thisVoucherCode);
        
        $.ajax({
            contentType: false,
            processData: false,
            type: "POST",
            data: fd,
            url: "/assets/tools/select_voucher.php",
            success: function(data){
                var result = JSON.parse(data);
                thisSelectBtn.text(thisSelectBtnOriText);
                
                $(voucherSelectReloadElement).each(function(i){
                    var endCount = $(voucherSelectReloadElement).length-1;
                    var thisVoucherReloadElement = $(this);
                    var thisVoucherReloadElementId = thisVoucherReloadElement.attr("id");
                    $("#"+thisVoucherReloadElementId).load(location.href+" #"+thisVoucherReloadElementId+">*");
                    
                    if(endCount == i){
                        voucherBtmModalWrapper.data("requestRunning", false);
                        
                        if(result.passcheck==1){
                            swal(result.msg,{icon:"success"}).then(function(){
                                allSelectBtn.each(function(i){
                                    if($(this).hasClass("voucherAppliedBtn")){
                                        $(this).addClass("voucherSelectBtn");
                                        $(this).removeClass("voucherAppliedBtn");
                                        $(this).text(voucherUseBtnText);
                                    }
                                    if(allSelectBtn.length==i+1){
                                        thisSelectBtn.addClass("voucherAppliedBtn");
                                        thisSelectBtn.text(voucherAppliedBtnText);
                                    }
                                })
                                hideBtmModal(thisModalWrapper,"#mask-overlay");
                            });
                        }else{
                            swal(result.msg,{icon:"warning"});
                        }
                    }
                })
            },error: function(){
                swal("ERROR",{icon:"warning"});
                thisSelectBtn.text(thisSelectBtnOriText);
            }
        })
    })
}