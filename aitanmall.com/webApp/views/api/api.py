from flask import Blueprint, jsonify, request, session, make_response, current_app, render_template
import html
from webApp.helper import otp
from webApp.helper import general
from webApp.helper import product
from webApp.helper import orders
from webApp.helper import stripe
from passlib.hash import sha256_crypt
from webApp.helper import user
from webApp.helper import stripe as strp
from webApp.helper import merchant
from webApp.helper import twilio
from webApp.classes.user.order import Order
from webApp.classes.user.orders import Orders
from webApp.classes.user.voucher import Voucher
from webApp.classes.user.membership import Membership
from webApp.classes.cart_item import Cart_item
from webApp.classes.cart import Cart
from webApp.mysql_connector import use_db, close_mysql_cursor,close_mysql_conn
from webApp.helper import telegram
from webApp.helper import checkout
from webApp.helper import toyyibpay
from webApp.helper import voucher
from datetime import datetime
from webApp.helper import mailer

api = Blueprint("api", __name__, static_folder=None, template_folder=None)

#====================================================================
#Method for this Blueprint
#======================================================================
def request_otp(user_phone_number, language):
    """
    Request OTP
    """
    try:
        #generate current time and new time for easier access
        current_time = general.get_current_datetime()
        new_expiration_time = general.get_datetime_from_now(300)
        #connect to user database
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        assert otp.OTP_regenation_permitted(db_conn_cursor, user_phone_number, current_time), "Please only request OTP after 5 minutes"
        new_OTP = otp.generate_unique_OTP(db_conn_cursor, user_phone_number)
        if language == "my":
            sms_authentication_message = "AiTan SDN. BHD.: {} adalah OTP anda. Untuk keselamatan anda, jangan kongsikan kod ini.".format(new_OTP)
            whatsapp_authentication_message = f"*{new_OTP}* adalah kod penentusahan anda. Untuk keselamatan anda, jangan kongsikan kod ini."
        elif language == "cn":
            sms_authentication_message = "AiTan SDN. BHD.: {} 是你的验证码. 为安全起见，请不要分享这组验证码.".format(new_OTP)
            whatsapp_authentication_message = f"*{new_OTP}*是你的验证码。为安全起见，请不要分享这组验证码。"
        else:
            sms_authentication_message = "AiTan SDN. BHD.: {} is your OTP. Please do not share with anyone.".format(new_OTP)
            whatsapp_authentication_message = f"*{new_OTP}* is your verification code. For your security, do not share this code."
        sms_result = twilio.send_sms(sms_authentication_message, user_phone_number)
        sms_result_status = sms_result.status
        whatsapp_result = twilio.send_whatsapp(whatsapp_authentication_message, user_phone_number)
        whatsapp_result_status = whatsapp_result.status
        testing = False
        assert testing or sms_result_status in ["queued", "accepted", "sent", "delivered"] or whatsapp_result_status in ["queued", "accepted", "sent", "delivered"], "OTP not delivered"
        assert otp.remove_old_OTP(db_conn, db_conn_cursor, user_phone_number), "OTP not properly renewed"
        assert otp.insert_new_OTP(db_conn, db_conn_cursor, new_OTP, current_time, new_expiration_time, user_phone_number), "OTP not recorded"
        session["otp_requested"] = True
        session["otp_request_exp_datetime"] = new_expiration_time
        return True
    except Exception as e:
        return e
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)

def verify_otp(user_phone_number, user_otp):
    try:
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #time now
        current_time = general.get_current_datetime()
        #connect to user database
        if otp.OTP_user_verify(user_otp, db_conn_cursor, user_phone_number, current_time):
            otp.remove_old_OTP(db_conn, db_conn_cursor, user_phone_number)
            session["otp_verified"] = True
            session["otp"] = user_otp
            session["otp_verified_phone_number"] = user_phone_number

        return True
    except Exception as e:
        return e
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)

def create_account(user_email, phone_number, country_code, password, user_first_name, user_last_name, user_preferred_language):
    try:
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        password = sha256_crypt.encrypt(password)
        if user_preferred_language == "my":
            pass
        elif user_preferred_language == "cn":
            pass
        else:
            pass
        #connect to user database
        user_id = user.generate_unique_user_id(db_conn_cursor, "SAMY")
        assert user.create_account(db_conn, db_conn_cursor, user_id, user_email, country_code, phone_number[2:], password, user_first_name, user_last_name, user_preferred_language) == True, "Failed to create account"
        #Send email verification email to user
        try:
            #remove the old one first before adding
            if user.email_verification_key_exist(db_conn_cursor, user_id):
                assert user.remove_email_verification_key(db_conn, db_conn_cursor, user_id) == True, "Old key not removed"
            user_verification_key = user.generate_email_verification_key(db_conn,db_conn_cursor,user_id,user_email)
            assert user.user_specific_send_verification_email(db_conn_cursor, user_id, user_first_name, user_verification_key) == True,\
            "Verification email was not sent. Please request again later in profile page."
        except Exception as e:
            pass
        #Try log user in
        try:
            #Log user in
            log_in_user_result = user.log_in_user(db_conn_cursor, user_id)
            assert log_in_user_result == True, str(user_id)
        except Exception as e:
            pass

        return (True, user_id)
    except Exception as e:
        return e
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)

def create_order(mysql_conn, mysql_cursor, should_notify_sellers, payment_method, user_id, user_checkout_address_id, checkout_shipping_fees, warranty_extension_in_days, cart_items, aitanmall_handling_fees_fixed, aitanmall_handling_fees_percentage, user_first_name, user_last_name, user_phone_number, checkout_discount, free_shipping = False) -> tuple | Exception:
    """
    This method create an order
    :param: cart_items: cart items in the format [{id, cart_prd_id, cart_prd_name, cart_prd_img, cart_quantity, cart_prd_price, cart_prd_var_id, cart_prd_var_name, cart_prd_sku, cart_prd_var_img,cart_sub_total, cart_merchant_id}]
    :return: tuple (cust_orders, total_customer_payment, final_customer_payment, successful_action_count, failed_action_count, failed_reason_msg); Exception else
    """
    #1) Create a Order object
    try:
        current_datetime = general.get_current_datetime()
        checkout_shipping_fees = float(checkout_shipping_fees)
        selected_merchant_payment_method = merchant.select_payment_method_option(mysql_cursor, None, payment_method, True)
        selected_merchant_payment_method_name = selected_merchant_payment_method[0][2]
        
        selected_merchant_payment_method_fixed_fees = float(selected_merchant_payment_method[0][5])
        selected_merchant_payment_method_percent_fees = float(selected_merchant_payment_method[0][6])
        user_checkout_address_details  = user.select_address(mysql_cursor, user_id, user_checkout_address_id, True)
        if user_checkout_address_details == None:
            raise Exception("Shipping address not found")
        user_checkout_address_unit_number = user_checkout_address_details[0][1]
        user_checkout_address_street = user_checkout_address_details[0][2]
        user_checkout_address_city = user_checkout_address_details[0][3]
        user_checkout_address_zip = user_checkout_address_details[0][5]
        user_checkout_address_state = user_checkout_address_details[0][6]
        user_checkout_address_country = user_checkout_address_details[0][7]
        #Append unit number if it is not empty
        user_checkout_address = f"{user_checkout_address_unit_number}, {user_checkout_address_street}, {user_checkout_address_city}, {user_checkout_address_zip}, {user_checkout_address_state}, {user_checkout_address_country}" if\
            user_checkout_address_unit_number != "" else f"{user_checkout_address_street}, {user_checkout_address_city}, {user_checkout_address_zip}, {user_checkout_address_state}, {user_checkout_address_country}"
        assert len(selected_merchant_payment_method) > 0, "Invalid payment method ID"
        assert len(user_checkout_address_details) > 0, "Invalid address ID" 
        #declare successful actions and failed actions
        successful_action_count = 0
        failed_action_count = 0
        failed_reason_msg = ""
        total_customer_payment = 0.00
        merchant_total_dict = dict()
        merchant_shipping_fees = dict()
        current_merchant_id = None
        merchant_telegram_bot = dict()
        merchant_telegram_bot_chat = dict()
        #orders 
        cust_orders = Orders(user_id, current_datetime, 0.00, 0.00, "pending", "pending")
        order_id = cust_orders.get_ord_id()
        assert orders.create_orders(mysql_conn, mysql_cursor, order_id, user_id, user_checkout_address, user_checkout_address_id, payment_method, current_datetime, 0.00, 0.00, 0.00, "pending") == True, "Create order failed"
        
        for i in range(len(cart_items)):
            cart_item = cart_items[i]
            cart_prd_id = cart_item["prd_id"]
            cart_prd_name = cart_item["prd_name"]
            cart_prd_img = cart_item["prd_img"]
            cart_quantity = cart_item["quantity"]
            cart_prd_price = cart_item["prd_price"]
            cart_prd_var_id = cart_item["prd_var_id"]
            cart_prd_var_name = cart_item["prd_var_name"]
            cart_prd_sku = cart_item["prd_sku"]
            cart_prd_var_img = cart_item["prd_var_img"]
            cart_sub_total = cart_item["sub_total"]
            cart_merchant_id = cart_item["merchant_id"]
            
            #if it is a new merchant we then proceed onto getting their shipping option and payment methods
            if current_merchant_id == None or current_merchant_id != cart_merchant_id:
                merchant_telegram_bot_details = merchant.select_telegram_bot(mysql_cursor, cart_merchant_id)
                merchant_telegram_bot[cart_merchant_id] = merchant_telegram_bot_details
                if isinstance(merchant_telegram_bot_details, list) and len(merchant_telegram_bot_details) > 0:
                    merchant_telegram_bot_id = merchant_telegram_bot_details[0][1]
                    merchant_telegram_bot_chat_details = merchant.select_telegram_bot_chat(mysql_cursor, cart_merchant_id, merchant_telegram_bot_id, "orders", True)
                    if isinstance(merchant_telegram_bot_chat_details, list) and len(merchant_telegram_bot_chat_details) > 0:
                        merchant_telegram_bot_chat[cart_merchant_id] = merchant_telegram_bot_chat_details
                    else:
                        merchant_telegram_bot_chat[cart_merchant_id] = None
                merchant_total_dict[cart_merchant_id] = 0.00
                merchant_shipping_fees[cart_merchant_id] = 0.00
                #shipping details
                merchant_shipping_detail = merchant.get_shipping(mysql_cursor, cart_merchant_id)
                merchant_shipping_status = merchant_shipping_detail[0][2]
                merchant_shipping_option_id = merchant_shipping_detail[0][4]
                merchant_shipping_option_details = merchant.get_shipping_option(mysql_cursor, merchant_shipping_option_id)
                merchant_shipping_fixed_fees = merchant_shipping_option_details[0][5]
                merchant_shipping_percentage_fees = float(merchant_shipping_option_details[0][6])
                #add the fixed cost of shipping fees to merchant first
                merchant_shipping_fees[cart_merchant_id] += float(merchant_shipping_fixed_fees)
                #update current_merchant_id and wait for next potential different merchant
                current_merchant_id = cart_merchant_id
            product_warranty_details = product.get_warranty(mysql_cursor, cart_prd_id)
            if isinstance(product_warranty_details, list) and len(product_warranty_details) > 0:
                product_has_warranty = "true"
                product_warranty_period = product_warranty_details[0][1]
                #Change customer warranty to 6 more months if it is member of VIP
                product_warranty_period += warranty_extension_in_days
                    
            else:
                product_has_warranty = "false"
                product_warranty_period = 0
            merchant_shipping_fees[cart_merchant_id] += float(cart_sub_total)*merchant_shipping_percentage_fees/100
            merchant_total_dict[cart_merchant_id] += float(cart_sub_total)
            
            order = Order(id = i, ord_id = order_id, ord_prd_id = cart_prd_id, ord_quantity = cart_quantity, ord_price = cart_prd_price,\
                ord_date = current_datetime, ord_prd_name = cart_prd_name, merchant_id = cart_merchant_id)
            cust_orders.add_ord_details(order)
            assert orders.create_order_details(mysql_conn, mysql_cursor, cart_prd_id, cart_prd_name, cart_prd_img, cart_prd_sku, cart_prd_var_id, cart_prd_var_name, \
                cart_prd_var_img, cart_quantity, cart_prd_price, product_has_warranty, product_warranty_period, cart_merchant_id, order_id) == True, "Create order details failed"
            successful_action_count += 1
        #Merchant Income details
        customer_shipping_discount = 0.00
        for mcht in merchant_total_dict:
            each_merchant_total = merchant_total_dict[mcht]
            each_merchant_shipping_fees = merchant_shipping_fees[mcht]
            each_merchant_final_total = each_merchant_total+each_merchant_shipping_fees
            #keep track of what customer pay because shipping fees are free if user is member
            each_customer_merchant_payment_final = 0.00
            #Change customer shipping fees to 0 if it is member of VIP
            #for customer
            if free_shipping==True:
                each_order_customer_shipping_discount = each_merchant_shipping_fees
            else:
                each_order_customer_shipping_discount = 0.00
            each_customer_merchant_payment_final += each_merchant_final_total - each_order_customer_shipping_discount
            #create income record for merchant
            each_total_aitanmall_handling_fees = aitanmall_handling_fees_fixed + (aitanmall_handling_fees_percentage*each_merchant_final_total/100)
            each_total_payment_gateway_fees = selected_merchant_payment_method_fixed_fees + (selected_merchant_payment_method_percent_fees*each_merchant_final_total/100)
            each_merchant_total_fees = each_total_aitanmall_handling_fees + each_total_payment_gateway_fees + each_merchant_shipping_fees
            each_merchant_total_income = round(each_merchant_final_total - each_merchant_total_fees, 2)
            assert create_merchant_income(mysql_conn, mysql_cursor, order_id, mcht, each_merchant_final_total, each_merchant_shipping_fees, each_total_aitanmall_handling_fees, each_total_payment_gateway_fees, each_merchant_total_income) == True, "System failed to record merchant's income"
            customer_shipping_discount += each_order_customer_shipping_discount
            #Record order shipping
            orders.create_order_fees(mysql_conn, mysql_cursor, each_merchant_shipping_fees, "Shipping fees", order_id)
            
            #send telegram notification if there exists a bot and chat
            if merchant_telegram_bot_chat[mcht] != None:
                if should_notify_sellers:
                    try:
                        merchant_telegram_bot_token = merchant_telegram_bot[mcht][0][3]
                        merchant_telegram_bot_chat_id = merchant_telegram_bot_chat[mcht][0][1]
                        merchant_telegram_order_message = f"""{str(selected_merchant_payment_method_name).upper()} Order\nOrder ID: {order_id}\n\nCustomer Information:\nName: {user_first_name} {user_last_name}\nAddress: {user_checkout_address}\nPostcode: {user_checkout_address_zip}\nContact: {user_phone_number}\nTotal Before Fees: Rm{round(each_merchant_final_total, 2)}\nHandling Fees: Rm{round(each_total_aitanmall_handling_fees, 2)}\nPayment Gateway Fees: Rm{round(each_total_payment_gateway_fees, 2)}\nShipping Fees: Rm{round(each_merchant_shipping_fees, 2)}\nTotal Final: Rm{round(each_merchant_total_income, 2)}\n\n<a href='https://merchant.aitanmall.com/quickcall/check_order?ord_id={order_id}'>Check Order Details</a>\n<a href='api.whatsapp.com/send?phone={user_phone_number}'>Whatsapp Customer Now</a>"""
                        merchant_telegram_response = telegram.send_message(merchant_telegram_bot_token, merchant_telegram_bot_chat_id, merchant_telegram_order_message)
                        assert merchant_telegram_response["ok"] == True
                        successful_action_count += 1
                    except Exception as e:
                        failed_reason_msg += f"Failed to notify seller.\n"
                        failed_action_count += 1
            total_customer_payment += each_customer_merchant_payment_final
        final_customer_payment = total_customer_payment - checkout_discount
        #Update order details
        assert orders.update_orders(mysql_conn, mysql_cursor, payment_method, total_customer_payment, customer_shipping_discount, final_customer_payment,"pending", order_id) == True, "Failed to update orders"
        return (cust_orders, total_customer_payment, final_customer_payment, successful_action_count, failed_action_count, failed_reason_msg)
    except Exception as e:
        return e

