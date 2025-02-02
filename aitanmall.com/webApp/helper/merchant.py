from webApp.mysql_connector import use_db
import random
from webApp.helper import general

#======================================
#accesor
#=====================================
def product_id_exists(mysql_cursor, merchant_id, product_id):
    try:
        use_db(mysql_cursor, "merchant_{}".format(merchant_id))
        #insert into merchant's database
        query = """
        SELECT prd_name
        FROM product
        WHERE prd_id = %s
        """

        mysql_cursor.execute(query, (product_id,))
        results = mysql_cursor.fetchall()
        if len(results) >= 1:
            return  True
        return False
    except Exception as e:
        return False

def product_variation_id_exists(mysql_cursor, merchant_id, product_var_id, product_var_cat_id, by_cat_id = True):
    try:
        use_db(mysql_cursor, "merchant_{}".format(merchant_id))
        #insert into merchant's database
        if by_cat_id:
            query = """
            SELECT prd_var
            FROM prd_var
            WHERE prd_var_id = %s AND prd_var_cat_id = %s
            """
            mysql_cursor.execute(query, (product_var_id,product_var_cat_id))
        else:
            query = """
            SELECT prd_var
            FROM prd_var
            WHERE prd_var_id = %s
            """
            mysql_cursor.execute(query, (product_var_id,))

        results = mysql_cursor.fetchall()
        if len(results) >= 1:
            return  True
        return False
    except Exception as e:
        return False
    
def product_id_exists(mysql_cursor, merchant_id, product_id):
    try:
        use_db(mysql_cursor, "product")
        #insert into merchant's database
        query = """
        SELECT prd_name
        FROM product
        WHERE prd_id = %s AND merchant_id = %s
        """

        mysql_cursor.execute(query, (product_id,merchant_id))
        results = mysql_cursor.fetchall()
        if len(results) > 0:
            return  True
        return False
    except Exception as e:
        return False
    
def get_product_variation(mysql_cursor, product_var_id, product_var_cat_id, by_cat_id = True):
    """
    This method get the product's variation from database if exist
    :return: List of product variation details in the format: [[prd_var_id, prd_var, prd_var_des, prd_var_price, prd_var_quantity, prd_var_sku, prd_var_img, prd_var_cat_id]]
    """
    try:
        use_db(mysql_cursor, "product")
        #insert into merchant's database
        if by_cat_id:
            query = """
            SELECT id,prd_var,prd_var_des,prd_var_price,prd_var_quantity,prd_var_sku,prd_var_img,prd_var_cat_id
            FROM prd_var
            WHERE id = %s AND prd_var_cat_id = %s
            """
            mysql_cursor.execute(query, (product_var_id,product_var_cat_id))
        else:
            query = """
            SELECT id,prd_var,prd_var_des,prd_var_price,prd_var_quantity,prd_var_sku,prd_var_img,prd_var_cat_id
            FROM prd_var
            WHERE id = %s
            """
            mysql_cursor.execute(query, (product_var_id,))

        results = mysql_cursor.fetchall()
        if len(results) >= 1:
            return  results
        return None
    except Exception as e:
        return None

