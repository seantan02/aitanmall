from webApp.helper import general
from webApp.helper import user
from webApp.mysql_connector import use_db, close_mysql_conn, close_mysql_cursor

def handle_customer_subscription_created(event) -> Exception | bool:
    try:
        data = event["data"]
        data_object = data["object"]
        customer_id = data_object["customer"]
        stripe_subscription_id = data_object["id"]
        object_type = data_object["object"]
        items = data_object["items"]
        items_data = items["data"][0]
        product_id = items_data["price"]["product"]
        price_id = items_data["price"]["id"]
        if object_type == "subscription":
            #connect to mysql
            db_conn = general.create_general_mysql_conn()
            db_conn_cursor = db_conn.cursor()
            subscription_data = user.get_subscription_product_from_stripe_id(db_conn_cursor, product_id, price_id)
            subscription_product_id = subscription_data[0][1]
            subscription_product_name = subscription_data[0][2]
            subscription_product_nku = subscription_data[0][3]
            subscription_product_interval = subscription_data[0][4]
            subscription_product_count = subscription_data[0][5]
            subscription_product_trial_period = subscription_data[0][6]
            subscription_product_price = subscription_data[0][7]
            if subscription_product_interval == "month":
                subscription_interval = 2628288
            elif subscription_product_interval == "year":
                subscription_interval = 31536000
            #get user id
            user_id = user.get_user_id_from_stripe_customer_id(db_conn_cursor, customer_id)
            user_subscription_data = user.get_subscription(db_conn_cursor, user_id, subscription_product_id, by_product_id=True)

            if user_subscription_data != None:
                user_subscription_id = user_subscription_data[0][1]
                user_subscription_status = user_subscription_data[0][2]
                user_subscription_start_date = user_subscription_data[0][3]
                user_subscription_bill_start_date = user_subscription_data[0][4]
                user_subscription_end_date = user_subscription_data[0][5]
                
                assert user_subscription_status == "cancelled", "System error"
                assert user.update_subscription_status(mysql_conn=db_conn, mysql_cursor=db_conn_cursor,\
                    status="active",user_id= user_id, user_subscription_id=user_subscription_id) == True,\
                    "User subscription not updated"
                assert user.update_membership_status(mysql_conn = db_conn, mysql_cursor = db_conn_cursor,\
                    status = "active", user_id = user_id, user_membership_id=None, subscription_product_nku=subscription_product_nku,\
                    by_id = False, by_nku= True) == True,"User membership not updated"
                assert user.create_stripe_subscription(db_conn, db_conn_cursor,stripe_subscription_id,product_id,subscription_product_id,customer_id,user_subscription_id) == True, "Stripe subscription not recorded"
                return True
            #if it is first webhook then we record stripe subscription into database
            else:
                user_subscription_start_date = general.get_current_datetime()
                subscription_free_trial = int(subscription_product_trial_period)
                user_subscription_bill_start_date = general.get_datetime_from_now(subscription_free_trial*24*60*60)
                user_subscription_end_date = general.get_datetime_from_now(subscription_free_trial*24*60*60+subscription_interval)
                user_subscription_id = user.create_user_subscription(db_conn,db_conn_cursor,"active", user_subscription_start_date, user_subscription_bill_start_date, user_subscription_end_date, subscription_product_id, user_id)
                assert user_subscription_id != None, "Subscription ID not created"
                user_membership_id = user.create_user_membership(db_conn,db_conn_cursor,subscription_product_name,subscription_product_nku,"active",user_subscription_start_date, user_subscription_end_date,user_id)
                assert user_membership_id != None, "Membership ID not created"
                assert user.create_stripe_subscription(db_conn, db_conn_cursor,stripe_subscription_id,product_id,subscription_product_id,customer_id,user_subscription_id) == True, "Stripe subscription not recorded"
                return True

        return False
    except Exception as e:
        return str(e)
    finally:
        if 'db_conn_cursor' in locals():
            close_mysql_cursor(db_conn_cursor)
        if 'db_conn' in locals():
            close_mysql_cursor(db_conn)

