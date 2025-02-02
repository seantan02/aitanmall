import random
from flask import session, request, render_template
from passlib.hash import sha256_crypt
from webApp.helper import json_tools
from webApp import mysql_connector
from webApp.helper import general
from webApp.helper import mailer
import datetime

#FUNCTION CONNECTING TO MYSQL
#FUNCTION CONNECTING TO MYSQL
#FUNCTION CONNECTING TO MYSQL
#FUNCTION CONNECTING TO MYSQL
def connect_database():
    db_dict = json_tools.read_json("/var/www/aitanmall.com/private/data/databases.json")
    user_db = db_dict["user"]
    user_db_username = user_db["username"]
    user_db_password = user_db["password"]
    user_db_database = user_db["database"]
    db_conn = mysql_connector.create_mysql_conn(user_db_username,user_db_password,db_name = user_db_database)
    db_conn_cursor = db_conn.cursor(prepared=True)
    return [db_conn,db_conn_cursor]

#FUNCTION CHECKING EXISTION
#FUNCTION CHECKING EXISTION
#FUNCTION CHECKING EXISTION
#FUNCTION CHECKING EXISTION
def account_exist(mysql_cursor, email, phone_number) -> bool:
    mysql_connector.use_db(mysql_cursor, "user")
    query = """
    SELECT user_id FROM user 
    WHERE user_email = %s OR CONCAT(user_phone_number_code , user_phone_number) = %s
    """
    mysql_cursor.execute(query, (email,phone_number))
    result = list(mysql_cursor)
    #no OTP yet so yea we can send new OTP
    if len(result) > 0:
        return True
    return False

def user_temporarily_key_exist(mysql_cursor, user_id) -> bool:
    try:
        query = """
        SELECT id FROM user_temporarily_key WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)

        if num_result > 0:
            return True
        return False
    except:
        return False 

def email_verification_key_exist(mysql_cursor, user_id) -> bool:
    try:
        mysql_connector.use_db(mysql_cursor, "user")

        query = """
        SELECT id 
        FROM user_email_verification 
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)

        if num_result > 0:
            return True
        return False
    except:
        return False 
    
def membership_exist(mysql_cursor, user_id) ->bool :
    try:
        query = """
        SELECT user_membership_id FROM user_membership_id
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)

        if num_result == 1:
            return True
        return False
    except:
        return False 
#MUTATORS FUNCTION 
#MUTATORS FUNCTION 
#MUTATORS FUNCTION 
#MUTATORS FUNCTION 
def create_user_database(db_conn, user_id) -> bool:
    try:
        assert mysql_connector.create_database(db_conn, user_id), "Failed to create database"
        sql_file_path = "/var/www/aitanmall.com/backups/database/user_specific.sql"
        mysql_connector.execute_sql_file(sql_file_path, db_conn, user_id)
        response = True
    except Exception as e:
        response = False

    return response

def create_account(db_conn, mysql_cursor, user_id, email, country_code, phone_number, password, first_name = "user", last_name="new", user_language="eng") -> bool:
    mysql_connector.use_db(mysql_cursor, "user")
    #insert user data into our main database
    query = """
    INSERT INTO user (user_id, user_first_name, user_last_name, user_email, user_phone_number_code, \
        user_phone_number, user_password, user_account_status, user_language) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    mysql_cursor.execute(query, (user_id, first_name, last_name, email, country_code, phone_number, password, "new", user_language))
    num_inserted= mysql_cursor.rowcount
    db_conn.commit()
    if num_inserted == 1:
        return True
    return False

