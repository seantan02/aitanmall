from flask import session
from webApp.helper import general
import random
from passlib.hash import sha256_crypt

#accessor
def generate_unique_cs_id(mysql_cursor, prefix = "SAMY") -> str:
    query = """
    SELECT id FROM customer_service WHERE customer_service_id = %s
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
#mutator
def log_in_cs(mysql_cursor, customer_service_id):
    query = """
    SELECT id,customer_service_first_name,customer_service_last_name,customer_service_email,customer_service_phone_number_code,customer_service_phone_number 
    FROM customer_service 
    WHERE customer_service_id = %s
    """
    
    mysql_cursor.execute(query, (customer_service_id,))
    result = mysql_cursor.fetchall()
    num_result = len(result)
    if num_result == 1:
        #set session
        session["cs_logged_in"] = True
        session["cs_id"] = customer_service_id
        session["cs_first_name"] = result[0][1]
        session["cs_last_name"] = result[0][2]
        session["cs_email"] = result[0][3]
        session["cs_phone_number"] = str(result[0][4]) + str(result[0][5])

        return True
    return False
#mysql
#accessor
def user_log_in_details_is_valid(mysql_cursor, username:str, password:str, verify_by = "email") -> bool:
    if verify_by == "email":
        query = """
        SELECT customer_service_id,customer_service_password 
        FROM customer_service WHERE customer_service_email = %s
        """
    elif verify_by == "username":
        query = """
        SELECT customer_service_id,customer_service_password 
        FROM customer_service WHERE customer_service_username = %s
        """
    
    mysql_cursor.execute(query, (username,))
    result = mysql_cursor.fetchall()
    num_result = len(result)
    if num_result == 1:
        password_to_match = result[0][1]
        return sha256_crypt.verify(password, password_to_match)
    else:
        return False 
    
def get_cs_id(mysql_cursor, username:str, verify_by = "email") -> str:
    if verify_by == "username":
        query = """
        SELECT customer_service_id 
        FROM customer_service 
        WHERE customer_service_username = %s
        """
    elif verify_by == "email":
        query = """
        SELECT customer_service_id 
        FROM customer_service 
        WHERE customer_service_email = %s
        """
    mysql_cursor.execute(query, (username,))
    result = mysql_cursor.fetchall()
    num_result = len(result)
    
    if num_result == 1:
        return result[0][0]
    else:
        return None

def user_temporarily_key_exist(mysql_cursor, cs_id) -> bool:
    try:
        query = """
        SELECT customer_service_temporarily_key_id FROM customer_service_temporarily_key WHERE customer_service_id = %s
        """
        mysql_cursor.execute(query, (cs_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)

        if num_result == 1:
            return True
        return False
    except:
        return False 
    
def remove_user_temporarily_key(mysql_conn, mysql_cursor, cs_id) -> bool:
    try:
        query = """
        DELETE FROM customer_service_temporarily_key WHERE customer_service_id = %s
        """
        mysql_cursor.execute(query, (cs_id,))
        num_affected= mysql_cursor.rowcount
        mysql_conn.commit()

        return True
    except:
        return False

def insert_user_temporarily_key(mysql_conn, mysql_cursor, temporarily_key, created_date, expire_date, cs_id) -> bool:
    try:
        query = """
        INSERT INTO customer_service_temporarily_key (customer_service_temporarily_key, customer_service_temporarily_key_created_date, customer_service_temporarily_key_expire_date, customer_service_id) VALUES(%s, %s, %s, %s)
        """
        mysql_cursor.execute(query, (temporarily_key, created_date, expire_date, cs_id))
        num_inserted= mysql_cursor.rowcount
        mysql_conn.commit()

        if num_inserted == 1:
            return True
        return False
    except:
        return False

def log_in_cookie_is_valid(mysql_cursor,temporarily_key_cookie,cs_id_cookie,current_time):
    try:
        query = """
        SELECT customer_service_temporarily_key_expire_date FROM customer_service_temporarily_key WHERE customer_service_temporarily_key = %s AND customer_service_id = %s
        """
        
        mysql_cursor.execute(query, (temporarily_key_cookie,cs_id_cookie))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        assert num_result == 1, "ERROR"
        assert current_time < str(result[0][0]), "Temporarily key has expired"
        return True
    except Exception as e:
        return False
#mysql mutator
def create_account(db_conn, mysql_cursor, username, email, country_code, phone_number, password, first_name = "user", last_name="new") -> bool:
    #insert user data into our main database
    query = """
    INSERT INTO customer_service (customer_service_id, customer_service_username, customer_service_first_name, customer_service_last_name, customer_service_email, customer_service_phone_number_code, \
        customer_service_phone_number, customer_service_password, customer_service_account_status, customer_service_photo) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    customer_service_id = generate_unique_cs_id(mysql_cursor)
    mysql_cursor.execute(query, (customer_service_id,username,first_name,last_name,email,country_code,phone_number,password,"new",""))
    num_inserted= mysql_cursor.rowcount
    if num_inserted != 1:
        revert_create_account(db_conn, customer_service_id)
        return False
    db_conn.commit()
    
    return True

def revert_create_account(db_conn, cs_id) -> bool:
    try:
        mysql_cursor = db_conn.cursor()
        query = """
        DELETE FROM customer_service WHERE customer_service_id = %s
        """
        mysql_cursor.execute(query, (cs_id,))
        db_conn.commit()

        return True
    except:
        return False
    
def generate_temporarily_key(string) -> str:
    try:
        temporarily_key = sha256_crypt.encrypt(string)
        return temporarily_key
    except:
        return None

        