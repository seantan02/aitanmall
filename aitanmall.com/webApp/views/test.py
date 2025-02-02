from flask import Blueprint, render_template, request
from webApp import mysql_connector
from webApp.helper import twilio
from webApp.helper import general
from webApp.helper import user
from webApp.helper.search_engine import primary_language_cortex
from webApp.helper import telegram
from webApp.classes.user.voucher import Voucher
from webApp.helper import voucher

test = Blueprint("test", __name__, static_folder="static", template_folder="templates")

@test.route("assign_prd_lang")
def assign_prd_lang():
    testing = False
    db_conn_need_close = False
    db_conn_cursor_need_close = False
    if testing:
        try:
            db_conn_list = general.connect_to_assets_database()
            db_conn = db_conn_list[0]
            db_conn_need_close = True
            db_conn_cursor = db_conn_list[1]
            db_conn_cursor_need_close = True
            query = """
            SELECT prd_id,prd_name FROM product
            """
            db_conn_cursor.execute(query)
            result = db_conn_cursor.fetchall()
            for row in result:
                prd_id = row[0]
                prd_name = row[1]
                languages_to_detect = primary_language_cortex.get_lingua_languages()
                prd_lang = primary_language_cortex.detect_language(languages_to_detect, prd_name)
                query = """
                UPDATE product SET prd_lang = %s WHERE prd_id = %s
                """
                db_conn_cursor.execute(query, (prd_lang, prd_id))
                db_conn.commit()

            db_conn_cursor.close()
            #close our connection
            db_conn.close()
            response = "Success"
        except Exception as e:
            response = str(e)
        if db_conn_cursor_need_close:
            db_conn_cursor.close()
        if db_conn_need_close:
            db_conn.close()
        return response
    return render_template("error.html")

@test.route("search_product")
def search_product():
    testing = False
    db_conn_need_close = False
    db_conn_cursor_need_close = False
    if testing:
        try:
            string_list = ["airbuds 2021", "MANCODES cleanser", "airbuds pro"]
            search_key = "airbuds"

            #operation algorithm here
            #1 convert search and database names to lower case
            search_key = search_key.lower()
            #2 for efficiency purposes, we convert database names to lower case during the loop
            #3 
            #case #1 : If search key is in the one of our name
            #we then just pop it out and take the len of word as number of char matches
            #case #2 : Search key not directly in name so we check letter by letter in order and see the similarity
            #we then add 1 for each matched letter in order and sum the total matches up and compare
            #list from case 2 is prioritize over case 1 so we will add list from case 1 to case 2 in the end
            x = []
            string_list_size = len(string_list)
            i = 0
            while i < string_list_size:
                string_value = string_list[i].lower()
                #case 1
                if search_key in string_value:
                    string_list.pop(i)
                    matched_value_total = len(search_key)
                    i -= 1
                    string_list_size -= 1
                #case 2
                else:
                    tokenized_search_key = general.tokenize(search_key)
                    ignore = ["?",".","@"]
                    #for efficiency purposes we dont tokenize each string but we compare directly by index
                    for idx in range(len(tokenized_search_key)):
                        matched_value_total = 0
                        token_search_key = tokenized_search_key[idx]
                        #if this token needs to be ignored 
                        if token_search_key in ignore:
                            continue
                        if string_value[idx] == token_search_key:
                            matched_value = 1
                        else:
                            matched_value = 0
                        matched_value_total += matched_value
                x.append(matched_value_total)
                i += 1
            response = x
        except Exception as e:
            response = str(e)
        return response
    else:
        return render_template("error.html")

@test.route("twilio_sms")
def twilio_sms():
    development_mode = False
    if development_mode:
        try:
            result = twilio.send_sms("This is testing message from AiTan SDN BHD", 60195278779)
            return result
        except Exception as e:
            return e
    else:
        return render_template("error.html")

@test.route("database")
def database():
    development_mode = False
    if development_mode:
        try:
            db_conn = general.create_general_mysql_conn()
            mysql_connector.set_up_user_database(db_conn)
            db_conn.close()
            return "Success"
        except Exception as e:
            return str(e)
    else:
        return render_template("error.html")

@test.route("merchant_database")
def merchant_database():
    development_mode = False
    if development_mode:
        try:
            db_conn = general.create_general_mysql_conn()
            mysql_connector.set_up_merchant_all_database(db_conn)
            mysql_connector.set_up_merchant_datebase(db_conn)
            db_conn.close()
            return "Success"
        except Exception as e:
            return str(e)
    else:
        return render_template("error.html")
    
