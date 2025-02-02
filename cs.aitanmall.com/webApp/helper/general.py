from flask import request, make_response
import random
import string
from webApp.helper import json_tools
from webApp import mysql_connector
import datetime

def tokenize(string):
    if isinstance(string, str):
        list_to_return = list()
        tokenized_string = [char for char in string]
        list_to_return += tokenized_string
                
    else:
        raise Exception("Only list can be tokenized")
    return list_to_return

def get_response_recaptcha_v3(g_response) -> object:
    #import module needed
    from flask import request
    from requests import post

    g_response_url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': '6Le5uQwkAAAAALD4RMkZ7aVRnKeXaublVihETczh',
        'response': g_response,
        'remoteip': request.remote_addr,
    }
    g_response_verification = post(g_response_url, data=data)
            
    return g_response_verification.json()

def pass_recaptcha_v3_test(g_response) -> bool:
    #import module needed
    from flask import request
    from requests import post

    g_response_url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': '6Le5uQwkAAAAALD4RMkZ7aVRnKeXaublVihETczh',
        'response': g_response,
        'remoteip': request.remote_addr,
    }
    g_response_verification = post(g_response_url, data=data)
    g_response_result = g_response_verification.json()
            
    if g_response_result["success"] and g_response_result["score"] > 0.5:
        return True
    return False


def standardize_phone_number(phone_number, country_code = "60") -> str:
    if phone_number[:2] == "01":
        phone_number = country_code+phone_number[1:]
    elif phone_number[:2] != "60":
        phone_number = country_code+phone_number

    return phone_number

def create_general_mysql_conn():
    database_json = json_tools.read_json("/var/www/cs.stage-aitanmall.tech/private/data/databases.json")

    cs_db = database_json["customer_service"]
    db_username = cs_db["username"]
    db_password = cs_db["password"]
    #connect and return
    db_conn = mysql_connector.create_mysql_conn(db_username,db_password)
    return db_conn

def connect_to_cs_database():
    database_json = json_tools.read_json("/var/www/cs.stage-aitanmall.tech/private/data/databases.json")

    cs_db = database_json["customer_service"]
    cs_db_username = cs_db["username"]
    cs_db_password = cs_db["password"]
    cs_db_database = cs_db["database"]
    #connect and return
    db_conn = mysql_connector.create_mysql_conn(cs_db_username,cs_db_password,db_name = cs_db_database)
    db_conn_cursor = db_conn.cursor(prepared=True)
    return [db_conn,db_conn_cursor]

def cookie_exist(cookie_name) -> bool:
    if cookie_name in request.cookies:
        return True
    return False

def get_cookie(cookie_name):
    try:
        cookie_value = request.cookies.get(cookie_name)
        return cookie_value
    except:
        return None

def generate_random_string(length) -> str:
    try:
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string
    except:
        return None
    
def get_current_datetime():
    try:
        current_time = datetime.datetime.now()
        current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        return current_time
    except:
        return None

def get_datetime_from_now(seconds):
    try:
        new_expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        new_expiration_time = new_expiration_time.strftime('%Y-%m-%d %H:%M:%S')
        return new_expiration_time
    except:
        return None

def get_datetime_difference(datetime1, datetime2, absolute = False) -> Exception | int:
    try:
        datetime1 = datetime.datetime.strptime(datetime1, '%Y-%m-%d %H:%M:%S')
        datetime2 = datetime.datetime.strptime(datetime2, '%Y-%m-%d %H:%M:%S')

        difference = datetime2 - datetime1
        seconds = int(difference.total_seconds())
        if absolute:
            seconds = abs(seconds)

        return seconds
    except Exception as e:
        return e

def get_unix_datetime_from_now(seconds):
    try:
        current_datetime = datetime.datetime.now()

        # Increment the datetime by 1 hour
        incremented_datetime = current_datetime + datetime.timedelta(seconds=seconds)

        # Convert the incremented datetime to a Unix timestamp
        incremented_timestamp = int(incremented_datetime.timestamp())
        return incremented_timestamp
    except:
        return None
    
def make_str_datetime_object(datetime_string) -> None|datetime.datetime:

    try:
        return datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
    except:
        return None