from flask import Blueprint, render_template, url_for, request, redirect, session, make_response
from webApp.helper import json_tools
from webApp import mysql_connector
from webApp.helper.search_engine import product as prd
from webApp.helper import general
from webApp.helper import product
from webApp.helper import user
from webApp.classes.cart import Cart
import html

shared = Blueprint("shared", __name__, static_folder="static", template_folder="templates")

@shared.before_request
def before_request():
    #Check if we need to redirect user somewhere
    next_url = session.get("next_url", None)
    if next_url != None:
        session.pop("next_url")
        return redirect(next_url)
    
@shared.route("home")
@shared.route("")
def home():
    try:
        response = "ERROR"
        #connect to database
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #if user logged in
        if user.is_logged_in():
            user_id = session.get("user_id", None)
            #Check user status so we can show them tutorial
            user_account_status = session.get("user_account_status", None)
            show_new_user_tutorial = True if user_account_status == "new" else False
            #Now we update their status if they are new
            if user_account_status == "new":
                user.update_user_account_status(db_conn, db_conn_cursor, "normal", user_id)
            assert user_id != None, "User not logged in"
            language = user.user_specific_get_language(db_conn_cursor, user_id)
            user_cart_details = user.user_specific_get_cart(db_conn_cursor, user_id)
            user_cart_sub_total = 0.00
            for cart_detail in user_cart_details:
                user_cart_sub_total+=float(cart_detail[10])
            session["language"] = language
            session["websocket_api_key"] = "u17828bdabd1782gdbaudsbaby1812b"
            #connect to mysql and select all products
            product_list = general.get_product(db_conn_cursor, 6)
            last_new_product_index_id = product_list[-1][0]
            #trending products
            trending_product_list = product.get_product_by_fame(db_conn_cursor, 6)
            last_trending_product_index_id = trending_product_list[-1][0]
            #highest discount products
            highest_discount_product_list = product.get_product_by_discount(db_conn_cursor, 6)
            last_discount_product_index_id = highest_discount_product_list[-1][0]
            response = render_template("index.html", products = product_list, trending_product_list = trending_product_list, user_cart_details = user_cart_details, user_cart_sub_total = user_cart_sub_total, language = language,\
                last_trending_product_index_id = last_trending_product_index_id, last_new_product_index_id = last_new_product_index_id, highest_discount_product_list = highest_discount_product_list,\
                last_discount_product_index_id = last_discount_product_index_id, show_new_user_tutorial = show_new_user_tutorial)
        else:
            if general.cookie_exist("user_id") and general.cookie_exist("temporarily_key"):
                response = redirect('/user/login')
            else:
                #connect to mysql and select all products
                if session.get("language", None) == None:
                    language = general.guest_language(session)
                else:
                    language = session.get("language", None)

                guest_cart = session.get("guest_cart", None)
                if guest_cart == None:
                    guest_cart = Cart()
                    guest_cart_sub_total = 0.00
                else:
                    guest_cart = Cart.from_dict(guest_cart)
                    guest_cart_sub_total = guest_cart.get_total()
                product_list = []
                mysql_connector.use_db(db_conn_cursor,"assets")
                product_list = general.get_product(db_conn_cursor, 6)
                last_new_product_index_id = product_list[-1][0]
                #trending products
                trending_product_list = product.get_product_by_fame(db_conn_cursor, 6)
                last_trending_product_index_id = trending_product_list[-1][0]
                #highest discount products
                highest_discount_product_list = product.get_product_by_discount(db_conn_cursor, 4)
                last_discount_product_index_id = highest_discount_product_list[-1][0]
                response = render_template("index.html", products = product_list, trending_product_list = trending_product_list, language = language, last_trending_product_index_id = last_trending_product_index_id,\
                    last_new_product_index_id = last_new_product_index_id, highest_discount_product_list = highest_discount_product_list, last_discount_product_index_id = last_discount_product_index_id,\
                    guest_cart_items = guest_cart.get_cart_items(), guest_cart_sub_total = guest_cart_sub_total)
    except Exception as e:
        response = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            mysql_connector.close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            mysql_connector.close_mysql_cursor(db_conn)
        #serialize key and send it to search engine then redirect to result
        return response

@shared.route('/robots.txt')
def robots_txt():
    # Create the content of the robots.txt file
    content = "User-agent: Googlebot\nDisallow:"

    # Create a response with the content and set the appropriate headers
    response = make_response(content)
    response.headers['Content-Type'] = 'text/plain'

    return response

