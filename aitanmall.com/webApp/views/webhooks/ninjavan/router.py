from flask import Blueprint, jsonify, request, abort
from webApp.helper import telegram
import base64
import hashlib
import hmac
from webApp.views.webhooks.ninjavan.handlers import pending_pickup
from webApp.views.webhooks.ninjavan.handlers import successful_pickup
from webApp.views.webhooks.ninjavan.handlers import on_vehical
from webApp.views.webhooks.ninjavan.handlers import complete
from webApp.views.webhooks.ninjavan.handlers import returned

ninjavan_webhook= Blueprint("ninjavan_webhook", __name__, static_folder="static", template_folder="templates")

CLIENT_SECRET = '51fb31a34da84a1a9528f3b464bc5f97'

def verify_webhook(data, hmac_header) -> bool:
    # This is equivalent to the PHP hash_hmac function.
    # It creates a new HMAC object, then digests it and finally encodes it in base64
    calculated_hmac = base64.b64encode(hmac.new(bytes(CLIENT_SECRET, 'utf-8'), data, digestmod=hashlib.sha256).digest())
    
    # Converting bytes to string for comparison
    calculated_hmac = calculated_hmac.decode('utf-8')
    
    # This checks whether the calculated HMAC matches the HMAC header from the request
    if hmac_header == calculated_hmac:
        return True
    return False

#verification before EVERY REQUEST
@ninjavan_webhook.before_request
def before_request_function():
    try:
        # This is equivalent to PHP's file_get_contents('php://input')
        # It gets the raw data from the incoming request
        data = request.get_data()
        assert request.method == 'POST', "Webhook request can only a POST request."
        # The 'Ru6nS2bSEPRaRAq+GM0cMMvVxyFz8sVkKjSI6rD1jgY=' is the HMAC header in your PHP code
        hmac_header = request.headers.get('X-Ninjavan-Hmac-SHA256')

        # This calls the verify_webhook function (equivalent to the PHP function of the same name)
        verified = verify_webhook(data, hmac_header)
        assert verified == True, "Incoming request not from Ninjavan"
    except Exception as e:
        telegram_bot_token = telegram.get_token()
        telegram_chat_id = telegram.get_tracking_chat_id()
        telegram.send_message(telegram_bot_token, telegram_chat_id, str(e))
        abort(400, description=str(e))
    
# webhook URL
@ninjavan_webhook.route("", methods=["POST"])
@ninjavan_webhook.route("/", methods=["POST"])
def handle_webhooks():
    try:
        #Retrieve the data
        data = request.get_json()
        
        parcel_status = data["status"]
        if parcel_status == "Pending Pickup":
            handler_status = pending_pickup.handler_pending_pickup_parcel(data)
        elif parcel_status == "On Vehicle for Delivery":
            handler_status = on_vehical.handler_on_vehical_parcel(data)
        elif parcel_status == "Completed":
            handler_status = complete.handler_complete_parcel(data)
        elif parcel_status == "Successful Pickup":
            handler_status = successful_pickup.handler_successful_pickup_parcel(data)
        elif parcel_status == "Return to Sender Triggered":
            handler_status = returned.handler_returned_parcel(data)
        else:
            handler_status = True
        
        telegram_bot_token = telegram.get_token()
        telegram_chat_id = telegram.get_tracking_chat_id()
        telegram.send_message(telegram_bot_token, telegram_chat_id, str(handler_status))

        return str(f"handler_status:{handler_status}"), 200
    except Exception as e:
        telegram_bot_token = telegram.get_token()
        telegram_chat_id = telegram.get_tracking_chat_id()
        telegram.send_message(telegram_bot_token, telegram_chat_id, str(e))
        abort(400, description=str(e))