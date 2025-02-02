from webApp.helper import user as usr
from webApp.helper import general
from webApp.helper import merchant
from webApp.helper import product
from webApp.helper import voucher
from webApp.classes.cart import Cart
from webApp.classes.cart_item import Cart_item
from flask import Blueprint, render_template, redirect, make_response, session, request
from webApp.mysql_connector import use_db, close_mysql_conn, close_mysql_cursor
import html

user = Blueprint("user", __name__, static_folder="static", template_folder="templates")

@user.route("")
@user.route("login")
@user.route("login/")
def login():
    try:
        response = render_template("user/sign-in.html")
        db_conn_cursor_need_close = False
        db_conn_need_close = False
        if session.get("user_logged_in") != True:
            if general.cookie_exist("user_id") and general.cookie_exist("temporarily_key"):
                user_id_cookie = general.get_cookie("user_id")
                temporarily_key_cookie = general.get_cookie("temporarily_key")
                user_id_cookie = html.escape(user_id_cookie)
                temporarily_key_cookie = html.escape(temporarily_key_cookie)
                #connect to databse
                db_conn = general.create_general_mysql_conn()
                db_conn_cursor = db_conn.cursor()

                if usr.user_temporarily_key_exist(db_conn_cursor,user_id_cookie):
                    current_time = general.get_current_datetime()
                    if usr.user_log_in_cookie_is_valid(db_conn_cursor,temporarily_key_cookie,user_id_cookie,current_time):
                        assert usr.log_in_user(db_conn_cursor,user_id_cookie) == True, "System failed to log you in. Please refresh browser."
                        response = redirect('/')
        else:
            response = redirect('/')
    except Exception as e:
        response = render_template("user/sign-in.html", str(e))
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response

@user.route("log_out")
def log_out():
    try:
        if usr.log_out_user():
            response = make_response(redirect('/'))
        
            response.set_cookie("temporarily_key", '', max_age=0)
            response.set_cookie("user_id", '', max_age=0)
            return response
        else:
            return "ERROR Logging you out."
    except Exception as e:
        return "ERROR#2 Logging you out."
    
@user.route("membership")
def membership():
    try:
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        use_db(db_conn_cursor, "user")
        
        if session.get("user_logged_in") == True:
            user_id = session.get("user_id")
            #user_cart_details
            user_cart_details = usr.user_specific_get_cart(db_conn_cursor, user_id)
            user_cart_sub_total = 0.00
            for cart_detail in user_cart_details:
                user_cart_sub_total+=float(cart_detail[10])

            usr.set_user_membership_session(db_conn_cursor, user_id)

            user_membership = session.get("user_membership")
            assert user_id != None, "User session ID not found"
            email_verified = usr.user_specific_email_is_verified(db_conn_cursor, user_id)
            membership_subscription_product_details = usr.select_subscription_products(db_conn_cursor, None, "vipmonth", True)
            membership_subscription_product_details += usr.select_subscription_products(db_conn_cursor, None, "vipyear", True)
            response = render_template("/user/membership.html",email_verified=email_verified,resend_email_verification_link = "resend_verification_email", user_cart_details = user_cart_details,\
                user_cart_sub_total = user_cart_sub_total, membership_subscription_product_details = membership_subscription_product_details)
            
            if user_membership:
                response = render_template("/user/membership/active.html")
                    
        else:
            response = redirect("/user/login")
    except Exception as e:
        response = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response