@shared.route("search_product", methods = ["POST"])
def search_product():
    try:
        assert request.method == "POST", "ERROR#1"
        searched_key = request.form["searched_key"]
        #connect to mysql and select product names
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor(named_tuple=True)
        # special case because we want a cursor returning named_tuple
        mysql_connector.use_db(db_conn_cursor,"product")
        query = """
        SELECT merchant_id,prd_name,prd_id FROM product
        """
        db_conn_cursor.execute(query)
        assets_prd_list = db_conn_cursor.fetchall()
        db_conn_cursor.close()
        db_conn.close()
        # now use product search engine to get result
        matched_prd_id = prd.search_products(assets_prd_list, searched_key, 20)
        session["search_matched_prd_ids"] = matched_prd_id
        response = redirect("/main")
    except Exception as e:
        response = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            mysql_connector.close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            mysql_connector.close_mysql_cursor(db_conn)
        #serialize key and send it to search engine then redirect to result
        return response

@shared.route("main")
def main():
    # read_cookies()
    try:
        assert "search_matched_prd_ids" in session, "Failed to search."
        #connect to mysql and select product names
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        matched_prd_id = session.get("search_matched_prd_ids", [])
        #parse in result and get product details
        matched_prd_list= list()
        for idx in range(len(matched_prd_id)):
            product_id = matched_prd_id[idx][0]
            merchant_id = matched_prd_id[idx][1]
            matched_prd = general.select_product(db_conn_cursor,merchant_id,product_id, by_merchant=False)
            if matched_prd != None:
                matched_prd_list.append(matched_prd) 
        #trending products
        trending_product_list = product.get_product_by_fame(db_conn_cursor, 5)
        #check if user is logged in or not
        #if user logged in
        user_is_logged_in = user.is_logged_in()
        if user_is_logged_in:
            user_id = session.get("user_id", None)
            language = user.user_specific_get_language(db_conn_cursor, user_id)
            user_cart_details = user.user_specific_get_cart(db_conn_cursor, user_id)
            user_cart_sub_total = 0.00
            for cart_detail in user_cart_details:
                user_cart_sub_total+=float(cart_detail[10])
            session["language"] = language
            session["websocket_api_key"] = "u17828bdabd1782gdbaudsbaby1812b"
        else:
            #Set guest language
            if session.get("language", None) == None:
                language = general.guest_language(session)
            else:
                language = session.get("language", None)
            guest_cart = session.get("guest_cart", None)
            if guest_cart == None:
                guest_cart = Cart()
                guest_cart_sub_total = 0.00
            else:
                guest_cart = Cart.from_dict(guest_cart)
                guest_cart_sub_total = guest_cart.get_total()

        #response dewpending if user i logged in 
        if user_is_logged_in:
            response = render_template("main.html", products = matched_prd_list, user_cart_details = user_cart_details, user_cart_sub_total = user_cart_sub_total, language = language, trending_product_list = trending_product_list)
        else:
            response = render_template("main.html", products = matched_prd_list, guest_cart_items = guest_cart.get_cart_items(), user_cart_sub_total = guest_cart_sub_total, language = language, trending_product_list = trending_product_list)
    except AssertionError as e:
        response = redirect("/")
    except Exception as e:
        response = str(e)
    finally:
        if 'db_conn_cursor' in locals():
            mysql_connector.close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            mysql_connector.close_mysql_cursor(db_conn)
        #serialize key and send it to search engine then redirect to result
        return response

@shared.route("membership/")
@shared.route("membership")
def membership():
    # read_cookies()
    return render_template("membership.html")

@shared.route("terms_and_conditions")
def terms_and_conditions():
    if session.get("language") == None:
        session["language"] = "eng"
    return render_template("/terms_conditions.html")

@shared.route("privacy_policy")
def privacy_policy():
    if session.get("language") == None:
        session["language"] = "eng"
    return render_template("/privacy_policy.html")

