$(document).ready(function(){
    /* scrpit for address */
    /* adding address */
    $(document).on("submit", "#addAddressForm",function(e){
        e.preventDefault()
        showLoader();
  
        var thisForm = $(this)
        var thisFormBtn = thisForm.find("button[name='submit']")
        //check if this form is processing
        if(thisFormBtn.data("requestRunning")){
            return false;
        }
        thisFormBtn.data("requestRunning", true);
          
        //get values of inputs
        var streetInput = thisForm.find("input[name='street']")
        var unitNumberInput = thisForm.find("input[name='unitNumber']")
        var cityInput = thisForm.find("input[name='city']")
        var stateInput = thisForm.find("select[name='state']")
        var zipInput = thisForm.find("input[name='zip']")
        var countryInput = thisForm.find("select[name='country']")
          
        var streetInputValue = streetInput.val()
        var unitNumberInputValue = unitNumberInput.val()
        var cityInputValue = cityInput.val()
        var stateInputValue = stateInput.val()
        var zipInputValue = zipInput.val()
        var countryInputValue = countryInput.val()
  
        var fd = new FormData()
        fd.append("street", streetInputValue);
        fd.append("unitNumber", unitNumberInputValue);
        fd.append("city", cityInputValue);
        fd.append("state", stateInputValue);
        fd.append("zip", zipInputValue);
        fd.append("country", countryInputValue);
  
        $.ajax({
          contentType: false,
          processData: false,
          type: "POST",
          url: "/api/user_add_address",
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
                }).then(function(){
                  $("#addresses").load(location.href + " #addresses>*", "");
                  thisFormBtn.data("requestRunning", false);
                  thisForm.modal("hide")
                  hideLoader();
                })
              }else if(result.passcheck == 2){
                swal({
                  title: "Opps",
                  text: result.msg,
                  icon: "error",
                  buttons: true,
                }).then(function(){
                  thisFormBtn.data("requestRunning", false);
                  hideLoader();
                })
              }else if(result.passcheck == 3){
                swal({
                  title: "Server ERROR",
                  text: result.msg,
                  icon: "error",
                  buttons: true,
                }).then(function(){
                  window.location.href = "";
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
          thisFormBtn.data("requestRunning", false);
          hideLoader();
        })
    })
    /* scrpit for removing address */
    $(document).on("click", ".deleteAddressBtn",function(e){
        e.preventDefault()
        showLoader();
  
        var thisBtn = $(this)
        //check if this form is processing
        if(thisBtn.data("requestRunning")){
            return false;
        }
        thisBtn.data("requestRunning", true);
          
        //get values of inputs
        var addressId = thisBtn.closest(".address").data("address-id")
  
        var fd = new FormData()
        fd.append("addressId", addressId);
  
        $.ajax({
          contentType: false,
          processData: false,
          type: "POST",
          url: "/api/user_remove_address",
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
                }).then(function(){
                  $("#addresses").load(location.href + " #addresses>*", "");
                  thisBtn.data("requestRunning", false);
                  hideLoader();
                })
              }else if(result.passcheck == 2){
                swal({
                  title: "Opps",
                  text: result.msg,
                  icon: "error",
                  buttons: true,
                }).then(function(){
                  thisBtn.data("requestRunning", false);
                  hideLoader();
                })
              }else if(result.passcheck == 3){
                swal({
                  title: "Server ERROR",
                  text: result.msg,
                  icon: "error",
                  buttons: true,
                }).then(function(){
                  window.location.href = "";
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
          thisBtn.data("requestRunning", false);
          hideLoader();
        })
    })
    /* scrpit for payment */
    /* adding payment method */
    $(document).on("click", "#addPaymentMethodBtn",function(e){
        showLoader();
  
        var thisBtn = $(this)
        //check if this form is processing
        if(thisBtn.data("requestRunning")){
            return false;
        }
        thisBtn.data("requestRunning", true);
          
  
        var fd = new FormData()
        fd.append("action", "add_payment_method");
  
        $.ajax({
          contentType: false,
          processData: false,
          type: "POST",
          url: "/api/user_add_payment_method",
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
                }).then(function(){
                  $("#paymentMethods").load(location.href + " #paymentMethods>*", "");
                  thisBtn.data("requestRunning", false);
                  hideLoader();
                })
              }else if(result.passcheck == 2){
                swal({
                  title: "Opps",
                  text: result.msg,
                  icon: "error",
                  buttons: true,
                }).then(function(){
                  thisBtn.data("requestRunning", false);
                  hideLoader();
                })
              }else if(result.passcheck == 3){
                swal({
                  title: "Server ERROR",
                  text: result.msg,
                  icon: "error",
                  buttons: true,
                }).then(function(){
                  window.location.href = "";
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
          thisBtn.data("requestRunning", false);
          hideLoader();
        })
    });
    //ajax for membership confirmation
    $(document).on("click", ".manage-card-btn",function(e){
      e.preventDefault();
      var thisBtn = $(this);
      //check if this form is processing
      if(thisBtn.data("requestRunning")){
          return false;
      }
      thisBtn.data("requestRunning", true);
      showLoader();
  
      var fd = new FormData()
      fd.append("action", "create_portal_session");
          
      $.ajax({
      contentType: false,
      processData: false,
      type: "POST",
      url: "/api/user_create_stripe_portal_session",
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
      })
      hideLoader();
      thisBtn.data("requestRunning", false);
    })
    $(".toggle").click(function() {
        var target = $(this).data("target");
        $(target).slideToggle();
    });
    $(document).on("click", ".change-language-btn", function(){
          var thisBtn = $(this);
          var thisLanguage = thisBtn.data("language");
          showLoader();
          
          var fd = new FormData()
          fd.append("language", thisLanguage);
          $.ajax({
              contentType: false,
              processData: false,
              type: "POST",
              url: "/api/user_change_language",
              dataType: "json",
              data: fd,
              success: function(data){
                  var result = data;
                  if(result.passcheck == 1){
                      location.reload();
                  }else{
                      alert("System failed to update your language preference. Please reload webpage.")
                  }
              },error:function(){
          alert("System failed to update your language preference. Please reload webpage.")
              }
          }).then(function(){
              hideLoader();
          })
      })
  });