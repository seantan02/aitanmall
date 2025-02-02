from webApp.mysql_connector import use_db
import random
from webApp.helper import general

#======================================
#accesor
#=====================================
def select_orders(mysql_cursor, ord_id):
    """
    This method gets the orders details from database
    :return: List of tuple: [(id, ord_id, user_id, user_address, user_address_id, merchant_payment_method_option_nku, ord_date, ord_total, ord_shipping_discount, ord_final_total, ord_status)]; None otherwise.
    """
    try:
        use_db(mysql_cursor, "orders")
        query = """
        SELECT id, ord_id, user_id, user_address, user_address_id, merchant_payment_method_option_nku, ord_date, ord_total, ord_shipping_discount, ord_final_total, ord_status
        FROM orders
        WHERE ord_id = %s
        """

        mysql_cursor.execute(query, (ord_id,))
        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0 :
            return results
        return []
    except Exception as e:
        return e

def select_order_details(mysql_cursor, ord_id):
    """
    This method gets the ord_details from database
    :return: List of tuple: [(id, ord_prd_id, ord_prd_name, ord_prd_img, ord_prd_sku, ord_prd_var_id, ord_prd_var_name, ord_prd_var_img, ord_quantity, ord_price, ord_has_warranty, ord_warranty_period, merchant_id, ord_id)]; None otherwise.
    """
    try:
        use_db(mysql_cursor, "orders")
        query = """
        SELECT id, ord_prd_id, ord_prd_name, ord_prd_img, ord_prd_sku, ord_prd_var_id, ord_prd_var_name, ord_prd_var_img, ord_quantity, ord_price, ord_has_warranty, ord_warranty_period, merchant_id, ord_id
        FROM ord_details
        WHERE ord_id = %s
        """

        mysql_cursor.execute(query, (ord_id,))
        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0 :
            return results
        return []
    except Exception as e:
        return e
    
def select_order_shipment(mysql_cursor, shipment_index_id, ord_id = None):
    """
    This method gets the ord_details from database
    :return: List of tuple: [(id, shipment_courier, shipment_tracking_number, shipment_courier_status, ord_id)]; None otherwise.
    """
    try:
        use_db(mysql_cursor, "orders")
        if ord_id != None:
            query = """
            SELECT id, shipment_courier, shipment_tracking_number, shipment_courier_status, ord_id
            FROM ord_shipment
            WHERE ord_id = %s
            """
            mysql_cursor.execute(query, (ord_id,))
        else:
            query = """
            SELECT id, shipment_courier, shipment_tracking_number, shipment_courier_status, ord_id
            FROM ord_shipment
            WHERE id = %s
            """
            mysql_cursor.execute(query, (shipment_index_id,))

        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0 :
            return results
        return []
    except Exception as e:
        return e
#======================================
#GET
#=====================================
def get_orders(mysql_cursor, limit = 5):
    """
    This method gets the orders details from database
    :return: List of tuple: [(id, ord_id, user_id, user_address, user_address_id, merchant_payment_method_option_nku, ord_date, ord_total, ord_shipping_discount, ord_final_total, ord_status)]; None otherwise.
    """
    try:
        use_db(mysql_cursor, "orders")
        query = """
        SELECT id, ord_id, user_id, user_address, user_address_id, merchant_payment_method_option_nku, ord_date, ord_total, ord_shipping_discount, ord_final_total, ord_status
        FROM orders
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query)
        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0 :
            return results
        return []
    except Exception as e:
        return e

def get_order_details(mysql_cursor, limit = 5):
    """
    This method gets the ord_details from database
    :return: List of tuple: [(id, ord_prd_id, ord_prd_name, ord_prd_img, ord_prd_sku, ord_prd_var_id, ord_prd_var_name, ord_prd_var_img, ord_quantity, ord_price, ord_has_warranty, ord_warranty_period, merchant_id, ord_id)]; None otherwise.
    """
    try:
        use_db(mysql_cursor, "orders")
        query = """
        SELECT id, ord_prd_id, ord_prd_name, ord_prd_img, ord_prd_sku, ord_prd_var_id, ord_prd_var_name, ord_prd_var_img, ord_quantity, ord_price, ord_has_warranty, ord_warranty_period, merchant_id, ord_id
        FROM ord_details
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query)
        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0 :
            return results
        return []
    except Exception as e:
        return e

