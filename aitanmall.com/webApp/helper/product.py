from webApp.mysql_connector import use_db
import random
from webApp.helper import general

#======================================
#accesor
#=====================================

def product_id_and_variation_id_valid(mysql_cursor, product_id, product_variation_index_id):
    """
    This method cehck if given product id and product variation id are valid
    :return: bool
    """
    try:
        product_variation_details = select_product_variation(mysql_cursor, product_variation_index_id)
        use_db(mysql_cursor, "product")
        product_variation_category_id = product_variation_details[0][7]
        query = """
        SELECT prd_var_cat_name
        FROM prd_var_cat
        WHERE prd_id = %s AND id = %s
        """
        mysql_cursor.execute(query, (product_id,product_variation_category_id))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return True
        return False
    except Exception as e:
        return str(e)

def get_warranty(mysql_cursor, product_id):
    """
    This method select details from prd_warranty table
    :return: List in format [(id, warranty_period, prd_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        query = """
        SELECT id, warranty_period, prd_id
        FROM prd_warranty
        WHERE prd_id = %s
        """
        mysql_cursor.execute(query, (product_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_offerlines(mysql_cursor, product_id, language):
    """
    This method select product's offerlines
    :return: List in format [(id, prd_offerline, prd_offerline_order, prd_lang, prd_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")

        query = """
        SELECT id, prd_offerline, prd_offerline_order, prd_lang, prd_id
        FROM prd_offerline
        WHERE prd_id = %s AND prd_lang = %s
        """
        mysql_cursor.execute(query, (product_id,language))

        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_product(mysql_cursor, prd_id, index_id = None, by_index = False):
    """
    This method select products base on prd_fame
    :return: List in format [(id, prd_id, prd_name, prd_status, prd_fame, cat_id, brand_id, merchant_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")

        if by_index:
            query = """
            SELECT id, prd_id, prd_name, prd_status, prd_fame, cat_id, brand_id, merchant_id
            FROM product
            WHERE id = %s
            """
            mysql_cursor.execute(query, (index_id,))
        else:
            query = """
            SELECT id, prd_id, prd_name, prd_status, prd_fame, cat_id, brand_id, merchant_id
            FROM product
            WHERE prd_id = %s
            """
            mysql_cursor.execute(query, (prd_id,))

        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_product_details(mysql_cursor, prd_id, index_id = None, by_index = False):
    """
    This method select products base on prd_fame
    :return: List in format [(id, prd_name, prd_status, prd_price, prd_offer_price, prd_image, prd_quantity, prd_sku, prd_date, prd_level, prd_cost, prd_preorders_status, prd_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")

        if by_index:
            query = """
            SELECT id, prd_name, prd_status, prd_price, prd_offer_price, prd_image, prd_quantity, prd_sku, prd_date, prd_level, prd_cost, prd_preorders_status, prd_id
            FROM prd_details
            WHERE id = %s
            """
            mysql_cursor.execute(query, (index_id,))
        else:
            query = """
            SELECT id, prd_name, prd_status, prd_price, prd_offer_price, prd_image, prd_quantity, prd_sku, prd_date, prd_level, prd_cost, prd_preorders_status, prd_id
            FROM prd_details
            WHERE prd_id = %s
            """
            mysql_cursor.execute(query, (prd_id,))

        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)
    
def get_product_by_fame(mysql_cursor, limit = 3):
    """
    This method select products base on prd_fame
    :return: List in format [(product)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        query = """
        SELECT product.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id
        FROM prd_details
        JOIN product ON prd_details.prd_id = product.prd_id
        WHERE prd_details.prd_status = 'active'
        ORDER BY product.prd_fame DESC
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query)
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)
    
def get_product_by_discount(mysql_cursor, limit = 2):
    """
    This method select products base on prd_fame
    :return: List in format [(product)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        query = """
        SELECT product.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id
        FROM prd_details
        JOIN product ON prd_details.prd_id = product.prd_id
        WHERE prd_details.prd_status = 'active'
        ORDER BY ((prd_details.prd_price - prd_details.prd_offer_price) / prd_details.prd_price) * 100 DESC
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query)
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)
    
