from webApp.helper import user
from webApp.helper import stripe as strp
from webApp.helper import general
from webApp.mysql_connector import use_db, close_mysql_cursor, create_mysql_conn

def handle_payment_method_attached(event):
    try:
        data_object = event["data"]["object"]
        type = data_object["type"]
        if type == "card":
            stripe_payment_id = data_object["id"]
            customer_id = data_object["customer"]
            card = data_object["card"]
            card_brand = card["brand"]
            card_exp_month = card["exp_month"]
            card_exp_year = card["exp_year"]
            card_last4 = card["last4"]
            card_holder = "unknown"
            card_holder = data_object["billing_details"]["name"]
            #connect to mysql
            db_conn = general.create_general_mysql_conn()
            db_conn_cursor = db_conn.cursor()
            #get user id
            user_id = user.get_user_id_from_stripe_customer_id(db_conn_cursor,customer_id)
            if user.user_specific_has_default_payment_method(db_conn_cursor, user_id):
                payment_method_status = "backup"
            else:
                payment_method_status = "default"
            return user.user_specific_record_payment_method_card(db_conn, db_conn_cursor, user_id, stripe_payment_id, customer_id, card_brand,\
                card_last4, card_exp_month, card_exp_year, card_holder, payment_method_type = "card", status = payment_method_status)
        return False
    except Exception as e:
        return False
    finally:
        if db_conn_cursor:
            close_mysql_cursor(db_conn_cursor)
        if db_conn:
            close_mysql_cursor(db_conn)


def handle_payment_method_detached(event):
    try:
        data = event["data"]
        data_object = data["object"]
        stripe_payment_id = data_object["id"]
        customer_id = data["previous_attributes"]["customer"]
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        #change cursor to user database
        use_db(db_conn_cursor, "user")
        #get user id
        user_id = user.get_user_id_from_stripe_customer_id(db_conn_cursor,customer_id)
        user_payment_method_id = user.stripe_payment_method_exist(db_conn_cursor,stripe_payment_id,customer_id)
        assert user_payment_method_id != None, "Payment method ID not exist"
        assert user.user_specific_remove_stripe_payment_method(db_conn, db_conn_cursor, user_id, user_payment_method_id), "User payment method not removed"
        return True
    except Exception as e:
        return str(e)
    finally:
        if db_conn_cursor:
            close_mysql_cursor(db_conn_cursor)
        if db_conn:
            close_mysql_cursor(db_conn)