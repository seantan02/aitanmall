from twilio.rest import Client
from webApp.helper import json_tools as jst

twilio_dict = jst.read_json("/var/www/aitanmall.com/private/data/twilio.json")

twilio_token = twilio_dict["token"]
twilio_sid = twilio_dict["sid"]
twilio_message_sid = twilio_dict["message_service_sid"]

def get_token()->str:
    return twilio_token

def get_sid()->str:
    return twilio_sid

def get_message_sid() -> str:
    return twilio_message_sid

def send_sms(sms_text, to, callback_url = None) -> tuple:
    sid = get_sid()
    token = get_token()
    client_object = Client(sid, token)
    message_sid = get_message_sid()
    message = client_object.messages.create(
                    from_="+12253348123",
                    body=str(sms_text),
                    status_callback=callback_url,
                    to='+{}'.format(to)
                )
    return(message)

def send_whatsapp(whatsapp_text, to, callback_url = None) -> tuple:
    sid = get_sid()
    token = get_token()
    client_object = Client(sid, token)
    message = client_object.messages.create(
        from_='whatsapp:+601157753611',
        body=str(whatsapp_text),
        to='whatsapp:+{}'.format(to)
    )
    return (message)

def send_media_whatsapp(caption, to, media_url, callback_url = None) -> tuple:
    sid = get_sid()
    token = get_token()
    client_object = Client(sid, token)
    message = client_object.messages.create(
        media_url=[media_url],
        body=str(caption),
        from_='whatsapp:+601157753611',
        to='whatsapp:+{}'.format(to)
    )
    return (message)

def send_test_whatsapp(whatsapp_text, to, callback_url = None) -> tuple:
    sid = get_sid()
    token = get_token()
    client_object = Client(sid, token)
    message = client_object.messages.create(
        from_='whatsapp:+14155238886',
        body=str(whatsapp_text),
        to='whatsapp:+{}'.format(to)
    )
    return (message)

def send_test_media_whatsapp(caption, to, media_url, callback_url = None) -> tuple:
    sid = get_sid()
    token = get_token()
    client_object = Client(sid, token)
    message = client_object.messages.create(
        media_url=[media_url],
        body=str(caption),
        from_='whatsapp:+14155238886',
        to='whatsapp:+{}'.format(to)
    )
    return (message)