def create_merchant_income(mysql_conn, mysql_cursor, order_id, merchant_id, merchant_final_total, merchant_shipping_fees, total_aitanmall_handling_fees, total_payment_gateway_fees, merchant_total_income):
    try:
        current_datetime = general.get_current_datetime()
        merchant_income_id = merchant.create_income(mysql_conn, mysql_cursor, merchant_final_total, merchant_total_income, current_datetime, "pending", order_id, merchant_id)
        assert not isinstance(merchant_income_id, Exception) and merchant_income_id != None, "Merchant's income not recorded."
        assert merchant.create_income_details(mysql_conn, mysql_cursor, total_aitanmall_handling_fees, "AiTanMall handling fees", merchant_income_id) == True, "Handling fees not recorded"
        assert merchant.create_income_details(mysql_conn, mysql_cursor, total_payment_gateway_fees, "Payment gateway fees", merchant_income_id),  "Payment gateway fees not recorded"
        assert merchant.create_income_details(mysql_conn, mysql_cursor, merchant_shipping_fees, "Shipping fees", merchant_income_id),  "Shipping fees not recorded"
        return True
    except Exception as e:
        return e

# API URL
@api.route("request_otp_create_account", methods=["POST"])
def request_otp_create_account():
    try:
        passcheck = 2
        msg = "ERROR"
        assert request.method == "POST", "REQUEST ERROR"
        g_response = request.form["g-response"]
        assert len(g_response) > 0, "REQUEST ERROR#2"
        assert general.pass_recaptcha_v3_test(g_response), "REQUEST ERROR#3"
        #get user preferred lanaguage
        language = session.get("language", None)
        language = "eng" if language == None else language
        # otp_request_exp_datetime = session.get("otp_request_exp_datetime")
        # if otp_request_exp_datetime == None or current_time > otp_request_exp_datetime:
        user_phone_number = html.escape(str(request.form["phone_number"]))
        #modify phone number to include country code
        country_code = "60"
        user_phone_number = general.standardize_phone_number(user_phone_number, country_code)
        user_password = html.escape(request.form["password"])
        user_password2 = html.escape(request.form["password2"])
        
        #verify password and proceed
        assert user_password == user_password2, "Please make sure both passwords match"
        assert len(str(user_password)) >= 8, "Password has to be 8 or more characters."
        request_for_otp = request_otp(user_phone_number, language)
        assert request_for_otp == True, request_for_otp
        passcheck = 1
        msg = "Success"
    except Exception as e:
        passcheck = 3
        msg = str(e)
    finally:
        return jsonify({"passcheck":passcheck, "msg":msg})

@api.route("resend_user_otp", methods=["POST"])
def resend_user_otp():
    try:
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        assert request.method == "POST", "REQUEST ERROR"
        assert session.get("otp_requested") == True, "REQUEST ERROR#2"
        #generate current time and new time for easier access
        current_time = general.get_current_datetime()
        new_expiration_time = general.get_datetime_from_now(300)
        # #use try block so we can do finally
        user_phone_number = html.escape(str(request.form["phone_number"]))
        #modify phone number to include country code
        user_phone_number = general.standardize_phone_number(user_phone_number, "60")
        #connect to user database
        assert otp.OTP_regenation_permitted(db_conn_cursor, user_phone_number, current_time), "Please request OTP in 5 minutes."
        #generate random otp number
        new_OTP = otp.generate_unique_OTP(db_conn_cursor, user_phone_number)
        result = twilio.send_sms("AiTan SDN. BHD.: {} is your OTP. Please do not share with anyone.".format(new_OTP)\
          , user_phone_number)
        result_status = result.status
        testing = False
        assert (testing or result_status in ["queued", "accepted", "sent", "delivered"]), "OTP not delivered"
        assert otp.remove_old_OTP(db_conn, db_conn_cursor, user_phone_number), "Old otp not removed"
        assert otp.insert_new_OTP(db_conn, db_conn_cursor, new_OTP, current_time, new_expiration_time, user_phone_number), "New OTP not recorded"
        passcheck = 1
        msg = "OTP has been resent successfully."
        session["otp_requested"] = True
    except Exception as e:
        passcheck = 2
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
    return jsonify({"passcheck":passcheck, "msg":msg})

@api.route("verify_user_otp", methods=["POST"])
def verify_user_otp():
    try:
        assert request.method == "POST", "Invalid request"
        assert session.get("otp_requested") == True, "Request OTP first before verifying"
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        user_phone_number = html.escape(str(request.form["phone_number"]))
        user_otp = html.escape(request.form["otp"])
        #modify phone number to include country code
        user_phone_number = general.standardize_phone_number(user_phone_number)
        #connect to user database
        if verify_otp(user_phone_number, user_otp) == True:
            passcheck = 1
            msg = "Success"
        else:
            passcheck = 2
            msg = "OTP has expired or invalid. Please request again."
    except Exception as e:
        passcheck = 3
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify({"passcheck":passcheck, "msg":msg})

@api.route("create_user_account", methods=["POST"])
def create_user_account():
    try:
        passcheck = 2
        msg = "ERROR"
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        assert request.method == "POST", "ERROR#1"
        assert session.get("otp_verified"), "ERROR#2"
        user_first_name = html.escape(str(request.form["first_name"]))
        user_last_name = html.escape(str(request.form["last_name"]))
        user_email = html.escape(str(request.form["email"]))
        phone_number = html.escape(str(request.form["phone_number"]))
        password = html.escape(str(request.form["password"]))
        password2 = html.escape(str(request.form["password2"]))
        country_code = "60"
        phone_number = general.standardize_phone_number(phone_number, country_code)
        user_preferred_language = session.get("language", None)
        if user_preferred_language == None:
            user_preferred_language = "eng"

        if user_preferred_language == "cn":
            failed_to_create_account_msg = "System failed to create account"
            failed_to_log_you_in_msg = "系统未能让您登录到您的帐户"
            account_exists_msg = "您的电子邮件或电话号码已经注册。请先尝试使用不同的电子邮件再次尝试。"
        elif user_preferred_language == "my":
            failed_to_create_account_msg = "System failed to create account"
            failed_to_log_you_in_msg = "Sistem gagal untuk log masuk anda ke dalam akaun anda"
            account_exists_msg = "Penghantaran e-mel ATAU nombor telefon anda telah didaftarkan. Cuba lagi dengan e-mel yang berbeza terlebih dahulu."
        else:
            failed_to_create_account_msg = "System failed to create account"
            failed_to_log_you_in_msg = "System failed to log you into your account"
            account_exists_msg = "Your email OR phone number has been registered. Try again with different email first."

        assert session.get("otp_verified_phone_number") == phone_number, "ERROR#3"
        assert password == password2, "Please make sure both password matches"
        assert user.account_exist(db_conn_cursor, user_email, phone_number) != True, account_exists_msg
        create_account_result = create_account(user_email, phone_number, country_code, password, user_first_name, user_last_name, user_preferred_language)
        assert isinstance(create_account_result, tuple) and create_account_result[0] == True, failed_to_create_account_msg
        user_id = create_account_result[1]
        passcheck = 1
        msg = "Account created! Welcome! Check out more to have the best shopping experience!"
        
        #FOR PROMOTION ONLY!!!!
        voucher_details = voucher.select_voucher(db_conn_cursor, None, "NEWUSER20", by_code= True)
        voucher_id = voucher_details[0][1]
        if voucher.assign_user_voucher(db_conn, db_conn_cursor, 1, voucher_id, user_id) == True:
            msg += "20% OFF Voucher has been added to your account!"
        else:
            msg += "20% OFF Voucher failed to be added to your account. Please contact us to add one for you at whatsapp +6011-5775-3538!"
        
        passcheck = 1
    except Exception as e:
        passcheck = 2
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify({"passcheck":passcheck, "msg":msg})
        
@api.route("log_in_user", methods = ["POST"])
def log_in_user():
    try:
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        assert request.method == "POST", "REQUEST ERROR"
        g_response = request.form["g-response"]
        assert len(g_response) > 0, "REQUEST ERROR#2"
        assert general.pass_recaptcha_v3_test(g_response), "REQUEST ERROR#3"
        user_phone_number = html.escape(str(request.form["phone_number"]))
        user_phone_number = general.standardize_phone_number(user_phone_number, "60")
        password = request.form["password"]
        #change cursor to user database
        
        user_id = user.user_log_in_details_is_valid(db_conn_cursor, user_phone_number[2:], password)
        assert user_id != None, "Username/Password invalid"
        log_in_user_result = user.log_in_user(db_conn_cursor, user_id)
        assert log_in_user_result == True, log_in_user_result
        #generate cookie for automatic login when user visit back
        temporarily_key = general.generate_random_string(20)
        created_datetime = general.get_current_datetime()
        seconds_in_a_month = 2628288
        expire_datetime = general.get_datetime_from_now(seconds_in_a_month)
        if user.user_temporarily_key_exist(db_conn_cursor, user_id):
            assert user.remove_user_temporarily_key(db_conn, db_conn_cursor, user_id), "Old temporarily key not removed"
        assert user.insert_user_temporarily_key(db_conn, db_conn_cursor, temporarily_key, created_datetime, expire_datetime, user_id), "Temporarily key not recorded"
        passcheck = 1
        msg = "Welcome"
    except Exception as e:
        passcheck = 3
        msg = str(e)
        temporarily_key = None
        user_id = None
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_cursor(db_conn)
    return jsonify({"passcheck":passcheck, "msg":msg, "temporarily_key":temporarily_key, "user_id":user_id})

@api.route("create_user_temporarily_key", methods=["POST"])
def create_user_temporarily_key():
    try:
        assert request.method == "POST", "ERROR#1"
        temporarily_key = request.form["temporarily_key"]
        user_id = request.form["user_id"]

        # Create a response object
        response = make_response()
        seconds_in_a_month = 2628288
        # Set the cookie using the Set-Cookie header
        response.set_cookie(
            "temporarily_key",
            value=temporarily_key,
            max_age=seconds_in_a_month,
            secure=True,  # Set secure flag for HTTPS-only transmission
            httponly=True,  # Set HTTP-only flag to prevent JavaScript access
            samesite='Strict'  # Set SameSite attribute to 'Strict'
        )
        response.set_cookie(
            "user_id",
            value=user_id,
            max_age=seconds_in_a_month,
            secure=True,  # Set secure flag for HTTPS-only transmission
            httponly=True,  # Set HTTP-only flag to prevent JavaScript access
            samesite='Strict'  # Set SameSite attribute to 'Strict'
        )
    except:
        response = jsonify({"passcheck":3})
    return response

