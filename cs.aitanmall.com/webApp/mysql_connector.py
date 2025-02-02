from flask import request
import mysql.connector as mysqlconnector

def create_mysql_conn(db_user, db_pass, db_name=None):
    """
    This method creates a mysql connection
    :param db_user: MYSQL user
    :param db_pass: MYSQL password
    :param db_name: MYSQL database name; None by default
    :return: Mysql object or None
    """
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

def set_up_cs_database(db_conn):
    sql_file_path = "/var/www/cs.stage-aitanmall.tech/backups/database/customer_service.sql"
    execute_sql_file(sql_file_path, db_conn, "customer_service")

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
