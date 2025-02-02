from flask import Blueprint, render_template, session
from webApp.helper import cs
from webApp.helper import general
from webApp import mysql_connector
from passlib.hash import sha256_crypt

test = Blueprint("test", __name__, static_folder="static", template_folder="templates")

@test.route("mysql")
def mysql():
    DEVELOP_MODE = False
    if DEVELOP_MODE:
        try:
            db_conn = general.create_general_mysql_conn()
            mysql_connector.set_up_cs_database(db_conn)
            response = "Yes"
        except Exception as e:
            response = str(e)
        finally:
            if 'db_conn' in locals():
                mysql_connector.close_mysql_cursor(db_conn)
            return response
    else:
        render_template("error.html")

@test.route("create_cs")
def create_cs():
    DEVELOP_MODE = False
    if DEVELOP_MODE:
        try:
            db_conn = general.create_general_mysql_conn()
            db_cursor = db_conn.cursor()
            mysql_connector.use_db(db_cursor, "customer_service")
            
            username = "testing"
            password = "abcd1234"
            password = sha256_crypt.encrypt(password)
            email = "testing@gmail.com"
            if cs.create_account(db_conn,db_cursor,username,email,"60","1982818283", password, "Nadia", "Nur"):
                response = "Customer service created"
            else:
                response = "Failed to create Customer Service"
        except Exception as e:
            response = str(e)
        finally:
            if 'db_cursor' in locals():
                mysql_connector.close_mysql_cursor(db_cursor)
            if 'db_conn' in locals():
                mysql_connector.close_mysql_cursor(db_conn)
            return response
    else:
        render_template("error.html")