@shared.route("products/<merchant_identification>/<product_id>")
def products_prd_id(merchant_identification, product_id):
    try:
        response = "ERROR"
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #=======================================
        #if user logged in we get the language
        user_is_logged_in = user.is_logged_in()
        if user_is_logged_in:
            user_id = session.get("user_id", None)
            language = user.user_specific_get_language(db_conn_cursor, user_id)
            session["language"] = language
            session["websocket_api_key"] = "u17828bdabd1782gdbaudsbaby1812b"
        else:
            #Set guest language
            if session.get("language", None) == None:
                language = general.guest_language(session)
            else:
                language = session.get("language", None)
        #=======================================
        if merchant_identification[4:8] == "MRCT" and len(merchant_identification) == 20:
            merchant_id = merchant_identification
            merchant_details = general.select_merchant(db_conn_cursor, id=merchant_id, nku = None, username=None, by_id=True, by_nku = False)
        else:
            merchant_nku = html.escape(merchant_identification)
            merchant_details = general.select_merchant(db_conn_cursor, id=None, nku = merchant_nku, username=None, by_id=False, by_nku = True)

        product_id = html.escape(product_id)
        assert len(merchant_identification) > 0, "Invalid merchant NKU" 
        assert len(product_id) > 5, "Invalid Product ID" 
        assert merchant_details != None, "No associated merchant / seller found!"

        merchant_id = merchant_details[1]
        assert merchant_id[4:8] == "MRCT", "Invalid merchant ID found!"
        merchant_product_details = general.select_product(db_conn_cursor, merchant_id=merchant_id, product_id=product_id, by_merchant= False)
        merchant_product_details += (merchant_id,)
        assert len(merchant_product_details) > 0, f"No product found with ID {product_id}"
        #get reviews from merchant
        merchant_product_reviews = general.select_prd_review(db_conn_cursor, product_id=product_id, review_status=None, by_prd_id=True, by_review_status= False)
        #get gallery
        merchant_product_gallery = general.select_prd_gallery(db_conn_cursor, product_id=product_id, product_language=language)
        #get variation
        merchant_product_variations = general.select_prd_variations(db_conn_cursor, product_id=product_id, language = None, by_language= False)
        #get product description by language
        merchant_product_descriptions = general.select_prd_descriptions(db_conn_cursor, product_id=product_id, language = language)
        #get product offerlines
        offerlines = product.get_offerlines(db_conn_cursor, product_id, language)
        videos = product.get_video(db_conn_cursor, product_id, language)
        #Find the prices to show
        #1) Check if the product variation has different prices
        price_to_show = merchant_product_details[4]
        show_price_range = False
        minimum_variation_price = None
        maximum_variation_price = None
        if len(merchant_product_variations)>0:
            show_price_range = True
            for i in range(len(merchant_product_variations)):
                product_variation_price = float(merchant_product_variations[i][3])
                #assign a value for start and compare
                #For minimum
                if minimum_variation_price == None or minimum_variation_price > product_variation_price:
                    minimum_variation_price = product_variation_price
                #For maximum
                if maximum_variation_price == None or maximum_variation_price < product_variation_price:
                    maximum_variation_price = product_variation_price
            if minimum_variation_price != maximum_variation_price :
                price_to_show = minimum_variation_price
        else:
            show_price_range = False

        if user_is_logged_in:
            user_cart_details = user.user_specific_get_cart(db_conn_cursor, user_id)
            user_cart_sub_total = 0.00
            for cart_detail in user_cart_details:
                user_cart_sub_total+=float(cart_detail[10])
            response = render_template("products/electronic.html", product_details = merchant_product_details, product_reviews = merchant_product_reviews, product_gallery = merchant_product_gallery,\
                product_variations = merchant_product_variations, product_descriptions = merchant_product_descriptions, user_cart_details = user_cart_details, user_cart_sub_total = user_cart_sub_total,\
                offerlines = offerlines, videos = videos, show_price_range = show_price_range, price_to_show = price_to_show,\
                minimum_variation_price = minimum_variation_price, maximum_variation_price = maximum_variation_price)
        else:
            guest_cart = session.get("guest_cart", None)
            if guest_cart == None:
                guest_cart = Cart()
                guest_cart_sub_total = 0.00
            else:
                guest_cart = Cart.from_dict(guest_cart)
                guest_cart_sub_total = guest_cart.get_total()
            response = render_template("products/electronic.html", product_details = merchant_product_details, product_reviews = merchant_product_reviews, product_gallery = merchant_product_gallery,\
                product_variations = merchant_product_variations, product_descriptions = merchant_product_descriptions, offerlines = offerlines, guest_cart_items = guest_cart.get_cart_items(), guest_cart_sub_total = guest_cart_sub_total, videos = videos,\
                show_price_range = show_price_range, price_to_show = price_to_show, minimum_variation_price = minimum_variation_price, maximum_variation_price = maximum_variation_price)
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        if 'db_conn_cursor' in locals():
            mysql_connector.close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            mysql_connector.close_mysql_cursor(db_conn)
        #serialize key and send it to search engine then redirect to result
        return response
    
@shared.route("checkout")
def checkout():
    try:
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #=======================================
        #if user logged in we get the language
        user_is_logged_in = user.is_logged_in()
        if user_is_logged_in:
            response = redirect("/user/cart")
        else:
            language = general.guest_language(session)
            session["language"] = language
            guest_cart = session.get("guest_cart", None)
            if guest_cart == None:
                guest_cart = Cart()
                guest_cart_sub_total = 0.00
            else:
                guest_cart = Cart.from_dict(guest_cart)
                guest_cart_sub_total = guest_cart.get_total()
            response = render_template("checkout.html", guest_cart_items = guest_cart.get_cart_items(), guest_cart_sub_total = guest_cart_sub_total)
        
    except Exception as e:
        response = render_template("error.html", msg = str(e))
    finally:
        #serialize key and send it to search engine then redirect to result
        return response