def get_user_orders(mysql_cursor, user_id, limit = 5):
    """
    This method gets the orders details from database
    :return: List of tuple: [(id, ord_id, user_id, user_address, user_address_id, merchant_payment_method_option_nku, ord_date, ord_total, ord_shipping_discount, ord_final_total, ord_status)]; None otherwise.
    """
    try:
        use_db(mysql_cursor, "orders")
        query = """
        SELECT id, ord_id, user_id, user_address, user_address_id, merchant_payment_method_option_nku, ord_date, ord_total, ord_shipping_discount, ord_final_total, ord_status
        FROM orders
        WHERE user_id = %s
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query, (user_id,))
        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0 :
            return results
        return []
    except Exception as e:
        return e

def get_user_order_details(mysql_cursor, user_id, limit = 5):
    """
    This method gets the ord_details from database
    :return: List of tuple: [(orders.id, orders.ord_id, orders.user_id, orders.user_address, orders.user_address_id, orders.merchant_payment_method_option_nku, orders.ord_date, orders.ord_total, orders.ord_shipping_discount, orders.ord_final_total, orders.ord_status,\
        ord_details.ord_prd_id, ord_details.ord_prd_name, ord_details.ord_prd_img, ord_details.ord_prd_sku, ord_details.ord_prd_var_id, ord_details.ord_prd_var_name, ord_details.ord_prd_var_img, ord_details.ord_quantity, ord_details.ord_price, ord_details.ord_has_warranty, ord_details.ord_warranty_period, ord_details.merchant_id)]; None otherwise.
    """
    try:
        use_db(mysql_cursor, "orders")
        query = """
        SELECT orders.id, orders.ord_id, orders.user_id, orders.user_address, orders.user_address_id, orders.merchant_payment_method_option_nku, orders.ord_date, orders.ord_total, orders.ord_shipping_discount, orders.ord_final_total, orders.ord_status,\
        ord_details.ord_prd_id, ord_details.ord_prd_name, ord_details.ord_prd_img, ord_details.ord_prd_sku, ord_details.ord_prd_var_id, ord_details.ord_prd_var_name, ord_details.ord_prd_var_img, ord_details.ord_quantity, ord_details.ord_price, ord_details.ord_has_warranty, ord_details.ord_warranty_period, ord_details.merchant_id
        FROM orders
        JOIN ord_details ON orders.ord_id = ord_details.ord_id
        WHERE orders.user_id = %s
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query, (user_id,))
        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0:
            return results
        return []
    except Exception as e:
        return e

def get_merchant_order_details(mysql_cursor, merchant_id, limit = 5):
    """
    This method gets the ord_details from database
    :return: List of tuple: [(id, ord_prd_id, ord_prd_name, ord_prd_img, ord_prd_sku, ord_prd_var_id, ord_prd_var_name, ord_prd_var_img, ord_quantity, ord_price, ord_has_warranty, ord_warranty_period, merchant_id, ord_id)]; None otherwise.
    """
    try:
        use_db(mysql_cursor, "orders")
        query = """
        SELECT id, ord_prd_id, ord_prd_name, ord_prd_img, ord_prd_sku, ord_prd_var_id, ord_prd_var_name, ord_prd_var_img, ord_quantity, ord_price, ord_has_warranty, ord_warranty_period, merchant_id, ord_id
        FROM ord_details
        WHERE merchant_id = %s
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query, (merchant_id,))
        results = mysql_cursor.fetchall()
        num_result = len(results)

        if num_result > 0 :
            return results
        return []
    except Exception as e:
        return e
#======================================
#Mutator
#=====================================
def create_orders(mysql_conn, mysql_cursor, ord_id, user_id, user_address, user_address_id, merchant_payment_method_option_nku, ord_date, ord_total, ord_shipping_discount, ord_final_total, ord_status):
    try:
        response = False
        use_db(mysql_cursor, "orders")
        #check user's address
        query1 = """
        INSERT INTO orders (ord_id, user_id, user_address, user_address_id, merchant_payment_method_option_nku, ord_date, ord_total, ord_shipping_discount, ord_final_total, ord_status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query1, (ord_id, user_id, user_address, user_address_id, merchant_payment_method_option_nku, ord_date, ord_total, ord_shipping_discount, ord_final_total, ord_status))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        num_results_expected = 1
        if  num_results == num_results_expected:
            response = True
    except Exception as e:
        response = e
    finally:
        return response

