def handle_checkout_session_complete(event):
    data_object = event["data"]["object"]
    session_id = data_object["id"]
    object = data_object["object"]
    billing_address_collection = data_object["billing_address_collection"]
    cancel_url = data_object["cancel_url"]
    client_reference_id = data_object["client_reference_id"]
    customer = data_object["customer"]
    customer_email = data_object["customer_email"]
    mode = data_object["mode"]
    setup_intent = data_object["setup_intent"]
    success_url = data_object["success_url"]
    
    return True

def handle_checkout_session_payment_failed():
    return True

def handle_checkout_session_payment_succeeded():
    return True