def revert_create_account(db_conn, user_id) -> bool:
    try:
        mysql_cursor = db_conn.cursor()
        query = """
        DELETE FROM user WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        db_conn.commit()

        query = """
        DROP DATABASE [IF EXISTS] {};
        """
        mysql_cursor.execute(query.format(user_id))
        db_conn.commit()

        return True
    except:
        return False
def generate_unique_user_id(mysql_cursor, prefix = "SAMY") -> str:
    mysql_connector.use_db(mysql_cursor, "user")
    query = """
    SELECT id FROM user WHERE user_id = %s
    """
    random_int = random.randint(100000000000, 999999999999)
    random_id = prefix+str(random_int)
    random_id_is_unique = False
    while(not random_id_is_unique):
        mysql_cursor.execute(query, (random_id,))
        if len(list(mysql_cursor)) == 0:
            random_id_is_unique = True
        else:
            random_int = random.randint(100000000000, 999999999999)
            random_id = prefix + str(random_int)

    return random_id

def generate_unique_payment_method_id(mysql_cursor, prefix = "SAMYPMT") -> str:
    mysql_connector.use_db(mysql_cursor, "user")
    query = """
    SELECT id 
    FROM user_payment_method 
    WHERE user_payment_method_id = %s
    """
    random_int = random.randint(100000000000, 999999999999)
    unique_random_id = prefix+str(random_int)
    mysql_cursor.execute(query, (unique_random_id,))
    results = mysql_cursor.fetchall()
    num_results = len(results)
    while(num_results != 0):
        random_int = random.randint(100000000000, 999999999999)
        unique_random_id = prefix+str(random_int)
        mysql_cursor.execute(query, (unique_random_id,))
        results = mysql_cursor.fetchall()
        num_results = len(results)

    return unique_random_id

def generate_unique_user_subscription_id(mysql_cursor, prefix = "SAMYUSC") -> str:
    mysql_connector.use_db(mysql_cursor, "user")
    query = """
    SELECT id 
    FROM user_subscription 
    WHERE user_subscription_id = %s
    """
    random_int = random.randint(100000000000, 999999999999)
    unique_random_id = prefix+str(random_int)
    mysql_cursor.execute(query, (unique_random_id,))
    results = mysql_cursor.fetchall()
    num_results = len(results)
    while(num_results != 0):
        random_int = random.randint(100000000000, 999999999999)
        unique_random_id = prefix+str(random_int)
        mysql_cursor.execute(query, (unique_random_id,))
        results = mysql_cursor.fetchall()
        num_results = len(results)

    return unique_random_id

def generate_unique_user_membership_id(mysql_cursor, prefix = "SAMYMBS") -> str:
    mysql_connector.use_db(mysql_cursor, "user")
    query = """
    SELECT id 
    FROM user_membership 
    WHERE user_membership_id = %s
    """
    random_int = random.randint(100000000000, 999999999999)
    unique_random_id = prefix+str(random_int)
    mysql_cursor.execute(query, (unique_random_id,))
    results = mysql_cursor.fetchall()
    num_results = len(results)
    while(num_results != 0):
        random_int = random.randint(100000000000, 999999999999)
        unique_random_id = prefix+str(random_int)
        mysql_cursor.execute(query, (unique_random_id,))
        results = mysql_cursor.fetchall()
        num_results = len(results)

    return unique_random_id

def log_in_user(mysql_cursor, user_id) -> bool | Exception:
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        SELECT id,user_first_name,user_last_name,user_email,user_phone_number_code,user_phone_number,user_account_status,user_language
        FROM user 
        WHERE user_id = %s
        """
        
        mysql_cursor.execute(query, (user_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result == 1:
            #set session
            session["user_logged_in"] = True
            session["user_id"] = user_id
            session["user_first_name"] = result[0][1]
            session["user_last_name"] = result[0][2]
            session["user_email"] = result[0][3]
            session["user_phone_number"] = str(result[0][4]) + str(result[0][5])
            session["user_account_status"] = result[0][6]
            session["language"] = result[0][7]
            set_user_membership_session(mysql_cursor, user_id)
            return True
        return False
    except Exception as e:
        return e

def log_out_user() -> bool:
    try:
        session.clear()
        return True
    except Exception as e:
        return str(e)

def user_log_in_details_is_valid(mysql_cursor, username:str, password:str, verify_by = "phone_number") -> None|str:
    """
    This method select user with given id and password
    :return: UserID if both valid; None otherwise;
    """
    mysql_connector.use_db(mysql_cursor, "user")
    if verify_by == "phone_number":
        query = """
        SELECT user_id,user_password FROM user WHERE user_phone_number = %s
        """
    elif verify_by == "email":
        query = """
        SELECT user_id,user_password FROM user WHERE user_email = %s
        """
    mysql_cursor.execute(query, (username,))
    result = mysql_cursor.fetchall()
    num_result = len(result)
    if num_result == 1:
        password_to_match = result[0][1]
        if sha256_crypt.verify(password, password_to_match) == True:
            return result[0][0]
    else:
        return None
    
def get_user(mysql_cursor, user_id) -> str:
    """
    This method select details from user from user database
    :return: List of tuple: [(id, user_id, user_first_name, user_last_name, user_email, user_email_verification, user_phone_number_code, user_phone_number, user_password)]
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")

        query = """
        SELECT id, user_id, user_first_name, user_last_name, user_email, user_email_verification, user_phone_number_code, user_phone_number, user_password
        FROM user 
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        
        if num_result > 0:
            return result
        else:
            return []
    except Exception as e:
        return e
    
def get_user_id(mysql_cursor, username:str, verify_by = "phone_number") -> str:
    mysql_connector.use_db(mysql_cursor, "user")
    if verify_by == "phone_number":
        query = """
        SELECT user_id FROM user WHERE user_phone_number = %s
        """
    elif verify_by == "email":
        query = """
        SELECT user_id FROM user WHERE user_email = %s
        """
    mysql_cursor.execute(query, (username,))
    result = mysql_cursor.fetchall()
    num_result = len(result)
    
    if num_result == 1:
        return result[0][0]
    else:
        return None

def is_logged_in() -> bool:
    return session.get("user_logged_in")

def user_log_in_cookie_is_valid(mysql_cursor, temporarily_key_cookie, user_id_cookie, current_time) -> bool:
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        SELECT user_temporarily_key_expire_date 
        FROM user_temporarily_key 
        WHERE user_temporarily_key = %s AND user_id = %s
        """
        
        mysql_cursor.execute(query, (temporarily_key_cookie, user_id_cookie))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        assert num_result == 1, "ERROR"
        assert current_time < str(result[0][0]), "Temporarily key has expired"
        return True
    except Exception as e:
        return e
    
def insert_user_temporarily_key(mysql_conn, mysql_cursor, user_temporarily_key, created_date, expire_date, user_id) -> bool:
    try:
        query = """
        INSERT INTO user_temporarily_key (user_temporarily_key, user_temporarily_key_created_date, user_temporarily_key_expire_date, user_id) VALUES(%s, %s, %s, %s)
        """
        mysql_cursor.execute(query, (user_temporarily_key, created_date, expire_date, user_id))
        num_inserted= mysql_cursor.rowcount
        mysql_conn.commit()

        if num_inserted == 1:
            return True
        return False
    except:
        return False

def remove_user_temporarily_key(mysql_conn, mysql_cursor, user_id) -> bool:
    try:
        query = """
        DELETE FROM user_temporarily_key WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        num_affected= mysql_cursor.rowcount
        mysql_conn.commit()

        return True
    except:
        return False

def remove_email_verification_key(mysql_conn, mysql_cursor, user_id) -> bool:
    try:
        mysql_connector.use_db(mysql_cursor, "user")

        query = """
        DELETE FROM user_email_verification 
        WHERE user_id = %s
        """

        mysql_cursor.execute(query, (user_id,))
        num_affected = mysql_cursor.rowcount
        mysql_conn.commit()

        return True
    except:
        return False

def remove_whatsapp_session(mysql_conn, mysql_cursor, user_whatsapp_phone_number) -> bool:
    try:
        mysql_connector.use_db(mysql_cursor, "user")

        query = """
        DELETE FROM user_whatsapp_chat_session 
        WHERE user_whatsapp_phone_number = %s
        """

        mysql_cursor.execute(query, (user_whatsapp_phone_number,))
        num_affected = mysql_cursor.rowcount
        mysql_conn.commit()

        return True
    except:
        return False
    
def generate_email_verification_key(mysql_conn, mysql_cursor, user_id, user_email) -> None|str:
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        INSERT INTO user_email_verification (user_email, user_email_key, user_id) 
        VALUES(%s, %s, %s)
        """

        user_email_key = general.generate_random_string(30)
        mysql_cursor.execute(query, (user_email, user_email_key, user_id))
        num_inserted= mysql_cursor.rowcount
        mysql_conn.commit()
        if num_inserted == 1:
            return user_email_key
        return None
    except Exception as e:
        return None

def get_email_verification_key_resend_permission(mysql_cursor, user_id, current_datetime):
    try:
        mysql_connector.use_db(mysql_cursor, "user")

        query = """
        SELECT user_email_verification_created_date 
        FROM user_email_verification 
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)

        if num_result == 0:
           return True 
        elif num_result == 1:
            current_datetime = datetime.datetime.strptime(current_datetime, '%Y-%m-%d %H:%M:%S')
            user_email_verification_created_datetime = datetime.datetime.strptime(str(result[0][0]), '%Y-%m-%d %H:%M:%S')
            if current_datetime >= user_email_verification_created_datetime:
                return True
        return False
    except:
        return False

def get_membership(mysql_cursor, user_id, status = None, by_status = False ) -> None|list:
    """
    This method get the membership data in database by status and user_id
    :param mysql_cursor: MYSQL cursor in user database
    :param status: The status of membership you looking for
    :param user_id: User ID 
    :return: None if nothing found; List of tuple otherwise in format of: [(id, user_membership_id, user_membership_status, user_membership_start_date, user_membership_end_date,user_id)]
    """

    try:
        mysql_connector.use_db(mysql_cursor, "user")
        if by_status:
            query = """
            SELECT id,user_membership_id,user_membership_status,user_membership_start_date,user_membership_end_date,user_id
            FROM user_membership
            WHERE user_id = %s AND user_membership_status = %s
            """
            mysql_cursor.execute(query, (user_id, status))
        else:
            query = """
            SELECT id,user_membership_id,user_membership_status,user_membership_start_date,user_membership_end_date,user_id
            FROM user_membership
            WHERE user_id = %s
            """
            mysql_cursor.execute(query, (user_id,))
        
        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0 :
            return results
        return None
    except:
        return None

def get_subscription(mysql_cursor, user_id, subscription_product_id = None, by_product_id = False ) -> None|list:
    """
    This method get the membership data in database by user_id OR BOTH product_id
    :param mysql_cursor: MYSQL cursor in user database
    :param status: The status of membership you looking for
    :param user_id: User ID 
    :param product_id: Subscription product ID
    :return: None if nothing found; List of tuple otherwise in format of: [(id, user_subscription_id, user_subscription_status, user_subscription_start_date, user_subscription_bill_start_date, user_subscription_end_date, subscription_product_id, user_id)]
    """

    try:
        mysql_connector.use_db(mysql_cursor, "user")
        if by_product_id:
            query = """
            SELECT id,user_subscription_id,user_subscription_status,user_subscription_start_date,user_subscription_bill_start_date,user_subscription_end_date,subscription_product_id,user_id
            FROM user_subscription
            WHERE user_id = %s AND subscription_product_id = %s
            """
            mysql_cursor.execute(query, (user_id, subscription_product_id))
        else:
            query = """
            SELECT id,user_subscription_id,user_subscription_status,user_subscription_start_date,user_subscription_bill_start_date,user_subscription_end_date,subscription_product_id,user_id
            FROM user_subscription
            WHERE user_id = %s
            """
            mysql_cursor.execute(query, (user_id,))
        
        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0 :
            return results
        return None
    except:
        return None
    
def get_subscription_by_id(mysql_cursor, user_id, user_subscription_id) -> None|list:
    """
    This method get the membership data in database by user_id and user_subscription_id
    :param mysql_cursor: MYSQL cursor in user database
    :param user_id: User ID 
    :param user_subscription_id: User subscription ID
    :return: None if nothing found; List of tuple otherwise in format of: [(id, user_subscription_id, user_subscription_status, user_subscription_start_date, user_subscription_bill_start_date, user_subscription_end_date, subscription_product_id, user_id)]
    """

    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        SELECT id,user_subscription_id,user_subscription_status,user_subscription_start_date,user_subscription_bill_start_date,user_subscription_end_date,subscription_product_id,user_id
        FROM user_subscription
        WHERE user_id = %s AND user_subscription_id = %s
        """
        mysql_cursor.execute(query, (user_id, user_subscription_id))

        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0 :
            return results
        return None
    except:
        return None
    
    
def email_verification_valid(mysql_cursor, user_id, user_email, key) -> bool:
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        SELECT id 
        FROM user_email_verification
        WHERE user_id = %s AND user_email = %s AND user_email_key = %s
        """
        mysql_cursor.execute(query, (user_id,user_email,key))
        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result == 1:
            return True
        return False
    except Exception as e:
        return str(e)

def verify_user_email(mysql_conn, mysql_cursor, user_id, record) -> bool:
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        UPDATE user 
        SET user_email_verification = %s 
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (record,user_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        return True
    except:
        return False

def add_stripe_customer_id(mysql_conn, mysql_cursor, stripe_customer_id, user_id) -> bool:
    try:
        mysql_connector.use_db(mysql_cursor, "user")

        query = """
        INSERT INTO stripe_customer (stripe_customer_id, user_id) VALUES
        (%s, %s)
        """
        mysql_cursor.execute(query, (stripe_customer_id,user_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        
        if num_result == 1:
            return True
        return False
    except:
        return False

def create_subscription(mysql_conn, mysql_cursor, user_membership_id, user_id, user_membership_status, user_membership_start_date, user_membership_bill_start_date, user_membership_end_date, user_subscription_id):
    try:
        query = """
        INSERT INTO user_membership (user_membership_id, user_id, user_membership_status, user_membership_start_date, user_membership_bill_start_date, user_membership_end_date, user_subscription_id) VALUES
        (%s, %s, %s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query, (user_membership_id, user_id,user_membership_status,user_membership_start_date,user_membership_bill_start_date,user_membership_end_date,user_subscription_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        
        if num_result == 1:
            return True
        return False
    except:
        return False
def update_membership_status(mysql_conn, mysql_cursor, status, user_id, user_membership_id, subscription_product_nku, by_id = True, by_nku = False):
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        if by_id and not by_nku:
            query = """
            UPDATE user_membership
            SET user_membership_status = %s
            WHERE user_id = %s AND user_membership_id = %s
            """
            mysql_cursor.execute(query, (status, user_id, user_membership_id))
        elif not by_id and by_nku:
            query = """
            UPDATE user_membership
            SET user_membership_status = %s
            WHERE user_id = %s AND user_membership_nku = %s
            """
            mysql_cursor.execute(query, (status, user_id, subscription_product_nku))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        return True
    except:
        return False

def update_subscription_status(mysql_conn, mysql_cursor, status, user_id, user_subscription_id):
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        UPDATE user_subscription
        SET user_subscription_status = %s
        WHERE user_id = %s AND user_subscription_id = %s
        """
        mysql_cursor.execute(query, (status, user_id, user_subscription_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        return True
    except:
        return False
    
def set_user_membership_session(mysql_cursor, user_id) -> bool:

    try:
        user_membership = get_membership(mysql_cursor, user_id, "active", by_status= True)
        if user_membership != None:
            id = user_membership[0][0]
            user_membership_id = user_membership[0][1]
            user_membership_status = user_membership[0][2]
            user_membership_start_date = user_membership[0][3]
            user_membership_end_date = user_membership[0][4]
            session["user_membership"] = True
            session["user_membership_id"] = user_membership_id
            session["user_membership_start_date"] = user_membership_start_date
            session["user_membership_end_date"] = user_membership_end_date
        else:
            del session["user_membership"]
            del session["user_membership_id"]
            del session["user_membership_start_date"]
            del session["user_membership_end_date"]
        return True
    except Exception as e:
        return e

def clear_user_checkout_voucher_session():
    try:
        session["checkout_platform_voucher_selected"] = False
        session.pop('checkout_platform_voucher_selected', None)
        session.pop('checkout_platform_voucher_id', None)
        session.pop('checkout_platform_voucher_discount', None)
        session.pop('checkout_platform_voucher_discount_type', None)
        session.pop('checkout_platform_voucher_discount_amount', None)
        session.pop('checkout_platform_voucher_discount_type', None)
        session.pop('checkout_platform_voucher_discount_cap', None)
        session.pop('checkout_platform_voucher_usage_cap', None)
        return True
    except Exception as e:
        return False
# STRIPE FUNCTIONS

def get_stripe_customer_id(mysql_cursor,user_id) -> None|str:
    """
    This method select stripe customer data from database 
    :return: Tuple: (id, stripe_customer_id, user_id) if found. None otherwise;
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        SELECT id,stripe_customer_id,user_id
        FROM stripe_customer 
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        
        if num_result == 1:
            return result[0]
        return None
    except:
        return None

def get_stripe_subscription_id(mysql_cursor, stripe_cutomer_id, status = None, by_status = False) -> None|str:
    """
    This method select stripe subscription data from database 
    :return: List of tuple: [(id, stripe_subscription_id, stripe_subscription_status, stripe_product_id, subscription_product_id, stripe_customer_id, user_subscription_id)] if found. None otherwise;
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        if by_status:
            query = """
            SELECT id,stripe_subscription_id,stripe_subscription_status,stripe_product_id,subscription_product_id,stripe_customer_id,user_subscription_id 
            FROM stripe_subscription 
            WHERE stripe_customer_id = %s AND stripe_subscription_status = %s
            """
            mysql_cursor.execute(query, (stripe_cutomer_id,status))
        else:
            query = """
            SELECT id,stripe_subscription_id,stripe_subscription_status,stripe_product_id,subscription_product_id,stripe_customer_id,user_subscription_id
            FROM stripe_subscription 
            WHERE stripe_customer_id = %s
            """
            mysql_cursor.execute(query, (stripe_cutomer_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        
        if num_result > 0:
            return result
        return None
    except:
        return None


def get_user_id_from_stripe_customer_id(mysql_cursor, customer_id) -> None|str:
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        SELECT user_id 
        FROM stripe_customer 
        WHERE stripe_customer_id = %s
        """
        mysql_cursor.execute(query, (customer_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        
        if num_result == 1:
            return result[0][0]
        return None
    except Exception as e:
        return None

def get_subscription_product_from_stripe_id(mysql_cursor, stripe_product_id, stripe_price_id) -> None|list:
    """
    This method get the subscription data from database by stripe product id & price id
    :param mysql_cursor: MYSQL cursor in user's database
    :param product_id: stripe product id
    :param price_id: stripe price id
    :raise Exception: If anything goes wrong
    :return: None if nothing found; A list of tuple in format: [(id, subscription_product_id, subscription_product_name, subscription_product_nku, subscription_product_interval, subscription_product_count, subscription_product_trial_period, subscription_product_price)]
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        SELECT id, subscription_product_id,subscription_product_name,subscription_product_nku,subscription_product_interval,subscription_product_count,subscription_product_trial_period,subscription_product_price
        FROM subscription_product 
        WHERE stripe_product_id = %s AND stripe_price_id = %s
        """
        mysql_cursor.execute(query, (stripe_product_id,stripe_price_id))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        
        if num_result == 1:
            return result
        return None
    except Exception as e:
        return None

def get_stripe_subscription(mysql_cursor, stripe_subscription_id, stripe_customer_id = None, by_customer_id = False) -> None | list:
    """
    This method get the stripe subscription data from database
    :param mysql_cursor: MYSQL cursor in user's database
    :param stripe_subscription_id: stripe  subscription ID
    :param stripe_customer_id: stripe customer id
    :param by_customer_id: Set True if you want to select by customer ID only
    :raise Exception: If anything goes wrong
    :return: None if nothing found; A list of tuple in format: [(id, stripe_subscription_id, stripe_product_id, subscription_product_id, stripe_customer_id, user_subscription_id)]
    """

    try:
        mysql_connector.use_db(mysql_cursor, "user")
        if by_customer_id == True:
            query = """
            SELECT id,stripe_subscription_id,stripe_product_id,subscription_product_id,stripe_customer_id,user_subscription_id
            FROM stripe_subscription
            WHERE stripe_subscription_id = %s  AND stripe_customer_id = %s
            """
            mysql_cursor.execute(query, (stripe_subscription_id, stripe_customer_id))
        else:
            query = """
            SELECT id,stripe_subscription_id,stripe_product_id,subscription_product_id,stripe_customer_id,user_subscription_id
            FROM stripe_subscription
            WHERE stripe_subscription_id = %s
            """
            mysql_cursor.execute(query, (stripe_subscription_id,))
        
        results = mysql_cursor.fetchall()
        num_result = len(results)
        if num_result > 0:
            return results
        return None
    except Exception as e:
        return str(e)
    
def verify_stripe_checkout_session_id(mysql_cursor, checkout_session_id, mode, user_id) -> bool:
    """
    This method verify user_id with the stripe checkout session id recorded
    :param mysql_cursor: MYSQL cursor in user's database
    :param checkout_session_id: stripe checkout_session_id
    :param user_id: User ID
    :raise Exception: If anything goes wrong
    :return: True if both matches; False if not.
    """

    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        SELECT id
        FROM stripe_checkout 
        WHERE stripe_checkout_id = %s AND stripe_checkout_mode = %s AND user_id = %s
        """
        mysql_cursor.execute(query, (checkout_session_id,mode,user_id))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        
        if num_result == 1:
            return True 
        return False
    except Exception as e:
        return False
    
def record_stripe_checkout_session(mysql_conn,mysql_cursor,session_id,mode,user_id) -> bool:
    #because user_id is always unique, we always get a unique string no matter what
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        INSERT INTO stripe_checkout (stripe_checkout_id, stripe_checkout_mode, user_id) VALUES
        (%s, %s, %s)
        """
        mysql_cursor.execute(query, (session_id,mode,user_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        
        if num_result == 1:
            return True
        return False
    except:
        return False
    
def create_user_subscription(mysql_conn,mysql_cursor,user_subscription_status, user_subscription_start_date, user_subscription_bill_start_date, user_subscription_end_date, subscription_product_id, user_id) -> None | str:
    try:
        user_subscription_id = generate_unique_user_subscription_id(mysql_cursor)
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        INSERT INTO user_subscription (user_subscription_id, user_subscription_status, user_subscription_start_date, user_subscription_bill_start_date, user_subscription_end_date, subscription_product_id, user_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query, (user_subscription_id,user_subscription_status,user_subscription_start_date, user_subscription_bill_start_date, user_subscription_end_date, subscription_product_id, user_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        
        if num_result == 1:
            return user_subscription_id
        return None
    except:
        return None

def create_user_membership(mysql_conn,mysql_cursor,user_membership_name, user_membership_nku, user_membership_status, user_membership_start_date, user_membership_end_date, user_id) -> None | str:
    try:
        user_membership_id = generate_unique_user_membership_id(mysql_cursor)
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        INSERT INTO user_membership (user_membership_id, user_membership_name, user_membership_nku, user_membership_status, user_membership_start_date, user_membership_end_date, user_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query, (user_membership_id,user_membership_name,user_membership_nku, user_membership_status, user_membership_start_date, user_membership_end_date, user_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        
        if num_result == 1:
            return user_membership_id
        return None
    except:
        return None

def create_stripe_subscription(mysql_conn, mysql_cursor,stripe_subscription_id,stripe_product_id,subscription_product_id,stripe_customer_id,user_subscription_id) -> None | str:
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        INSERT INTO stripe_subscription (stripe_subscription_id, stripe_product_id, subscription_product_id, stripe_customer_id, user_subscription_id) VALUES
        (%s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query, (stripe_subscription_id,stripe_product_id,subscription_product_id,stripe_customer_id,user_subscription_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        
        if num_result == 1:
            return True
        return False
    except:
        return False

def create_whatsapp_session(mysql_conn, mysql_cursor, user_whatsapp_chat_session_state, user_whatsapp_chat_session_data, user_whatsapp_phone_number, user_whatsapp_language) -> None | str:
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        INSERT INTO user_whatsapp_chat_session (user_whatsapp_chat_session_state, user_whatsapp_chat_session_data, user_whatsapp_phone_number, user_whatsapp_language) VALUES
        (%s, %s, %s, %s)
        """
        mysql_cursor.execute(query, (user_whatsapp_chat_session_state, user_whatsapp_chat_session_data, user_whatsapp_phone_number, user_whatsapp_language))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        
        if num_result == 1:
            return True
        return False
    except:
        return False
    
def update_whatsapp_session_language(mysql_conn, mysql_cursor, language, user_whatsapp_phone_number) -> bool:
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        UPDATE user_whatsapp_chat_session
        SET user_whatsapp_language = %s
        WHERE user_whatsapp_phone_number = %s
        """
        mysql_cursor.execute(query, (language, user_whatsapp_phone_number))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        return True
    except:
        return False
    
def update_stripe_subscription_status(mysql_conn,mysql_cursor,status,stripe_subscription_id,stripe_customer_id) -> bool:
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        UPDATE stripe_subscription
        SET stripe_subscription_status = %s
        WHERE stripe_subscription_id = %s AND stripe_customer_id = %s
        """
        mysql_cursor.execute(query, (status, stripe_subscription_id, stripe_customer_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        return True
    except:
        return False

def update_language_settings(mysql_conn, mysql_cursor, language, user_id):
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        UPDATE user
        SET user_language = %s
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (language, user_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        return True
    except:
        return False

def update_user_account_status(mysql_conn, mysql_cursor, status, user_id):
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        UPDATE user
        SET user_account_status = %s
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (status, user_id))
        num_result = mysql_cursor.rowcount
        mysql_conn.commit()
        return True
    except:
        return False

def reset_checkout_sessions():
    try:
        session.pop("user_checkout_payment_method", None)
        session.pop("user_checkout_payment_method_name", None)
        assert clear_user_checkout_voucher_session() == True, "User checkout session not cleared"
        return True
    except Exception as e:
        return e

#USER SPECIFIC OPERATION FUNCITON IN USER DATASE!!!!
#!!!!!!!!!!!!!!!!!!
def user_specific_connect_database(user_id):
    db_dict = json_tools.read_json("/var/www/aitanmall.com/private/data/databases.json")
    user_db = db_dict["user"]
    user_db_username = user_db["username"]
    user_db_password = user_db["password"]
    db_conn = mysql_connector.create_mysql_conn(user_db_username,user_db_password,db_name = user_id)
    db_conn_cursor = db_conn.cursor(prepared=True)
    return [db_conn,db_conn_cursor]

def user_specific_set_up_is_complete(mysql_cursor, user_id) -> bool:
    """
    This method checks if this user's database neccessary information for checking out is all completed
    :param: user_id: ID associate to identify this user
    :raises Exception: If any process in between goes wrong
    :return: True if user has all neccessary information for checkout
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        response = False
        #check user's address
        query = """
        SELECT * 
        FROM user_address
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        results = mysql_cursor.fetchall()
        if len(results) >= 1:
            response = True
    except Exception as e:
        response = False
    finally:
        return response

def user_specific_get_language(mysql_cursor, user_id):
    """
    This method get the preferred language set by user
    :param: user_id: ID associate to identify this user
    :raises Exception: If any process in between goes wrong
    :return: language parameter; None otherwise
    """
    try:
        response = None
        #connect to user's database
        mysql_connector.use_db(mysql_cursor, "user")
        #check user's address
        query = """
        SELECT user_language 
        FROM user
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        results = mysql_cursor.fetchall()
        if len(results) > 0:
            response = results[0][0]
    except Exception as e:
        response = e
    finally:
        return response
    
def user_specific_add_address(mysql_conn, mysql_cursor, user_id, street, city, zip, state, country, unit_number = "") -> None | str:
    """
    This method create a new record in user's database under table user_address
    :raises Exception: If any process in between goes wrong
    :return: True if record added
    """

    try:
        mysql_connector.use_db(mysql_cursor, "user")
        response = None
        #check user's address
        query = """
        INSERT INTO user_address (user_address_unit_number, user_address_street, user_address_city, user_address_zip, user_address_state, user_address_country,user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query, (unit_number, street, city, zip, state, country, user_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        if num_results == 1:
            response = mysql_cursor.lastrowid
    except Exception as e:
        response = str(e)
    finally:
        return response

def add_shipping_address(mysql_conn, mysql_cursor, user_id, user_address_id, status):
    """
    This method create a new record in user's database under table user_address
    :raises Exception: If any process in between goes wrong
    :return: True if record added
    """

    try:
        mysql_connector.use_db(mysql_cursor, "user")
        response = False
        #check user's address
        query = """
        INSERT INTO user_shipping_address (user_address_id, user_address_status, user_id)
        VALUES (%s, %s, %s)
        """
        mysql_cursor.execute(query, (user_address_id, status, user_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        if num_results == 1:
            response = True
    except Exception as e:
        response = False
    finally:
        return response
    
def get_shipping_address(mysql_cursor, user_id, limit = 1):
    """
    This method select user's shipping address
    :raises Exception: If any process in between goes wrong
    :return: List in format [(id, user_address_id, user_address_status, user_id)]
    """

    try:
        mysql_connector.use_db(mysql_cursor, "user")
        response = []
        #check user's address
        query = """
        SELECT  id, user_address_id, user_address_status, user_id
        FROM user_shipping_address
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
    except Exception as e:
        response = str(e)
    finally:
        return response
    
def user_specific_get_address(mysql_cursor, user_id, limit = None):
    """
    This method return records in user's database under table user_address
    :raises Exception: If any process in between goes wrong
    :return: a list of tuple containing [
    (id, user_address_unit_number, user_address_street, user_address_city, user_address_zip, user_address_state, user_address_country,user_id )
    ]
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        response = []
        #check user's address
        query = """
        SELECT id, user_address_unit_number, user_address_street, user_address_city, user_address_zip, user_address_state, user_address_country,user_id 
        FROM user_address
        WHERE user_id = %s
        {}
        """
        if limit != None:
            query = query.format("LIMIT "+str(limit))
        else:
            query = query.format("")
        
        mysql_cursor.execute(query, (user_id,))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results >= 1:
            response = results
        else:
            response = []
    except Exception as e:
        response = e
    finally:
        return response

def select_address(mysql_cursor, user_id, address_id, by_id = True):
    """
    This method return records in user's database under table user_address
    :raises Exception: If any process in between goes wrong
    :return: a list of tuple containing [
    (id, user_address_unit_number, user_address_street, user_address_city, user_address_zip, user_address_state, user_address_country,user_id )
    ]
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        response = False
        if by_id:
            query = """
            SELECT id, user_address_unit_number, user_address_street, user_address_city, user_address_zip, user_address_state, user_address_country,user_id 
            FROM user_address
            WHERE user_id = %s AND id = %s
            """
            mysql_cursor.execute(query, (user_id,address_id))
        else:
            query = """
            SELECT id, user_address_unit_number, user_address_street, user_address_city, user_address_zip, user_address_state, user_address_country,user_id 
            FROM user_address
            WHERE user_id = %s
            """
            mysql_cursor.execute(query, (user_id,))

        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
        else:
            response = None
    except Exception as e:
        response = None
    finally:
        return response
    
def select_payment_method(mysql_cursor, user_id, payment_method_id, by_id = True):
    """
    This method return records in user's database under table user_payment_method
    :raises Exception: If any process in between goes wrong
    :return: a list of tuple containing [
    (id, user_address_unit_number, user_address_street, user_address_city, user_address_zip, user_address_state, user_address_country,user_id )
    ]
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        response = False
        if by_id:
            query = """
            SELECT id, user_payment_method_type, user_payment_method_status, user_payment_method_id, user_id
            FROM user_payment_method
            WHERE user_id = %s AND user_payment_method_id = %s
            """
            mysql_cursor.execute(query, (user_id,payment_method_id))
        else:
            query = """
            SELECT id, user_payment_method_type, user_payment_method_status, user_payment_method_id, user_id
            FROM user_payment_method
            WHERE user_id = %s 
            """
            mysql_cursor.execute(query, (user_id,))

        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
        else:
            response = None
    except Exception as e:
        response = None
    finally:
        return response
    
def select_user(mysql_cursor, user_id) -> list|Exception:
    """
    This method select user by user_id in user database
    :raises Exception: If any process in between goes wrong
    :return: a list of tuple containing [
    (id, user_id, user_first_name, user_last_name, user_email, user_email_verification, user_phone_number_code, user_phone_number, user_account_status, user_language, user_date_created)
    ]
    """
    try:
        response = []
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        SELECT id, user_id, user_first_name, user_last_name, user_email, user_email_verification, user_phone_number_code, user_phone_number, user_account_status, user_language, user_date_created
        FROM user
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))

        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
    except Exception as e:
        response = e
    finally:
        return response
    
def select_user_by_phone_number(mysql_cursor, country_code, phone_number) -> list|Exception:
    """
    This method select user by phone_number in user database
    :raises Exception: If any process in between goes wrong
    :return: a list of tuple containing [
    (id, user_address_unit_number, user_address_street, user_address_city, user_address_zip, user_address_state, user_address_country,user_id )
    ]
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        response = False
        query = """
        SELECT id, user_id, user_first_name, user_last_name, user_email, user_email_verification, user_phone_number_code, user_phone_number, user_account_status, user_language, user_date_created
        FROM user
        WHERE user_phone_number_code = %s AND user_phone_number = %s
        """
        mysql_cursor.execute(query, (country_code,phone_number))

        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
        else:
            response = []
    except Exception as e:
        response = e
    finally:
        return response

def user_specific_format_address_to_one_string(address_tuple_list):
    results = address_tuple_list
    for i in range(len(results)):
        new_value = dict()
        new_value["address"] = ""
        new_value["address_id"] = results[i][0]
        for i2 in range(1,len(results[i]),1):
            if len(results[i][i2]) >= 1:
                new_value["address"] += str(results[i][i2])+", "
        results[i] = new_value
    return results

def user_specific_remove_address(mysql_conn, mysql_cursor, user_id, address_id):
    """
    This method delete a record in user's database under table user_address
    :raises Exception: If any process in between goes wrong
    :return: True if record deleted
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        response = False
        #check user's address
        query = """
        DELETE FROM user_address 
        WHERE id = %s AND user_id = %s
        """
        mysql_cursor.execute(query, (address_id,user_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        if num_results == 1:
            response = True
    except Exception as e:
        response = False
    finally:
        return response

def user_specific_email_is_verified(mysql_cursor, user_id):
    """
    This method check the record under user in user database to determine if email is verified
    :raises Exception: If any process in between goes wrong
    :return: True if record satisfied
    """

    try:
        response = False
        mysql_connector.use_db(mysql_cursor, "user")
        #check user's address
        query = """
        SELECT user_email
        FROM user 
        WHERE user_email_verification = %s AND user_id = %s
        """
        mysql_cursor.execute(query, ("verified", user_id))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results == 1:
            response = True
    except Exception as e:
        response = False
    finally:
        return response

def user_specific_send_verification_email(mysql_cursor, user_id, user_name, user_email_key):
    """
    This method select user's email and send a verification email to them
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: True if email is sent
    """

    try:
        mysql_connector.use_db(mysql_cursor, "user")
        domain_name = "https://aitanmall.com"
        response = False
        #check user's address
        query = """
        SELECT user_email 
        FROM user
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results == 1:
            user_email = results[0][0]
            verification_link = domain_name+"/user/verify_email?user_id="+str(user_id)+"&user_email="+str(user_email)+"&key="+str(user_email_key)
            html_template = render_template("mail/email_verification.html", name= user_name, url = verification_link)
            subject = "Verify your email account"

            if mailer.send_html_email(user_email,subject,html_template):
                response = True
    except Exception as e:
        response = False
    finally:
        return response

def user_specific_record_payment_method_card(mysql_conn, mysql_cursor, user_id, stripe_payment_id, stripe_customer_id, card_brand, card_last4, card_exp_month, card_exp_year, card_holder, payment_method_type = "card", status = "backup"):
    """
    This method create a new record in user's database under table user_payment_method and user_payment_method_card
    :raises Exception: If any process in between goes wrong
    :return: True if record added
    """

    try:
        response = False
        accepted_payment_methods = ["card"]
        assert payment_method_type in accepted_payment_methods, "Payment method currently not accepted"
        mysql_connector.use_db(mysql_cursor, "user")
        unique_payment_method_id = generate_unique_payment_method_id(mysql_cursor)
        assert isinstance(unique_payment_method_id, str) and unique_payment_method_id[4:7] == "PMT", "Payment method ID not created"
        #check user's address
        query1 = """
        INSERT INTO user_payment_method (user_payment_method_type, user_payment_method_status, user_payment_method_id, user_id) 
        VALUES (%s, %s, %s, %s)
        """
        mysql_cursor.execute(query1, (payment_method_type, status, unique_payment_method_id, user_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        num_results_expected = 1
        if num_results == num_results_expected:
            
            query2 = """
            INSERT INTO stripe_payment_method (stripe_payment_method_type, stripe_payment_method_status, stripe_payment_method_id, stripe_customer_id, user_payment_method_id) 
            VALUES (%s, %s, %s, %s, %s)
            """
            mysql_cursor.execute(query2, (payment_method_type, status, stripe_payment_id, stripe_customer_id, unique_payment_method_id))
            num_results += mysql_cursor.rowcount
            mysql_conn.commit()
            num_results_expected = 2
            if payment_method_type == "card":
                query3 = """
                INSERT INTO user_card (user_payment_method_id, card_brand, card_last4, card_exp_month, card_exp_year, card_holder, status, user_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                mysql_cursor.execute(query3, (unique_payment_method_id, card_brand, card_last4, card_exp_month, card_exp_year, card_holder, status, user_id))
                num_results += mysql_cursor.rowcount
                mysql_conn.commit()
                num_results_expected = 3

            if num_results == num_results_expected:
                response = True
    except Exception as e:
        response = str(e)
    finally:
        return response

def user_specific_has_default_payment_method(mysql_cursor, user_id):
    """
    This method select user's payment method to check if there exist default payment method
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: True if it exist
    """

    try:
        response = False
        mysql_connector.use_db(mysql_cursor, "user")
        #check user's address
        query = """
        SELECT id 
        FROM user_payment_method 
        WHERE user_payment_method_status = %s AND user_id = %s
        """
        mysql_cursor.execute(query, ("default", user_id))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results == 1:
            response = True
    except Exception as e:
        response = False
    finally:
        return response
def get_default_payment_method(mysql_cursor, user_id):
    """
    This method select user's default payment method
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: List in format: [(id, user_payment_method_type, user_payment_method_status, user_payment_method_id, user_id)]
    """

    try:
        response = False
        mysql_connector.use_db(mysql_cursor, "user")
        #check user's address
        query = """
        SELECT id, user_payment_method_type, user_payment_method_status, user_payment_method_id, user_id
        FROM user_payment_method
        WHERE user_payment_method_status = %s AND user_id = %s
        """
        mysql_cursor.execute(query, ("default",user_id))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
    except Exception as e:
        response = False
    finally:
        return response

def get_default_payment_card(mysql_cursor, user_id):
    """
    This method select user's default payment card
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: List in format: [(id, user_payment_method_id, card_brand, card_last4, card_exp_month, card_exp_year, card_holder, status, user_id)]
    """

    try:
        response = False
        mysql_connector.use_db(mysql_cursor, "user")
        #check user's address
        query = """
        SELECT id, user_payment_method_id, card_brand, card_last4, card_exp_month, card_exp_year, card_holder, status, user_id
        FROM user_card
        WHERE status = %s AND user_id = %s
        """
        mysql_cursor.execute(query, ("default",user_id))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
    except Exception as e:
        response = False
    finally:
        return response
def get_default_shipping_address(mysql_cursor, user_id):
    """
    This method select user's default shipping address
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: List in format: [(id, user_address_id, user_address_status, user_id)]
    """

    try:
        response = []
        mysql_connector.use_db(mysql_cursor, "user")
        #check user's address
        query = """
        SELECT id, user_address_id, user_address_status, user_id
        FROM user_shipping_address
        WHERE user_address_status = %s AND user_id = %s
        """
        mysql_cursor.execute(query, ("default",user_id))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
    except Exception as e:
        response = e
    finally:
        return response

def select_subscription_products(mysql_cursor, subscription_product_id, subscription_product_nku = None, by_nku = False):
    """
    This method select subscription products in user database
    :raises Exception: If any process in between goes wrong
    :return: List in format: [(id, subscription_product_id, subscription_product_name, subscription_product_nku, subscription_product_interval, subscription_product_count, subscription_product_trial_period, subscription_product_price, stripe_product_id, stripe_price_id)]
    """

    try:
        response = []
        mysql_connector.use_db(mysql_cursor, "user")
        if by_nku:
            query = """
            SELECT id, subscription_product_id, subscription_product_name, subscription_product_nku, subscription_product_interval, subscription_product_count, subscription_product_trial_period, subscription_product_price, stripe_product_id, stripe_price_id
            FROM subscription_product
            WHERE subscription_product_nku = %s
            """
            mysql_cursor.execute(query, (subscription_product_nku,))
        else:
            query = """
            SELECT id, subscription_product_id, subscription_product_name, subscription_product_nku, subscription_product_interval, subscription_product_count, subscription_product_trial_period, subscription_product_price, stripe_product_id, stripe_price_id
            FROM subscription_product
            WHERE subscription_product_id = %s
            """
            mysql_cursor.execute(query, (subscription_product_id,))
        
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
    except Exception as e:
        response = e
    finally:
        return response
    
def user_specific_get_payment_methods(mysql_cursor, user_id, limit=5) -> None|list:
    """
    This method select user's payment method by limit
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: List of payment methods tuple in the format: [payment_method_id, payment_method_type,
    :details of method CARD: (id, user_payment_method_id, card_brand, card_last4, card_exp_month, card_exp_year, card_holder, user_id)]
    """

    try:
        response = None
        mysql_connector.use_db(mysql_cursor, "user")
        #check user's address
        query = """
        SELECT id, user_payment_method_type, user_payment_method_status, user_payment_method_id, user_id 
        FROM user_payment_method
        WHERE user_id = %s
        LIMIT {}
        """.format(limit)
        mysql_cursor.execute(query, (user_id,))
        payment_methods = mysql_cursor.fetchall()
        num_results = len(payment_methods)
        if num_results > 0:
            list_to_return = []
            for payment_method in payment_methods:
                payment_method_id = payment_method[3]
                payment_method_type = payment_method[1]
                if payment_method_type == "card":
                    query = """
                    SELECT id,user_payment_method_id,card_brand,card_last4,card_exp_month,card_exp_year,card_holder,user_id
                    FROM user_card 
                    WHERE user_payment_method_id = %s AND user_id = %s
                    """
                    mysql_cursor.execute(query, (payment_method_id,user_id))
                else:
                    #put here for now to avoid complciations
                    query = """
                    SELECT id,user_payment_method_id,card_brand,card_last4,card_exp_month,card_exp_year,card_holder,user_id
                    FROM user_card 
                    WHERE user_payment_method_id = %s AND user_id = %s
                    """
                    mysql_cursor.execute(query, (payment_method_id,user_id))
                methods_detail = mysql_cursor.fetchall()
                list_to_return.append([payment_method_id,payment_method_type,methods_detail[0]])
            response = list_to_return
    except Exception as e:
        response = []
    finally:
        return response

def user_specific_get_payment_method_by_id(user_id, payment_method_id = None,stripe_payment_method_id = None) -> None|list:
    """
    This method select user's payment method by id
    :param user_id: User's session id defined when logged in
    :param payment_method_id: User's payment method id in database. *Prioritized*
    :param stripe_payment_method_id: User's payment method id in Stripe
    :raises Exception: If any process in between goes wrong
    :return: List of payment if found, format: [(method_id,type,status,stripe_payment_id)]; None otherwise
    """

    try:
        response = None
        #connect to user's database
        db_conn_list = user_specific_connect_database(user_id)
        db_conn = db_conn_list[0]
        db_conn_cursor = db_conn_list[1]
        #set query
        if stripe_payment_method_id != None and payment_method_id == None:
            use_stripe_payment_method_id = True
            query = """
            SELECT user_payment_method_id,user_payment_method_type,user_payment_method_status,stripe_payment_method_id FROM user_payment_method
            WHERE stripe_payment_method_id = %s
            """
        else:
            use_payment_method_id = True
            query = """
            SELECT user_payment_method_id,user_payment_method_type,user_payment_method_status,stripe_payment_method_id FROM user_payment_method
            WHERE user_payment_method_id = %s
            """

        if use_stripe_payment_method_id:
            param1 = stripe_payment_method_id
        else:
            param1 = payment_method_id
        db_conn_cursor.execute(query, (param1,))
        payment_method = db_conn_cursor.fetchall()
        num_results = len(payment_method)
        if num_results > 0:
            response = payment_method
    except Exception as e:
        response = None
    finally:
        if 'db_conn_cursor' in locals():
            mysql_connector.close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            mysql_connector.close_mysql_conn(db_conn)
        return response

def stripe_payment_method_exist(mysql_cursor, stripe_payment_id, stripe_customer_id) -> None | list:
    """
    This method select user's payment method by stripe_payment_id
    :param stripe_payment_id: payment_id sent by Stripe webhooks
    :param stripe_customer_id: customer_id sent by Stripe webhooks
    :raises Exception: If any process in between goes wrong
    :return: True if it exist
    """

    try:
        response = None
        mysql_connector.use_db(mysql_cursor, "user")
        #check user's address
        query = """
        SELECT user_payment_method_id 
        FROM stripe_payment_method 
        WHERE stripe_payment_method_id = %s AND stripe_customer_id = %s
        """
        mysql_cursor.execute(query, (stripe_payment_id,stripe_customer_id))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results == 1:
            response = results[0][0]
    except Exception as e:
        response = None
    finally:
        return response

def select_stripe_payment_method(mysql_cursor, user_payment_method_id, stripe_payment_method_id = None, stripe_customer_id = None, by_stripe_id = False, by_customer_id = False) -> None | list:
    """
    This method select user's stripe payment method  details
    :raises Exception: If any process in between goes wrong
    :return: List of tuple in format: [(id, stripe_payment_method_type, stripe_payment_method_status, stripe_payment_method_id, stripe_customer_id, user_payment_method_id)]
    """

    try:
        response = None
        mysql_connector.use_db(mysql_cursor, "user")
        if by_stripe_id:
            query = """
            SELECT id, stripe_payment_method_type, stripe_payment_method_status, stripe_payment_method_id, stripe_customer_id, user_payment_method_id
            FROM stripe_payment_method 
            WHERE stripe_payment_id = %s
            """
            mysql_cursor.execute(query, (stripe_payment_method_id,))
        elif by_customer_id:
            query = """
            SELECT id, stripe_payment_method_type, stripe_payment_method_status, stripe_payment_method_id, stripe_customer_id, user_payment_method_id
            FROM stripe_payment_method 
            WHERE stripe_customer_id = %s
            """
            mysql_cursor.execute(query, (stripe_customer_id,))
        else:
            query = """
            SELECT id, stripe_payment_method_type, stripe_payment_method_status, stripe_payment_method_id, stripe_customer_id, user_payment_method_id
            FROM stripe_payment_method 
            WHERE user_payment_method_id = %s
            """
            mysql_cursor.execute(query, (user_payment_method_id,))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results == 1:
            response = results
    except Exception as e:
        response = e
    finally:
        return response
    

def select_whatsapp_session(mysql_cursor, phone_number) -> list|Exception:
    """
    This method select user whatsapp chat session by phone number
    :raises Exception: If any process in between goes wrong
    :return: a list of tuple containing [
    (id, user_whatsapp_chat_session_state, user_whatsapp_chat_session_datetime, user_whatsapp_chat_session_data, user_whatsapp_phone_number, user_whatsapp_language)
    ]
    """
    try:
        mysql_connector.use_db(mysql_cursor, "user")
        response = False
        query = """
        SELECT id, user_whatsapp_chat_session_state, user_whatsapp_chat_session_datetime, user_whatsapp_chat_session_data, user_whatsapp_phone_number, user_whatsapp_language
        FROM user_whatsapp_chat_session
        WHERE user_whatsapp_phone_number = %s
        """
        mysql_cursor.execute(query, (phone_number,))

        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
        else:
            response = []
    except Exception as e:
        response = e
    finally:
        return response
    
def user_specific_get_cart(mysql_cursor, user_id, merchant_id = None, by_merchant = False, limit = 3):
    """
    This method selects the cart items for user
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: List of cart items in the format: [[id, prd_id, prd_name, prd_img, quantity, prd_price, prd_var_id, prd_var_name, prd_sku, prd_var_img, sub_total, total, merchant_id, user_id]]
    List will be sorted by merchant ID if by_merchant == True
    """
    try:
        response = []
        #connect to user's database
        mysql_connector.use_db(mysql_cursor, "user")
        #if limit is None
        if limit == None:
            limit_extension = ""
        else:
            assert isinstance(limit, int), "Limit need to be None or int"
            limit_extension = "LIMIT {}".format(limit)
            
        if by_merchant:
            query = """
            SELECT id, prd_id, prd_name, prd_img, quantity, prd_price, prd_var_id, prd_var_name, prd_sku, prd_var_img, sub_total, total, merchant_id, user_id
            FROM user_cart
            WHERE user_id = %s
            ORDER BY merchant_id
            """
            parameters = (user_id,)
        else:
            query = """
            SELECT id, prd_id, prd_name, prd_img, quantity, prd_price, prd_var_id, prd_var_name, prd_sku, prd_var_img, sub_total, total, merchant_id, user_id
            FROM user_cart
            WHERE user_id = %s
            """
            parameters = (user_id,)
        query = query + limit_extension
        mysql_cursor.execute(query, parameters)
        results = mysql_cursor.fetchall()
        if len(results) > 0:
            response = results
    except Exception as e:
        response = []
    finally:
        return response


def user_specific_cart_prd_exist(mysql_cursor, user_id, product_id, merchant_id, product_variation_id):
    """
    This method check if a prd_id already exists in user cart
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: True if exist; False otherwise
    """
    try:
        response = False
        #connect to user's database
        mysql_connector.use_db(mysql_cursor, "user")
        #if limit is None
        query = """
        SELECT prd_name
        FROM user_cart
        WHERE user_id = %s AND prd_id = %s AND merchant_id = %s AND prd_var_id = %s
        """
        mysql_cursor.execute(query, (user_id, product_id, merchant_id, product_variation_id))
        results = mysql_cursor.fetchall()
        if len(results) > 0:
            response = True
    except Exception as e:
        response = str(e)
    finally:
        return response
    
def user_specific_remove_stripe_payment_method(mysql_conn, mysql_cursor, user_id, user_payment_method_id):
    """
    This method remove user's payment method by stripe_payment_id
    :param user_id: User's session id defined when logged in
    :param stripe_payment_id: payment_id sent by Stripe webhooks
    :raises Exception: If any process in between goes wrong
    :return: True if it is removed
    """

    try:
        response = False
        mysql_connector.use_db(mysql_cursor, "user")
        #check user's address
        query = """
        DELETE FROM user_payment_method 
        WHERE user_id = %s AND user_payment_method_id = %s 
        """
        mysql_cursor.execute(query, (user_id, user_payment_method_id))
        num_affected = mysql_cursor.rowcount
        mysql_conn.commit()
        if num_affected == 1:
            response = True
    except Exception as e:
        response = False
    finally:
        return response

def user_specific_add_to_cart(mysql_conn, mysql_cursor, user_id, product_id, product_name,  product_image, quantity, price, product_variation_id, product_variation_name, product_sku, product_variation_image, sub_total, total, merchant_id):
    """
    This method add a product to cart for user
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: True if product added; False otherwise
    """
    try:
        response = False
        #connect to user's database
        mysql_connector.use_db(mysql_cursor, "user")
        #check user's address
        query = """
        INSERT INTO user_cart (prd_id, prd_name, prd_img, quantity, prd_price, prd_var_id, prd_var_name, prd_sku, prd_var_img, sub_total, total, merchant_id, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query, (product_id, product_name, product_image, quantity, price, product_variation_id, product_variation_name, product_sku, product_variation_image, sub_total, total, merchant_id, user_id))
        num_affected = mysql_cursor.rowcount
        mysql_conn.commit()
        if num_affected == 1:
            response = True
    except Exception as e:
        response = False
    finally:
        return response

def user_specific_reduce_cart_item(mysql_conn, mysql_cursor, user_id, cart_item_id, quantity = 1):
    """
    This method reduce a cart item quantity for user. It removes all quantity = 0 after reducing current item.
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: True if cart item quantity reduced; False otherwise
    """
    try:
        #connect to user's database
        mysql_connector.use_db(mysql_cursor, "user")
        #update user_cart item quantity to -1
        query = """
        UPDATE user_cart
        SET quantity = quantity - %s, sub_total = sub_total - (%s*prd_price), total = total - (%s*prd_price)
        WHERE id = %s AND user_id = %s
        """
        mysql_cursor.execute(query, (quantity, quantity, quantity, cart_item_id, user_id))
        mysql_conn.commit()
        #delete all item that has quantity = 0
        query = """
        DELETE FROM user_cart
        WHERE quantity <= 0 AND user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        mysql_conn.commit()
        response = True
    except Exception as e:
        response = str(e)
    finally:
        return response

def user_specific_increase_cart_item(mysql_conn , mysql_cursor, user_id, cart_item_id,  quantity = 1):
    """
    This method increase a cart item quantity for user
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: True if cart item quantity increased; False otherwise
    """
    try:
        #connect to user's database
        mysql_connector.use_db(mysql_cursor, "user")
        #update user_cart item quantity to +1
        query = """
        UPDATE user_cart
        SET quantity = quantity + %s, sub_total = sub_total + (%s*prd_price), total = total + (%s*prd_price)
        WHERE id = %s AND user_id = %s
        """
        mysql_cursor.execute(query, (quantity, quantity, quantity, cart_item_id, user_id))
        mysql_conn.commit()
        response = True
    except Exception as e:
        response = str(e)
    finally:
        return response

def clear_cart(mysql_conn , mysql_cursor, user_id):
    """
    This method clears a cart for user
    :param user_id: User's session id defined when logged in
    :raises Exception: If any process in between goes wrong
    :return: True if cart is cleared; False otherwise
    """
    try:
        response = False
        mysql_connector.use_db(mysql_cursor, "user")
        query = """
        DELETE FROM user_cart
        WHERE user_id = %s
        """
        mysql_cursor.execute(query, (user_id,))
        num_affected = mysql_cursor.rowcount
        mysql_conn.commit()
        if num_affected > 0:
            response = True
    except Exception as e:
        response = str(e)
    finally:
        return response