@test.route("mailer")
def mailer():
    development_mode = False
    if development_mode:
        from webApp.helper import mailer
        try:
            html_template = render_template("mail/email_verification.html", name= "Aitan", url = "https://aitanmall.com")
            testing_recipient = "seantsa02@gmail.com"
            subject = "Verify your email account"
            return str(mailer.send_html_email(testing_recipient, subject, html_template))
        except Exception as e:
            return str(e)
    else:
        return render_template("error.html")
    
@test.route("country_code")
def country_code():
    country_list = """{ country: 'Argentina', code: 'AR' }, { country: 'Australia', code: 'AU' }, { country: 'Austria', code: 'AT' }, { country: 'Belgium', code: 'BE' }, { country: 'Bolivia', code: 'BO' }, { country: 'Brazil', code: 'BR' }, { country: 'Bulgaria', code: 'BG' }, { country: 'Canada', code: 'CA' }, { country: 'Chile', code: 'CL' }, { country: 'Columbia', code: 'CO' }, { country: 'Costa Rica', code: 'CR' }, { country: 'Croatia', code: 'HR' }, { country: 'Cyprus', code: 'CY' }, { country: 'Czech Republic', code: 'CZ' }, { country: 'Denmark', code: 'DK' }, { country: 'Dominican Republic', code: 'DO' }, { country: 'Egypt', code: 'EG' }, { country: 'Estonia', code: 'EE' }, { country: 'Finland', code: 'FI' }, { country: 'France', code: 'FR' }, { country: 'Germany', code: 'DE' }, { country: 'Greece', code: 'GR' }, { country: 'Hong Kong SAR China', code: 'HK' }, { country: 'Hungary', code: 'HU' }, { country: 'Iceland', code: 'IS' }, { country: 'India', code: 'IN' }, { country: 'Indonesia', code: 'ID' }, { country: 'Ireland', code: 'IE' }, { country: 'Israel', code: 'IL' }, { country: 'Italy', code: 'IT' }, { country: 'Japan', code: 'JP' }, { country: 'Latvia', code: 'LV' }, { country: 'Liechtenstein', code: 'LI' }, { country: 'Lithuania', code: 'LT' }, { country: 'Luxembourg', code: 'LU' }, { country: 'Malta', code: 'MT' }, { country: 'Mexico ', code: 'MX' }, { country: 'Netherlands', code: 'NL' }, { country: 'New Zealand', code: 'NZ' }, { country: 'Norway', code: 'NO' }, { country: 'Paraguay', code: 'PY' }, { country: 'Peru', code: 'PE' }, { country: 'Poland', code: 'PL' }, { country: 'Portugal', code: 'PT' }, { country: 'Romania', code: 'RO' }, { country: 'Singapore', code: 'SG' }, { country: 'Slovakia', code: 'SK' }, { country: 'Slovenia', code: 'SI' }, { country: 'Spain', code: 'ES' }, { country: 'Sweden', code: 'SE' }, { country: 'Switzerland', code: 'CH' }, { country: 'Thailand', code: 'TH' }, { country: 'Trinidad & Tobago', code: 'TT' }, { country: 'United Arab Emirates', code: 'AE' }, { country: 'United Kingdom', code: 'GB' }, { country: 'United States', code: 'US' }, { country: 'Uraguay', code: 'UY' }"""
    development_mode = False
    if development_mode:
        try:
            country_list = country_list.split("},")
            new_list = []
            for value in country_list:
                value = value.strip()
                if value[-1] != "}":
                    value += "}"
                value = value[0:1]+"'"+value[2:]
                value = value[0:1]+"'"+value[2:]
                value = value[:9]+"'"+value[9:]
                index_of_code = value.index("code")
                value = value[:index_of_code]+"'"+value[index_of_code:-7]+"'"+value[-7:]
                new_list.append(value)
            return new_list
        except Exception as e:
            return str(e)
    else:
        return render_template("error.html") 

