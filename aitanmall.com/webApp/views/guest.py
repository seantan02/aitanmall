from flask import Blueprint, render_template, request, session, redirect
from webApp.helper import general
from webApp.helper import product
from webApp.helper.user import is_logged_in
import html
from webApp.classes.cart import Cart
from webApp.classes.cart_item import Cart_item
from webApp.helper import merchant
from webApp.mysql_connector import close_mysql_conn, close_mysql_cursor

guest = Blueprint("guest", __name__, static_folder="static", template_folder="templates")

@guest.route("createAccount")
@guest.route("createAccount/")
@guest.route("create_account")
@guest.route("create_account/")
def create_account():
    try:
        #Check if user came from checkout; If yes, we will set session["next_url"] to redirect them after
        guest_cart = session.get("guest_cart", None)
        if guest_cart != None:
            guest_cart = Cart.from_dict(guest_cart)
            guest_cart_total = guest_cart.get_total()
            if float(guest_cart_total) > 5.00:
                session["next_url"] = "/user/checkout_after_registration"

        return render_template("guest/create-account.html")
    except Exception as e:
        return str(e)
    
@guest.route("checkout")
def checkout():
    try:
        response = "ERROR"
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #======================================================================================
        #Set error message base on user preffered language
        #======================================================================================
        language = general.guest_language(session)
        
        if language == "cn":
            please_add_product_to_cart_msg = "请在结账前添加商品到购物车。"
            cart_value_less_than_five_msg = "对不起。结账至少需要5令吉。"
        elif language == "my":
            please_add_product_to_cart_msg = "Sila tambah produk ke troli sebelum membuat bayaran."
            cart_value_less_than_five_msg = "Maaf. Sekurang-kurangnya Rm5 diperlukan untuk membuat pembayaran."
        else:
            please_add_product_to_cart_msg = "Please add a product to cart before checking out."
            cart_value_less_than_five_msg = "Sorry. Atleast Rm5 is required for checking out."
        #if user logged in we get the language
        user_is_logged_in = is_logged_in()
        if user_is_logged_in:
            response = redirect("/user/checkout")
            
        guest_cart = session.get("guest_cart", None)
        assert guest_cart != None, please_add_product_to_cart_msg
        guest_cart = Cart.from_dict(guest_cart)
        assert guest_cart.get_total() > 5, cart_value_less_than_five_msg
        guest_cart_details = guest_cart.get_cart_items()
        guest_cart_sub_total = 0.00
        merchant_shipping_details = dict()
        current_merchant_id = None
        guest_cart_shipping_fees = 0.00
        merchant_names = dict()
        product_warranties = dict()
        for cart_detail in guest_cart_details:
            cart_detail = Cart_item.from_dict(cart_detail)
            product_id = cart_detail.get_prd_id()
            merchant_sub_total = float(cart_detail.get_sub_total())
            merchant_id = cart_detail.get_merchant_id()
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
                guest_cart_shipping_fees += float(merchant_shipping_fixed_fees)
                #merchant names
                merchant_names[merchant_id] = merchant.get_business_name(db_conn_cursor, merchant_id)[0]
                
            product_warranties[merchant_id][product_id] = product.get_warranty(db_conn_cursor, product_id)[0]
            guest_cart_shipping_fees += (merchant_sub_total * merchant_shipping_percentage_fees / 100)
            guest_cart_sub_total+=merchant_sub_total
        #payment methods
        payment_method_options = merchant.get_payment_method_option(db_conn_cursor, "active", True)
        assert isinstance(payment_method_options, list) and len(payment_method_options) > 0, "No payment methods are available"
        #Free shipping for now
        guest_cart_shipping_fees = 0.00
        session["guest_checkout_shipping_fees"] = guest_cart_shipping_fees

        response = render_template("guest/checkout/index.html", guest_cart_items = guest_cart_details, guest_cart_sub_total = guest_cart_sub_total, guest_cart_shipping_fees = guest_cart_shipping_fees, merchant_shipping_details = merchant_shipping_details, payment_method_options = payment_method_options, merchant_names = merchant_names, product_warranties = product_warranties)
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_conn(db_conn)
        return response