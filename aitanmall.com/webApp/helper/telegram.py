import requests

def get_token() -> str:
    return "6001927791:AAHGkN3jfzi8WM3fNX5SEVqV6XL0K8wacRg"

def get_all_orders_chat_id() -> str:
    return "-398304626"

def get_tracking_chat_id() -> str:
    return "-958840594"

def send_message(token, chat_id, text):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode' : 'html'
    }
   
    response = requests.post(url, data=payload)
    return response.json()