@test.route("country_code2")
def country_code2():
    country_list = "{'country': 'Argentina', 'code': 'AR'}","{'country': 'Australia', 'code': 'AU'}","{'country': 'Austria', 'code': 'AT'}","{'country': 'Belgium', 'code': 'BE'}","{'country': 'Bolivia', 'code': 'BO'}","{'country': 'Brazil', 'code': 'BR'}","{'country': 'Bulgaria', 'code': 'BG'}","{'country': 'Canada', 'code': 'CA'}","{'country': 'Chile', 'code': 'CL'}","{'country': 'Columbia', 'code': 'CO'}","{'country': 'Costa Rica', 'code': 'CR'}","{'country': 'Croatia', 'code': 'HR'}","{'country': 'Cyprus', 'code': 'CY'}","{'country': 'Czech Republic', 'code': 'CZ'}","{'country': 'Denmark', 'code': 'DK'}","{'country': 'Dominican Republic', 'code': 'DO'}","{'country': 'Egypt', 'code': 'EG'}","{'country': 'Estonia', 'code': 'EE'}","{'country': 'Finland', 'code': 'FI'}","{'country': 'France', 'code': 'FR'}","{'country': 'Germany', 'code': 'DE'}","{'country': 'Greece', 'code': 'GR'}","{'country': 'Hong Kong SAR China', 'code': 'HK'}","{'country': 'Hungary', 'code': 'HU'}","{'country': 'Iceland', 'code': 'IS'}","{'country': 'India', 'code': 'IN'}","{'country': 'Indonesia', 'code': 'ID'}","{'country': 'Ireland', 'code': 'IE'}","{'country': 'Israel', 'code': 'IL'}","{'country': 'Italy', 'code': 'IT'}","{'country': 'Japan', 'code': 'JP'}","{'country': 'Latvia', 'code': 'LV'}","{'country': 'Liechtenstein', 'code': 'LI'}","{'country': 'Lithuania', 'code': 'LT'}","{'country': 'Luxembourg', 'code': 'LU'}","{'country': 'Malta', 'code': 'MT'}","{'country': 'Mexico ', 'code': 'MX'}","{'country': 'Netherlands', 'code': 'NL'}","{'country': 'New Zealand', 'code': 'NZ'}","{'country': 'Norway', 'code': 'NO'}","{'country': 'Paraguay', 'code': 'PY'}","{'country': 'Peru', 'code': 'PE'}","{'country': 'Poland', 'code': 'PL'}","{'country': 'Portugal', 'code': 'PT'}","{'country': 'Romania', 'code': 'RO'}","{'country': 'Singapore', 'code': 'SG'}","{'country': 'Slovakia', 'code': 'SK'}","{'country': 'Slovenia', 'code': 'SI'}","{'country': 'Spain', 'code': 'ES'}","{'country': 'Sweden', 'code': 'SE'}","{'country': 'Switzerland', 'code': 'CH'}","{'country': 'Thailand', 'code': 'TH'}","{'country': 'Trinidad & Tobago', 'code': 'TT'}","{'country': 'United Arab Emirates', 'code': 'AE'}","{'country': 'United Kingdom', 'code': 'GB'}","{'country': 'United States', 'code': 'US'}","{'country': 'Uraguay', 'code:' 'UY' }"
    development_mode = False
    if development_mode:
        try:
            country_list = country_list.replace("'", '"')
            return country_list
        except Exception as e:
            return str(e)
    else:
        return render_template("error.html") 

@test.route("stripe_charge")
def stripe_charge():
    development_mode = False
    if development_mode:
        try:
            import stripe
            from webApp.helper import stripe as strp
            stripe.api_key = strp.get_test_key()

            customer_id = "cus_O6wb5qvL1ljJZV"
            payment_id = "pm_1NLiyNA7FlkpmYzdn07bCNfG"

            payment_intent = stripe.PaymentIntent.create(
                customer= customer_id,
                payment_method= payment_id,
                amount=200,
                currency="myr",
                confirm=True,
            )
            
            
            return payment_intent
        except Exception as e:
            return str(e)
    else:
        return render_template("error.html") 

@test.route("product_page")
def product_page():
    development_mode = False
    if development_mode:
        try:
            return render_template("product.html")
        except Exception as e:
            return str(e)
    else:
        return render_template("error.html", msg = "Sorry") 

@test.route("twilio_whatsapp")
def twilio_whatsapp():
    development_mode = False
    if development_mode:
        try:
            import os
            from twilio.rest import Client

            # Find your Account SID and Auth Token at twilio.com/console
            # and set the environment variables. See http://twil.io/secure
            account_sid = "ACb80e464633722d37b6b1c5d545d0330e"
            auth_token = "444a70b5bd2921824b4c767a6f8991e5"
            client = Client(account_sid, auth_token)

            message = client.messages \
                .create(
                    media_url=['https://upload.wikimedia.org/wikipedia/commons/f/f0/500_kb.jpg?20140827034232'],
                    from_='whatsapp:+14155238886',
                    to='whatsapp:+60195278779'
                )

            return(message.status)
        except Exception as e:
            return str(e)
    else:
        return render_template("error.html", msg = "Sorry") 

