from flask import Blueprint, jsonify, request
import json
import os 

chat_webhook= Blueprint("chat_webhook", __name__, static_folder="static", template_folder="templates")

# webhook URL
@chat_webhook.route("", methods=["POST"])
@chat_webhook.route("/", methods=["POST"])
def handle_webhooks():
    data = request.get_json()

    if data != None and len(data) >0:
        data_event_type = data.get("event_type")
        data_from_name = data.get("from_name")
        data_to_name = data.get("to_name", None)
        data_from_room_id = data.get("from_room_id")
        data_broadcast = data.get("broadcast")
        data_client_sid = data.get("client_sid")
        data_message = data.get("message")

        if data_from_name[:4] == "USER":
            file_name = data_from_name[5:]+".txt"
        elif data_from_name[:2] == "CS":
            file_name = data_to_name[5:]+".txt"
        else:
            return jsonify({"success":False}), 200
            
        chat_log_file_path = os.path.join("/var","www","aitanmall.com","data","chat", file_name)

        with open(chat_log_file_path, "a") as f:
            if data_event_type == "message":
                f.write(f"@Name:{data_from_name} @Room:{data_from_room_id} Msg:{data_message}\n")
                
    # return jsonify({"success":True, "handler_sttus":True}), 200
    return jsonify({"success":True}), 200