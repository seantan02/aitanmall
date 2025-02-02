from webApp.mysql_connector import use_db, close_mysql_conn, close_mysql_cursor
import random

#============================================================================
#Accessor
#============================================================================
def select_voucher(mysql_cursor, voucher_id, voucher_code = None, voucher_status = None, by_code = False, by_status = False) -> str:
    """
    This method select details from voucher table
    :return: List in format [(id, voucher_id, voucher_code, voucher_description, voucher_discount_amount, voucher_discount_type, voucher_discount_cap, voucher_created_date, voucher_expire_date, voucher_max_usage, voucher_usage_count, voucher_status)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "voucher")
        
        if by_code:
            assert voucher_code != None, "Voucher code cannot be None"
            query = """
            SELECT id, voucher_id, voucher_code, voucher_description, voucher_discount_amount, voucher_discount_type, voucher_discount_cap, voucher_created_date, voucher_expire_date, voucher_max_usage, voucher_usage_count, voucher_status
            FROM voucher 
            WHERE voucher_code = %s
            """
            mysql_cursor.execute(query, (voucher_code,))
        elif by_status:
            assert voucher_status != None, "Voucher status cannot be None"
            query = """
            SELECT id, voucher_id, voucher_code, voucher_description, voucher_discount_amount, voucher_discount_type, voucher_discount_cap, voucher_created_date, voucher_expire_date, voucher_max_usage, voucher_usage_count, voucher_status
            FROM voucher 
            WHERE voucher_status = %s
            """
            mysql_cursor.execute(query, (voucher_status,))
        else:
            assert voucher_id != None, "Voucher ID cannot be None"
            query = """
            SELECT id, voucher_id, voucher_code, voucher_description, voucher_discount_amount, voucher_discount_type, voucher_discount_cap, voucher_created_date, voucher_expire_date, voucher_max_usage, voucher_usage_count, voucher_status
            FROM voucher 
            WHERE voucher_id = %s
            """
            mysql_cursor.execute(query, (voucher_id,))

        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            return results
        return []
    except Exception as e:
        return e

def get_user_voucher(mysql_cursor, user_id, limit = None):
    """
    This method return records in user's database under table user_voucher
    :raises Exception: If any process in between goes wrong
    :return: a list of tuple containing [
    (id, voucher_user_usage_cap, voucher_id, user_id)
    ]
    """
    try:
        use_db(mysql_cursor, "voucher")
        response = None
        #check user's address
        query = """
        SELECT id, voucher_user_usage_cap, voucher_id, user_id
        FROM voucher_user_map
        WHERE user_id = %s
        {}
        """
        if limit != None:
            assert isinstance(limit, int) or (isinstance(limit, str) and limit.isdigit()), "Limit has to be either integer or digit number"
            query = query.format("LIMIT "+str(limit))
        else:
            query = query.format("")
        
        mysql_cursor.execute(query, (user_id,))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
    except Exception as e:
        response = e
    finally:
        return response
    
def select_user_voucher(mysql_cursor, user_id, voucher_id):
    """
    This method return records in user's database under table user_voucher
    :raises Exception: If any process in between goes wrong
    :return: a list of tuple containing [
    (id, voucher_user_usage_cap, voucher_id, user_id)
    ]
    """
    try:
        use_db(mysql_cursor, "voucher")
        response = None
        #check user's address
        query = """
        SELECT id, voucher_user_usage_cap, voucher_id, user_id
        FROM voucher_user_map
        WHERE user_id = %s AND voucher_id = %s
        """

        mysql_cursor.execute(query, (user_id,voucher_id))
        results = mysql_cursor.fetchall()
        num_results = len(results)
        if num_results > 0:
            response = results
    except Exception as e:
        response = e
    finally:
        return response
    
def generate_unique_voucher_id(mysql_cursor, prefix = "SAMYVCH") -> str:
    try:
        use_db(mysql_cursor, "voucher")
        query = """
        SELECT id 
        FROM voucher 
        WHERE voucher_id = %s
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

#============================================================================
#Mutator
#============================================================================

def create_voucher(mysql_conn, mysql_cursor, voucher_id, voucher_code, voucher_description, voucher_discount_amount, voucher_discount_type, voucher_discount_cap, voucher_created_date, voucher_expire_date, voucher_max_usage, voucher_usage_count, voucher_status) -> str:
    try:
        response = False
        use_db(mysql_cursor, "voucher")
        #check user's address
        query1 = """
        INSERT INTO voucher (voucher_id, voucher_code, voucher_description, voucher_discount_amount, voucher_discount_type, voucher_discount_cap, voucher_created_date, voucher_expire_date, voucher_max_usage, voucher_usage_count, voucher_status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query1, (voucher_id, voucher_code, voucher_description, voucher_discount_amount, voucher_discount_type, voucher_discount_cap, voucher_created_date, voucher_expire_date, voucher_max_usage, voucher_usage_count, voucher_status))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        num_results_expected = 1
        if  num_results == num_results_expected:
            response = True
    except Exception as e:
        response = e
    finally:
        return response

def assign_user_voucher(mysql_conn, mysql_cursor, voucher_user_usage_cap, voucher_id, user_id) -> str:
    try:
        response = False
        use_db(mysql_cursor, "voucher")
        #check user's address
        query1 = """
        INSERT INTO voucher_user_map (voucher_user_usage_cap, voucher_id, user_id) 
        VALUES (%s, %s, %s)
        """
        mysql_cursor.execute(query1, (voucher_user_usage_cap, voucher_id, user_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        num_results_expected = 1
        if  num_results == num_results_expected:
            response = True
    except Exception as e:
        response = e
    finally:
        return response

def reduce_user_voucher_usage_cap(mysql_conn, mysql_cursor, voucher_reduce_amount, voucher_id, user_id) -> bool | Exception:
    try:
        response = False
        use_db(mysql_cursor, "voucher")
        #update voucher usage_cap to 1 lower
        query1 = """
        UPDATE voucher_user_map
        SET voucher_user_usage_cap = voucher_user_usage_cap - %s
        WHERE voucher_id = %s AND user_id = %s
        """
        mysql_cursor.execute(query1, (voucher_reduce_amount, voucher_id, user_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        #DELETE ALL voucher_user_map where usage_cap == 0
        query2 = """
        DELETE FROM voucher_user_map
        WHERE voucher_user_usage_cap <= 0
        """
        mysql_cursor.execute(query2)
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        response = True
    except Exception as e:
        response = e
    finally:
        return response