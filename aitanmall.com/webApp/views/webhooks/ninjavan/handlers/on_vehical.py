from webApp.helper import orders
from webApp.helper import user
from webApp.helper import general
from webApp.helper import twilio

STATUS = "On Vehicle for Delivery"

def handler_on_vehical_parcel(json_data:dict):
    try:
        assert json_data["status"] == STATUS, f"Ninjavan Webhook for {STATUS}: Wrong handler used. This handler is for On Vehicle for Delivery"
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
        assert isinstance(select_orders_result, list) and len(select_orders_result) > 0, f"Ninjavan Webhook for {STATUS}Failed to retrieve order details for Order: {order_id}"
        select_orders_user_id = select_orders_result[0]["user_id"]
        select_orders_status = select_orders_result[0]["ord_status"]
        select_orders_total = select_orders_result[0]["ord_final_total"]
        select_orders_payment_method_nku = select_orders_result[0]["merchant_payment_method_option_nku"]
        #Assert order status is in accepted status so we have no error
        accepted_status = ["pending_pickup", "picked_up", "returned"]
        assert select_orders_status in accepted_status, f"Ninjavan webhoook for {STATUS}: Order: {order_id} status : {select_orders_status} prevented order to be updated"
        #Now we select user and send them a notification
        select_user_result = user.select_user(db_conn_cursor, select_orders_user_id)
        assert isinstance(select_user_result, list) and len(select_user_result) > 0, f"Ninjavan Webhook for {STATUS} System failed to retrieve user details associated with Order: {order_id}"
        user_phone_number_country_code = select_user_result[0]["user_phone_number_code"]
        user_phone_number = select_user_result[0]["user_phone_number"]
        user_phone_number_with_code = str(user_phone_number_country_code)+str(user_phone_number)
        user_first_name = select_user_result[0]["user_first_name"]
        user_language = select_user_result[0]["user_language"]
        #Now we update order status and notify customer via whatsapp
        assert orders.update_orders_status(db_conn, db_conn_cursor, "on_vehical_for_delivery", order_id) == True, f"Ninjavan Webhook for {STATUS}System failed to update order status for Order: {order_id}"
        #Create a shipment for this order in database; Update if it already exists
        select_order_shipment_result = orders.select_order_shipment(db_conn_cursor, None, order_id)
        assert isinstance(select_order_shipment_result, list), f"Ninjavan Webhook for {STATUS}System failed to retrieve order shipment details"
        if len(select_order_shipment_result) > 0:
            assert orders.update_ord_shipment_tracking_number(db_conn, db_conn_cursor, tracking_number, None, order_id, True) == True, f"Ninjavan webhoook for {STATUS}: System failed to update order shipment status for Order: {order_id}"
            assert orders.update_ord_shipment_status(db_conn, db_conn_cursor, "on_vehical_for_delivery", None, order_id, True) == True, f"Ninjavan webhoook for {STATUS}: System failed to update order shipment status for Order: {order_id}"
        else:
            assert orders.create_ord_shipment(db_conn, db_conn_cursor, "ninjavan", tracking_number, "on_vehical_for_delivery", order_id) == True, f"Ninjavan webhoook for {STATUS}: System failed to create a shipment record for Order: {order_id}"
        #Now we have updated the order shipment things, we can notify customer
        #We only notify if it is COD to save cost
        if select_orders_payment_method_nku == "cod":
            if user_language == "my":
                whatsapp_msg = """Salam {}, *_Postage anda akan dihantar oleh postman dari {} sebentar lagi._*\n*_Sila menyediakan Rm{} untuk parcel COD ni_*\n\n*Kalau postage anda tidak sampai lepas pukul {} hari ini ATAUPUN postman tidak menghubungi awak sebelum hantaran, sila buat laporan melalui link ni: {} .*\n\nSemoga lelahmu menjadi lillah,\n*AiTan SDN BHD*"""
            elif user_language == "cn":
                whatsapp_msg = """你好{}, *_{}的送货员即将把货物送给你了._* \n*_请您准备Rm{} 来付款您的货到付款货物_*\n\n*如果您的货物在{}之前没送到或是送货员没有正常的联系你, 请您不要犹豫地向我们举报改名送货员: {} .*\n\n祝您美好的一天,\n*AiTan SDN BHD*"""
            else: 
                whatsapp_msg = """Dear {}, *_Your parcel is _OUT FOR DELIVERY_  by {}._* \n*_Please prepare Rm{} for the parcel_*\n\n*If your parcel is not delivered today after {} OR if the postman did not contact you properly, please report to us via this link: {} .*\n\nWish you a good day ahead,\n*AiTan SDN BHD*"""
    
            courier = "Ninjavan"
            report_url = "https://shorturl.at/ijLR2"
            #Remember to update when you go international
            last_delivery_hour = "10pm"
            whatsapp_msg = whatsapp_msg.format(user_first_name, courier, select_orders_total, last_delivery_hour, report_url)
            assert twilio.send_whatsapp(whatsapp_msg, user_phone_number_with_code).status == "queued", f"System failed to notify customer via whatsapp for Order: {order_id}"
        
        return True
    except Exception as e:
        return e