def handle_customer_subscription_updated(event) -> Exception | bool:
    try:
        data = event["data"]
        data_object = data["object"]
        object_type = data_object["object"]
        stripe_subscription_id = data_object["id"]
        stripe_customer_id = data_object["customer"]
        subscription_plan = data_object["plan"]
        subscription_price_id = subscription_plan["id"]
        subscription_product_id = subscription_plan["product"]
        stripe_subscription_cancel_details = data_object["cancellation_details"]
        stripe_subscription_cancel_reason = stripe_subscription_cancel_details["reason"]
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        
        if object_type == "subscription" and stripe_subscription_cancel_reason == "cancellation_requested":
            #get user id
            user_id = user.get_user_id_from_stripe_customer_id(db_conn_cursor,stripe_customer_id)
            stripe_subscription_data = user.get_stripe_subscription(db_conn_cursor, stripe_subscription_id, stripe_customer_id, by_customer_id=True)
            assert isinstance(stripe_subscription_data, list), "System failed to find stripe subscription data"
            user_subscription_id = stripe_subscription_data[0][5]
            subscription_product_data = user.get_subscription_product_from_stripe_id(db_conn_cursor, subscription_product_id, subscription_price_id)
            subscription_product_nku = subscription_product_data[0][3]
            assert user.update_subscription_status(mysql_conn=db_conn, mysql_cursor=db_conn_cursor,\
                    status="cancelled",user_id= user_id, user_subscription_id=user_subscription_id) == True, "User subscription not updated"
            assert user.update_membership_status(mysql_conn = db_conn, mysql_cursor = db_conn_cursor,\
                    status = "cancelled", user_id = user_id, user_membership_id=None, subscription_product_nku=subscription_product_nku,\
                    by_id = False, by_nku= True) == True, "User membership not updated"
            return True
        return False
    except Exception as e:
        return str(e)
    finally:
        if db_conn_cursor:
            close_mysql_cursor(db_conn_cursor)
        if db_conn:
            close_mysql_cursor(db_conn)

def handle_customer_subscription_deleted(event) -> Exception | bool:
    try:
        data = event["data"]
        data_object = data["object"]
        object_type = data_object["object"]
        stripe_subscription_id = data_object["id"]
        stripe_customer_id = data_object["customer"]
        subscription_plan = data_object["plan"]
        subscription_price_id = subscription_plan["id"]
        subscription_product_id = subscription_plan["product"]
        stripe_subscription_cancel_details = data_object["cancellation_details"]
        stripe_subscription_cancel_reason = stripe_subscription_cancel_details["reason"]
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        
        if object_type == "subscription":
            user_id = user.get_user_id_from_stripe_customer_id(db_conn_cursor,stripe_customer_id)
            stripe_subscription_data = user.get_stripe_subscription(db_conn_cursor, stripe_subscription_id, stripe_customer_id, by_customer_id=True)
            assert isinstance(stripe_subscription_data, list), "System failed to find stripe subscription data"
            user_subscription_id = stripe_subscription_data[0][5]
            subscription_product_data = user.get_subscription_product_from_stripe_id(db_conn_cursor, subscription_product_id, subscription_price_id)
            subscription_product_nku = subscription_product_data[0][3]
            assert user.update_subscription_status(mysql_conn=db_conn, mysql_cursor=db_conn_cursor,\
                    status="cancelled",user_id= user_id, user_subscription_id=user_subscription_id) == True, "User subscription not updated"
            assert user.update_membership_status(mysql_conn = db_conn, mysql_cursor = db_conn_cursor,\
                    status = "cancelled", user_id = user_id, user_membership_id=None, subscription_product_nku=subscription_product_nku,\
                    by_id = False, by_nku= True) == True, "User membership not updated"
            assert user.update_stripe_subscription_status(mysql_conn = db_conn, mysql_cursor = db_conn_cursor,\
                status = "deleted", stripe_subscription_id=stripe_subscription_id, stripe_customer_id=stripe_customer_id) == True, "Stripe subscription not removed"
            return True
        return False
    except Exception as e:
        return str(e)
    finally:
        if db_conn_cursor:
            close_mysql_cursor(db_conn_cursor)
        if db_conn:
            close_mysql_conn(db_conn)