from flask import Blueprint, jsonify, request, abort
from webApp.helper import twilio
from webApp.views.webhooks.twilio.handlers import whatsapp as whatsapp_subscription

twilio_webhook= Blueprint("twilio_webhook", __name__, static_folder="static", template_folder="templates")

#verification before EVERY REQUEST
@twilio_webhook.before_request
def before_request_function():
    try:
        account_sid_from_request = request.form.get("AccountSid", None)
        account_sid = twilio.get_sid()
        assert account_sid_from_request != None and account_sid == account_sid_from_request, "Invalid account SID"
    except Exception as e:
        abort(400, description=str(e))
    
# webhook URL
@twilio_webhook.route("", methods=["POST"])
@twilio_webhook.route("/", methods=["POST"])
def handle_webhooks():
    try:
        text_from = request.form.get("From", None)
        #Detect whether if it is a whatsapp message
        if text_from[:8] == "whatsapp":
            is_a_whatsapp = True
        else:
            is_a_whatsapp = False

        #Handle it base on type
        #First convert POST data to dict
        data = request.form.to_dict()
        if is_a_whatsapp == True:
            handler_status = whatsapp_subscription.handle_initiated_message(data)

        return jsonify({"success":True, "handler_status":str(handler_status)})
    except Exception as e:
        abort(400, description=str(e))