@user.route("membership/checkout")
def membership_checkout():
    try:
        #initial variable 
        checkout_session_verified = False
        response = render_template("error.html", msg = "Could not find relevant checkout session")
        
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()

        assert session.get("user_logged_in") == True, "Please login"
        user_id = session.get("user_id")
        assert user_id != None, "User session ID not found"
        checkout_session = request.args.get("session_id")
        checkout_session_type = request.args.get("type")
        assert checkout_session != None and len(checkout_session) > 0, "No checkout session found"
        assert checkout_session_type != None and len(checkout_session_type) > 0, "No checkout session type found"
        if checkout_session_type == "stripe":
            assert usr.verify_stripe_checkout_session_id(db_conn_cursor,checkout_session,"subscription",user_id)
            checkout_session_verified = True
        
        if checkout_session_verified:
            assert usr.set_user_membership_session(db_conn_cursor, user_id), "Membership data not processed properly"
            if session.get("user_membership") == True:
                response = render_template("user/membership/checkout_success.html")
    except Exception as e:
        response = render_template("error.html", msg = e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response

@user.route("/profile")
def profile():
    try:
        response = render_template("error.html", msg = "ERROR")
        assert session.get("user_logged_in") == True, "Please login"
        #connect to database
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        
        user_id = session.get("user_id")
        user_email = session.get("user_email")
        user_address = usr.user_specific_get_address(db_conn_cursor, user_id, 3)
        assert not isinstance(user_address, Exception), "Exception found when reading your address"
        email_verified = usr.user_specific_email_is_verified(db_conn_cursor, user_id)
        #user_cart_details
        user_cart_details = usr.user_specific_get_cart(db_conn_cursor, user_id)
        user_cart_sub_total = 0.00
        for cart_detail in user_cart_details:
            user_cart_sub_total+=float(cart_detail[10])
        #user_membership
        usr.set_user_membership_session(db_conn_cursor, user_id)
        #payment methods
        payment_methods = usr.user_specific_get_payment_methods(db_conn_cursor, user_id, limit=3)
        user_memberships = usr.get_membership(db_conn_cursor, user_id)
        response = render_template("/user/profile.html", user_address = user_address,\
            email_verified = email_verified, resend_email_verification_link = "resend_verification_email",\
            payment_methods = payment_methods, user_memberships = user_memberships, user_cart_details=user_cart_details,\
            user_cart_sub_total = user_cart_sub_total)
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response

@user.route("resend_verification_email")
def resend_verification_email():
    try:
        permission_for_resend = False
        #connect to database
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        assert session.get("user_logged_in") == True, "Please login"
        user_id = session.get("user_id")
        user_email = session.get("user_email")
        user_name = session.get("user_first_name")
        assert user_id != None, "User session ID not found"
        assert user_email != None, "User session email not found"
        assert user_name != None, "User session first name not found"
        assert not usr.user_specific_email_is_verified(db_conn_cursor, user_id), "You have already verified your email. If you suspect someone hacked your account, please contact customer service."

        
        five_minutes_from_now  = general.get_datetime_from_now(300)
        five_minutes_ago_datetime = general.get_datetime_from_now(-50)
        permission_for_resend = usr.get_email_verification_key_resend_permission(db_conn_cursor,user_id,five_minutes_ago_datetime)
        if permission_for_resend == True:
            #remove the old one first before adding
            if usr.email_verification_key_exist(db_conn_cursor, user_id):
                assert usr.remove_email_verification_key(db_conn, db_conn_cursor, user_id) == True, "Old key not removed"
            user_verification_key = usr.generate_email_verification_key(db_conn,db_conn_cursor,user_id,user_email)
            if usr.user_specific_send_verification_email(db_conn_cursor, user_id, user_name, user_verification_key):
                response = render_template("/user/send_verification_email_post.html", status = 1, next_resend_datetime = five_minutes_from_now)
            else:
                response = render_template("/user/send_verification_email_post.html", status = 2)
        else:
            response = render_template("error.html", msg = "Your email verification has been sent and you need to wait 5 minutes before requesting a new one.")
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response

@user.route("verify_email")
def verify_email():
    try:
        response = "ERROR"
        db_conn_need_close = False
        db_conn_cursor_need_close = False
        user_id = html.escape(str(request.args.get("user_id")))
        user_email = html.escape(str(request.args.get("user_email")))
        key = request.args.get("key")

        db_conn = general.create_general_mysql_conn()
        db_conn_need_close = True
        db_conn_cursor = db_conn.cursor()
        db_conn_cursor_need_close = True
 
        if usr.email_verification_valid(db_conn_cursor,user_id,user_email,key):
            assert usr.verify_user_email(db_conn,db_conn_cursor,user_id,"verified"), "Email failed to be verified"
            assert usr.remove_email_verification_key(db_conn,db_conn_cursor,user_id), "Email key not removed"
            response = render_template("user/email_verification_success.html")
        else:
            raise Exception("Key invalid")
        
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    if db_conn_cursor_need_close == True:
        db_conn_cursor.close()
    if db_conn_need_close == True:
        db_conn.close()
    return response

@user.route("cart")
def cart():
    try:
        response = "ERROR"
        user_id = html.escape(str(request.args.get("user_id")))

        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #if user logged in we get the language
        user_is_logged_in = usr.is_logged_in()
        if user_is_logged_in:
            user_id = session.get("user_id", None)
            language = usr.user_specific_get_language(db_conn_cursor, user_id)
            session["language"] = language
            session["websocket_api_key"] = "u17828bdabd1782gdbaudsbaby1812b"

            user_cart_details = usr.user_specific_get_cart(db_conn_cursor, user_id, by_merchant=True, limit=None)
            user_cart_sub_total = 0.00
            merchant_shipping_details = dict()
            current_merchant_id = None
            user_cart_shipping_fees = 0.00
            merchant_names = dict()
            product_warranties = dict()
            for cart_detail in user_cart_details:
                product_id = cart_detail[1]
                merchant_sub_total = float(cart_detail[10])
                merchant_id = cart_detail[12]
                #if it is a new merchant we then proceed onto getting their shipping option and payment methods
                if current_merchant_id == None or current_merchant_id != merchant_id:
                    current_merchant_id = merchant_id
                    #initiate product warranty dict to list
                    product_warranties[merchant_id] = dict()
                    #shipping details
                    merchant_shipping_detail = merchant.get_shipping(db_conn_cursor, merchant_id)
                    merchant_shipping_status = merchant_shipping_detail[0][2]
                    merchant_shipping_option_id = merchant_shipping_detail[0][4]
                    if merchant_shipping_status == "active":
                        merchant_shipping_option_details = merchant.get_shipping_option(db_conn_cursor, merchant_shipping_option_id)
                        merchant_shipping_details[merchant_id] = merchant_shipping_option_details[0]
                        merchant_shipping_fixed_fees = merchant_shipping_option_details[0][5]
                        merchant_shipping_percentage_fees = float(merchant_shipping_option_details[0][6])
                    user_cart_shipping_fees += float(merchant_shipping_fixed_fees)
                    #merchant names
                    merchant_names[merchant_id] = merchant.get_business_name(db_conn_cursor, merchant_id)[0]

                product_warranties[merchant_id][product_id] = product.get_warranty(db_conn_cursor, product_id)[0]
                user_cart_shipping_fees += (merchant_sub_total * merchant_shipping_percentage_fees / 100)
                user_cart_sub_total+=merchant_sub_total
                user_vouchers = list()
                user_voucher_details = voucher.get_user_voucher(db_conn_cursor, user_id)
                if user_voucher_details != None:
                    for user_voucher_detail in user_voucher_details:
                        user_voucher_id = user_voucher_detail[2]
                        user_voucher = voucher.select_voucher(db_conn_cursor, user_voucher_id)
                        user_vouchers.append(user_voucher[0])
        else:
            raise Exception("You are not logged in")
        
        response = render_template("/user/cart.html", user_cart_items = user_cart_details, user_cart_sub_total = user_cart_sub_total, user_cart_shipping_fees = user_cart_shipping_fees, merchant_shipping_details = merchant_shipping_details,\
            merchant_names = merchant_names, user_vouchers = user_vouchers, product_warranties = product_warranties)
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response
    
@user.route("checkout")
def checkout():
    try:
        response = "ERROR"
        user_id = session.get("user_id", None)
        user_email = session.get("user_email", None)
        key = html.escape(str(request.args.get("key")))

        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        assert user_id != None and user_id[:4] == "SAMY", "Please log in / create account"
        language = usr.user_specific_get_language(db_conn_cursor, user_id)

        if language == "cn":
            no_payment_method_available_msg = "目前所有付款方式正在维修. 无法下单."
        elif language == "my":
            no_payment_method_available_msg = "Tiada cara pembayaran untuk pesanan sekarang. Minta maaf."
        else:
            no_payment_method_available_msg = "No payment methods are available."
        
        #Free Shipping
        free_shipping_activated = True
        #if user logged in we get the language
        user_is_logged_in = usr.is_logged_in()
        if user_is_logged_in:
            user_id = session.get("user_id", None)
            language = usr.user_specific_get_language(db_conn_cursor, user_id)
            user_cart_details = usr.user_specific_get_cart(db_conn_cursor, user_id, by_merchant=True, limit=None)
            user_cart_sub_total = 0.00
            merchant_shipping_details = dict()
            current_merchant_id = None
            user_cart_shipping_fees = 0.00
            merchant_names = dict()
            product_warranties = dict()
            for cart_detail in user_cart_details:
                product_id = cart_detail[1]
                merchant_sub_total = float(cart_detail[10])
                merchant_id = cart_detail[12]
                #if it is a new merchant we then proceed onto getting their shipping option and payment methods
                if current_merchant_id == None or current_merchant_id != merchant_id:
                    current_merchant_id = merchant_id
                    #initiate product warranty dict to list
                    product_warranties[merchant_id] = dict()
                    #shipping details
                    merchant_shipping_detail = merchant.get_shipping(db_conn_cursor, merchant_id)
                    merchant_shipping_status = merchant_shipping_detail[0][2]
                    merchant_shipping_option_id = merchant_shipping_detail[0][4]
                    if merchant_shipping_status == "active":
                        merchant_shipping_option_details = merchant.get_shipping_option(db_conn_cursor, merchant_shipping_option_id)
                        merchant_shipping_details[merchant_id] = merchant_shipping_option_details[0]
                        merchant_shipping_fixed_fees = merchant_shipping_option_details[0][5]
                        merchant_shipping_percentage_fees = float(merchant_shipping_option_details[0][6])
                    user_cart_shipping_fees += float(merchant_shipping_fixed_fees)
                    #merchant names
                    merchant_names[merchant_id] = merchant.get_business_name(db_conn_cursor, merchant_id)[0]
                    
                product_warranties[merchant_id][product_id] = product.get_warranty(db_conn_cursor, product_id)[0]
                user_cart_shipping_fees += (merchant_sub_total * merchant_shipping_percentage_fees / 100)
                user_cart_sub_total+=merchant_sub_total

            session["language"] = language
            session["websocket_api_key"] = "u17828bdabd1782gdbaudsbaby1812b"
            user_address = usr.user_specific_get_address(db_conn_cursor, user_id, 10)
            #payment methods
            payment_method_options = merchant.get_payment_method_option(db_conn_cursor, "active", True)
            assert isinstance(payment_method_options, list) and len(payment_method_options) > 0, no_payment_method_available_msg
            if session.get("user_checkout_payment_method", None) == None or session.get("user_checkout_payment_method_name", None) == None:
                user_default_card_details = usr.get_default_payment_card(db_conn_cursor, user_id)
                if isinstance(user_default_card_details, list) and len(user_default_card_details) > 0:
                    session["user_checkout_payment_method"] = "card"
                    session["user_checkout_payment_method_name"] = str(user_default_card_details[0][2]).capitalize()+" ending in "+str(user_default_card_details[0][2])

            if session.get("user_checkout_address_id", None) == None:
                user_default_shipping_address = usr.get_default_shipping_address(db_conn_cursor, user_id)
                if isinstance(user_default_shipping_address, list) and len(user_default_shipping_address) > 0:
                    session["user_checkout_address_id"] = user_default_shipping_address[0][1]
                    
            if free_shipping_activated == True:
                session["user_checkout_shipping_fees"] = user_cart_shipping_fees
            else:
                session["user_checkout_shipping_fees"] = 0.00

            if session.get("checkout_platform_voucher_selected", None) == True:
                user_checkout_platform_voucher_discount_type = session.get("checkout_platform_voucher_discount_type")
                user_checkout_platform_voucher_discount_amount = float(session.get("checkout_platform_voucher_discount_amount"))
                user_checkout_platform_voucher_usage_cap = int(session.get("checkout_platform_voucher_usage_cap"))
                user_checkout_platform_voucher_discount_cap = float(session.get("checkout_platform_voucher_discount_cap"))
                session["checkout_platform_voucher_discount"] = (user_checkout_platform_voucher_discount_amount) if user_checkout_platform_voucher_discount_type == "fixed" else (user_cart_sub_total*user_checkout_platform_voucher_discount_amount/100)
                user_checkout_platform_voucher_discount = float(session.get("checkout_platform_voucher_discount"))
                if user_checkout_platform_voucher_discount > user_checkout_platform_voucher_discount_cap:
                    session["checkout_platform_voucher_discount"] = user_checkout_platform_voucher_discount_cap
            
            user_vouchers = list()
            user_voucher_details = voucher.get_user_voucher(db_conn_cursor, user_id)
            if user_voucher_details != None:
                for user_voucher_detail in user_voucher_details:
                    user_voucher_id = user_voucher_detail[2]
                    user_voucher = voucher.select_voucher(db_conn_cursor, user_voucher_id)
                    user_vouchers.append(user_voucher[0])
            response = render_template("/user/checkout/index.html", user_cart_items = user_cart_details, user_cart_sub_total = user_cart_sub_total, user_cart_shipping_fees = user_cart_shipping_fees, merchant_shipping_details = merchant_shipping_details,\
            user_address= user_address, payment_method_options = payment_method_options, merchant_names = merchant_names, user_vouchers=user_vouchers, product_warranties = product_warranties)
        else:
            response = redirect("/user/login")
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response

@user.route("checkout_complete")
def checkout_complete():
    try:
        response = "ERROR"
        user_id = html.escape(str(request.args.get("user_id")))
        #if user logged in we get the language
        user_is_logged_in = usr.is_logged_in()
        response = redirect("/user/login")
        assert user_is_logged_in == True, "Please log in first"
        user_id = session.get("user_id", None)
        assert user_id != None and user_id[:4] == "SAMY", "Please log in first."
        user_checkout_complete_status = session.get("user_checkout_complete_status", None)
        assert user_checkout_complete_status != None , "System can not detect your checkout status"

        if user_checkout_complete_status == "succeeded":
            response = redirect("/user/checkout_success")
        else:
            #If there is a payment code
            get_bill_code = request.args.get("billcode", None)
            response = redirect("/user/checkout_failed")
            #If there is a status code
            get_status_code = request.args.get("status_id", None)
            if get_status_code == 1 or get_status_code == "1":
                response = redirect("/user/checkout_success?billcode="+str(get_bill_code))
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        return response

@user.route("checkout_success")
def checkout_success():
    try:
        response = "ERROR"
        user_id = html.escape(str(request.args.get("user_id")))
        user_email = html.escape(str(request.args.get("user_email")))
        key = html.escape(str(request.args.get("key")))

        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #if user logged in we get the language
        user_is_logged_in = usr.is_logged_in()
        response = redirect("/user/login")
        assert user_is_logged_in == True, "Please log in first"
        user_id = session.get("user_id", None)
        assert user_id != None and user_id[:4] == "SAMY", "Please log in first."
        get_bill_code = request.args.get("billcode", None)
        if get_bill_code == None:
            payment_link = ""
        else:
            payment_link = "htpps://dev.toyyibpay.com/"+str(get_bill_code)
        response = render_template("/user/checkout/success.html", payment_link = payment_link)
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response
    
@user.route("checkout_failed")
def checkout_failed():
    try:
        response = "ERROR"
        user_id = html.escape(str(request.args.get("user_id")))
        user_email = html.escape(str(request.args.get("user_email")))
        key = html.escape(str(request.args.get("key")))

        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #if user logged in we get the language
        user_is_logged_in = usr.is_logged_in()
        response = redirect("/user/login")
        assert user_is_logged_in == True, "Please log in first"
        user_id = session.get("user_id", None)
        assert user_id != None and user_id[:4] == "SAMY", "Please log in first."
        response = render_template("/user/checkout/failed.html")
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response

#AFTER REGISTRATION TO CHECKOUT
@user.route("checkout_after_registration")
def checkout_after_registration():
    try:
        response = render_template("error.html", msg = "ERROR")
        user_id = html.escape(str(request.args.get("user_id")))

        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #if user logged in we get the language
        user_is_logged_in = usr.is_logged_in()
        response = redirect("/user/login")
        assert user_is_logged_in == True, "Please log in first"
        user_id = session.get("user_id", None)
        assert user_id != None and user_id[:4] == "SAMY", "Please log in first."
        language = usr.user_specific_get_language(db_conn_cursor, user_id)

        if language == "cn":
            please_add_product_to_cart_msg = "您的购物车里没有任何商品. 请添加了产品之后才结账."
        elif language == "my":
            please_add_product_to_cart_msg = "Sila tambah produk sebelum pergi pembayaran."
        else:
            please_add_product_to_cart_msg = "Please add atleast items to cart with total over Rm5 before checking out."
            failed_to_cart_items_to_cart_msg = "So sorry. Our system faield to add your items to cart. Please can you add items to cart again and checkout. Sorry."
        #Check if there's anything in guest_cart
        guest_cart = session.get("guest_cart", None)
        assert guest_cart != None, please_add_product_to_cart_msg
        guest_cart = Cart.from_dict(guest_cart)
        guest_cart_details = guest_cart.get_cart_items()
        #Now we loop through the cart details and add them to user_cart database
        for cart_detail in guest_cart_details:
            cart_detail = Cart_item.from_dict(cart_detail)
            #Now we will proceed to clear out the guest-cart seesion
            session.pop("guest_cart")
            #Continue operation here
            product_id = cart_detail.get_prd_id()
            product_name = cart_detail.get_prd_name()
            product_image = cart_detail.get_prd_img()
            quantity = cart_detail.get_quantity()
            price = cart_detail.get_prd_price()
            product_variation_id = cart_detail.get_prd_var_id()
            product_variation_name = cart_detail.get_prd_var_name()
            product_sku = cart_detail.get_prd_sku()
            product_variation_image = cart_detail.get_prd_var_img()
            sub_total = float(cart_detail.get_sub_total())
            total = float(cart_detail.get_total())
            merchant_id = cart_detail.get_merchant_id()
            assert usr.user_specific_add_to_cart(db_conn, db_conn_cursor, user_id, product_id, product_name, product_image, quantity, price, product_variation_id, product_variation_name, product_sku,\
                product_variation_image, sub_total, total, merchant_id) == True, failed_to_cart_items_to_cart_msg
        
        response = redirect("/user/checkout")
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response
    
@user.route("orders")
def orders():
    try:
        response = render_template("error.html")
        user_id = html.escape(str(request.args.get("user_id")))

        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #if user logged in we get the language
        user_is_logged_in = usr.is_logged_in()
        if user_is_logged_in:
            user_id = session.get("user_id", None)
            language = usr.user_specific_get_language(db_conn_cursor, user_id)
            session["language"] = language
            #Message to return by languages
            if language == "my":
                failed_to_get_orders_msg = "Sistem gagal mendapatkan pesanan anda dari pangkalan data."
            elif language == "cn":
                failed_to_get_orders_msg = "系统无法从数据库获取您的订单。"
            else:
                failed_to_get_orders_msg = "System failed to get your orders from database."

            response = render_template("user/orders/index.html")
        else:
            raise Exception((201901, "You are not logged in"))
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response