@api.route("remove_user_temporarily_key", methods=["POST"])
def remove_user_temporarily_key():
    try:
        assert request.method == "POST", "ERROR#1"
        # Create a response object
        response = make_response()
        # Set the cookie using the Set-Cookie header
        response.set_cookie(
            "temporarily_key",
            max_age=0,
            secure=True,  # Set secure flag for HTTPS-only transmission
            httponly=True,  # Set HTTP-only flag to prevent JavaScript access
            samesite='Strict'  # Set SameSite attribute to 'Strict'
        )
        response.set_cookie(
            "user_id",
            max_age=0,
            secure=True,  # Set secure flag for HTTPS-only transmission
            httponly=True,  # Set HTTP-only flag to prevent JavaScript access
            samesite='Strict'  # Set SameSite attribute to 'Strict'
        )
    except:
        response = jsonify({"passcheck":3})
    return response

@api.route("user_activate_membership", methods=["POST"])
def user_activate_membership():
    current_domain = current_app.config.get("DOMAIN_NAME")
    try:
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()

        passcheck = 4
        msg = "ERROR"
        redirect = ""
        
        action = html.escape(str(request.form["action"]))
        option_id = html.escape(str(request.form["option_id"]))
        assert action == "user_activate_membership", "Invalid verification#1"
        assert option_id != None, "Invalid option ID"
        assert session.get("user_id") != None, "User not logged in"
        user_id = session.get("user_id")
        user_email = session.get("user_email")
        
        stripe_api_key = strp.get_key()
        assert strp.price_id_valid(stripe_api_key, option_id), "Option ID Invalid"
        stripe_price = strp.get_price(stripe_api_key, option_id)
        stripe_prd_id = stripe_price["product"]
        
        subscription = user.get_subscription_product_from_stripe_id(db_conn_cursor,stripe_prd_id,option_id)
        assert subscription != None, "No subscriptable product found. Sorry."
        subscription_product_id = subscription[0][1]
        subscription_free_trial_period = subscription[0][6]
        if user.user_specific_set_up_is_complete(db_conn_cursor, user_id):
            #update msg and redirect
            msg = "Please add a payment method first."
            redirect = "profile#addPaymentMethodBtn"
            
            if strp.customer_exist(stripe_api_key,user_email):
                user_stripe_customer = user.get_stripe_customer_id(db_conn_cursor, user_id)
                user_stripe_customer_id = user_stripe_customer[1]
                if strp.customer_payment_method_exist(stripe_api_key,user_stripe_customer_id,type="card"):
                    assert user.get_stripe_subscription_id(db_conn_cursor, user_stripe_customer_id, "active", by_status= True) == None, "System record says you already have an active subscription."
                    user_membership_subscription = user.get_subscription(db_conn_cursor, user_id, subscription_product_id, by_product_id=True)
                    #check if there's existing membership
                    user_membership_exists = False
                    if user_membership_subscription != None:
                        user_membership_exists = True
                        user_membership_subscription_status = user_membership_subscription[0][2]
                        if user_membership_subscription_status == "active" :
                            raise Exception("You have already activate your VIP membership.")
                        elif user_membership_subscription_status == "cancelled":
                            user_cancelled_subscription = user_membership_subscription
                    #Initial free trial period
                    subscription_free_trial_period_in_seconds = (subscription_free_trial_period*24*60*60)+120

                    if not user_membership_exists:
                        pass
                    elif user_membership_exists:
                        #get current datetime and compare to the previous recorded first bill date (fbd)
                        #if current datetime >= fbd, free trial period = 0
                        #else free trial period = fbd - current datetime
                        current_datetime = general.get_current_datetime()
                        user_cancelled_membership_data = user_cancelled_subscription[0]
                        user_cancelled_membership_bill_start_date = str(user_cancelled_membership_data[4])
                        if current_datetime >= user_cancelled_membership_bill_start_date:
                            subscription_free_trial_period_in_seconds = 0
                        else:
                            subscription_free_trial_period_in_seconds = general.get_datetime_difference(user_cancelled_membership_bill_start_date, current_datetime, absolute= True)
                    else:
                        raise Exception("Fatal error. Contact customer support")
                    subscription_free_trial_end = general.get_unix_datetime_from_now(subscription_free_trial_period_in_seconds)
                    success_url = current_domain+"/user/membership/checkout"
                    cancel_url = current_domain+"/user/membership/checkout"
                    item_list = [{"price":option_id, "quantity":1},]
                    checkout_session = strp.create_subscription_checkout(stripe_api_key, user_stripe_customer_id, item_list, success_url, cancel_url, subscription_free_trial_end)
                    user_stripe_checkout_session_id = checkout_session["id"]
                    assert user.record_stripe_checkout_session(db_conn,db_conn_cursor,user_stripe_checkout_session_id,"subscription",user_id), "Checkout session ID not recorded"
                    msg = "You will be redirect to Stripe checkout. After you have successfully pay, you will be redirect back! Thanks!"
                    redirect = checkout_session["url"]  
        else: 
            passcheck = 4
            msg = "Please complete your profile set up."
            redirect = "/user/profile"
    except Exception as e:
        passcheck = 3
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})
    
@api.route("user_change_language", methods=["POST"])
def user_change_language():
    try:
        passcheck = 2
        msg = "ERROR"
        language = request.form.get("language", None)
        assert language != None, "Language selected cannot be None"
        allowed_languages = ["eng", "cn", "my"]
        assert language in allowed_languages, "Language selected is invalid"
        user_id = session.get("user_id", None)
        assert user_id != None and user_id[:4] == "SAMY", "User not logged in"
        
        #connect to db 
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()

        assert user.update_language_settings(db_conn, db_conn_cursor, language, user_id) == True, "Language preference not updated"
        session["language"] = language
        passcheck = 1
        msg = f"Language changed to {language}"
    except Exception as e:
        msg = str(e)
    finally:
        return jsonify({"passcheck":passcheck, "msg":msg})

@api.route("user_add_address", methods=["POST"])
def user_add_address():
    try:
        #initiate all neccessary variables
        redirect = ""
        passcheck = 2
        msg = "ERROR"
        #making sure conditions are met
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        assert request.method == "POST", "ERROR#1"
        street = html.escape(str(request.form["street"]))
        unit_number = html.escape(str(request.form["unitNumber"]))
        assert len(str(unit_number)) >= 0, "Please make sure your unit number is string. Example: 32"
        unit_number = "" if len(str(unit_number)) == 0 else unit_number
        city = html.escape(str(request.form["city"]))
        zip = html.escape(str(request.form["zip"]))
        state = html.escape(str(request.form["state"]))
        country = html.escape(str(request.form["country"]))
        user_id = session.get("user_id", None)
        assert user_id != None and user_id[:4] == "SAMY", "User not logged in"
        newly_created_shipping_address_id = user.user_specific_add_address(db_conn, db_conn_cursor, user_id, street, city, zip, state, country, unit_number)
        if not isinstance(newly_created_shipping_address_id, Exception) and newly_created_shipping_address_id != None:
            user_shipping_address = user.get_shipping_address(db_conn_cursor, user_id, 1)
            assert isinstance(user_shipping_address, list), "System failure on select user's shipping address"
            if len(user_shipping_address) > 0:
                status = "backup"
            else:
                status = "default"
            assert user.add_shipping_address(db_conn, db_conn_cursor, user_id, newly_created_shipping_address_id, status) == True,\
                "Shipping address not added"
            passcheck = 1
        
        msg = "Address added!"
    except Exception as e:
        passcheck = 3
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})

@api.route("user_remove_address", methods=["POST"])
def user_remove_address():
    try:
        #initiate all neccessary variables
        redirect = ""
        passcheck = 2
        msg = "ERROR"
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        #connect to DB
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        addressId = html.escape(str(request.form["addressId"]))
        user_id = session.get("user_id", None)
        assert user_id != None and user_id[:4] == "SAMY", "User not logged in"
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)
        if language == "cn":
            default_address_cannot_remove = "在删除默认地址之前，请添加另一个备用地址并将其设为默认地址。"
            no_default_shipping_address_found_msg = "No default address found. Please add one default address."
        elif language == "my":
            default_address_cannot_remove = "Sila tambah alamat sandaran lain dan jadikan ia alamat lalai sebelum menghapuskan alamat lalai."
            no_default_shipping_address_found_msg = "No default address found. Please add one default address."
        else:
            default_address_cannot_remove = "Please add another backup address and make it default before removing default address."
            no_default_shipping_address_found_msg = "No default address found. Please add one default address."
        
        user_default_shipping_address = user.get_default_shipping_address(db_conn_cursor, user_id)
        assert isinstance(user_default_shipping_address, list) and len(user_default_shipping_address) > 0 ,no_default_shipping_address_found_msg
        assert str(user_default_shipping_address[0][1]) != addressId, default_address_cannot_remove
        if user.user_specific_remove_address(db_conn, db_conn_cursor, user_id, addressId):
            passcheck = 1
            msg = "Address removed!"
    except Exception as e:
        passcheck = 3
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})

@api.route("user_add_payment_method", methods=["POST"])
def user_add_payment_method():
    try:
        current_domain = current_app.config.get("DOMAIN_NAME")
        #initiate all neccessary variables
        redirect = ""
        passcheck = 2
        msg = "ERROR"
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "add_payment_method", "ERROR#2"
        user_id = session.get("user_id", None)
        assert user_id != None and user_id[:4] == "SAMY", "User not logged in"
        user_email = session.get("user_email")
        user_first_name = session.get("user_first_name")
        user_last_name = session.get("user_last_name")
        user_phone_number = session.get("user_phone_number")
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        if user.user_specific_set_up_is_complete(db_conn_cursor, user_id):
            if user.user_specific_email_is_verified(db_conn_cursor, user_id):
                api_key = strp.get_key()
                user_address = user.user_specific_get_address(db_conn_cursor, user_id, 1)
                user_address_dict = dict()
                user_address_dict["city"] = str(user_address[0][3]).capitalize()
                user_address_dict["country"] = strp.get_country_code(str(user_address[0][6]).capitalize())
                user_address_dict["line1"] = user_address[0][2]
                user_address_dict["line2"] = user_address[0][1]
                user_address_dict["postal_code"] = user_address[0][4]
                user_address_dict["state"] = str(user_address[0][5]).capitalize()
                #if customer exist we get their customer ID
                if strp.customer_exist(api_key, user_email) == True:
                    #change cursor to user database
                    use_db(db_conn_cursor, "user")

                    user_stripe_customer = user.get_stripe_customer_id(db_conn_cursor,user_id)
                    user_stripe_customer_id = user_stripe_customer[1]
                #if customer dont exist, we create one and get ID
                else:
                    customer_created = strp.create_customer(api_key, str(user_first_name+" "+user_last_name), user_phone_number, user_email, user_address_dict)
                    if len(customer_created) > 0:
                        user_stripe_customer_id = customer_created["id"]
                        assert user.add_stripe_customer_id(db_conn, db_conn_cursor, user_stripe_customer_id, user_id), "Customer ID not recorded"
                
                assert user_stripe_customer_id != None and len(user_stripe_customer_id) > 0, "Customer ID for user not found"
                success_url = current_domain+"/user/profile"
                cancel_url = current_domain+"/user/profile"
                user_stripe_checkout_session = strp.set_up_payments(api_key, user_stripe_customer_id, success_url, cancel_url)
                user_stripe_checkout_session_id = user_stripe_checkout_session["id"]
                redirect = user_stripe_checkout_session["url"]
                assert len(user_stripe_checkout_session_id) > 0, "Session ID is not valid"
                assert user.record_stripe_checkout_session(db_conn,db_conn_cursor,user_stripe_checkout_session_id,"setup",user_id), "Checkout session ID not recorded"
                passcheck = 4
                msg = "You will be redirect to Stripe for adding payment method. You will be redirected back once done. See ya!"
            else:
                msg = "Please verify your email first, thanks"
        else:
            msg = "Add a address first"
    except Exception as e:
        passcheck = 3
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})

@api.route("user_create_stripe_portal_session", methods=["POST"])
def user_create_stripe_portal_session():
    current_domain = current_app.config.get("DOMAIN_NAME")
    try:
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #initiate all neccessary variables
        redirect = ""
        passcheck = 4
        msg = "ERROR"
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "create_portal_session", "ERROR#2"
        user_id = session.get("user_id", None)
        assert user_id != None and user_id[:4] == "SAMY", "User not logged in"
        user_email = session.get("user_email")
        user_first_name = session.get("user_first_name")
        user_last_name = session.get("user_last_name")
        user_phone_number = session.get("user_phone_number")
        if user.user_specific_set_up_is_complete(db_conn_cursor, user_id):
            api_key = strp.get_key()
            #if customer exist we get their customer ID
            if strp.customer_exist(api_key,user_email):
                user_stripe_customer = user.get_stripe_customer_id(db_conn_cursor,user_id)
                user_stripe_customer_id = user_stripe_customer[1]
                return_url = current_domain+"/user/profile"
                portal_session = strp.create_portal_session(api_key,user_stripe_customer_id,return_url)
                redirect = portal_session["url"]
                msg = "You will be redirect to Stripe's portal"
    except Exception as e:
        passcheck = 3
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
    return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})

