from webApp.helper import orders
from webApp.helper import user
from webApp.helper import general
from webApp.helper import twilio

STATUS = "Successful Pickup"

def handler_successful_pickup_parcel(json_data):
    try:
        assert json_data["status"] == STATUS, f"Ninjavan webhoook for {STATUS}: Wrong handler used. This handler is for Successful Pickup."
        order_id = json_data["shipper_order_ref_no"]
        tracking_number = json_data["tracking_id"]
        #Now we assert the data and then we retrieve customer details
        assert len(str(order_id)) > 0, f"Ninjavan Webhook for {STATUS} Order ID: {order_id} cannot be empty"
        assert len(str(tracking_number)) > 0, f"Ninjavan Webhook for {STATUS} Tracking ID: {tracking_number} cannot be empty"
        #Connecting to database and select details from orders
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor(dictionary=True)
        #Select order result
        select_orders_result = orders.select_orders(db_conn_cursor, order_id)
        assert isinstance(select_orders_result, list) and len(select_orders_result) > 0, f"Failed to retrieve order details for Order: {order_id}"
        select_orders_user_id = select_orders_result[0]["user_id"]
        select_orders_status = select_orders_result[0]["ord_status"]
        #Assert order status is in accepted status so we have no error
        accepted_status = ["pending", "to_ship", "paid", "pending_pickup"]
        assert select_orders_status in accepted_status, f"Ninjavan webhoook for {STATUS}: Order: {order_id} status : {select_orders_status} prevented order to be updated"
        #Now we select user and send them a notification
        select_user_result = user.select_user(db_conn_cursor, select_orders_user_id)
        assert isinstance(select_user_result, list) and len(select_user_result) > 0, f"Ninjavan webhoook for {STATUS}:System failed to retrieve user details associated with Order: {order_id}"
        user_phone_number_country_code = select_user_result[0]["user_phone_number_code"]
        user_phone_number = select_user_result[0]["user_phone_number"]
        user_phone_number_with_code = str(user_phone_number_country_code)+str(user_phone_number)
        user_first_name = select_user_result[0]["user_first_name"]
        user_language = select_user_result[0]["user_language"]
        #Now we update order status and notify customer via whatsapp
        assert orders.update_orders_status(db_conn, db_conn_cursor, "picked_up", order_id) == True, f"Ninjavan webhoook for {STATUS}:System failed to update order status for Order: {order_id}"
        #Create a shipment for this order in database; Update if it already exists
        select_order_shipment_result = orders.select_order_shipment(db_conn_cursor, None, order_id)
        assert isinstance(select_order_shipment_result, list), f"Ninjavan webhoook for {STATUS}:System failed to retrieve order shipment details"
        if len(select_order_shipment_result) > 0:
            assert orders.update_ord_shipment_tracking_number(db_conn, db_conn_cursor, tracking_number, None, order_id, True) == True, f"Ninjavan webhoook for {STATUS}:System failed to update order shipment status for Order: {order_id}"
            assert orders.update_ord_shipment_status(db_conn, db_conn_cursor, "picked_up", None, order_id, True) == True, f"Ninjavan webhoook for {STATUS}:System failed to update order shipment status for Order: {order_id}"
        else:
            assert orders.create_ord_shipment(db_conn, db_conn_cursor, "ninjavan", tracking_number, "picked_up", order_id) == True, f"System failed to create a shipment record for Order: {order_id}"
        #Now we have updated the order shipment things, we can notify customer
        if user_language == "my":
            whatsapp_msg = """*AiTan SDN. BHD.*\n\nSalam {}, parcel anda untuk pesanan dengan ID Pesanan: {} telah berada dengan {}. Anda boleh mengesan parcel anda sekarang melalui pautan ini: {}\n\nUntuk bantuan, sila hubungi perkhidmatan pelanggan kami di {}\n\nHarapkan hari yang baik di hadapan,\nAiTanMall"""
            sms_msg = "AiTan SDN. BHD. Pesanan anda telah dihantar oleh penjual. Anda boleh mengesan pesanan sekarang di laman web ninjavan dengan nombor penjejakan ini: {}."
        elif user_language == "cn":
            whatsapp_msg = """*AiTan SDN. BHD.*\n\n你好，{}，你的订单编号为: {}的包裹已经成功被{}收取。你现在可以通过这个链接: {} 来跟踪你的包裹。\n\n如需帮助，请联系我们的客服，电话为：{}\n\n祝你今天过得愉快，\nAiTanMall"""
            sms_msg = "AiTan SDN. BHD. 您的订单已由卖家发出。您现在可以在ninjavan网站上使用此跟踪号码进行跟踪：{}."
        else: 
            whatsapp_msg = """*AiTan SDN. BHD.*\n\nHi {}, your parcel for order with Order ID: {} has been successfully picked by by {}. You can track your parcel now via this link: {}\n\nFor help, please contact our customer service at {}\n\nWish you a good day ahead,\nAiTanMall"""
            sms_msg = "AiTan SDN. BHD. Your order is shipped by seller. You can track the order now at ninjavan website with this tracking number: {}."

        courier = "Ninjavan"
        customer_service_number = "011-5775-3538"
        #Remember to update when you go international
        ninjavan_tracking_url_with_tracking = "https://www.ninjavan.co/en-my/tracking?id="+tracking_number
        whatsapp_msg = whatsapp_msg.format(user_first_name, order_id, courier, ninjavan_tracking_url_with_tracking, customer_service_number)
        assert twilio.send_whatsapp(whatsapp_msg, user_phone_number_with_code).status == "queued", f"System failed to notify customer via whatsapp for Order: {order_id}"
        sms_msg = sms_msg.format(tracking_number)
        twilio.send_sms(sms_msg, user_phone_number_with_code)
        return True
    except Exception as e:
        return e