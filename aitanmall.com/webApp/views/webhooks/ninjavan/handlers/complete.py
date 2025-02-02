from webApp.helper import orders
from webApp.helper import user
from webApp.helper import general
from webApp.helper import twilio

STATUS = "Completed"

def handler_complete_parcel(json_data:dict):
    try:
        
        assert json_data["status"] == STATUS, f"Ninjavan webhook for {STATUS}: Wrong handler used. This handler is for {STATUS}"
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
        assert isinstance(select_orders_result, list) and len(select_orders_result) > 0, f"Ninjavan webhook for {STATUS}: Failed to retrieve order details for Order: {order_id}"
        select_orders_user_id = select_orders_result[0]["user_id"]
        select_orders_status = select_orders_result[0]["ord_status"]
        select_orders_total = select_orders_result[0]["ord_final_total"]
        select_orders_payment_method_nku = select_orders_result[0]["merchant_payment_method_option_nku"]
        #Assert order status is in accepted status so we have no error
        accepted_status = ["picked_up", "on_vehical_for_delivery"]
        assert select_orders_status in accepted_status, f"Ninjavan webhoook for {STATUS}: Order: {order_id} status : {select_orders_status} prevented order to be updated"
        #Now we select user and send them a notification
        select_user_result = user.select_user(db_conn_cursor, select_orders_user_id)
        assert isinstance(select_user_result, list) and len(select_user_result) > 0, f"Ninjavan webhook for {STATUS}: System failed to retrieve user details associated with Order: {order_id}"
        user_phone_number_country_code = select_user_result[0]["user_phone_number_code"]
        user_phone_number = select_user_result[0]["user_phone_number"]
        user_phone_number_with_code = str(user_phone_number_country_code)+str(user_phone_number)
        user_first_name = select_user_result[0]["user_first_name"]
        user_language = select_user_result[0]["user_language"]
        #Now we update order status and notify customer via whatsapp
        assert orders.update_orders_status(db_conn, db_conn_cursor, STATUS.lower(), order_id) == True, f"Ninjavan webhook for {STATUS}: System failed to update order status for Order: {order_id}"
        #Create a shipment for this order in database; Update if it already exists
        select_order_shipment_result = orders.select_order_shipment(db_conn_cursor, None, order_id)
        assert isinstance(select_order_shipment_result, list), "System failed to retrieve order shipment details"
        assert len(select_order_shipment_result) > 0, f"No order shipment was found to be updated into On Vehical For Delivery. Order:{order_id}"
        assert orders.update_ord_shipment_status(db_conn, db_conn_cursor,  STATUS.lower(), None, order_id, True) == True, f"Ninjavan webhook for {STATUS}: System failed to update order shipment status for Order: {order_id}"
        
        #Now we have updated the order shipment things, we can notify customer
        #We only notify if it is COD to save cost
        if user_language == "my":
            whatsapp_msg = """\nSalam {}, *_Postage anda telah _SIAP DIHANTAR_ oleh postman {}._* \n\n*Kalau anda TIDAK MENDAPAT postage anda, sila buat laporan melalui lini ni : {} .*\n\nSemoga lelahmu menjadi lillah,\n*AiTan SDN BHD*"""
        elif user_language == "cn":
            whatsapp_msg = """您好{}, *_{}的送货员已_成功完成_您的订单了._* \n\n*如果您没有收到货物, 请您通过这个连接向我们举报: {} .*\n\n祝您美好的一天,\n*AiTan SDN BHD*"""
        else: 
            whatsapp_msg = """Dear {}, *_Your parcel is _SUCCESSFULLY DELIVERED_ by {}._* \n\n*If you DID NOT receive your parcel, please report to us via this link: {} .*\n\nWish you a good day ahead,\n*AiTan SDN BHD*"""
    
        courier = "Ninjavan"
        report_url = "https://shorturl.at/ijLR2"
        whatsapp_msg = whatsapp_msg.format(user_first_name, courier, report_url)
        assert twilio.send_whatsapp(whatsapp_msg, user_phone_number_with_code).status == "queued", f"System failed to notify customer via whatsapp for Order: {order_id}"
        return True
    except Exception as e:
        return e