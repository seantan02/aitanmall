from flask import request, make_response
import random
import string
from webApp.helper import json_tools
from webApp import mysql_connector
import datetime
from zoneinfo import ZoneInfo
import re

#=========================================================================
#MYSQL FUNCTIONS
#=========================================================================
def create_general_mysql_conn():
    database_json = json_tools.read_json("/var/www/aitanmall.com/private/data/databases.json")

    assets_db = database_json["assets"]
    db_username = assets_db["username"]
    db_password = assets_db["password"]
    #connect and return
    db_conn = mysql_connector.create_mysql_conn(db_username,db_password)
    return db_conn

def connect_to_assets_database():
    database_json = json_tools.read_json("/var/www/aitanmall.com/private/data/databases.json")

    assets_db = database_json["assets"]
    assets_db_username = assets_db["username"]
    assets_db_password = assets_db["password"]
    assets_db_database = assets_db["database"]
    #connect and return
    db_conn = mysql_connector.create_mysql_conn(assets_db_username,assets_db_password,db_name = assets_db_database)
    db_conn_cursor = db_conn.cursor(prepared=True)
    return [db_conn,db_conn_cursor]

def guest_language(session):
    language = "eng"
    session_language = session.get("language", None)
    if session_language != None:
        language = session_language
    return language

def get_product(mysql_cursor, limit = 10):
    """
    This method selects products from database
    :return: List in format: [[id, prd_name, prd_status, prd_price, prd_offer_price, prd_image ,prd_quantity, prd_sku, prd_date, prd_level, prd_cost , prd_preorders_status, prd_id, merchant_id]]
    """
    mysql_connector.use_db(mysql_cursor,"product")

    query = """
    SELECT product.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
        prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
        prd_details.prd_id, product.merchant_id
    FROM prd_details
    JOIN product ON prd_details.prd_id = product.prd_id
    WHERE prd_details.prd_status = %s
    LIMIT {}
    """.format(limit)

    mysql_cursor.execute(query, ("active",))
    product_list = mysql_cursor.fetchall()

    return product_list

def select_merchant(db_conn_cursor, id, nku, username, by_id = False, by_nku= True, by_username = False) -> None|list:
    """
    This method select merchant details except for password from merchant_all database 
    :return: List of details in the format: (id, merchant_id, merchant_username, merchant_phone_country_code, merchant_phone_number, merchant_email, merchant_email_verification_status, merchant_password, merchant_nku, merchant_level, merchant_registration_status)
    """

    mysql_connector.use_db(db_conn_cursor, "merchant")
    if by_id and by_nku:
        query = """
        SELECT id, merchant_id, merchant_username, merchant_phone_country_code, merchant_phone_number, merchant_email, merchant_email_verification_status, merchant_password, merchant_nku, merchant_level, merchant_registration_status
        FROM merchant
        WHERE merchant_id = %s AND merchant_nku = %s
        """
        parameters = (id, nku)
    elif by_id and not by_nku:
        query = """
        SELECT id, merchant_id, merchant_username, merchant_phone_country_code, merchant_phone_number, merchant_email, merchant_email_verification_status, merchant_password, merchant_nku, merchant_level, merchant_registration_status
        FROM merchant
        WHERE merchant_id = %s
        """
        parameters = (id,)
    elif not by_id and by_nku:
        query = """
        SELECT id, merchant_id, merchant_username, merchant_phone_country_code, merchant_phone_number, merchant_email, merchant_email_verification_status, merchant_password, merchant_nku, merchant_level, merchant_registration_status
        FROM merchant
        WHERE merchant_nku = %s
        """
        parameters = (nku,)
    elif by_username:
        query = """
        SELECT id, merchant_id, merchant_username, merchant_phone_country_code, merchant_phone_number, merchant_email, merchant_email_verification_status, merchant_password, merchant_nku, merchant_level, merchant_registration_status
        FROM merchant
        WHERE merchant_username = %s
        """
        parameters = (username,)

    db_conn_cursor.execute(query, parameters)
    result = db_conn_cursor.fetchall()
    if len(result) == 1:
        return result[0]
    return None

def select_product(db_conn_cursor, merchant_id, product_id, by_merchant = False) -> list:
    """
    This method select merchant product details by product ID OR both merchant ID
    :return: List of details in the format: [id, prd_name, prd_status, prd_price, prd_offer_price, prd_image ,prd_quantity, prd_sku, prd_date, prd_level, prd_cost , prd_preorders_status, prd_id, merchant_id]
    """

    mysql_connector.use_db(db_conn_cursor, "product")
    if by_merchant:
        query = """
        SELECT prd_details.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id
        FROM prd_details
        JOIN product ON prd_details.prd_id = product.prd_id
        WHERE product.merchant_id = %s AND product.prd_id = %s
        """
        db_conn_cursor.execute(query, (merchant_id, product_id))
    else:
        query = """
        SELECT prd_details.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id
        FROM prd_details
        JOIN product ON prd_details.prd_id = product.prd_id
        WHERE product.prd_id = %s
        """
        db_conn_cursor.execute(query, (product_id,))
    result = db_conn_cursor.fetchall()

    if len(result) > 0:
        return result[0]
    return None

