from webApp.helper import telegram

def send_main_orders_reminder(order_header, user_first_name, user_last_name,user_phone_number, total_customer_payment, checkout_platform_voucher_discount, user_email) -> bool:
    telegram_bot_token = telegram.get_token()
    telegram_all_orders_chat_id = telegram.get_all_orders_chat_id()
    total_customer_payment_rounded = round(total_customer_payment, 2)
    checkout_platform_voucher_discount_rounded = round(checkout_platform_voucher_discount, 2)
    text = f"""
{order_header}

Cust_info: 
Name: {user_first_name} {user_last_name}
Contact: {user_phone_number}
Total Received: RM {total_customer_payment_rounded}
Discounted Amount: RM {checkout_platform_voucher_discount_rounded}
Total Final: {total_customer_payment_rounded+checkout_platform_voucher_discount_rounded}
Email: {user_email}

<a href='api.whatsapp.com/send?phone={user_phone_number}'>Whatsapp Customer Now</a>
"""
    telegram_send_response = telegram.send_message(telegram_bot_token, telegram_all_orders_chat_id, text)
    return telegram_send_response["ok"]