$('.box-option').click(function () {
    var group = $(this).data("group")
    var inputTarget = $(this).data("aim")
    var neightbor = $(this).data("neightbor")
    $(".box-option"+group).css("border","1px solid rgba(128, 128, 128, 0.6)")
    $(this).css("border","2px solid blue")
    $("#"+inputTarget).val($(this).data("value"))
    if($("#"+inputTarget).val()!=''){
        $("#attribute"+neightbor).removeClass("masked")
        if( $("#attribute"+neightbor).removeClass("masked").length==0){
            $("#payment-wrapper").removeClass("masked")
        }
        $('#totalpart'+neightbor).text(" +("+$(this).data("price")+")")
    }
});