def get_product_after_fame(mysql_cursor, last_prd_fame, limit = 5):
    """
    This method select products base on prd_fame
    :return: List in format [(id, prd_name, prd_status, prd_price, prd_offer_price,prd_image , prd_quantity, prd_sku, prd_date, prd_level, prd_cost, prd_preorders_status, prd_id, merchant_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        query = """
        SELECT product.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id
        FROM prd_details
        JOIN product ON prd_details.prd_id = product.prd_id
        WHERE prd_details.prd_status = 'active' AND product.prd_fame < %s
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query, (last_prd_fame,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_product_by_discount_less_than(mysql_cursor, last_prd_discount_percentage, limit = 4):
    """
    This method select products base on product discount percentage
    :return: List in format [(id, prd_name, prd_status, prd_price, prd_offer_price,prd_image , prd_quantity, prd_sku, prd_date, prd_level, prd_cost, prd_preorders_status, prd_id, merchant_id)]; [] otherwise.
    """
    try:
        last_prd_discount_percentage = int(last_prd_discount_percentage)
        assert isinstance(last_prd_discount_percentage, int), "Last product discount percentage has to be integer"
        use_db(mysql_cursor, "product")
        query = """
        SELECT product.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id
        FROM prd_details
        JOIN product ON prd_details.prd_id = product.prd_id
        WHERE prd_details.prd_status = 'active' AND ((prd_details.prd_price - prd_details.prd_offer_price) / prd_details.prd_price * 100) < %s
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query, (last_prd_discount_percentage,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_product_after_id(mysql_cursor, last_prd_id, limit = 5):
    """
    This method select products base on last_prd_id
    :return: List in format [(id, prd_name, prd_status, prd_price, prd_offer_price,prd_image , prd_quantity, prd_sku, prd_date, prd_level, prd_cost, prd_preorders_status, prd_id, merchant_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        query = """
        SELECT product.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id
        FROM prd_details
        JOIN product ON prd_details.prd_id = product.prd_id
        WHERE prd_details.prd_status = 'active' AND product.id > %s
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query, (last_prd_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_product_before_id(mysql_cursor, last_prd_id, limit = 5):
    """
    This method select products base on last_prd_id
    :return: List in format [(id, prd_name, prd_status, prd_price, prd_offer_price,prd_image , prd_quantity, prd_sku, prd_date, prd_level, prd_cost, prd_preorders_status, prd_id, merchant_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        query = """
        SELECT product.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id
        FROM prd_details
        JOIN product ON prd_details.prd_id = product.prd_id
        WHERE prd_details.prd_status = 'active' AND product.id < %s
        ORDER BY product.prd_fame DESC
        LIMIT {}
        """.format(limit)

        mysql_cursor.execute(query, (last_prd_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)

def get_product_gallery(mysql_cursor, product_id, language = None):
    """
    This method select products base on last_prd_id
    :return: List in format [(id, prd_image, prd_lang, prd_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        if language == None:
            query = """
            SELECT id, prd_image, prd_lang, prd_id
            FROM prd_gallery
            WHERE prd_id = %s
            """
            mysql_cursor.execute(query, (product_id,))
        else:
            query = """
            SELECT id, prd_image, prd_lang, prd_id 
            FROM prd_gallery
            WHERE prd_id = %s AND prd_lang = %s
            """
            mysql_cursor.execute(query, (product_id, language))

        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return e
    
def get_recommended_products(mysql_cursor, current_product_id, limit = 5):
    """
    This method select recomended products from database; For now we select the highest discount
    :return: List in format [(id, prd_image, prd_lang, prd_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        query = """
        SELECT product.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id
        FROM prd_details
        JOIN product ON prd_details.prd_id = product.prd_id
        WHERE prd_details.prd_status = 'active' AND NOT product.prd_id = %s
        ORDER BY product.prd_fame DESC
        LIMIT {}
        """.format(limit)
        mysql_cursor.execute(query, (current_product_id,))

        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return e
    
def get_product_variations(mysql_cursor, product_id):
    """
    This method get the variation for a product
    :return: List in format [(prd_var.prd_var, prd_var.prd_var_des, prd_var.prd_var_price, 
            prd_var.prd_var_quantity, prd_var.prd_var_sku, prd_var.prd_var_img, prd_var.prd_var_cat_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        query = """
        SELECT prd_var.id, prd_var.prd_var, prd_var.prd_var_des, prd_var.prd_var_price, 
            prd_var.prd_var_quantity, prd_var.prd_var_sku, prd_var.prd_var_img, prd_var.prd_var_cat_id
        FROM prd_var
        JOIN prd_var_cat ON prd_var_cat.id = prd_var.prd_var_cat_id
        WHERE prd_var_cat.prd_id = %s
        """
        mysql_cursor.execute(query, (product_id,))

        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return e
    
def get_video(mysql_cursor, product_id, language = None):
    """
    This method get the prd_video for a product
    :return: List in format [(id, prd_video_url, prd_lang, prd_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        if language == None:
            query = """
            SELECT id, prd_video_url, prd_lang, prd_id
            FROM prd_video
            WHERE prd_id = %s
            """
            mysql_cursor.execute(query, (product_id,))
        else:
            query = """
            SELECT id, prd_video_url, prd_lang, prd_id
            FROM prd_video
            WHERE prd_id = %s AND prd_lang = %s
            """
            mysql_cursor.execute(query, (product_id,language))

        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return e
    
#=========================================================================
#SELECT
#==========================================================
def select_product(mysql_cursor, product_id):
    """
    This method select products by prd_id
    :return: List in format [(product.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id)]; [] otherwise.
    """
    try:
        use_db(mysql_cursor, "product")
        query = """
        SELECT product.id, prd_details.prd_name, prd_details.prd_status, prd_details.prd_price, prd_details.prd_offer_price, prd_details.prd_image ,\
            prd_details.prd_quantity, prd_details.prd_sku, prd_details.prd_date, prd_details.prd_level, prd_details.prd_cost , prd_details.prd_preorders_status,\
            prd_details.prd_id, product.merchant_id
        FROM prd_details
        JOIN product ON prd_details.prd_id = product.prd_id
        WHERE product.prd_id = %s
        """

        mysql_cursor.execute(query, (product_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)
    
def select_product_variation(mysql_cursor, product_variation_index_id):
    """
    This method select products by prd_id
    :return: List in format [(id, prd_var, prd_var_des, prd_var_price, prd_var_quantity, prd_var_sku , prd_var_img, prd_var_cat_id)]; [] otherwise.
    """
    try:

        use_db(mysql_cursor, "product")
        query = """
        SELECT id, prd_var, prd_var_des, prd_var_price, prd_var_quantity, prd_var_sku , prd_var_img, prd_var_cat_id
        FROM prd_var
        WHERE id = %s
        """

        mysql_cursor.execute(query, (product_variation_index_id,))
        result = mysql_cursor.fetchall()
        num_result = len(result)
        if num_result > 0:
            return result
        return []
    except Exception as e:
        return str(e)