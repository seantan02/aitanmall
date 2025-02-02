import random
import datetime
from webApp.mysql_connector import use_db

def OTP_regenation_permitted(mysql_cursor, phone_number, current_datetime):
    use_db(mysql_cursor, "user")
    query = """
    SELECT user_otp,user_otp_end_datetime FROM user_otp WHERE user_otp_phone_number = %s
    """
    mysql_cursor.execute(query, (phone_number,))
    result = mysql_cursor.fetchall()
    num_result = len(result)
    #no OTP yet so yea we can send new OTP
    if(num_result <= 0):
        return True
    elif(num_result  == 1):
        current_datetime = datetime.datetime.strptime(str(current_datetime), '%Y-%m-%d %H:%M:%S')
        user_otp_end_datetime = datetime.datetime.strptime(str(result[0][1]), '%Y-%m-%d %H:%M:%S')
        if current_datetime >=  user_otp_end_datetime:
            return True
    #more than 1 otp for phone number will cause issues
    else:
        return False
    #return False if none cases are true
    return False

def generate_unique_OTP(mysql_cursor, phone_number) -> int:
    use_db(mysql_cursor, "user")
    query = """
    SELECT user_otp FROM user_otp WHERE user_otp_phone_number = %s
    """
    mysql_cursor.execute(query, (phone_number,))
    num_result = mysql_cursor.rowcount
    result = mysql_cursor.fetchone()
    #no OTP yet so yea we can send new OTP
    new_otp = random.randint(1000000, 9999999)
    while(num_result == 1 and result.user_otp == new_otp):
        new_otp = random.randint(1000000, 9999999)
    
    return new_otp

def remove_old_OTP(db_conn, mysql_cursor, phone_number) -> bool:
    use_db(mysql_cursor, "user")
    query = """
    DELETE FROM user_otp WHERE user_otp_phone_number = %s
    """
    try:
        mysql_cursor.execute(query, (phone_number,))
        num_result = mysql_cursor.rowcount #useless but nice to define
        db_conn.commit()

        if num_result >= 0:
            return True
    except:
        return False
    
    return False

def insert_new_OTP(db_conn, mysql_cursor, unique_otp, start_datetime, end_datetime, phone_number,) -> bool:
    use_db(mysql_cursor, "user")
    query = """
    INSERT INTO user_otp (user_otp,user_otp_start_datetime,user_otp_end_datetime,user_session_id,user_otp_phone_number) 
    VALUES (%s,%s,%s,%s,%s)
    """
    try:
        mysql_cursor.execute(query, (unique_otp, start_datetime, end_datetime, "s", phone_number))
        num_result = mysql_cursor.rowcount #useless but nice to define
        db_conn.commit()

        if num_result == 1:
            return True
    except:
        return False
    
    return False

def OTP_user_verify(otp_to_compare, mysql_cursor, phone_number, current_datetime) -> bool:
    use_db(mysql_cursor, "user")
    query = """
    SELECT user_otp FROM user_otp WHERE user_otp_phone_number = %s AND user_otp_end_datetime >= %s
    """
    mysql_cursor.execute(query, (phone_number, current_datetime))
    result = mysql_cursor.fetchall()
    #no OTP yet so yea we can send new OTP
    if(len(result) <= 0):
        return False
    elif(len(result) == 1):
        user_otp = result[0][0]
        if user_otp == otp_to_compare:
            return True
    else:
        return result