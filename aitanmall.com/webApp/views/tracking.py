from flask import Blueprint, render_template, request, redirect
from webApp.helper import telegram

tracking = Blueprint("tracking", __name__, static_folder="static", template_folder="templates")

@tracking.route("", methods=["GET"])
def home():
    try:
        name = request.args.get("name", None)
        redirect_url = request.args.get("redirect", None)
        if name == "" or name == None or redirect_url == None or redirect_url == "":
            return "True"
        #Telegram
        telegram_bot_token = telegram.get_token()
        telegram_tracking_chat_id = telegram.get_tracking_chat_id()
        telegram.send_message(telegram_bot_token, telegram_tracking_chat_id, f"Tracking activated for {name}. User redirected to {redirect_url}")
        #redirect user
        return redirect(redirect_url)
    except Exception as e:
        telegram_bot_token = telegram.get_token()
        telegram_tracking_chat_id = telegram.get_tracking_chat_id()
        telegram.send_message(telegram_bot_token, telegram_tracking_chat_id, f"Tracking error: {str(e)}")
        return str(e)
    finally:
        pass