@api.route("user_join_general_cs", methods=["POST"])
def user_join_general_cs():
    try:
        passcheck = 2
        msg = "ERROR"
        redirect = ""
        api_key = ""
        room_id = ""
        user_id = session.get("user_id", None)
        assert user_id != None and user_id[:4] == "SAMY", "Please log in to user the live chat service"
        api_key = "u17828bdabd1782gdbaudsbaby1812b"
        room_id = user_id
        passcheck = 1
    except Exception as e:
        msg = str(e)
    finally:
        return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect, "api_key":api_key, "room_id":room_id})

@api.route("guest_change_language", methods = ["POST"])
def guest_change_language():
    try:
        passcheck = 2
        msg = "ERROR"
        language = request.form.get("language", None)
        assert language != None, "Language selected cannot be None"
        session["language"] = language
        passcheck = 1
        msg = f"Language changed to {language}"
    except Exception as e:
        msg = str(e)
    finally:
        return jsonify({"passcheck":passcheck, "msg":msg})

@api.route("user_add_to_cart", methods=["POST"])
def user_add_to_cart():
    try:
        #initiate all neccessary variables
        msg = "ERROR"
        passcheck = 3
        response = {"passcheck":passcheck, "msg":msg}
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "add_to_cart", "ERROR#2"
        user_id = session.get("user_id", None)
        language = user.user_specific_get_language(db_conn_cursor, user_id)
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        if language == "cn":
            wrong_api_msg = "Invalid request. Please refresh browser"
            crucial_ids_not_found_message = "其中一个重要ID无法被侦测"
            product_not_found_message = "无法在系统中找到要添加到购物车的产品。"
            product_variation_not_found_message = "您选择的产品变种已经不存在。"
            product_not_added_to_cart_message = "无法将产品添加到购物车。对不起。"
            product_exist_message = "产品已添加到购物车"
            merchant_product_id_unmatched_message = "商家的产品不存在。"
            failed_to_clear_session_message = "系统无法更新您的购物车项目。"
            confirm_btn_text = "好的。请带我去创建账户并获得50%的折扣券。"
            cancel_btn_text = "不。请带我去购买此产品。"
            product_id_and_var_id_invalid_msg = "Product ID and the variation you chosed are invalid"
        elif language == "my":
            wrong_api_msg = "Invalid request. Please refresh browser"
            crucial_ids_not_found_message = "ID yang penting tidak didapatkan"
            product_not_found_message = "Produk untuk ditambah ke troli tidak dapat ditemui dalam sistem."
            product_variation_not_found_message = "Varian produk yang anda pilih tidak lagi wujud."
            product_not_added_to_cart_message = "Produk tidak dapat ditambah ke troli. Maaf."
            product_exist_message= "Produk sudah ditambah ke dalam troli"
            merchant_product_id_unmatched_message = "Produk dari penjual tidak wujud."
            failed_to_clear_session_message = "System gagal mengemas kini item dalam troli anda."
            confirm_btn_text = "Ya. Sila ubah hala saya untuk mendaftarkan akaun dan dapatkan baucar diskaun 50%."
            cancel_btn_text = "Tidak. Sila ubah hala saya untuk membeli produk ini."
            product_id_and_var_id_invalid_msg = "Product ID and the variation you chosed are invalid"
        else:
            wrong_api_msg = "Invalid request. Please refresh browser"
            crucial_ids_not_found_message = "One of the crucial ID was not found"
            product_not_found_message = "Product to add to cart cannot be found in system."
            product_variation_not_found_message = "The product variation you selected no longer exists"
            product_not_added_to_cart_message = "Product cannot be add to cart. Sorry"
            product_exist_message = "Product already added to cart"
            merchant_product_id_unmatched_message = "Product from merchant does not exists."
            failed_to_clear_session_message = "System failed to update your cart items."
            confirm_btn_text = "Sure. Please redirect me to create account and get 50%"+" diskaun voucher."
            cancel_btn_text = "No. Please redirect me to buy this product."
            product_id_and_var_id_invalid_msg = "Product ID and the variation you chosed are invalid"
        #ASsserting 
        assert user_id != None, wrong_api_msg
        #Data from client side
        prd_id = request.form.get("prd_id", None)
        merchant_id = request.form.get("merchant_id", None)
        prd_var_id = request.form.get("prd_var_id", None)
        #Data ensuring
        assert prd_id != None and merchant_id != None, crucial_ids_not_found_message
        if prd_var_id == None:
            prd_var_id = -1
        prd_var_id = int(prd_var_id)
        assert prd_var_id >= -1, "Product variation ERROR"
        assert merchant.product_id_exists(db_conn_cursor, merchant_id, prd_id) == True, merchant_product_id_unmatched_message
        #1 check if prd_id already exists in the cart, if yes, just return passcheck 1
        if user.user_specific_cart_prd_exist(mysql_cursor = db_conn_cursor, user_id = user_id, product_id = prd_id,\
                merchant_id=merchant_id, product_variation_id = prd_var_id) == True:
            passcheck = 1
            raise Exception(product_exist_message)
        #2 prd_id doesn't exist so we add to card
        prd_details = general.select_product(db_conn_cursor, merchant_id= merchant_id, product_id= prd_id, by_merchant= False)
        assert prd_details != None, product_not_found_message
        #clear session first
        assert user.reset_checkout_sessions() == True, failed_to_clear_session_message
        id = prd_details[0]
        prd_name = prd_details[1]
        prd_status = prd_details[2]
        prd_price = prd_details[3]
        prd_price = float(prd_price)
        prd_offer_price = prd_details[4]
        prd_offer_price = float(prd_offer_price)
        prd_image = prd_details[5]
        prd_quantity = prd_details[6]
        prd_quantity = int(prd_quantity)
        prd_sku = prd_details[7]
        prd_date = prd_details[8]
        prd_level = prd_details[9]
        prd_cost = prd_details[10]
        prd_preorders_status = prd_details[11]
        prd_id = prd_details[12]
        if prd_var_id != -1:
            prd_var_details = merchant.get_product_variation(db_conn_cursor, prd_var_id, None, False)
            assert prd_var_details != None, product_variation_not_found_message
            prd_var_name = prd_var_details[0][1]
            prd_var_price = prd_var_details[0][3]
            prd_var_price = float(prd_var_price)
            prd_var_sku = prd_var_details[0][5]
            prd_var_img = prd_var_details[0][6]
            prd_image = prd_var_img if prd_var_img != "" and prd_var_img != "none" else prd_image
        else:
            prd_var_name = ""
            prd_var_price = -1.00
            prd_var_sku = "none"
            prd_var_img = "none"
        
        quantity = 1
        prd_sku = prd_var_sku if prd_var_sku not in ["none", None] else prd_sku
        prd_price = prd_var_price if prd_var_price != -1.00 else prd_offer_price
        sub_total = prd_price*quantity
        other_fees = 0.00
        total = sub_total + other_fees
        
        assert user.user_specific_add_to_cart(mysql_conn = db_conn, mysql_cursor = db_conn_cursor, user_id = user_id, product_id = prd_id, product_name = prd_name,  product_image = prd_image, quantity = quantity,\
            price = prd_price, product_variation_id = prd_var_id, product_variation_name = prd_var_name, product_sku = prd_sku, product_variation_image = prd_var_img, sub_total = sub_total,\
            total = total, merchant_id=merchant_id) == True, product_not_added_to_cart_message
        passcheck = 1
        response = {"passcheck":passcheck, "msg":msg}
        return jsonify(response)
    except Exception as e:
        msg = str(e)
        response = {"passcheck":passcheck, "msg":msg}
        return jsonify(response)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        

@api.route("user_update_cart_item", methods=["POST"])
def user_update_cart_item():
    try:
        #initiate all neccessary variables
        redirect = ""
        passcheck = 4
        msg = "ERROR"
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "increaseCartItemQuantity" or action == "decreaseCartItemQuantity", "ERROR#2"
        update_action = "increase" if action == "increaseCartItemQuantity" else "decrease"
        user_id = session.get("user_id", None)
        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        if language == "cn":
            not_logged_in_error_message = "请您在添加产品入购物车前事先登录您的账号. 不好意思."
            redeuce_cart_item_fail_message = "系统无法移除购物车中的商品"
            redeuce_cart_item_fail_message = "系统无法减少购物车中的商品数量"
            increase_cart_item_fail_message = "系统无法增加购物车中的商品数量"
            failed_to_clear_session_message = "系统无法更新您的购物车项目。"
        elif language == "my":
            not_logged_in_error_message = "Sila log in sebelum tambah produk ke kart ye. Minta maaf!"
            redeuce_cart_item_fail_message = "Sistem gagal untuk mengeluarkan item dari troli"
            redeuce_cart_item_fail_message = "Sistem gagal untuk mengurangkan kuantiti item dalam troli"
            increase_cart_item_fail_message = "Sistem gagal untuk menambah kuantiti item dalam troli"
            failed_to_clear_session_message = "System gagal mengemas kini item dalam troli anda."
        else:
            not_logged_in_error_message = "Please log in before adding product to cart. Sorry for the inconvinience."
            redeuce_cart_item_fail_message = "System failed to reduce cart item quantity."
            increase_cart_item_fail_message = "System failed to increase cart item quantity."
            failed_to_clear_session_message = "System failed to update your cart items."

        if user_id == None or user_id[:4] != "SAMY":
            passcheck = 4
            redirect = "/user/login"
            raise Exception(not_logged_in_error_message)
        #change cursor to user_specific database
        cart_item_id = request.form.get("cart_item_id", None)
        quantity = request.form.get("quantity", None)
        cart_item_id = html.escape(cart_item_id)
        quantity = html.escape(quantity)
        quantity = int(quantity)
        #clear session first
        assert user.reset_checkout_sessions() == True, failed_to_clear_session_message

        if update_action == "decrease":
            assert user.user_specific_reduce_cart_item(mysql_conn = db_conn, mysql_cursor=db_conn_cursor, user_id=user_id,\
             cart_item_id = cart_item_id, quantity = quantity) == True, redeuce_cart_item_fail_message
        else:
            assert user.user_specific_increase_cart_item(mysql_conn = db_conn, mysql_cursor=db_conn_cursor, user_id=user_id,\
             cart_item_id = cart_item_id, quantity = quantity) == True, increase_cart_item_fail_message
        
        passcheck = 1
    except Exception as e:
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
    return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})

@api.route("update_checkout_address", methods=["POST"])
def update_checkout_address():
    try:
        #initiate all neccessary variables
        redirect = ""
        passcheck = 4
        msg = "ERROR"
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "update_checkout_address", "ERROR#2"
        user_id = session.get("user_id", None)
        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)

        #make sure user is logged in
        redirect = "/user/login"
        assert user_id != None and user_id[:4] == "SAMY", "Please relogin as some of your information is lost."
        #data
        address_id = request.form.get("address_id", None)
        assert address_id != None, "Address ID cannot be None"
        user_address = user.select_address(db_conn_cursor, user_id, address_id, True)
        assert isinstance(user_address, list) and len(user_address) > 0, "Address ID invalid"
        session["user_checkout_address_id"] = int(address_id)
        passcheck = 1
        msg = "Successfully changed address!"
    except Exception as e:
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
    return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})

@api.route("update_checkout_payment_method", methods=["POST"])
def update_checkout_payment_method():
    try:
        #initiate all neccessary variables
        redirect = ""
        passcheck = 4
        msg = "ERROR"
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "update_checkout_payment_method", "ERROR#2"
        user_id = session.get("user_id", None)
        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)

        if language == "cn":
            empty_nku_error_msg = "所选付款方式不能为空"
            invalid_nku_error_msg = "付款方式ID无效" 
            empty_default_card_msg = "请先添加借记卡/信用卡!"
            please_relogin_message = "由于您的部分信息已丢失，请重新登录。"
        elif language == "my":
            empty_nku_error_msg = "Kaedah pembayaran yang dipilih tidak boleh menjadi Tiada"
            invalid_nku_error_msg =  "ID Kaedah Pembayaran tidak sah"
            empty_default_card_msg = "Sila tambahkan kad debit/kredit dahulu!"
            please_relogin_message =  "Sila log masuk semula kerana beberapa maklumat anda hilang."
        else:
            empty_nku_error_msg = "Selected payment method cannot be None"
            invalid_nku_error_msg = "Payment Method ID invalid"
            empty_default_card_msg = "Please add a debit/credit card first!"
            please_relogin_message = "Please relogin as some of your information is lost."
        #make sure user is logged in
        redirect = "/user/login"
        assert user_id != None and user_id[:4] == "SAMY", please_relogin_message
        #data
        payment_method_nku = request.form.get("payment_method_nku", None)
        assert payment_method_nku != None, empty_nku_error_msg
        payment_method_details = merchant.select_payment_method_option(db_conn_cursor, None, payment_method_nku, True)
        assert isinstance(payment_method_details, list) and len(payment_method_details) > 0, invalid_nku_error_msg
        session["user_checkout_payment_method"] = payment_method_nku
        if payment_method_nku == "card":
            user_default_card_details = user.get_default_payment_card(db_conn_cursor, user_id)
            redirect = "/user/profile"
            assert isinstance(user_default_card_details, list) and len(user_default_card_details) > 0, empty_default_card_msg
            session["user_checkout_payment_method_name"] = str(user_default_card_details[0][2]).capitalize()+" ending in "+str(user_default_card_details[0][2])
        else:
            session["user_checkout_payment_method_name"] = payment_method_details[0][2]

        passcheck = 1
        msg = "Successfully changed payment method!"
    except Exception as e:
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
    return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})

