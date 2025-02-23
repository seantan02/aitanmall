function reviewerPhotoFileReady(e, t) {
    $(document).on("change", "#reviewerPhotoFile", function (i) {
        var n = $(this),
            a = $("#reviewerPhotoFileCustomDisplay"),
            o = n[0].files[0].type,
            s = n[0].files[0].size,
            r = n[0].files[0].name;
        if (s > 5e6) {
            swal(e, { icon: "warning" }).then(function () {
                i.preventDefault(), (n[0].value = null);
            });
            var c = 2;
        } else c = 1;
        if (["image/jpg", "image/jpeg", "image/png"].includes(o)) var l = 1;
        else {
            swal(t, { icon: "warning" }), i.preventDefault(), (n[0].value = null);
            l = 2;
        }
        1 == l && 1 == c && a.text(r);
    });
}
function writeReviewAjaxReady(e) {
    $(document).ready(function () {
        $("#writereview-Modal").on("submit", function (t) {
            t.preventDefault();
            var i = $(this),
                n = new FormData(i[0]);
            n.append("submit", "writeReview"), n.append("productId", e);
            var a = i.find("button[type='submit']"),
                o = a.text();
            a.attr("disabled", !0),
                a.css({ opacity: "0.5", "pointer-events": "none" }),
                a.text("Loading..."),
                $.ajax({
                    contentType: !1,
                    processData: !1,
                    type: "POST",
                    url: "/assets/tools/write_product_review.php",
                    data: n,
                    success: function (e) {
                        var t = JSON.parse(e);
                        1 == t.passcheck
                            ? swal(t.msg, { icon: "success" }).then(function () {
                                  i.modal("hide");
                              })
                            : swal(t.msg, { icon: "warning" }),
                            a.attr("disabled", !1),
                            a.css({ opacity: "1", "pointer-events": "initial" }),
                            a.text(o);
                    },
                    error: function () {
                        swal("ERROR", { icon: "warning" }).then(function () {
                            a.attr("disabled", !1), a.css({ opacity: "1", "pointer-events": "initial" }), a.text(o);
                        });
                    },
                });
        });
    });
}
function loadPrdReviewAjaxReady(e) {
    $(document).ready(function () {
        var t = 3;
        var reviewImgHeightSelected = $(".product-review-board").find(".board").width();
        $("#showMoreReviewBtn").on("click", function (i) {
            var n = $(this),
                a = n.text();
            n.attr("disabled", !0),
                n.css({ opacity: "0.5", "pointer-events": "none" }),
                n.text("Loading..."),
                (t += 3),
                $("#reviewContainer").load("/assets/tools/load_product_review.php", { prdReviewCount: t, prdId: e, reviewImgHeight: reviewImgHeightSelected }, function (e,status,xhr) {
                    n.attr("disabled", !1), n.css({ opacity: "1", "pointer-events": "initial" }), n.text(a);
                });
        });
    });
}
$(document).on("change", "input[name='reviewPrdImg']", function(e){
    var uploadedFile=$(this);
    var customUploadFileInputOriText = $("#customReviewPrdImgInput").text();
    var uploadedFileName=$(this)[0].files[0].name;
    $("#customReviewPrdImgInput").text(uploadedFileName);
    var uploadedFileType= uploadedFile[0].files[0].type;
    var uploadedFileSize=$(this)[0].files[0].size;
    
    if(uploadedFile[0].files.length<=1){
        const validImageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/pdf'];
        if(validImageTypes.includes(uploadedFileType)){
            //dd
        }else{
            swal("Only jpeg, jpg, png, and pdf are accepted.",{
                icon:"warning",
            }).then(function(){
                uploadedFile[0].value=null;
                $("#customReviewPrdImgInput").text("No File");
            })
        }
        if(uploadedFileSize<=7000000){
            //dd
        }else{
            swal("Max 7MB",{
                icon:"warning",
            }).then(function(){
                uploadedFile[0].value=null;
                $("#customReviewPrdImgInput").text("No File");
            })
        }
    }else{
        swal("Maximum 1 File",{
            icon:"warning",
        }).then(function(){
            uploadedFile[0].value=null;
            $("#customReviewPrdImgInput").text("No File");
        })
    }
})