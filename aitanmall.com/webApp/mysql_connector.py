from flask import request
import mysql.connector as mysqlconnector

def create_mysql_conn(db_user, db_pass, db_name=None):
        return mysqlconnector.connect(user=str(db_user), password=str(db_pass), \
            host = "127.0.0.1", database=db_name)
#print statement to show it's working
#methods
def create_database(db_conn, db_name):
    try:
        cursor = db_conn.cursor()
        cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
        cursor.close()
        return True
    except mysqlconnector.Error as err:
        raise Exception(err)

def use_db(cursor, db_name) -> bool:
    """
    Change current cursor to another database

    :param cursor: Any mysql_cursor .
    :param db_name: The name of mysql database.
    :raises Exception: If there's any error in mysql processes.
    :return: True if every runs.
    """
    query = "USE {}".format(db_name)
    cursor.execute(query)
    return True
        
def execute_sql_file(sql_file_path,db_conn,db_name):
    """
    Exceute sql file for a database; Create a database if database not found

    :param sql_file_path: Mysql sql file .
    :param db_conn: A mysql connection
    :param db_name: The name of mysql database.
    :raises Exception: If there's any error in mysql processes.
    :return: True if every runs.
    """

    try:
        create_database(db_conn, db_name)
    except:
        pass
    cursor = db_conn.cursor()
    use_db(cursor, db_name)
    #read sql
    sql_file = open(sql_file_path, mode='r', encoding='utf-8')
    sql_file_data = sql_file.read()
    sql_file_command = sql_file_data.split(';')
    for data in sql_file_command:
        try:
            cursor.execute(str(data))
            db_conn.commit()
        except:
            continue
    cursor.close()
    return True

def table_exist(db_conn,db_name,table_name):
    try:
        use_db(db_conn, db_name)
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM {} LIMIT 1".format(table_name))
        return True
    except Exception:
        return False
    finally:
        cursor.close()
    
def drop_database(db_conn,db_name):
    try:
        cursor = db_conn.cursor()
        cursor.query("DROP DATABASE {}".format(db_name))
        db_conn.commit()
    except mysqlconnector.Error as err:
        raise Exception(err)
    finally:
        cursor.close()
#TO TRANSFER MERCHANT DATABASE CODE BELOW# DO NOT UNCOMMENT!!!

def set_up_merchant_datebase(db_conn):
    for i in range(1,5):
        sql_file_path = "/var/www/stage-aitanmall.tech/backups/database/merchant.sql"
        db_name = "merchant_"+str(i)
        execute_sql_file(sql_file_path, db_conn, db_name)
        sql_file_path = "/var/www/stage-aitanmall.tech/backups/database/merchant_"+str(i)+"_data.sql"
        execute_sql_file(sql_file_path, db_conn, db_name)

def set_up_merchant_all_database(db_conn):
    #TO TRANSFER ASSETS DATABASE TO HERE
    sql_file_path = "/var/www/stage-aitanmall.tech/backups/database/merchant_all.sql"
    db_name = "merchant_all"
    execute_sql_file(sql_file_path, db_conn, db_name)

     #TO DELETE Merchant from 5 and above
    db_conn_cursor = db_conn.cursor()
    use_db(db_conn_cursor, "merchant_all")
    #delete everything from merchant 5 and above 
    query = """
    DELETE FROM merchant WHERE merchant_id >4
    """
    db_conn_cursor.execute(query)
    db_conn.commit()
    db_conn_cursor.close()

def set_up_assets_database(db_conn):
    #TO TRANSFER ASSETS DATABASE TO HERE
    sql_file_path = "/var/www/stage-aitanmall.tech/backups/database/assets.sql"
    db_name = "assets"
    execute_sql_file(sql_file_path, db_conn, db_name)

    # This is to DELETE ALL mercjhant 5 and above data
    db_conn_cursor = db_conn.cursor()
    use_db(db_conn_cursor, "assets")
    #delete everything from merchant 5 and above 
    query = """
    DELETE FROM orders WHERE merchant_id >4
    """
    db_conn_cursor.execute(query)
    db_conn.commit()
    query = """
    DELETE FROM product WHERE merchant_id >4
    """
    db_conn_cursor.execute(query)
    db_conn.commit()
    query = """
    DELETE FROM merchant_income WHERE merchant_id >4
    """
    db_conn_cursor.execute(query)
    db_conn.commit()
    query = """
    DELETE FROM merchant_top_up WHERE merchant_id >4
    """
    db_conn_cursor.execute(query)
    db_conn.commit()

    db_conn_cursor.close()
    #close our connection
    db_conn.close()

def set_up_user_database(db_conn):
    sql_file_path = "/var/www/stage-aitanmall.tech/backups/database/user.sql"
    execute_sql_file(sql_file_path, db_conn, "user")

def close_mysql_cursor(db_cursor) -> bool:
    try:
        if isinstance(db_cursor, mysqlconnector.cursor_cext.CMySQLCursor):
            db_cursor.close()
        return True
    except:
        return False
    
def close_mysql_conn(db_conn) -> bool:
    try:
        if isinstance(db_conn, mysqlconnector.cursor_cext.CMySQLConnection):
            db_conn.close()
        return True
    except:
        return False
