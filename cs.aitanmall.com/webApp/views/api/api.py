from flask import Blueprint, jsonify, session, request, make_response
from webApp.helper import cs
from webApp.helper import websocket
from webApp.helper import general
import html
from webApp.mysql_connector import use_db, close_mysql_conn, close_mysql_cursor

api = Blueprint("api", __name__, static_folder=None, template_folder=None)

# websocket_connection = dict()

# API URL
# @api.route("general_cs_join_request", methods=["POST"])
# def general_cs_join_request():
#     try:
#         # global websocket_connections
#         msg = "ERROR"
#         redirect = ""
#         is_agent = session.get("is_agent")
#         agent_id = session.get("agent_id")
#         assert is_agent == True, "Agent is not verified"
#         api_key = "u17828bdabd1782gdbaudsbaby1812b"
#         response = jsonify({"passcheck":1, "api_key":api_key})
        # if agent_id not in websocket_connection:
        #     api_key = "u17828bdabd1782gdbaudsbaby1812b"
        #     websocket_uri = "wss://socket.stage-aitanmall.tech:59001"
        #     websocket_object = websocket.WebSocketClient(websocket_uri)
        #     websocket_object.connect()
        #     i = 0
        #     while i < 5:
        #         message = {"api_key":api_key}
        #         websocket_response = websocket_object.send_message(message)
        #         websocket_response = json.loads(websocket_response)
        #         websocket_event_type = websocket_response.get("event_type", None)
        #         websocket_message = websocket_response.get("message", None)
        #         if websocket_event_type == "verification":
        #             websocket_response = websocket_object.send_message(message)
        #         if websocket_event_type == "connected":
        #             websocket_object.send_message({"broadcast":True, "message":"Agent joined"})
        #             websocket_connection[agent_id] = websocket_object
        #             break
        #         i += 1
                
        #     response = jsonify({'event_type': websocket_event_type, 'message':websocket_message})
        # else:
        #     response = jsonify({'event_type':'connected'})
    # except Exception as e:
    #     passcheck = 3
    #     msg = str(e)
    #     response = jsonify({"response":msg})
    # finally:
        # if 'db_conn_cursor' in locals():
        #     close_mysql_cursor(db_conn_cursor)
        # if 'db_conn' in locals():
        #     close_mysql_cursor(db_conn)

        # return response
    
# @api.route("general_cs_websocket_send", methods=["POST"])
# def general_cs_websocket_send():
#     try:
#         global websocket_connection
#         msg = "ERROR"
#         passcheck = 2
#         redirect = ""
#         message = request.form["message"]
#         is_agent = session.get("is_agent")
#         agent_id = session.get("agent_id")
#         assert is_agent == True, "Agent is not verified"
#         if agent_id not in websocket_connection:
#             response = jsonify({'passcheck':passcheck,'event_type': "error", 'message':"please connect to websocket first"})
#         else:
#             websocket_object = websocket_connection
#             message = {"broadcast":True, "message":message}
#             x = json.load(websocket_object.send_message(message))
#             response = jsonify({'event_type':x})
#     except Exception as e:
#         passcheck = 3
#         msg = str(e)
#         response = jsonify({"response":msg})
#     finally:
#         # if 'db_conn_cursor' in locals():
#         #     close_mysql_cursor(db_conn_cursor)
#         # if 'db_conn' in locals():
#         #     close_mysql_cursor(db_conn)

#         return response

@api.route("login", methods=["POST"])
def general_cs_join_request():
    try:
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor()
        assert request.method == "POST", "REQUEST ERROR"
        # g_response = request.form["g-response"]
        # assert len(g_response) > 0, "REQUEST ERROR#2"
        # assert general.pass_recaptcha_v3_test(g_response), "REQUEST ERROR#3"
        username = html.escape(str(request.form["username"]))
        password = request.form["password"]
        #change cursor to user database
        use_db(db_conn_cursor, "customer_service")
        assert cs.user_log_in_details_is_valid(db_conn_cursor, username, password, verify_by="username"), "Username or Password incorrect"
        cs_id = cs.get_cs_id(db_conn_cursor, username, verify_by="username")
        assert cs_id != None, "Username invalid"
        assert cs.log_in_cs(db_conn_cursor, cs_id), "ERROR logging in user"
        #generate cookie for automatic login when user visit back
        random_string = general.generate_random_string(10)
        temporarily_key = cs.generate_temporarily_key(random_string)
        created_datetime = general.get_current_datetime()
        seconds_in_a_month = 2628288
        expire_datetime = general.get_datetime_from_now(seconds_in_a_month)
        if cs.user_temporarily_key_exist(db_conn_cursor, cs_id):
            assert cs.remove_user_temporarily_key(db_conn, db_conn_cursor, cs_id), "Old temporarily key not removed"
        assert cs.insert_user_temporarily_key(db_conn, db_conn_cursor, temporarily_key, created_datetime, expire_datetime, cs_id), "Temporarily key not recorded"
        passcheck = 1
        msg = "Welcome"
        response = jsonify({"passcheck":passcheck, "msg":msg, "temporarily_key": temporarily_key, "cs_id":cs_id})
    except Exception as e:
        passcheck = 3
        msg = str(e)
        response = jsonify({"passcheck":3, "msg":msg})
    finally:
        # if 'db_conn_cursor' in locals():
        #     close_mysql_cursor(db_conn_cursor)
        # if 'db_conn' in locals():
        #     close_mysql_cursor(db_conn)

        return response

@api.route("create_cs_temporarily_key", methods=["POST"])
def create_cs_temporarily_key():
    try:
        assert request.method == "POST", "ERROR#1"
        assert session.get("cs_logged_in") == True, "Customer service not authorized"
        temporarily_key = request.form["temporarily_key"]
        cs_id = request.form["customer_service_id"]

        # Create a response object
        response = make_response()
        seconds_in_a_month = 2628288
        # Set the cookie using the Set-Cookie header
        response.set_cookie(
            "temporarily_key",
            value=temporarily_key,
            max_age=seconds_in_a_month,
            secure=True,  # Set secure flag for HTTPS-only transmission
            httponly=True,  # Set HTTP-only flag to prevent JavaScript access
            samesite='Strict'  # Set SameSite attribute to 'Strict'
        )
        response.set_cookie(
            "cs_id",
            value=cs_id,
            max_age=seconds_in_a_month,
            secure=True,  # Set secure flag for HTTPS-only transmission
            httponly=True,  # Set HTTP-only flag to prevent JavaScript access
            samesite='Strict'  # Set SameSite attribute to 'Strict'
        )
    except:
        response = jsonify({"passcheck":3})
    return response