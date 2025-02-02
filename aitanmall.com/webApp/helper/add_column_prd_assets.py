import os
from webApp import mysql_connector
from webApp.helper.json_tools import read_json
from webApp.helper.search_engine import primary_language_cortex as lc1

#if we should run the script
should_run = False

if should_run == True:
    #database information
    json_data = read_json("/var/www/aitanmall.com/private/data/databases.json")
    assets_db = json_data["assets"]
    assets_db_username = assets_db["username"]
    assets_db_host = assets_db["host"]
    assets_db_password = assets_db["password"]
    assets_db_database = assets_db["database"]
    #connect to database
    db_conn = mysql_connector.create_mysql_conn(assets_db_username,\
        assets_db_password, assets_db_host)
    db_conn_cursor = db_conn.cursor()
    mysql_connector.use_db(db_conn_cursor,assets_db_database)
    query = """
    SELECT prd_id,prd_name FROM product
    """
    db_conn_cursor.execute(query)
    assets_prd_data_list = list(db_conn_cursor)
    db_conn_cursor.close()
    #read language detection mapping
    language_detection_map_path = os.path.join("/var","www/aitanmall.com"\
        ,"private","data","language_detection_map.json")
    language_detected_dict = read_json(language_detection_map_path)
    #initiate lingua
    languages_detectable = lc1.get_lingua_languages()
    #now we are ready to detect language
    #loop through each prod data and assign them a language
    for data in assets_prd_data_list:
        prd_id = data[0]
        prd_name = data[1]
        prd_name_language = lc1.detect_language(languages_detectable,prd_name)
        prd_name_language = language_detected_dict[prd_name_language]
        db_conn_cursor = db_conn.cursor()
        mysql_connector.use_db(db_conn_cursor, "merchant_"+str(data[0]))
        query = """
        UPDATE product SET lang = {} WHERE prd_id = {}
        """
        db_conn_cursor.execute(query, (prd_name,prd_id))
        db_conn.commit()
        db_conn_cursor.close()
    db_conn.close()