def select_prd_gallery(db_conn_cursor, product_id, product_language, by_prd_id = True, by_prd_lang = True):
    """
    This method select merchant product gallery
    :return: List of details in the format: [[id,prd_image,prd_lang,prd_id FROM prd_gallery]]
    """
    
    mysql_connector.use_db(db_conn_cursor, "product")
    #determin which query to use base on parameter
    if by_prd_id and by_prd_lang:
        query = """
        SELECT id,prd_image,prd_lang,prd_id 
        FROM prd_gallery 
        WHERE prd_id = %s AND prd_lang = %s
        """
        parameters = (product_id, product_language)
    elif by_prd_id and not by_prd_lang:
        query = """
        SELECT id,prd_image,prd_lang,prd_id 
        FROM prd_gallery 
        WHERE prd_id = %s
        """
        parameters = (product_id,)
    elif not by_prd_id and by_prd_lang:
        query = """
        SELECT id,prd_image,prd_lang,prd_id 
        FROM prd_gallery 
        WHERE prd_lang = %s
        """
        parameters = (product_language,)
    else:
        return None
    
    db_conn_cursor.execute(query, parameters)
    result = list(db_conn_cursor)
    return result

def select_prd_review(db_conn_cursor, product_id, review_status, by_prd_id = True, by_review_status = True):
    """
    This method select merchant product reviews
    :return: List of details in the format: [[id,prd_review_profile_img,prd_review,prd_review_img,prd_review_star,cust_id,ord_id,prd_id,prd_review_status]]
    """
    
    mysql_connector.use_db(db_conn_cursor, "product")
    
    #determin which query to use base on parameter
    if by_prd_id and by_review_status:
        query = """
        SELECT id,prd_review_profile_img,prd_review,prd_review_img,prd_review_star,cust_id,ord_id,prd_id,prd_review_status 
        FROM prd_review 
        WHERE prd_id = %s AND prd_review_status = %s
        """
        parameters = (product_id, review_status)
    elif by_prd_id and not by_review_status:
        query = """
        SELECT id,prd_review_profile_img,prd_review,prd_review_img,prd_review_star,cust_id,ord_id,prd_id,prd_review_status 
        FROM prd_review 
        WHERE prd_id = %s
        """
        parameters = (product_id,)
    elif not by_prd_id and by_review_status:
        query = """
        SELECT id,prd_review_profile_img,prd_review,prd_review_img,prd_review_star,cust_id,ord_id,prd_id,prd_review_status 
        FROM prd_review 
        WHERE prd_review_status = %s
        """
        parameters = (review_status,)
    else:
        return None
    
    db_conn_cursor.execute(query, parameters)
    result = list(db_conn_cursor)
    return result

def select_prd_variations(db_conn_cursor, product_id, language, by_language = True):
    """
    This method select merchant product reviews
    :return: List of details in the format: [[id, prd_var, prd_var_des, prd_var_price, prd_var_quantity, prd_var_sku, prd_var_img, prd_var_cat_id]]
    """
    result_to_return = list()
    mysql_connector.use_db(db_conn_cursor, "product")
    query = """
    SELECT id
    FROM prd_var_cat 
    WHERE prd_id = %s
    """
    db_conn_cursor.execute(query, (product_id,))
    results = db_conn_cursor.fetchall()
    for result in results:
        prd_var_cat_id = result[0]
        #determin which query to use base on parameter
        if by_language:
            query = """
            SELECT id,prd_var,prd_var_des,prd_var_price,prd_var_quantity,prd_var_sku,prd_var_img,prd_var_cat_id
            FROM prd_var 
            WHERE prd_var_cat_id = %s
            """
            parameters = (prd_var_cat_id,)
            #then carry out other things like names but for now we will forget about that
        else:
            query = """
            SELECT id,prd_var,prd_var_des,prd_var_price,prd_var_quantity,prd_var_sku,prd_var_img,prd_var_cat_id
            FROM prd_var 
            WHERE prd_var_cat_id = %s
            """
            parameters = (prd_var_cat_id,)
            
        db_conn_cursor.execute(query, parameters)
        result_to_return += db_conn_cursor.fetchall()

    return result_to_return

def select_prd_descriptions(db_conn_cursor, product_id, language) -> list:
    """
    This method select merchant product descriptions
    :return: List of details in the format: [[id,prd_des,prd_lang,prd_id]]
    """
    try:
        mysql_connector.use_db(db_conn_cursor, "product")
        query = """
        SELECT id,prd_des,prd_lang,prd_id
        FROM prd_des 
        WHERE prd_id = %s AND prd_lang = %s
        """
        db_conn_cursor.execute(query, (product_id,language))
        results = db_conn_cursor.fetchall()
        if len(results) > 0:
            return results
        return []
    except Exception as e:
        return []

