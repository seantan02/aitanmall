function attributeAction(initialTotal){
    $('.box-option').click(function () {
        var group = $(this).data("group")
        var inputTarget = $(this).data("aim")
        var neightbor = $(this).data("neightbor")
        var price = $(this).data("price");
        var priceNum = parseFloat(price*100);
        $(".box-option"+group).css({"border":"1px solid rgba(128, 128, 128, 0.6)","pointer-events":"initial"});
        $(this).css({"border":"2px solid blue","pointer-events":"none"});
        $("#"+inputTarget).val($(this).data("value"))
        if($("#"+inputTarget).val()!=''){
            $("#attribute"+neightbor).removeClass("masked")
            if( $("#attribute"+neightbor).removeClass("masked").length==0){
                $("#payment-wrapper").removeClass("masked")
            }
            calculateNewTotal(initialTotal,priceNum);
        }
    });
}
function calculateNewTotal(initialTotal,priceNum){
    var initialTotalNum = parseFloat(initialTotal*100);
    grandTotalNumNew=((initialTotalNum+priceNum)/100).toFixed(2);
    $("#grandtotal").text(grandTotalNumNew);
}