@api.route("update_checkout_voucher", methods=["POST"])
def update_checkout_voucher():
    try:
        #initiate all neccessary variables
        redirect = ""
        passcheck = 4
        msg = "ERROR"
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "update_checkout_voucher", "ERROR#2"
        user_id = session.get("user_id", None)
        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)

        if language == "cn":
            empty_voucher_error_msg = "您选择的Voucher已不存在!"
            please_relogin_message = "由于您的部分信息已丢失，请重新登录。"
        elif language == "my":
            empty_voucher_error_msg = "Voucher yang anda memilihi tidak ada."
            please_relogin_message =  "Sila log masuk semula kerana beberapa maklumat anda hilang."
        else:
            empty_voucher_error_msg = "Selected voucher does not exists"
            please_relogin_message = "Please relogin as some of your information is lost."
            user_voucher_error_message = "You do not have the selected voucher."
            voucher_expired_message = "Selected voucher has expired"
        #make sure user is logged in
        redirect = "/user/login"
        assert user_id != None and user_id[:4] == "SAMY", please_relogin_message
        #data
        voucher_id = request.form.get("voucher_id", None)
        assert voucher_id != None, empty_voucher_error_msg
        user_voucher_details = voucher.select_user_voucher(db_conn_cursor, user_id, voucher_id)
        assert isinstance(user_voucher_details, list) and len(user_voucher_details) > 0, user_voucher_error_message
        user_voucher = voucher.select_voucher(db_conn_cursor, voucher_id)

        user_voucher_id = user_voucher[0][1]
        user_voucher_code = user_voucher[0][2]
        user_voucher_description = user_voucher[0][3]
        user_voucher_discount_amount = user_voucher[0][4]
        user_voucher_discount_type = user_voucher[0][5]
        user_voucher_discount_cap = user_voucher[0][6]
        user_voucher_created_date = user_voucher[0][7]
        user_voucher_expire_date = user_voucher[0][8]
        user_voucher_max_usage = user_voucher[0][9]
        user_voucher_usage_count = user_voucher[0][10]
        user_voucher_status = user_voucher[0][11]
        user_voucher_usage_cap = user_voucher_details[0][1]
        
        current_datetime = general.get_current_datetime()
        current_datetime = datetime.strptime(str(current_datetime), '%Y-%m-%d %H:%M:%S')
        user_voucher_expire_date = datetime.strptime(str(user_voucher_expire_date), '%Y-%m-%d %H:%M:%S')
        assert current_datetime <= user_voucher_expire_date, voucher_expired_message
        
        session["checkout_platform_voucher_selected"] = True
        session["checkout_platform_voucher_id"] = user_voucher_id
        session["checkout_platform_voucher_discount_amount"] = user_voucher_discount_amount
        session["checkout_platform_voucher_discount_type"] = user_voucher_discount_type
        session["checkout_platform_voucher_discount_cap"] = user_voucher_discount_cap
        session["checkout_platform_voucher_usage_cap"] = user_voucher_usage_cap
        passcheck = 1
        msg = "Successfully applied voucher!"
    except Exception as e:
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})

@api.route("user_place_order", methods=["POST"])
def user_place_order():
    AITANMALL_HANDLING_FEES_PERCENTAGE = 0.1
    AITANMALL_HANDLING_FEES_FIXED = 0.5
    current_domain = current_app.config.get("DOMAIN_NAME")
    try:
        #initiate all neccessary variables
        redirect = ""
        passcheck = 2
        msg = "ERROR"
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "place_order", "ERROR#2"
        user_id = session.get("user_id", None)
        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        if language == "cn":
            not_logged_in_error_message = "请您在添加产品入购物车前事先登录您的账号. 不好意思."
            cart_empty_error_message = "购物车里没有可购买的东西"
            please_relogin_message = "由于您的部分信息已丢失，请重新登录。"
            user_cart_not_cleared_message = "您的购物车没有清空。对不起。"
            voucher_failed_to_reduce_message = "无法更新您的优惠券..."
            shipping_fees_not_detected_message = "系统无法检测到您的运费金额。请再试一次。"
            voucher_session_not_cleared = "系统无法删除您的优惠券记录。"
            no_shipping_address = "请在下订单前添加收货地址。您将被重定向到个人资料以添加地址。对不起！"
            checkout_session_not_cleared_msg = "系统未能准备您进行结算。请联系我们的管理员，电话：011-5775-3538。"
            payment_method_not_detected_message = "请在结账前选择一种支付方式。谢谢。"
            shipping_address_not_detected_message = "请在结账前点击'添加地址'按钮以添加地址。谢谢。"
        elif language == "my":
            not_logged_in_error_message = "Sila log in sebelum tambah produk ke kart ye. Minta maaf!"
            cart_empty_error_message = "Troli tidak ada apa-apa untuk dibeli"
            please_relogin_message = "Sila log masuk semula kerana beberapa maklumat anda hilang."
            user_cart_not_cleared_message = "Troli anda tidak dikosongkan. Maaf."
            voucher_failed_to_reduce_message = "Gagal mengemaskini baucer anda..."
            shipping_fees_not_detected_message = "Sistem tidak dapat mengesan jumlah yuran penghantaran anda. Sila cuba lagi."
            voucher_session_not_cleared = "Sistem gagal untuk memadam rekod baucer anda."
            no_shipping_address = "Sila tambah alamat penghantaran sebelum membuat pesanan. Anda akan dialihkan ke profil untuk menambah alamat. Maaf!"
            checkout_session_not_cleared_msg = "Sistem gagal untuk mempersiapkan anda untuk pembayaran. Sila hubungi pentadbir kami di 011-5775-3538."
            payment_method_not_detected_message = "Tolong bolehkah anda memilih kaedah pembayaran sebelum membuat pembayaran. Terima kasih."
            shipping_address_not_detected_message = "Tolong bolehkah anda klik pada butang 'Tambah Alamat' untuk menambah alamat sebelum membuat pembayaran. Terima kasih."
        else:
            not_logged_in_error_message = "Please log in before adding product to cart. Sorry for the inconvinience."
            cart_empty_error_message = "Cart has nothing to be purchased"
            please_relogin_message = "Please relogin as some of your information is lost."
            user_cart_not_cleared_message = "Your cart is not cleared. Sorry."
            voucher_failed_to_reduce_message = "Failed to update your voucher..."
            shipping_fees_not_detected_message = "System can not detect your shipping fees amount. Please try again."
            voucher_session_not_cleared = "System failed to remove your voucher records."
            no_shipping_address = "Please add a shipping address before placing an order. You will be redirect to profile to add address.Sorry!"
            checkout_session_not_cleared_msg = "System failed to prepare you to checkout. Please contact our admin at 011-5775-3538."
            payment_method_not_detected_message = "Please can you select a payment method before checking out. Thanks."
            shipping_address_not_detected_message = "Please can you click on 'Add Address' button to add an address before checking out. Thanks."

        if user_id == None or user_id[:4]!="SAMY":
            passcheck = 4
            redirect = "/user/login"
            raise Exception(not_logged_in_error_message)
        #Define payment_status_changed to manage any on-the-spot pay method 
        payment_status_changed = False
        #Now we get the session values
        user_first_name = session.get("user_first_name", None)
        user_last_name = session.get("user_last_name", None)
        user_email = session.get("user_email", None)
        user_phone_number = session.get("user_phone_number", None)
        #assertion on user's data
        assert user_first_name != None and user_last_name != None and user_email != None and user_phone_number != None, please_relogin_message
        #user membership status
        if session.get("user_membership", None) == True:
            user_membership_id = session.get("user_membership_id", None)
            user_membership_start_date = session.get("user_membership_start_date", None)
            user_membership_end_date = session.get("user_membership_end_date", None)
            user_membership = Membership(user_membership_id, "VIP membership", "vip", user_membership_start_date, user_membership_end_date)
        else:
            user_membership = None
        #check if there's anything in the cart to check out
        #Change it to dictionary based for standardizing purposes
        close_mysql_cursor(db_conn_cursor)
        db_conn_cursor = db_conn.cursor(dictionary=True)
        user_cart_items = user.user_specific_get_cart(db_conn_cursor, user_id, by_merchant=True)
        #Change cursor back to tuple based for now because I am lazy to update the rest
        close_mysql_cursor(db_conn_cursor)
        db_conn_cursor = db_conn.cursor()
        assert len(user_cart_items) > 0, cart_empty_error_message
        user_checkout_payment_method = session.get("user_checkout_payment_method", None)
        user_checkout_address_id = session.get("user_checkout_address_id", None)
        user_checkout_shipping_fees = session.get("user_checkout_shipping_fees", None)
        assert user_checkout_payment_method != None, payment_method_not_detected_message
        assert user_checkout_address_id != None, shipping_address_not_detected_message
        assert user_checkout_shipping_fees != None, shipping_fees_not_detected_message
        user_checkout_shipping_fees = float(user_checkout_shipping_fees)
        checkout_platform_voucher_id = session.get("checkout_platform_voucher_id", None)
        checkout_platform_voucher_discount = session.get("checkout_platform_voucher_discount", None)
        if checkout_platform_voucher_discount == None or checkout_platform_voucher_id == None:
            checkout_platform_voucher_discount = 0.00
        else:
            checkout_platform_voucher_discount = float(checkout_platform_voucher_discount)

        #Session should be cleared here after accessing it and save to variables
        assert user.reset_checkout_sessions() == True, checkout_session_not_cleared_msg 

        selected_merchant_payment_method = merchant.select_payment_method_option(db_conn_cursor, None, user_checkout_payment_method, True)
        selected_merchant_payment_method_name = selected_merchant_payment_method[0][2]
        should_notify_sellers = False if user_checkout_payment_method == "onlinebanking" else True
        should_notify_buyers = False if user_checkout_payment_method == "onlinebanking" else True
        user_checkout_address_details  = user.select_address(db_conn_cursor, user_id, user_checkout_address_id, True)
        if user_checkout_address_details == None:
            redirect = "/user/profile"
            msg = no_shipping_address
            passcheck = 4
            raise Exception(no_shipping_address)

        product_warranty_extension_in_days = 0
        #Change customer warranty to 6 more months if it is member of VIP
        if user_membership != None and user_membership.get_membership_label() == "vip":
            checkout_discount = user_checkout_shipping_fees
            product_warranty_extension_in_days = 180
        #loop through user's cart to add to orders
        #1) Create a Order object
        free_shipping = True if user_membership != None and user_membership.get_membership_label() == "vip" else False
        create_orders = create_order(db_conn, db_conn_cursor, should_notify_sellers, user_checkout_payment_method, user_id, user_checkout_address_id, user_checkout_shipping_fees, product_warranty_extension_in_days, user_cart_items, AITANMALL_HANDLING_FEES_FIXED, AITANMALL_HANDLING_FEES_PERCENTAGE, user_first_name, user_last_name, user_phone_number, checkout_platform_voucher_discount, free_shipping)
        assert isinstance(create_orders, tuple), "System failed to create an order for you."
        cust_orders = create_orders[0]
        total_customer_payment = create_orders[1]
        final_customer_payment = create_orders[2]
        #Make sure it is float and round it
        final_customer_payment = float(final_customer_payment)
        final_customer_payment = round(final_customer_payment, 2)
        successful_action_count = create_orders[3]
        failed_action_count = create_orders[4]
        failed_reason_msg = create_orders[5]
        assert failed_action_count == 0, failed_reason_msg
        order_id = cust_orders.get_ord_id()
        #Done creating orders and merchant income
        #Charge customer and notify customer
        successful_action_count = 0
        failed_action_count = 0
        failed_reason_msg = ""

        assert user.clear_user_checkout_voucher_session() == True, voucher_session_not_cleared
        if user_checkout_payment_method == "cod":
            assert orders.update_orders_status(db_conn, db_conn_cursor, "to_ship", order_id) == True, "Failed to final update orders' status"
            msg = "You have successfuly placed an order!"
            order_reminder_header = "COD Order"
            session["user_checkout_complete_status"] = "succeeded"
            passcheck = 4
            redirect = "/user/checkout_complete"
        elif user_checkout_payment_method == "card":
            user_default_card = user.get_default_payment_card(db_conn_cursor, user_id)
            user_payment_method_id = user_default_card[0][1]
            stripe_payment_method_details = user.select_stripe_payment_method(db_conn_cursor, user_payment_method_id)
            stripe_payment_id = stripe_payment_method_details[0][3]
            stripe_customer_id = stripe_payment_method_details[0][4]
            api_key = stripe.get_key()
            total_customer_payment_in_cent = int(round(final_customer_payment, 2)*100)
            stripe_charge_response = stripe.charge_customer(api_key, stripe_customer_id, stripe_payment_id, total_customer_payment_in_cent)
            stripe_charge_status = stripe_charge_response["status"]
            if stripe_charge_status == "succeeded":
                final_payment_status = "to_ship"
                final_merchant_income_status = "succeeded"
            else:
                final_payment_status = "failed"
                final_merchant_income_status = "failed"
            payment_status_changed = True
            order_reminder_header = "Card Payment Order"
            session["user_checkout_complete_status"] = "succeeded"
            passcheck = 4
            redirect = "/user/checkout_complete"
        elif user_checkout_payment_method == "onlinebanking":
            #Remember to change to production when going production
            toyyibpay_secret = toyyibpay.get_secret_key()
            expire_datetime = general.get_datetime_from_now(86400)
            total_customer_payment_in_cent = int(round(final_customer_payment, 2)*100)
            return_url = current_domain+'/user/checkout_complete'
            callback_url = current_domain+'/webhooks/toyyibpay/online_banking'
            bill_to_name = user_first_name+" "+user_last_name
            toyyibpay_billcode = toyyibpay.create_bill(toyyibpay_secret, expire_datetime, total_customer_payment_in_cent, return_url, callback_url, bill_to_name, user_email, user_phone_number, order_id)
            assert not isinstance(toyyibpay_billcode, Exception), "Exception thrown when creating toyyibpay bill!"
            session["user_checkout_complete_status"] = "pending"
            redirect = "https://toyyibpay.com/"+str(toyyibpay_billcode)
            passcheck = 4
            msg = f"You will be redirect to Toyyibpay to complete payment!"
            order_reminder_header = "Pending FPX Online Banking Order"
        
        order_reminder_status = checkout.send_main_orders_reminder(order_reminder_header, user_first_name, user_last_name,user_phone_number, final_customer_payment, checkout_platform_voucher_discount, user_email)
        if order_reminder_status != True:
            failed_action_count += 1
            failed_reason_msg += f"Failed to notify AiTanMall.\n"
            
        #final update on orders IF there's any payment status changes
        if payment_status_changed:
            for order in cust_orders.get_ord_details():
                merchant_id = order.get_merchant_id()
                assert merchant.update_income_status(db_conn, db_conn_cursor, final_merchant_income_status, order_id, merchant_id) == True, "Failed to final update merchant's income status"
            assert orders.update_orders_status(db_conn, db_conn_cursor, final_payment_status, order_id) == True, "Failed to final update orders' status"
            payment_status_changed = False
            passcheck = 1
            msg = f"Thank you for the order! Order total: Rm{round(final_customer_payment, 2)}!"
        #send whatsapp notification to customer
        if should_notify_buyers:
            try:
                customer_review_order_link = "https://aitanmall.com"
                customer_cancel_order_link = "https://aitanmall.com"
                customer_service_number = "601157753538"
                customer_order_whatsapp_text = f"""*AiTan System*\n\n*Dear {user_first_name}*,\n\nThank you for placing an order via our website, aitanmall.com . Your order's details are as followed :\n\n*Order ID:* {order_id}\n*Total:* Rm{round(final_customer_payment, 2)}\n*Payment Method:* {str(selected_merchant_payment_method_name).capitalize()}\n\nTo review your order, kindly click this link: {customer_review_order_link}\n\n*Did not place an order? KINDLY click this link IMMEDIATELY* : {customer_cancel_order_link} , *or contact {customer_service_number}*\n\n*_If you have not received your item after 10 day(s), please contact {customer_service_number} immediately! Thank you._*\n\nWish you a great day ahead,\n*AiTan SDN BHD*"""
                twilio.send_whatsapp(customer_order_whatsapp_text, user_phone_number)
            except Exception as e:
                failed_action_count += 1
                failed_reason_msg  += str(e)
        
        #update the voucher usage cap to 1 lower
        try:
            assert voucher.reduce_user_voucher_usage_cap(db_conn, db_conn_cursor, 1, checkout_platform_voucher_id, user_id) == True, voucher_failed_to_reduce_message
        except Exception as e:
            failed_action_count += 1
            failed_reason_msg  += str(e)
        #clear user's cart
        try:
            assert user.clear_cart(db_conn , db_conn_cursor, user_id) == True, user_cart_not_cleared_message
        except Exception as e:
            failed_action_count += 1
            failed_reason_msg  += str(e)
        

        if failed_action_count > 0:
            msg += failed_reason_msg
    except Exception as e:
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})


