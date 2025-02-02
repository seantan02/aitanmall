from webApp.helper import orders
from webApp.helper import user
from webApp.helper import general
from webApp.helper import twilio
from webApp.mysql_connector import use_db, close_mysql_conn, close_mysql_cursor

STATUS = "Pending Pickup"

def handler_pending_pickup_parcel(json_data:dict):
    try:
        assert json_data["status"] == STATUS, f"Ninjavan webhook for {STATUS}: Wrong handler used. This handler is for Pending Pickup."
        order_id = json_data["shipper_order_ref_no"]
        tracking_number = json_data["tracking_id"]
        #Now we assert the data and then we retrieve customer details
        assert len(str(order_id)) > 0, f"Ninjavan Webhook for {STATUS} Order ID: {order_id} cannot be empty"
        assert len(str(tracking_number)) > 0, f"Ninjavan Webhook for {STATUS} Tracking ID: {tracking_number} cannot be empty"
        #Connecting to database and select details from orders
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor(dictionary=True)

        select_orders_result = orders.select_orders(db_conn_cursor, order_id)
        assert isinstance(select_orders_result, list) and len(select_orders_result) > 0, f"Ninjavan webhook for {STATUS}:Failed to retrieve order details for Order: {order_id}"
        select_orders_user_id = select_orders_result[0]["user_id"]
        select_orders_status = select_orders_result[0]["ord_status"]
        #Assert order status is in accepted status so we have no error
        accepted_status = ["pending", "to_ship", "paid"]
        assert select_orders_status in accepted_status, f"Ninjavan webhoook for {STATUS}: Order: {order_id} status : {select_orders_status} prevented order to be updated"
        #Now we select user and send them a notification
        select_user_result = user.select_user(db_conn_cursor, select_orders_user_id)
        assert isinstance(select_user_result, list) and len(select_user_result) > 0, f"Ninjavan webhook for {STATUS}:System failed to retrieve user details associated with Order: {order_id}"
        user_phone_number_country_code = select_user_result[0]["user_phone_number_code"]
        user_phone_number = select_user_result[0]["user_phone_number"]
        user_phone_number_with_code = str(user_phone_number_country_code)+str(user_phone_number)
        user_first_name = select_user_result[0]["user_first_name"]
        user_language = select_user_result[0]["user_language"]
        #Now we update order status and notify customer via whatsapp
        assert orders.update_orders_status(db_conn, db_conn_cursor, "pending_pickup", order_id) == True, f"System failed to update order status for Order: {order_id}"
        #We do not send tracking yet because we will it during successfully picked up
        return True
    except Exception as e:
        return e
    finally:
        pass
        if "db_conn_cursor" in locals():
            close_mysql_cursor(db_conn_cursor)
        if "db_conn" in locals():
            close_mysql_conn(db_conn)