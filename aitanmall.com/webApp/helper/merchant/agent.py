from flask import session

def log_in():
    session["is_customer_service"] = True
    session["general_cs_name"] = "John Cena"

def log_out():
    try:
        if "is_customer_service" in session:
            del session["is_customer_service"]
        if "general_cs_name" in session:
            del session["general_cs_name"]
        return True
    except Exception as e:
        return False