@api.route("load_more_trending_product", methods=["POST"])
def load_more_trending_product():
    try:
        #initiate all neccessary variables
        redirect = ""
        passcheck = 4
        msg = "ERROR"
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor(dictionary=True)
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "load_more_product", "ERROR#2"
        user_id = session.get("user_id", None)
        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)

        if language == "cn":
            error_when_fetching_product_msg = "系统无法获取更多产品。请重新加载浏览器"
        elif language == "my":
            error_when_fetching_product_msg = "System gagal untuk mengambil lebih banyak produk. Sila muat semula pelayar"
        else:
            error_when_fetching_product_msg = "System failed to fetch more products. Please reload browser"
        
        last_trending_product_index_id = html.escape(str(request.form["last_product_index_id"]))
        last_trending_product_index_id = int(last_trending_product_index_id)
        #Assert this product ID is valid
        last_product_fame = product.get_product(db_conn_cursor, None, last_trending_product_index_id, by_index=True)
        assert isinstance(last_product_fame, list) and len(last_product_fame) > 0, error_when_fetching_product_msg
        last_product_fame = last_product_fame[0]["prd_fame"]
        if float(last_product_fame) != 0.00:
            more_trending_product_lists = product.get_product_after_fame(db_conn_cursor, last_product_fame)
            # Create a dictionary so we can return it nicely
            assert isinstance(more_trending_product_lists, list), error_when_fetching_product_msg
        else:
            more_trending_product_lists = []
            
        response = more_trending_product_lists
    except Exception as e:
        msg = str(e)
        response = {"msg" : msg}
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify(response)

@api.route("load_more_new_product", methods=["POST"])
def load_more_new_product():
    try:
        #initiate all neccessary variables
        {"msg" : "ERROR"}
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor(dictionary=True)
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "load_more_product", "ERROR#2"
        user_id = session.get("user_id", None)
        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)

        if language == "cn":
            error_when_fetching_product_msg = "系统无法获取更多产品。请重新加载浏览器"
        elif language == "my":
            error_when_fetching_product_msg = "System gagal untuk mengambil lebih banyak produk. Sila muat semula pelayar"
        else:
            error_when_fetching_product_msg = "System failed to fetch more products. Please reload browser"
        
        last_new_product_index_id = html.escape(str(request.form["last_product_index_id"]))
        last_new_product_index_id = int(last_new_product_index_id)
        #Assert this product ID is valid
        last_product_index_id = product.get_product(db_conn_cursor, None, last_new_product_index_id, by_index=True)
        assert isinstance(last_product_index_id, list) and len(last_product_index_id) > 0, error_when_fetching_product_msg
        last_product_index_id = last_product_index_id[0]["id"]
        #Carry out more products
        more_new_product_lists = product.get_product_after_id(db_conn_cursor, last_product_index_id)
        # Create a dictionary so we can return it nicely
        assert isinstance(more_new_product_lists, list), error_when_fetching_product_msg
            
        response = more_new_product_lists
    except Exception as e:
        msg = str(e)
        response = {"msg" : msg}
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify(response)
    

@api.route("load_more_discount_product", methods=["POST"])
def load_more_discount_product():
    try:
        #initiate all neccessary variables
        {"msg" : "ERROR"}
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor(dictionary=True)
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "load_more_product", "ERROR#2"
        user_id = session.get("user_id", None)
        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)

        if language == "cn":
            error_when_fetching_product_msg = "系统无法获取更多产品。请重新加载浏览器"
        elif language == "my":
            error_when_fetching_product_msg = "System gagal untuk mengambil lebih banyak produk. Sila muat semula pelayar"
        else:
            error_when_fetching_product_msg = "System failed to fetch more products. Please reload browser"
        
        last_discount_product_index_id = html.escape(str(request.form["last_product_index_id"]))
        last_discount_product_index_id = int(last_discount_product_index_id)
        #Assert this product ID is valid
        last_product = product.get_product(db_conn_cursor, None, last_discount_product_index_id, by_index=True)
        assert isinstance(last_product, list) and len(last_product) > 0, error_when_fetching_product_msg
        last_product_id = last_product[0]["prd_id"]
        #Get product details
        product_details = product.get_product_details(db_conn_cursor, last_product_id)
        product_original_price = product_details[0]["prd_price"]
        product_offer_price = product_details[0]["prd_offer_price"]
        last_product_discount_percentage = ((product_original_price - product_offer_price)/product_original_price) * 100
        last_product_discount_percentage = round(last_product_discount_percentage, 2)
        #Carry out more products
        if last_product_discount_percentage > 30:
            more_discount_product_lists = product.get_product_by_discount_less_than(db_conn_cursor, last_product_discount_percentage, 4)
            # Create a dictionary so we can return it nicely
            assert isinstance(more_discount_product_lists, list), error_when_fetching_product_msg
        else:
            more_discount_product_lists = []
        response = more_discount_product_lists
    except Exception as e:
        msg = str(e)
        response = {"msg" : msg}
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify(response)

#=============================================================
#Fetching or GET API
#==============================================================
@api.route("get_user_order_details", methods=["POST"])
def get_user_order_details():
    try:
        #initiate all neccessary variables
        response = {"msg" : "ERROR"}
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor(dictionary=True)
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "get_order_details", "ERROR#2"
        user_id = session.get("user_id", None)
        user_id_client_side = request.form.get("user_id", None)
        assert user_id_client_side == user_id, (404, "ERROR#1")
        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)

        if language == "cn":
            error_when_fetching_ord_details_msg = "系统无法获取您的订单历史。请重新加载浏览器"
            not_logged_in_msg = "您还没登录。"
        elif language == "my":
            error_when_fetching_ord_details_msg = "System gagal untuk mengambil details pesanan anda. Sila muat semula pelayar"
            not_logged_in_msg = "Anda tidak log masuk."
        else:
            error_when_fetching_ord_details_msg = "System failed to fetch your order details. Please reload browser"
            not_logged_in_msg = "You are not logged in."
        #Make sure user is logged in 
        assert session.get("user_logged_in", None) == True, not_logged_in_msg
        user_order_detail_details = orders.get_user_order_details(db_conn_cursor, user_id, limit = 5)
        assert isinstance(user_order_detail_details, list) and len(user_order_detail_details) >= 0, error_when_fetching_ord_details_msg
        response = user_order_detail_details
    except Exception as e:
        msg = str(e)
        response = {"msg" : msg}
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify(response)

@api.route("fetch_product", methods=["POST"])
def fetch_product():
    try:
        #initiate all neccessary variables
        response = {"msg" : "ERROR"}
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor(dictionary=True)
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "fetch_product", "ERROR#2"
        product_id = request.form.get("product_id", None)
        #Get user_id if exists
        user_id = session.get("user_id", None)

        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)

        if language == "cn":
            error_when_fetching_ord_details_msg = "系统无法获取您的产品。请重新加载浏览器"
        elif language == "my":
            error_when_fetching_ord_details_msg = "System gagal untuk mengambil details product anda. Sila muat semula pelayar"
        else:
            error_when_fetching_product_details_msg = "System failed to fetch your product details. Please reload browser"
        #Make sure user is logged in 
        #Data cleansing
        product_id = html.escape(product_id)
        product_details = product.select_product(db_conn_cursor, product_id)
        assert isinstance(product_details, list) and len(product_details) > 0, error_when_fetching_ord_details_msg
        response = product_details
    except Exception as e:
        msg = str(e)
        response = {"msg" : msg}
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return jsonify(response)

@api.route("get_recommendation_products", methods=["POST"])
def get_recommendation_products():
    try:
        #initiate all neccessary variables
        response = jsonify({"passcheck": 2 ,"msg" : "ERROR"})
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor(dictionary=True)
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "get_recommendation_products", "ERROR#2"
        current_product_id = request.form.get("current_product_id", None)
        #Get user_id if exists
        user_id = session.get("user_id", None)

        if user_id != None and user_id[:4] == "SAMY":
            language = user.user_specific_get_language(db_conn_cursor, user_id)
        else:
            language = general.guest_language(session)

        if language == "cn":
            error_when_fetching_ord_details_msg = "系统无法获取您的产品。请重新加载浏览器"
        elif language == "my":
            error_when_fetching_ord_details_msg = "System gagal untuk mengambil details product anda. Sila muat semula pelayar"
        else:
            error_when_fetching_product_details_msg = "System failed to fetch your product details. Please reload browser"
        #Make sure user is logged in 
        #Data cleansing
        recommended_products = product.get_recommended_products(db_conn_cursor, current_product_id, limit = 3)
        for recommended_product in recommended_products:
            recommended_product_id = recommended_product["prd_id"]
            product_variations = product.get_product_variations(db_conn_cursor, recommended_product_id)
            recommended_product["product_variations"] = product_variations

        response = jsonify(recommended_products)
    except Exception as e:
        msg = str(e)
        response = jsonify({"passcheck":3, "msg" : msg})
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response
    
