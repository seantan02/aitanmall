//script for g-recapcha
function onSubmit(token) {
    $("#login-user-form").submit()
}
function onClick(e) {
    e.preventDefault();
    grecaptcha.ready(function() {
    grecaptcha.execute('6Le5uQwkAAAAAGwbjfaxng7WdTXGRlviqS_NIbXW', {action: 'submit'}).then(function(token){
            $("#g-recaptcha-response").val(token);
        })
    });
}
//script for login
$(document).ready(function(){
    hideLoader();
    
    $(document).on("submit", "#login-user-form",function(e){
        showLoader();
        e.preventDefault()
        var thisBtn = $(this);
        var thisForm = thisBtn.closest("#login-user-form");
        var thisFormGResponse = thisBtn.closest("#login-user-form").find("#g-recaptcha-response")
        var thisFormGResponseValue = thisFormGResponse.val()
        //check if this form is processing
        if(thisFormGResponseValue.length == 0){
            alert("You are a bot")
            return false;
        }
        if(thisBtn.data("requestRunning")){
            return false;
        }
        thisBtn.data("requestRunning", true);
        
        //get values of inputs
        var emailInput = thisForm.find("input[name='email']")
        var phoneNumberInput = thisForm.find("input[name='phone-number']")
        var passwordInput = thisForm.find("input[name='password']")
        
        var emailInputValue = emailInput.val()
        var phoneNumberInputValue = phoneNumberInput.val()
        var passwordInputValue = passwordInput.val()
        var testEmail = /^[A-Z0-9._%+-]+@([A-Z0-9-]+\.)+[A-Z]{2,4}$/i;
        if(((emailInputValue.length > 0 && testEmail.test(emailInputValue)) || (phoneNumberInputValue.length > 0 && $.isNumeric(phoneNumberInputValue))) && passwordInputValue.length > 0){
            var fd = new FormData()
            fd.append("email", emailInputValue);
            fd.append("phone_number", phoneNumberInputValue);
            fd.append("password", passwordInputValue);
            fd.append("g-response", thisFormGResponseValue);
            
            $.ajax({
                contentType: false,
                processData: false,
                type: "POST",
                url: "/api/log_in_user",
                dataType: "json",
                data: fd,
                success: function(data){
                    var result = data;
                    if(result.passcheck==1){
                        $("body").trigger("sendTemporarilyKeyRequest", [result.temporarily_key, result.user_id]);
                        setTimeout(function(){}, 5000);
                        window.location.href="/"
                    }else{
                        swal({
                            title: "Opps",
                            text: result.msg,
                            icon: "error",
                            buttons: true,
                        })
                        thisBtn.data("requestRunning", false);
                        hideLoader();
                    }
                },error:function(){
                    swal({
                        title: "Server Error",
                        text: "Please refresh and reload the page",
                        icon: "error",
                        buttons: true,
                    });
                    thisBtn.data("requestRunning", false);
                    hideLoader();
                }
            })
        }else{
            swal({
                title: "Username or password invalid",
                text: "Please ensure username is in valid form, and password is filled.",
                icon: "error",
                buttons: true,
            })
            thisBtn.data("requestRunning", false);
            hideLoader();
        }
    })
    
    $(document).on("click","#login-user-form .change-username-btn",function(){
        var thisBtn = $(this);
        var targetInputWrapper = $("."+thisBtn.data("target"));
        var targetInput = targetInputWrapper.find("input")
        var thisInputWrapper = thisBtn.closest(".form-input");
        var thisInput = thisInputWrapper.find("input");
        
        thisInput.attr("required",false);
        thisInput.val("");
        targetInput.attr("required",true);
        thisInputWrapper.addClass("hide");
        targetInputWrapper.removeClass("hide");
    })

    $(document).on("sendTemporarilyKeyRequest", "body", function(event, temporarily_key, user_id){
        
        var fd = new FormData()
        fd.append("temporarily_key", temporarily_key);
        fd.append("user_id", user_id);
        
        $.ajax({
            contentType: false,
            processData: false,
            type: "POST",
            url: "/api/create_user_temporarily_key",
            dataType: "json",
            data: fd
        })
    })
})