@test.route("mysql_user_test")
def mysql_user_test():
    development_mode = False
    if development_mode:
        try:
            db_conn = general.create_general_mysql_conn()
            db_conn_cursor = db_conn.cursor()
            user_subscription_start_date = general.get_current_datetime()
            user_subscription_bill_start_date = general.get_datetime_from_now(50*24*60*60)
            user_subscription_end_date = general.get_datetime_from_now(50*24*60*60+3625000)
            subscription_product_id = "SAMYSPRD012831283"
            user_id = "SAMY335479878626"
            x = user.update_subscription_status(mysql_conn=db_conn, mysql_cursor=db_conn_cursor,\
                    status="cancelled",user_id= user_id, user_subscription_id="SAMYUSC477327741067")
            return str(x)
        except Exception as e:
            return str(e)
        finally:
            if 'db_conn_cursor' in locals():
                mysql_connector.close_mysql_cursor(db_conn_cursor)
            if 'db_conn' in locals():
                mysql_connector.close_mysql_conn(db_conn)
    else:
        return render_template("error.html", msg = "Sorry") 
    
@test.route("telegram_bot")
def telegram_bot():
    development_mode = False
    if development_mode:
        try:
            token = telegram.get_token()
            chat_id = telegram.get_all_orders_chat_id()
            text = f"""
{"cod".upper()} Order
Order ID: SAMYORD19239123

Customer Information:
Name: John
Address: 32, jaklajaainw, mlaysia
Postcode: 123123
Contact: 601283718237
Total Before Fees: Rm1239.10
Handling Fees: Rm1239.10
Payment Gateway Fees: Rm1239.10
Shipping Fees: Rm1239.10
Total Final: Rm1239.10

<a href='https://merchant.aitanmall.com/quickcall/check_order?ord_id=SAMYORD19239123'>Check Order Details</a>
<a href='api.whatsapp.com/send?phone=601283718237'>Whatsapp Customer Now</a>"""
            x = telegram.send_message(token, chat_id, text)
            return x
        except Exception as e:
            return str(e)
    else:
        return render_template("error.html", msg = "Sorry") 

@test.route("create_voucher")
def create_voucher():
    development_mode = False
    if development_mode:
        try:
            db_conn = general.create_general_mysql_conn()
            db_conn_cursor = db_conn.cursor()
            voucher_id = voucher.generate_unique_voucher_id(db_conn_cursor)
            expire_date = general.get_datetime_from_now(5256000)
            voucher_object = Voucher(voucher_id, "NEWUSER20", "For new user! 20% off any product capped at Rm50.", 20.00, "percentage", expire_date, 999999, 0, "active")
            
            create_voucher = voucher.create_voucher(db_conn, db_conn_cursor, voucher_object.get_voucher_id(), voucher_object.get_voucher_code(),\
                voucher_object.get_voucher_description(), voucher_object.get_voucher_discount_amount(), voucher_object.get_voucher_discount_type(), \
                voucher_object.get_voucher_created_date(), voucher_object.get_voucher_expire_date(), voucher_object.get_voucher_max_usage(), voucher_object.get_voucher_usage_count(), "active")
            return str(create_voucher)
        except Exception as e:
            return str(e)
        finally:
            if 'db_conn_cursor' in locals():
                mysql_connector.close_mysql_cursor(db_conn_cursor)
            if 'db_conn' in locals():
                mysql_connector.close_mysql_conn(db_conn)
    else:
        return render_template("error.html", msg = "Sorry") 

@test.route("get_all_user")
def get_all_user():
    development_mode = True
    if development_mode:
        try:
            token = request.args.get("token", None)
            token_to_match = "aitan551813abcd1234"
            assert token == token_to_match, (404, "Bad request")
            db_conn = general.create_general_mysql_conn()
            db_conn_cursor = db_conn.cursor()
            mysql_connector.use_db(db_conn_cursor, "user")
            query = """
SELECT * FROM user
"""
            db_conn_cursor.execute(query)
            results = db_conn_cursor.fetchall()

            return render_template("/test/get_all_user.html", items = results)
        except Exception as e:
            return str(e)
        finally:
            if 'db_conn_cursor' in locals():
                mysql_connector.close_mysql_cursor(db_conn_cursor)
            if 'db_conn' in locals():
                mysql_connector.close_mysql_conn(db_conn)
    else:
        return render_template("error.html", msg = "Sorry") 
    
@test.route("langdetect")
def langdetect():
    development_mode = True
    if development_mode:
        try:
            from webApp.helper.search_engine import primary_language_cortex as plc1

            return str(plc1.detect_language("Assalam saya berminat nak $Aitanmall Earbuds$ ?"))
        except Exception as e:
            return str(e)
    else:
        return render_template("error.html", msg = "Sorry") 