#=========================================================
#Guest API
#================================================================
@api.route("guest_add_to_cart", methods=["POST"])
def guest_add_to_cart():
    try:
        #initiate all neccessary variables
        msg = "ERROR"
        passcheck = 3
        response = {"passcheck":passcheck, "msg":msg}
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "add_to_cart", "ERROR#2"
        user_id = session.get("user_id", None)
        language = general.guest_language(session)
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        if language == "cn":
            wrong_api_msg = "Invalid request. Please refresh your browser"
            crucial_ids_not_found_message = "其中一个重要ID无法被侦测"
            product_not_found_message = "无法在系统中找到要添加到购物车的产品。"
            merchant_product_id_unmatched_message = "商家的产品不存在。"
            product_id_and_var_id_invalid_msg = "Product ID and the variation you chosed are invalid"
        elif language == "my":
            wrong_api_msg = "Invalid request. Please refresh your browser"
            crucial_ids_not_found_message = "ID yang penting tidak didapatkan"
            product_not_found_message = "Produk untuk ditambah ke troli tidak dapat ditemui dalam sistem."
            merchant_product_id_unmatched_message = "Produk dari penjual tidak wujud."
            product_id_and_var_id_invalid_msg = "Product ID and the variation you chosed are invalid"
        else:
            wrong_api_msg = "Invalid request. Please refresh your browser"
            crucial_ids_not_found_message = "One of the crucial ID was not found"
            product_not_found_message = "Product to add to cart cannot be found in system."
            merchant_product_id_unmatched_message = "Product from merchant does not exists."
            product_id_and_var_id_invalid_msg = "Product ID and the variation you chosed are invalid"
        assert user_id == None, wrong_api_msg
        #Data from client side
        prd_id = request.form.get("prd_id", None)
        merchant_id = request.form.get("merchant_id", None)
        prd_var_id = request.form.get("prd_var_id", None)
        #Data ensuring
        assert prd_id != None and merchant_id != None, crucial_ids_not_found_message
        if prd_var_id == None:
            prd_var_id = -1
        prd_var_id = int(prd_var_id)
        assert prd_var_id >= -1, "Product variation ERROR"
        assert merchant.product_id_exists(db_conn_cursor, merchant_id, prd_id) == True, merchant_product_id_unmatched_message
        #First check if the product already exists in guest_cart
        guest_cart = session.get("guest_cart", None)
        if guest_cart != None:
            guest_cart = Cart.from_dict(guest_cart)
        else:
            guest_cart = Cart()

        product_already_added = guest_cart.product_already_exist(prd_id, prd_var_id)
        assert isinstance(product_already_added, bool), product_already_added
        if product_already_added == True:
            response = {"passcheck":1, "msg": msg}
        else:
            select_product_details = product.select_product(db_conn_cursor, prd_id)
            assert isinstance(select_product_details, list) and len(select_product_details) > 0, product_not_found_message
            #Define all needed details for cart item class
            prd_name = select_product_details[0][1]
            prd_img = select_product_details[0][5]
            quantity = 1
            prd_price = select_product_details[0][4]
            prd_var_name = "none"
            prd_sku = select_product_details[0][7]
            prd_var_img = "none"
            #If theere's a product variation ID
            if prd_var_id != -1:
                assert product.product_id_and_variation_id_valid(db_conn_cursor, prd_id, prd_var_id) == True, product_id_and_var_id_invalid_msg
                select_product_variation_details = product.select_product_variation(db_conn_cursor, prd_var_id)
                prd_price = select_product_variation_details[0][3]
                prd_var_name = select_product_variation_details[0][1]
                prd_sku = prd_sku if select_product_variation_details[0][5] == "" else select_product_variation_details[0][5]
                prd_var_img = select_product_variation_details[0][6]
                prd_img = prd_var_img if prd_var_img != "" and prd_var_img != "none" else prd_img
            #Define subtotal and total
            subtotal = prd_price * quantity
            other_fees = 0
            total = subtotal + other_fees
            merchant_id = select_product_details[0][13]
            #Create Cart Object and add item to it
            guest_cart_item = Cart_item(len(guest_cart), prd_id, prd_name, prd_img, quantity, prd_price, prd_var_id, prd_var_name, prd_sku, prd_var_img, subtotal, total, merchant_id)
            guest_cart.add_cart_item(guest_cart_item.to_dict())
            session["guest_cart"] = guest_cart.to_dict()
            response = {"passcheck":1, "msg": msg}
        return jsonify(response)
    except Exception as e:
        msg = str(e)
        response = {"passcheck":passcheck, "msg":msg}
        return jsonify(response)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)

@api.route("guest_update_cart_item", methods=["POST"])
def guest_update_cart_item():
    try:
        #initiate all neccessary variables
        redirect = ""
        passcheck = 2
        msg = "ERROR"
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "increaseCartItemQuantity" or action == "decreaseCartItemQuantity", "ERROR#2"
        update_action = "increase" if action == "increaseCartItemQuantity" else "decrease"
        user_id = session.get("user_id", None)
        language = general.guest_language(session)
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        if language == "cn":
            wrong_api_msg = "Invalid request. Please refresh your browser"
            no_cart_session_msg = "System cannot retrieve your shopping cart. Sorry. Please refresh browser."
            redeuce_cart_item_fail_message = "系统无法移除购物车中的商品"
            redeuce_cart_item_fail_message = "系统无法减少购物车中的商品数量"
            increase_cart_item_fail_message = "系统无法增加购物车中的商品数量"
        elif language == "my":
            wrong_api_msg = "Invalid request. Please refresh your browser"
            no_cart_session_msg = "System cannot retrieve your shopping cart. Sorry. Please refresh browser."
            redeuce_cart_item_fail_message = "Sistem gagal untuk mengeluarkan item dari troli"
            redeuce_cart_item_fail_message = "Sistem gagal untuk mengurangkan kuantiti item dalam troli"
            increase_cart_item_fail_message = "Sistem gagal untuk menambah kuantiti item dalam troli"
        else:
            wrong_api_msg = "Invalid request. Please refresh your browser"
            no_cart_session_msg = "System cannot retrieve your shopping cart. Sorry. Please refresh browser."
            redeuce_cart_item_fail_message = "System failed to reduce cart item quantity."
            increase_cart_item_fail_message = "System failed to increase cart item quantity."

        assert user_id == None, wrong_api_msg
        #change cursor to user_specific database
        cart_item_id = request.form.get("cart_item_id", None)
        quantity = request.form.get("quantity", None)
        cart_item_id = html.escape(cart_item_id)
        quantity = html.escape(quantity)
        quantity = int(quantity)
        #1. Retrieve the guest cart object from session
        guest_cart = session.get("guest_cart", None)
        assert guest_cart != None, no_cart_session_msg
        guest_cart = Cart.from_dict(guest_cart)
        guest_cart_items = guest_cart.cart_items
        #2. Check what actions are guest trying to perform
        if update_action == "decrease":
            #We have to loop through the cart items (Make sure to convert them back to dict) and then adjust this cart total
            status = False
            break_loop = False
            for i in range(len(guest_cart_items)):
                #To check if we should pop this
                pop_this = False
                cart_item = guest_cart_items[i]
                #If it is a dict
                if isinstance(cart_item, dict):
                    cart_item_object = Cart_item.from_dict(cart_item)
                #Now we go ahead and update it
                assert isinstance(cart_item_object, Cart_item), "Cart item has to be class object of Cart_item for operation"
                
                if str(cart_item_object.get_id()) == str(cart_item_id):
                    #Check if quantity should be remove (If quantity <=0 after deduction)
                    if cart_item_object.get_quantity() <= quantity:
                        amount_sub_total_decrease = (float(cart_item_object.get_prd_price()) * cart_item_object.get_quantity())
                        pop_this = True
                    else:
                        amount_sub_total_decrease = float(float(cart_item_object.get_prd_price()) * quantity)
                        
                    guest_cart.reduce_cart_total(amount_sub_total_decrease)
                    #Now we need to adjust cart item quantity and total
                    cart_item_object.decrease_quantity(quantity)
                    #Update cart subtotal and total
                    assert cart_item_object.decrease_sub_total(amount_sub_total_decrease) == True, "Failed to update cart item's total"
                    assert cart_item_object.decrease_total(amount_sub_total_decrease) == True, "Failed to update cart item's total"
                    break_loop = True
                #Now we convert it back to dict
                if pop_this == True:
                    guest_cart_items.pop(i)
                else:
                    guest_cart_items[i] = cart_item_object.to_dict()
                
                #We check if we wants to break things
                if break_loop == True:
                    break
                
            # assert status == True, "Failed to decreased cart item"
        else:
            #We have to loop through the cart items (Make sure to convert them back to dict) and then adjust this cart total
            status = False
            break_loop = False
            for i in range(len(guest_cart_items)):
                cart_item = guest_cart_items[i]
                #If it is a dict
                if isinstance(cart_item, dict):
                    cart_item_object = Cart_item.from_dict(cart_item)
                #Now we go ahead and update it
                assert isinstance(cart_item_object, Cart_item), "Cart item has to be class object of Cart_item for operation"
                if str(cart_item_object.get_id()) == str(cart_item_id):
                    amount_sub_total_increase = float(float(cart_item_object.get_prd_price()) * quantity)
                    #Update cart total
                    guest_cart.increase_cart_total(amount_sub_total_increase)
                    #Update cart item's subtotal and total
                    cart_item_object.increase_quantity(quantity)
                    assert cart_item_object.increase_sub_total(amount_sub_total_increase) == True, "Failed to update cart item's total"
                    assert cart_item_object.increase_total(amount_sub_total_increase) == True, "Failed to update cart item's total"
                    status = True
                    break_loop = True
                #Now we convert it back to dict
                guest_cart_items[i] = cart_item_object.to_dict()
                #We check if we wants to break things
                if break_loop == True:
                    break
            assert status == True, "Failed to increase cart item"
        #Update guest cart after
        session["guest_cart"] = guest_cart.to_dict()

        passcheck = 1
    except Exception as e:
        msg = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
    return jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect})

@api.route("guest_request_otp_for_checkout", methods=["POST"])
def guest_request_otp_for_checkout():
    try:
        #initiate all neccessary variables
        response = jsonify({"passcheck":2, "msg":"ERROR"})
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "guest_request_otp_for_checkout", "ERROR#2"
        language = general.guest_language(session)
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        if language == "cn":
            wrong_api_msg = "Invalid request. Please refresh browser"
            phone_number_has_id_msg = "该电话号码已在我们这里注册。请登录并结账。"
            otp_sent_msg = "已向您发送了一条验证码。"
        elif language == "my":
            wrong_api_msg = "Invalid request. Please refresh browser"
            phone_number_has_id_msg = "Nombor telefon ini sudah mempunyai ID dengan kami. Sila log masuk dan buat pembayaran."
            otp_sent_msg = "Sebuah OTP telah dihantar kepada anda."
        else:
            wrong_api_msg = "Invalid request. Please refresh browser"
            phone_number_has_id_msg = "This phone number already has an ID with us. Please login and checkout."
            otp_sent_msg = "An OTP has been sent to you."
        user_id = session.get("user_id", None)
        assert user_id == None, wrong_api_msg
        user_phone_number = html.escape(str(request.form["phone_number"]))
        #modify phone number to include country code
        country_code = "60"
        user_phone_number = general.standardize_phone_number(user_phone_number, country_code)
        
        request_otp_number = request_otp(user_phone_number, language)
        assert isinstance(request_otp_number, bool), request_otp_number
        response = jsonify({"passcheck":1, "msg":otp_sent_msg})
    except Exception as e:
        msg = str(e)
        response = jsonify({"passcheck":3, "msg":msg})
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response

@api.route("guest_verify_otp_for_checkout", methods=["POST"])
def guest_verify_otp_for_checkout():
    try:
        #initiate all neccessary variables
        response = jsonify({"passcheck":2, "msg":"ERROR"})
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "guest_verify_otp_for_checkout", "ERROR#2"
        language = general.guest_language(session)
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        if language == "cn":
            pass
        elif language == "my":
            pass
        else:
            pass
        user_phone_number = html.escape(str(request.form["phone_number"]))
        otp = html.escape(str(request.form["otp"]))
        #modify phone number to include country code
        country_code = "60"
        user_phone_number = general.standardize_phone_number(user_phone_number, country_code)
        response = jsonify({"passcheck":2, "msg":"18293812"})
        if verify_otp(user_phone_number, otp) == True:
            response = jsonify({"passcheck":1, "msg":"Successful!"})
    except Exception as e:
        msg = str(e)
        response = jsonify({"passcheck":3, "msg":msg})
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response