def get_shipping(mysql_cursor, merchant_id):
    """
    This method select details from merchant_shipping_option table
    :return: List in format [(id,merchant_shipping_name,merchant_shipping_status,merchant_shipping_fee_target,merchant_shipping_option_id,merchant_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "merchant")
        query = """
        SELECT id,merchant_shipping_name,merchant_shipping_status,merchant_shipping_fee_target,merchant_shipping_option_id,merchant_id
        FROM merchant_shipping
        WHERE merchant_id = %s
        """
        mysql_cursor.execute(query, (merchant_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_shipping_option(mysql_cursor, merchant_shipping_option_id):
    """
    This method select details from merchant_shipping_option table
    :return: List in format [(id, merchant_shipping_option_id, merchant_shipping_option_name, merchant_shipping_option_nku, merchant_shipping_option_image, merchant_shipping_option_charge_fixed, merchant_shipping_option_charge_percent, merchant_shipping_option_status)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "merchant")
        query = """
        SELECT id,merchant_shipping_option_id,merchant_shipping_option_name,merchant_shipping_option_nku,merchant_shipping_option_image,merchant_shipping_option_charge_fixed,merchant_shipping_option_charge_percent,merchant_shipping_option_status
        FROM merchant_shipping_option
        WHERE merchant_shipping_option_id = %s
        """
        mysql_cursor.execute(query, (merchant_shipping_option_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_payment_method(mysql_cursor, merchant_id):
    """
    This method select details from merchant_payment_method table
    :return: List in format [(id, merchant_payment_method_name, merchant_payment_method_status, merchant_payment_method_fee_target, merchant_payment_method_option_id, merchant_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "merchant")
        query = """
        SELECT id, merchant_payment_method_name, merchant_payment_method_status, merchant_payment_method_fee_target, merchant_payment_method_option_id, merchant_id
        FROM merchant_payment_method
        WHERE merchant_id = %s
        """
        mysql_cursor.execute(query, (merchant_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)
    
def get_income(mysql_cursor, order_id, merchant_id):
    """
    This method select details from income table
    :return: List in format [(id, income_id, income_initial_total, income_real_total, income_date, income_status, ord_id, merchant_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "merchant")
        query = """
        SELECT id, income_id, income_initial_total, income_real_total, income_date, income_status, ord_id, merchant_id
        FROM income
        WHERE ord_id = %s AND merchant_id = %s
        """
        mysql_cursor.execute(query, (order_id, merchant_id))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def select_payment_method_option(mysql_cursor, merchant_payment_method_option_id, merchant_payment_method_option_nku = None, by_nku = False):
    """
    This method select details from merchant_payment_method_option table
    :return: List in format [(id, merchant_payment_method_option_id, merchant_payment_method_option_name, merchant_payment_method_option_nku, merchant_payment_method_option_image, merchant_payment_method_option_charge_fixed, merchant_payment_method_option_charge_percent, merchant_payment_method_option_status)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "merchant")
        if by_nku:
            query = """
            SELECT id, merchant_payment_method_option_id, merchant_payment_method_option_name, merchant_payment_method_option_nku, merchant_payment_method_option_image, merchant_payment_method_option_charge_fixed, merchant_payment_method_option_charge_percent, merchant_payment_method_option_status
            FROM merchant_payment_method_option
            WHERE merchant_payment_method_option_nku = %s
            """
            mysql_cursor.execute(query, (merchant_payment_method_option_nku,))
        else:
            query = """
            SELECT id, merchant_payment_method_option_id, merchant_payment_method_option_name, merchant_payment_method_option_nku, merchant_payment_method_option_image, merchant_payment_method_option_charge_fixed, merchant_payment_method_option_charge_percent, merchant_payment_method_option_status
            FROM merchant_payment_method_option
            WHERE merchant_payment_method_option_id = %s
            """
            mysql_cursor.execute(query, (merchant_payment_method_option_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_payment_method_option(mysql_cursor, status =None, by_status = False):
    """
    This method select details from merchant_payment_method_option table
    :return: List in format [(id, merchant_payment_method_option_id, merchant_payment_method_option_name, merchant_payment_method_option_nku, merchant_payment_method_option_image, merchant_payment_method_option_charge_fixed, merchant_payment_method_option_charge_percent, merchant_payment_method_option_status)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "merchant")
        if by_status:
            query = """
            SELECT id, merchant_payment_method_option_id, merchant_payment_method_option_name, merchant_payment_method_option_nku, merchant_payment_method_option_image, merchant_payment_method_option_charge_fixed, merchant_payment_method_option_charge_percent, merchant_payment_method_option_status
            FROM merchant_payment_method_option
            WHERE merchant_payment_method_option_status = %s
            """
            mysql_cursor.execute(query, (status,))
        else:
            query = """
            SELECT id, merchant_payment_method_option_id, merchant_payment_method_option_name, merchant_payment_method_option_nku, merchant_payment_method_option_image, merchant_payment_method_option_charge_fixed, merchant_payment_method_option_charge_percent, merchant_payment_method_option_status
            FROM merchant_payment_method_option
            """
            mysql_cursor.execute(query)
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_business_name(mysql_cursor, merchant_id):
    """
    This method select details from merchant business profile table
    :return: List in format [(id, business_profile_name, business_profile_location, business_profile_address, business_profile_email, business_profile_phone_country_code, business_profile_phone_number, business_profile_shoppage, business_profile_shoptype, business_profile_shopimg, business_profile_shopdes)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "merchant")
        query = """
        SELECT id, business_profile_name, business_profile_location, business_profile_address, business_profile_email, business_profile_phone_country_code, business_profile_phone_number, business_profile_shoppage, business_profile_shoptype, business_profile_shopimg, business_profile_shopdes
        FROM business_profile
        WHERE merchant_id = %s
        """
        mysql_cursor.execute(query, (merchant_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def select_telegram_bot(mysql_cursor, merchant_id) -> list | Exception:
    """
    This method select telegram bot for a merchant
    :return: List in format [(id, telegram_bot_id, telegram_bot_name, telegram_bot_token, telegram_bot_nku, merchant_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "merchant")
        query = """
        SELECT id, telegram_bot_id, telegram_bot_name, telegram_bot_token, telegram_bot_nku, merchant_id
        FROM telegram_bot
        WHERE merchant_id = %s
        """
        mysql_cursor.execute(query, (merchant_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return e

def select_telegram_bot_chat(mysql_cursor, merchant_id, telegram_bot_id, telegram_bot_chat_usage = None, by_usage = False) -> list | Exception:
    """
    This method select telegram bot chat for a merchant
    :return: List in format [(id, telegram_bot_chat_id, telegram_bot_chat_name, telegram_bot_chat_usage, telegram_bot_id, merchant_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "merchant")
        if by_usage:
            query = """
            SELECT id, telegram_bot_chat_id, telegram_bot_chat_name, telegram_bot_chat_usage, telegram_bot_id, merchant_id
            FROM telegram_bot_chat
            WHERE merchant_id = %s AND telegram_bot_id = %s AND telegram_bot_chat_usage = %s
            """
            mysql_cursor.execute(query, (merchant_id, telegram_bot_id, telegram_bot_chat_usage))
        else:
            query = """
            SELECT id, telegram_bot_chat_id, telegram_bot_chat_name, telegram_bot_chat_usage, telegram_bot_id, merchant_id
            FROM telegram_bot_chat
            WHERE merchant_id = %s AND telegram_bot_id = %s
            """
            mysql_cursor.execute(query, (merchant_id, telegram_bot_id))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return e

def generate_unique_income_id(mysql_cursor, prefix="SAMYMICM"):
    """
    This method generate a unique income id for merchant
    :return: str, None otherwise;
    """
    try:
        use_db(mysql_cursor, "merchant")
        query = """
        SELECT id 
        FROM income 
        WHERE income_id = %s
        """
        random_int = random.randint(1000000000, 9999999999)
        unique_random_id = prefix+str(random_int)
        mysql_cursor.execute(query, (unique_random_id,))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        while(num_results != 0):
            random_int = random.randint(1000000000, 9999999999)
            unique_random_id = prefix+str(random_int)
            mysql_cursor.execute(query, (unique_random_id,))
            results = mysql_cursor.fetchall()
            num_results = len(results)

        return unique_random_id
    except Exception as e:
        return str(e)
    
#============================================================================================
#Mutator
#============================================================================================

def create_income(mysql_conn, mysql_cursor, income_initial_total, income_real_total, income_date, income_status, ord_id, merchant_id):
    try:
        response = None
        use_db(mysql_cursor, "merchant")
        unique_income_id = generate_unique_income_id(mysql_cursor)
        #check user's address
        query1 = """
        INSERT INTO income (income_id, income_initial_total, income_real_total, income_date, income_status, ord_id, merchant_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query1, (unique_income_id, income_initial_total, income_real_total, income_date, income_status, ord_id, merchant_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        num_results_expected = 1
        if  num_results == num_results_expected:
            response = unique_income_id
    except Exception as e:
        response = e
    finally:
        return response

def create_income(mysql_conn, mysql_cursor, income_initial_total, income_real_total, income_date, income_status, ord_id, merchant_id):
    try:
        response = None
        use_db(mysql_cursor, "merchant")
        unique_income_id = generate_unique_income_id(mysql_cursor)
        #check user's address
        query1 = """
        INSERT INTO income (income_id, income_initial_total, income_real_total, income_date, income_status, ord_id, merchant_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query1, (unique_income_id, income_initial_total, income_real_total, income_date, income_status, ord_id, merchant_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        num_results_expected = 1
        if  num_results == num_results_expected:
            response = unique_income_id
    except Exception as e:
        response = e
    finally:
        return response

def create_income_details(mysql_conn, mysql_cursor, income_fees, income_description, income_id):
    try:
        response = False
        use_db(mysql_cursor, "merchant")
        #check user's address
        query1 = """
        INSERT INTO income_details (income_fees, income_description, income_id) 
        VALUES (%s, %s, %s)
        """
        mysql_cursor.execute(query1, (income_fees, income_description, income_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        num_results_expected = 1
        if  num_results == num_results_expected:
            response = True
    except Exception as e:
        response = e
    finally:
        return response

def update_income_status(mysql_conn, mysql_cursor, income_status, ord_id, merchant_id = None):
    try:
        response = False
        use_db(mysql_cursor, "merchant")
        if merchant_id != None:
            query1 = """
            UPDATE income
            SET income_status = %s
            WHERE ord_id = %s AND merchant_id = %s
            """
            mysql_cursor.execute(query1, (income_status, ord_id, merchant_id))
        else:
            query1 = """
            UPDATE income
            SET income_status = %s
            WHERE ord_id = %s
            """
            mysql_cursor.execute(query1, (income_status, ord_id,))

        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        response = True
    except Exception as e:
        response = e
    finally:
        return response