def generate_unique_order_id(mysql_cursor, prefix = "SAMYORD", length = 11):
    """
    This method generate a unique order base on assets database
    """
    mysql_connector.use_db(mysql_cursor, "orders")
    random_integer = generate_random_integer(length)
    assert random_integer != None, "Error in generating unique order ID#1"
    unique_ord_id = prefix+str(random_integer)
    
    query = """
    SELECT id
    FROM orders
    WHERE ord_id = %s
    """

    mysql_cursor.execute(query, (unique_ord_id,))
    num_results = len(mysql_cursor.fetchall())

    while(num_results > 0):
        random_integer = generate_random_integer(length)
        assert random_integer != None, "Error in generating unique order ID#1"
        unique_ord_id = prefix+str(random_integer)
        mysql_cursor.execute(query, (unique_ord_id,))
        num_results = len(mysql_cursor.fetchall())

    return unique_ord_id 
#=========================================================================
#General
#=========================================================================
def tokenize(string):
    if isinstance(string, str):
        list_to_return = list()
        tokenized_string = [char for char in string]
        list_to_return += tokenized_string
                
    else:
        raise Exception("Only list can be tokenized")
    return list_to_return

def get_response_recaptcha_v3(g_response) -> object:
    #import module needed
    from flask import request
    from requests import post

    g_response_url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': '6Le5uQwkAAAAALD4RMkZ7aVRnKeXaublVihETczh',
        'response': g_response,
        'remoteip': request.remote_addr,
    }
    g_response_verification = post(g_response_url, data=data)
            
    return g_response_verification.json()

def pass_recaptcha_v3_test(g_response) -> bool:
    #import module needed
    from flask import request
    from requests import post

    g_response_url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': '6Le5uQwkAAAAALD4RMkZ7aVRnKeXaublVihETczh',
        'response': g_response,
        'remoteip': request.remote_addr,
    }
    g_response_verification = post(g_response_url, data=data)
    g_response_result = g_response_verification.json()
            
    if g_response_result["success"] and g_response_result["score"] > 0.5:
        return True
    return False


def standardize_phone_number(phone_number, country_code = "60") -> str:
    if phone_number[:2] == "01":
        phone_number = country_code+phone_number[1:]
    elif phone_number[:2] != "60":
        phone_number = country_code+phone_number

    return phone_number

def cookie_exist(cookie_name) -> bool:
    if cookie_name in request.cookies:
        return True
    return False

def get_cookie(cookie_name):
    try:
        cookie_value = request.cookies.get(cookie_name)
        return cookie_value
    except:
        return None

def generate_random_string(length) -> str:
    try:
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string
    except:
        return None
    
def generate_random_integer(length) -> int:
    try:
        if length <= 0:
            return "Length must be a positive integer."
        elif length == 1:
            return random.randint(0, 9)
        else:
            start = 10 ** (length - 1)
            end = (10 ** length) - 1
            return random.randint(start, end)
    except:
        return None
    
def get_current_datetime():
    try:
        zone_info = ZoneInfo('Asia/Kuala_Lumpur')
        current_time = datetime.datetime.now(zone_info)
        current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        return current_time
    except:
        return None

def get_datetime_from_now(seconds):
    try:
        zone_info = ZoneInfo('Asia/Kuala_Lumpur')
        new_expiration_time = datetime.datetime.now(zone_info) + datetime.timedelta(seconds=seconds)
        new_expiration_time = new_expiration_time.strftime('%Y-%m-%d %H:%M:%S')
        return new_expiration_time
    except:
        return None

def is_datetime(string):
    try:
        datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        return True
    except Exception:
        return False

def is_valid_email(email):
    # Define a regular expression for a typical email address
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if re.match(email_regex, email):
        return True
    else:
        return False
    
def get_datetime_difference(datetime1, datetime2, absolute = False) -> Exception | int:
    try:
        datetime1 = datetime.datetime.strptime(datetime1, '%Y-%m-%d %H:%M:%S')
        datetime2 = datetime.datetime.strptime(datetime2, '%Y-%m-%d %H:%M:%S')

        difference = datetime2 - datetime1
        seconds = int(difference.total_seconds())
        if absolute:
            seconds = abs(seconds)

        return seconds
    except Exception as e:
        return e

def get_unix_datetime_from_now(seconds):
    try:
        zone_info = ZoneInfo('Asia/Kuala_Lumpur')
        current_datetime = datetime.datetime.now(zone_info)

        # Increment the datetime by 1 hour
        incremented_datetime = current_datetime + datetime.timedelta(seconds=seconds)

        # Convert the incremented datetime to a Unix timestamp
        incremented_timestamp = int(incremented_datetime.timestamp())
        return incremented_timestamp
    except:
        return None
    
def make_str_datetime_object(datetime_string, format = None) -> None|datetime.datetime:

    try:
        if format == None:
            return datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.datetime.strptime(datetime_string, str(format))
    except:
        return None
    
