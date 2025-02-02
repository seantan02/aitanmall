$(document).ready(function(){
    // Add selected class to plan card on click
    function update_membership_option(element){
      var thisOption = $(element)
      var thisOptionId = thisOption.data("id")
      var closestParent = thisOption.closest(".membership")
      if(closestParent.find("input[name='option_id']").val(thisOptionId)){
        closestParent.find(".alert[data-target='membership_option']").addClass("d-none")
        closestParent.find('.membership_option').removeClass('red-border');
        closestParent.find('.membership_option').removeClass('selected');
        thisOption.addClass('selected');
        return true
      }
      return false
    }

    $('.membership_option').on('click', function() {
      update_membership_option(this)
    });

    $(document).on("click", ".activate-membership-btn",function(e){
        var thisBtn = $(this);
        //check if this form is processing
        if(thisBtn.data("requestRunning")){
            return false;
        }
        thisBtn.data("requestRunning", true);
        $("#membershipModal").modal("show")
        thisBtn.data("requestRunning", false);
    })

    //ajax for membership confirmation
    $(document).on("submit", "#membershipModal",function(e){
      e.preventDefault();
      var thisForm = $(this);
      //check if this form is processing
      if(thisForm.data("requestRunning")){
          return false;
      }
      thisForm.data("requestRunning", true);
      if (!$('.membership_option.selected').length) {
        thisForm.find(".alert[data-target='membership_option']").removeClass("d-none")
        $('.membership_option').addClass('red-border');
      }else{
        showLoader();
        
        var optionInput = thisForm.find("input[name='option_id']")
        var optionInputValue = optionInput.val()
        
        var fd = new FormData()
        fd.append("option_id", optionInputValue)
        fd.append("action", "user_activate_membership");
            
        $.ajax({
          contentType: false,
          processData: false,
          type: "POST",
          url: "/api/user_activate_membership",
          dataType: "json",
          data: fd,
        success: function(data){
            var result = data;
            if(result.passcheck == 1){
              swal({
                title: "Success",
                text: result.msg,
                icon: "success",
                buttons: true,
              })
              }else if(result.passcheck == 4){
                swal({
                  title: "Attention",
                  text: result.msg,
                  icon: "info",
                  buttons: true,
                }).then(function(){
                  window.location.href = result.redirect;
                })
              }
          },error:function(){
          }
        }).then(function(){
          thisForm.modal("hide")
          hideLoader();
        })
      }
      thisForm.data("requestRunning", false);
  })
})