from flask import Blueprint, render_template, session, redirect
from webApp.helper import cs
from webApp.helper import general
from webApp.mysql_connector import use_db, close_mysql_conn, close_mysql_cursor

dashboard = Blueprint("dashboard", __name__, static_folder="static", template_folder="templates")

@dashboard.route("")
@dashboard.route("/")
def home():
    try:
        assert session.get("cs_logged_in") == True, "Log in please"
        session["websocket_api_key"] = "u17828bdabd1782gdbaudsbaby1812b"
        response = render_template("main/chat.html")
    except Exception as e:
        response = render_template("error.html", msg = e)
    finally:
        return response
    
@dashboard.route("/create_orders")
@dashboard.route("/create_orders/")
def create_orders():
    try:
        response = "TRUE"
    except Exception as e:
        response = render_template("error.html", msg = e)
    finally:
        return response