@api.route("guest_place_order", methods=["POST"])
def guest_place_order():
    AITANMALL_HANDLING_FEES_PERCENTAGE = 0.1
    AITANMALL_HANDLING_FEES_FIXED = 0.5
    current_domain = current_app.config.get("DOMAIN_NAME")
    try:
        #initiate all neccessary variables
        passcheck = 2
        msg = "ERROR"
        redirect = ""
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #making sure conditions are met
        assert request.method == "POST", "ERROR#1"
        action = html.escape(str(request.form["action"]))
        assert action == "guest_place_order", "ERROR#2"
        language = general.guest_language(session)
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        if language == "cn":
            otp_not_verified_msg = "系统检测到您尚未验证您的电话号码。"
            failed_to_create_account_msg = "系统无法为您创建账户。"
            failed_to_record_address_msg = "系统无法记录您的送货地址。"
            shipping_fees_not_detected_msg = "系统无法检测到您的运费。"
            no_cart_detected_msg = "系统无法检索您的购物车。请刷新浏览器。"
            card_payment_method_only_for_user_msg = "抱歉，只有注册用户才能使用卡支付方法。"
            payment_method_invalid_msg = "所选的付款方式不可用。"
            account_temporarily_login_subject = "感谢您的订单！以下是您的临时登录密码！"
            guest_account_created_whatsapp_msg = """*AiTan System*\n\n*亲爱的 {}，*\n\n我们已为您创建了一个账户，以便您可以跟踪订单，享受更简单的购物体验，以及更多！\n\nID: {}\n暂时性密码: {}\n登录链接: {}\n\n*_如果您认为这是一个错误，请忽略它_*\n\n祝您未来的日子充满快乐，\n*AiTan SDN. BHD.*"""
        elif language == "my":
            otp_not_verified_msg = "Sistem mendapati bahawa anda belum mengesahkan nombor telefon anda."
            failed_to_create_account_msg = "Sistem gagal untuk mewujudkan akaun untuk anda."
            failed_to_record_address_msg = "Sistem gagal untuk merekod alamat penghantaran anda."
            shipping_fees_not_detected_msg = "Sistem gagal untuk mengesan yuran penghantaran anda."
            no_cart_detected_msg = "Sistem gagal untuk mendapatkan troli belanja anda. Sila muat semula pelayar."
            card_payment_method_only_for_user_msg = "Maaf. Kaedah pembayaran kad hanya dibuka untuk pengguna berdaftar."
            payment_method_invalid_msg = "Kaedah pembayaran yang dipilih tidak tersedia."
            account_temporarily_login_subject = "Terima kasih kerana membuat pesanan! Berikut adalah kata laluan log masuk sementara anda!"
            guest_account_created_whatsapp_msg = """*Sistem AiTan*\n\n*Yang Berhormat {},*\n\nKami telah membuat akaun untuk anda supaya anda dapat mengesan pesanan, menikmati pengalaman membeli-belah yang lebih mudah, dan banyak lagi!\n\nID: {}\nKata Laluan sementara: {}\nPautan Log Masuk: {}\n\n*_Jika anda fikir ini adalah kesilapan, sila ABAIKAN IANYA_*\n\nSemoga hari anda indah,\n*AiTan SDN BHD*"""
        else:
            otp_not_verified_msg = "System detected that you have yet to verify your phone number."
            failed_to_create_account_msg = "System failed to create an account for you."
            failed_to_record_address_msg = "System failed to record your shipping address"
            shipping_fees_not_detected_msg = "System failed to detect your shipping fees."
            no_cart_detected_msg = "System failed to retrieve your shopping cart. Please refresh browser."
            card_payment_method_only_for_user_msg = "Sorry. Card payment method is only opened for registered user."
            payment_method_invalid_msg = "Payment method chosed is not available."
            account_temporarily_login_subject = "Thanks for placing order! Here's your temporarily login password!"
            guest_account_created_whatsapp_msg = """*AiTan System*\n\n*Dear {}*,\n\nWe have created an account for you so you could track orders, enjoy easier shopping experience, and more!\n\nID: {}\nTemporarily Password: {}\nLogin Link: {}\n\n*_If you think this is a mistake, please IGNORE IT_*\n\nWish you a great day ahead,\n*AiTan SDN BHD*"""
        #data from client
        user_phone_number = request.form.get("phone_number", None)
        name = request.form.get("name", None)
        email = request.form.get("email", None)
        street = request.form.get("street", None)
        unit_number = request.form.get("unitNumber", None)
        city = request.form.get("city", None)
        zip_code = request.form.get("zip", None)
        state = request.form.get("state", None)
        country = request.form.get("country", None)
        product_id = request.form.get("product_id", None)
        payment_method = request.form.get("payment_method", None)
        #data cleansing
        user_phone_number = html.escape(str(user_phone_number))
        country_code = "60"
        user_phone_number = general.standardize_phone_number(user_phone_number, country_code)
        name = html.escape(str(name))
        email = html.escape(str(email))
        street = html.escape(str(street))
        unit_number = html.escape(str(unit_number))
        city = html.escape(str(city))
        zip_code = html.escape(str(zip_code))
        state = html.escape(str(state))
        country = html.escape(str(country))
        product_id = html.escape(str(product_id))
        payment_method = html.escape(str(payment_method))
        user_checkout_address = f"{street}, {city}, {zip_code}, {state}, {country}" if unit_number == "" else \
            f"{unit_number}, {street}, {city}, {zip_code}, {state}, {country}"
        #Check if there's shipping fees variable
        checkout_shipping_fees = session.get("guest_checkout_shipping_fees", None)
        assert checkout_shipping_fees != None, shipping_fees_not_detected_msg
        #Check if the selected payment method is allowed
        selected_merchant_payment_method = merchant.select_payment_method_option(db_conn_cursor, None, payment_method, True)
        assert isinstance(selected_merchant_payment_method, list) and len(selected_merchant_payment_method) > 0, payment_method_invalid_msg
        selected_merchant_payment_method_name = selected_merchant_payment_method[0][2]
        #Now we check if otp is verified
        otp_verified = session.get("otp_verified", None)
        otp_verified_phone_number = session.get("otp_verified_phone_number", None)
        assert otp_verified == True, otp_not_verified_msg
        assert user_phone_number != None and otp_verified_phone_number == user_phone_number, otp_not_verified_msg
        #Now we move on
        guest_cart = session.get("guest_cart", None)
        assert guest_cart != None, no_cart_detected_msg
        guest_cart = Cart.from_dict(guest_cart)
        name_splitted = name.split(" ", 1)
        user_first_name = name_splitted[0]
        user_last_name = name_splitted[1] if len(name_splitted) > 1 else ""
        #Create account if it doesn't exist
        if user.account_exist(db_conn_cursor, email, user_phone_number) != True:
            temporarily_password = general.generate_random_string(10)
            create_user_account = create_account(email, user_phone_number, country_code, temporarily_password, user_first_name, user_last_name, language)
            assert isinstance(create_user_account, tuple), create_user_account
            create_account_status = create_user_account[0]
            user_id = create_user_account[1]
            assert create_account_status == True, failed_to_create_account_msg
            #Now we will whatsapp and email them their temporarily password
            mail_html = render_template("/guest/mail/temporarily_login_details.html", language=language, name=user_first_name,\
                username = user_phone_number, password = temporarily_password)
            mailer.send_html_email(email, account_temporarily_login_subject, mail_html)
            #Now we send whatsapp
            user_login_link = "https://aitanmall.com/user/login"
            guest_account_created_whatsapp_msg = guest_account_created_whatsapp_msg.format(user_first_name, user_phone_number, temporarily_password, user_login_link)
            twilio.send_whatsapp(guest_account_created_whatsapp_msg, user_phone_number)
        else:
            user_id = user.get_user_id(db_conn_cursor, user_phone_number[2:], verify_by="phone_number")
            assert user_id != None, "User ID not found"
            user.log_in_user(db_conn_cursor,user_id)
        #Now we their user_id. Let's now add the address to the database for them
        address_id = str(user.user_specific_add_address(db_conn, db_conn_cursor, user_id, street, city, zip_code, state, country, unit_number))
        assert isinstance(address_id, str) and len(address_id) > 0, failed_to_record_address_msg
        assert user.add_shipping_address(db_conn, db_conn_cursor, user_id, address_id, "default") == True, failed_to_record_address_msg
        #Now we can create orders and merchant income
        #1) Create a Order object
        free_shipping = True
        should_notify_sellers = False if payment_method == "onlinebanking" else True
        should_notify_buyers = False if payment_method == "onlinebanking" else True
        create_orders = create_order(db_conn, db_conn_cursor, should_notify_sellers, payment_method, user_id, address_id, checkout_shipping_fees, 0, guest_cart.get_cart_items(), AITANMALL_HANDLING_FEES_FIXED, AITANMALL_HANDLING_FEES_PERCENTAGE, user_first_name, user_last_name, user_phone_number, 0, free_shipping)
        assert isinstance(create_orders, tuple), create_orders
        cust_orders = create_orders[0]
        total_customer_payment = create_orders[1]
        final_customer_payment = create_orders[2]
        #Make sure it is float and round it
        final_customer_payment = float(final_customer_payment)
        final_customer_payment = round(final_customer_payment, 2)
        successful_action_count = create_orders[3]
        failed_action_count = create_orders[4]
        failed_reason_msg = create_orders[5]
        
        assert failed_action_count == 0, failed_reason_msg
        order_id = cust_orders.get_ord_id()
        #Done creating orders and merchant income
        #Charge customer and notify customer
        successful_action_count = 0
        failed_action_count = 0
        failed_reason_msg = ""
        payment_status_changed = False
        final_payment_status = "pending"
        
        if payment_method == "cod":
            assert orders.update_orders_status(db_conn, db_conn_cursor, "to_ship", order_id) == True, "Failed to final update orders' status"
            msg = "You have successfuly placed an order!"
            order_reminder_header = "COD Order"
            session["user_checkout_complete_status"] = "succeeded"
            passcheck = 4
            redirect = "/user/checkout_complete"
        elif payment_method == "card":
            raise Exception(card_payment_method_only_for_user_msg)
        elif payment_method == "onlinebanking":
            #Remember to change to production when going production
            toyyibpay_secret = toyyibpay.get_secret_key()
            expire_datetime = general.get_datetime_from_now(86400)
            total_customer_payment_in_cent = int(round(final_customer_payment, 2)*100)
            return_url = current_domain+'/user/checkout_complete'
            callback_url = current_domain+'/webhooks/toyyibpay/online_banking'
            bill_to_name = user_first_name+" "+user_last_name
            toyyibpay_billcode = toyyibpay.create_bill(toyyibpay_secret, expire_datetime, total_customer_payment_in_cent, return_url, callback_url, bill_to_name, email, user_phone_number, order_id)
            assert not isinstance(toyyibpay_billcode, Exception), "Exception thrown when creating test toyyibpay bill!"
            session["user_checkout_complete_status"] = "pending"
            redirect = "https://toyyibpay.com/"+str(toyyibpay_billcode)
            passcheck = 4
            msg = f"You will be redirect to Toyyibpay to complete payment!"
            order_reminder_header = "Pending FPX Online Banking Order"
        
        order_reminder_status = checkout.send_main_orders_reminder(order_reminder_header, user_first_name, user_last_name,user_phone_number, final_customer_payment, 0, email)
        if order_reminder_status != True:
            failed_action_count += 1
            failed_reason_msg += f"Failed to notify AiTanMall.\n"
        
        #final update on orders IF there's any payment status changes
        if payment_status_changed:
            for order in cust_orders.get_ord_details():
                merchant_id = order.get_merchant_id()
                assert merchant.update_income_status(db_conn, db_conn_cursor, final_payment_status, order_id, merchant_id) == True, "Failed to final update merchant's income status"
            assert orders.update_orders_status(db_conn, db_conn_cursor, final_payment_status, order_id) == True, "Failed to final update orders' status"
            payment_status_changed = False
            passcheck = 1
            msg = f"Thank you for the order! Order total: Rm{round(final_customer_payment, 2)}!"
        #send whatsapp notification to customer
        if should_notify_buyers:
            try:
                max_order_waiting_days = 10
                customer_service_number = "011-5775-3538"
                if language == "my":
                    customer_order_whatsapp_text = """*Sistem AiTan*\n\n*Yang Berhormat {},*\n\nTerima kasih kerana membuat pesanan melalui laman web kami, aitanmall.com. Butiran pesanan anda adalah seperti berikut:\n\n*ID Pesanan:* {}\n*Jumlah:* {}\n*Kaedah Pembayaran:* {}\n\n*_Jika anda belum menerima item anda selepas {} hari, sila hubungi {} segera! Terima kasih._*\n\nSemoga hari anda indah,\n*AiTan SDN BHD*"""
                elif language == "cn":
                    customer_order_whatsapp_text = """*AiTan System*\n\n*亲爱的 {}，*\n\n感谢您通过我们的网站 aitanmall.com 下订单。您的订单详情如下：\n\n*订单ID：* {}\n*总计：* {}\n*付款方式：* {}\n\n*_如果在{}天后，您还未收到您的商品，请立即联系{}！谢谢。_*\n\n祝您未来的日子充满快乐，\n*AiTan SDN. BHD.*"""
                else:
                    customer_order_whatsapp_text = """*AiTan System*\n\n*Dear {}*,\n\nThank you for placing an order via our website, aitanmall.com . Your order's details are as followed :\n\n*Order ID:* {}\n*Total:* {}\n*Payment Method:* {}\n\n*_If you have not received your item after {} day(s), please contact {} immediately! Thank you._*\n\nWish you a great day ahead,\n*AiTan SDN BHD*"""
                customer_order_whatsapp_text = customer_order_whatsapp_text.format(user_first_name, order_id, f"Rm{round(final_customer_payment, 2)}", str(selected_merchant_payment_method_name).capitalize(), max_order_waiting_days, customer_service_number)
                twilio.send_whatsapp(customer_order_whatsapp_text, user_phone_number)
            except Exception as e:
                failed_action_count += 1
                failed_reason_msg  += str(e)
        #clear user's cart
        try:
            session.pop("guest_cart", None)
        except Exception as e:
            failed_action_count += 1
            failed_reason_msg  += str(e)
        
        if failed_action_count > 0:
            msg += failed_reason_msg
            
        response = jsonify({"passcheck":passcheck, "msg":msg, "redirect":redirect}) 
    except Exception as e:
        msg = str(e)
        response = jsonify({"passcheck":3, "msg":msg})
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response