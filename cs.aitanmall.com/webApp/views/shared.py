from flask import Blueprint, render_template, session, redirect
from webApp.helper import cs
from webApp.helper import general
from webApp.mysql_connector import use_db, close_mysql_conn, close_mysql_cursor

shared = Blueprint("shared", __name__, static_folder="static", template_folder="templates")

@shared.route("home")
@shared.route("")
def home():
    try:
        session.clear()
        response = render_template("index.html")
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        use_db(db_conn_cursor, "customer_service")
        if general.cookie_exist("cs_id") and general.cookie_exist("temporarily_key"):
            cs_id_cookie = general.get_cookie("cs_id")
            temporarily_key_cookie = general.get_cookie("temporarily_key")

            if cs.user_temporarily_key_exist(db_conn_cursor,cs_id_cookie):
                current_time = general.get_current_datetime()
                if cs.log_in_cookie_is_valid(db_conn_cursor,temporarily_key_cookie,cs_id_cookie,current_time):
                    assert cs.log_in_cs(db_conn_cursor,cs_id_cookie), "Fail to log user in with cookie"
                    response = redirect('/dashboard')
    except Exception as e:
        response = str(e)
    finally:
        return response