def create_order_details(mysql_conn, mysql_cursor, ord_prd_id, ord_prd_name, ord_prd_img, ord_prd_sku, ord_prd_var_id, ord_prd_var_name, ord_prd_var_img, ord_quantity, ord_price, ord_has_warranty, ord_warranty_period, merchant_id, ord_id):
    try:
        response = False
        use_db(mysql_cursor, "orders")
        #check user's address
        query1 = """
        INSERT INTO ord_details (ord_prd_id, ord_prd_name, ord_prd_img, ord_prd_sku, ord_prd_var_id, ord_prd_var_name, ord_prd_var_img, ord_quantity, ord_price, ord_has_warranty, ord_warranty_period, merchant_id, ord_id) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        mysql_cursor.execute(query1, (ord_prd_id, ord_prd_name, ord_prd_img, ord_prd_sku, ord_prd_var_id, ord_prd_var_name, ord_prd_var_img, ord_quantity, ord_price, ord_has_warranty, ord_warranty_period, merchant_id, ord_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        num_results_expected = 1
        if  num_results == num_results_expected:
            response = True
    except Exception as e:
        response = e
    finally:
        return response

def create_order_fees(mysql_conn, mysql_cursor, fees, description, ord_id):
    try:
        response = False
        use_db(mysql_cursor, "orders")
        #check user's address
        query1 = """
        INSERT INTO ord_other_fees (fees, description, ord_id) 
        VALUES (%s, %s, %s)
        """
        mysql_cursor.execute(query1, (fees, description, ord_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        num_results_expected = 1
        if  num_results == num_results_expected:
            response = True
    except Exception as e:
        response = e
    finally:
        return response

def create_ord_shipment(mysql_conn, mysql_cursor, shipment_courier, shipment_tracking_number, shipment_courier_status, ord_id):
    try:
        response = False
        use_db(mysql_cursor, "orders")
        #check user's address
        query1 = """
        INSERT INTO ord_shipment (shipment_courier, shipment_tracking_number, shipment_courier_status, ord_id) 
        VALUES (%s, %s, %s, %s)
        """
        mysql_cursor.execute(query1, (shipment_courier, shipment_tracking_number, shipment_courier_status, ord_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        num_results_expected = 1
        if  num_results == num_results_expected:
            response = True
    except Exception as e:
        response = e
    finally:
        return response
    
#==================================================================
#Update
#==================================================================
def update_orders(mysql_conn, mysql_cursor, merchant_payment_method_option_nku, ord_total, ord_shipping_discount, ord_final_total, ord_status, ord_id):
    try:
        response = False
        use_db(mysql_cursor, "orders")
        #check user's address
        query1 = """
        UPDATE orders 
        SET merchant_payment_method_option_nku = %s, ord_total = %s, ord_shipping_discount = %s, ord_final_total = %s, ord_status = %s
        WHERE ord_id = %s
        """
        mysql_cursor.execute(query1, (merchant_payment_method_option_nku, ord_total, ord_shipping_discount, ord_final_total, ord_status, ord_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        response = True
    except Exception as e:
        response = e
    finally:
        return response

def update_orders_status(mysql_conn, mysql_cursor, ord_status, ord_id):
    try:
        response = False
        use_db(mysql_cursor, "orders")
        #check user's address
        query1 = """
        UPDATE orders 
        SET ord_status = %s
        WHERE ord_id = %s
        """
        mysql_cursor.execute(query1, (ord_status, ord_id))
        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        response = True
    except Exception as e:
        response = e
    finally:
        return response
    
def update_ord_shipment_status(mysql_conn, mysql_cursor, status, shipment_index_id, order_id = None, by_order_id = False):
    try:
        response = False
        use_db(mysql_cursor, "orders")
        #Update order
        if by_order_id == True:
            query1 = """
            UPDATE ord_shipment 
            SET shipment_courier_status = %s
            WHERE ord_id = %s
            """
            mysql_cursor.execute(query1, (status, order_id))
        else:
            query1 = """
            UPDATE ord_shipment 
            SET shipment_courier_status = %s
            WHERE id = %s
            """
            mysql_cursor.execute(query1, (status, shipment_index_id))

        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        response = True
    except Exception as e:
        response = e
    finally:
        return response

def update_ord_shipment_tracking_number(mysql_conn, mysql_cursor, tracking_number, shipment_index_id, order_id = None, by_order_id = False):
    try:
        response = False
        use_db(mysql_cursor, "orders")
        #Update order
        if by_order_id == True:
            query1 = """
            UPDATE ord_shipment 
            SET shipment_tracking_number = %s
            WHERE ord_id = %s
            """
            mysql_cursor.execute(query1, (tracking_number, order_id))
        else:
            query1 = """
            UPDATE ord_shipment 
            SET shipment_tracking_number = %s
            WHERE id = %s
            """
            mysql_cursor.execute(query1, (tracking_number, shipment_index_id))

        num_results = mysql_cursor.rowcount
        mysql_conn.commit()
        response = True
    except Exception as e:
        response = e
    finally:
        return response