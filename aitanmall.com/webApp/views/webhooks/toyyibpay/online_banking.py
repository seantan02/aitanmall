from flask import Blueprint, jsonify, request, current_app
from webApp.helper import toyyibpay
from webApp.helper import telegram
from webApp.helper import orders
from webApp.helper import general
from webApp.helper import merchant
from webApp.helper import user
from webApp.helper import twilio

toyyibpay_ob= Blueprint("toyyibpay_ob", __name__, static_folder=None, template_folder=None)

# webhook URL
@toyyibpay_ob.route("", methods=["POST"])
@toyyibpay_ob.route("/", methods=["POST"])
def handle_webhooks():
    current_domain = current_app.config.get("DOMAIN_NAME")
    try:
        #Get telegram details
        telegram_token = telegram.get_token()
        telegram_chat_id = telegram.get_all_orders_chat_id()
        #Get data and convert it to proper class accordingly
        refno = request.form.get("refno")
        refno = str(refno)
        #Status
        status = request.form.get("status")
        status = int(status)
        #Billcode
        billcode = request.form.get("billcode")
        billcode = str(billcode)
        #Order ID
        order_id = request.form.get("order_id")
        order_id = str(order_id)
        #Amount paid
        amount = request.form.get("amount")
        amount = float(amount)
        transaction_time = request.form.get("transaction_time")

        #Get transaction status in toyyibpay site
        bill_transaction_details = toyyibpay.get_bill(billcode)
        #connect to database
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #If exception thrown when getting bill then it fails
        if isinstance(bill_transaction_details, Exception):
            return "Bad request", 400
        #Visualize data
        #Get bill status from Toyyibpay and convert it to int
        bill_payment_status = bill_transaction_details[-1]["billpaymentStatus"]
        bill_payment_status = int(bill_payment_status)
        #Get bill reference no from Toyyibpay and convert it to str
        bill_external_reference_no = bill_transaction_details[-1]["billExternalReferenceNo"]
        bill_external_reference_no = str(bill_external_reference_no)
        #Get bill amount from Toyyibpay and convert it to float
        bill_payment_amount = bill_transaction_details[-1]["billpaymentAmount"]
        bill_payment_amount = float(bill_payment_amount)
        #Get bill invoice no from Toyyibpay and convert it to str
        bill_payment_invoiceNo = bill_transaction_details[-1]["billpaymentInvoiceNo"]
        bill_payment_invoiceNo = str(bill_payment_invoiceNo)
        #For now we forget about datetime
        bill_payment_date = bill_transaction_details[-1]["billPaymentDate"]
        # Convert them into datetime objects
        transaction_time = general.make_str_datetime_object(transaction_time, '%Y-%m-%d %H:%M:%S')
        bill_payment_date = general.make_str_datetime_object(bill_payment_date, '%d-%m-%Y %H:%M:%S')
        # assert transaction_time == bill_payment_date, "Datetime of transaction does not match"
        assert refno == bill_payment_invoiceNo, "Payment invoice ID does not match"
        assert order_id == bill_external_reference_no, "Order ID does not match"
        assert bill_payment_status == status, "Payment status does not match"
        assert bill_payment_amount == amount, "Payment amount does not match"
        #Now we can update order status and send telegram message to sellers (if they have) + whatsapp customer
        customer_orders_details = orders.select_orders(db_conn_cursor, order_id)
        assert isinstance(customer_orders_details, list), "Error in getting customer orders details"
        assert len(customer_orders_details) > 0, "Orders details is empty"
        
        customer_orders_user_id = customer_orders_details[0][2]
        customer_orders_user_address = customer_orders_details[0][3]
        customer_orders_ord_ord_final_total = customer_orders_details[0][9]
        customer_orders_ord_ord_status = customer_orders_details[0][10]

        assert customer_orders_ord_ord_status == "pending", "Orders' status has already been updated. There might be an issue."
        #If status is not successful then we update it
        if int(status) != 1:
            assert orders.update_orders_status(db_conn, db_conn_cursor, "failed", order_id) == True, "Failed to update orders' status"
            assert merchant.update_income_status(db_conn, db_conn_cursor, "failed", order_id) == True, "Failed to update merchant's income"
            return jsonify({"success":True}), 200
        #Update orders status and merchant income status
        assert merchant.update_income_status(db_conn, db_conn_cursor, "succeeded", order_id) == True, "Failed to update merchant's income"
        assert orders.update_orders_status(db_conn, db_conn_cursor, "to_ship", order_id) == True, "Failed to update orders' status"
        #Get user's details
        customer_details = user.get_user(db_conn_cursor, customer_orders_user_id)
        customer_first_name = customer_details[0][2]
        customer_phone_code = customer_details[0][6]
        customer_phone_number = customer_details[0][7]
        customer_full_phone_number = str(customer_phone_code)+str(customer_phone_number)
        #Now these are actions for status == 1
        ord_details = orders.select_order_details(db_conn_cursor, order_id)
        assert isinstance(ord_details, list), "Error in getting customer order details"
        assert len(ord_details) > 0, "Order details is empty"
        #loop through details and send all merchant telegram notification
        current_merchant_id = None
        for ord_detail in ord_details:
            ord_detail_merchant_id = ord_detail[12]
            if current_merchant_id == None or current_merchant_id != ord_detail_merchant_id:
                current_merchant_id = ord_detail_merchant_id
                #get merchant income details
                merchant_income_details = merchant.get_income(db_conn_cursor, order_id, ord_detail_merchant_id)
                merchant_income_initial_total = merchant_income_details[0][2]
                merchant_income_real_total = merchant_income_details[0][3]
                #send telegram notification if there exists a bot and chat
                try:
                    merchant_telegram_details = merchant.select_telegram_bot(db_conn_cursor, ord_detail_merchant_id)
                    if isinstance(merchant_telegram_details, list) and len(merchant_telegram_details) > 0:
                        merchant_telegram_bot_id = merchant_telegram_details[0][1]
                        merchant_telegram_bot_token = merchant_telegram_details[0][3]
                        merchant_telegram_chat_details = merchant.select_telegram_bot_chat(db_conn_cursor, ord_detail_merchant_id, merchant_telegram_bot_id, "orders", True)
                        if isinstance(merchant_telegram_chat_details, list) and len(merchant_telegram_chat_details) > 0:
                            merchant_telegram_bot_chat_id = merchant_telegram_chat_details[0][1]
                            merchant_telegram_order_message = f"""Online Banking Success Order\nOrder ID: {order_id}\n\nCustomer Information:\nName: {customer_first_name}\nAddress: {customer_orders_user_address}\nContact: {customer_full_phone_number}\nTotal Before Fees: Rm{round(merchant_income_initial_total, 2)}\nTotal Final: Rm{round(merchant_income_real_total, 2)}\n\n<a href='https://merchant.aitanmall.com/quickcall/check_order?ord_id={order_id}'>Check Order Details</a>\n<a href='api.whatsapp.com/send?phone={customer_full_phone_number}'>Whatsapp Customer Now</a>"""
                            merchant_telegram_response = telegram.send_message(merchant_telegram_bot_token, merchant_telegram_bot_chat_id, merchant_telegram_order_message)
                            assert merchant_telegram_response["ok"] == True
                except Exception as e:
                    pass
        #Send a whatsapp message to customer
        customer_review_order_link = current_domain+"/user/orders"
        customer_cancel_order_link = current_domain+"/user/orders"
        customer_service_number = "601157753538"
        customer_order_whatsapp_text = f"""*AiTan System*\n\n*Dear {customer_first_name}*,\n\nThank you for placing an order via our website, aitanmall.com . Your order's details are as followed :\n\n*Order ID:* {customer_first_name}\n*Total:* Rm{round(customer_orders_ord_ord_final_total, 2)}\n*Payment Method:* Online Banking\n\nTo review your order, kindly click this link: {customer_review_order_link}\n\n*Did not place an order? KINDLY click this link IMMEDIATELY* : {customer_cancel_order_link} , *or contact {customer_service_number}*\n\n*_If you have not received your item after 10 day(s), please contact {customer_service_number} immediately! Thank you._*\n\nWish you a great day ahead,\n*AiTan SDN BHD*"""
        twilio_whatsapp_response = twilio.send_whatsapp(customer_order_whatsapp_text, customer_full_phone_number)
        assert twilio_whatsapp_response.status in ["queued", "sent", "delivered"], "Whatsapp notification was not sent to customer"

        return jsonify({"success":True}), 200
    except Exception as e:
        telegram.send_message(telegram_token, telegram_chat_id, f"ERROR: {str(e)}")
        return "Bad request", 400