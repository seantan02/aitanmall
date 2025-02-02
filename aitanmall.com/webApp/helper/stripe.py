import stripe
from webApp.helper import json_tools

# GET & EXIST FUNCTIONS!!!!!!!!!!
# GET & EXIST FUNCTIONS!!!!!!!!!!
# GET & EXIST FUNCTIONS!!!!!!!!!!
def get_test_key():
    test_key_path = "/var/www/aitanmall.com/private/stripe/test_key.txt"
    test_key_file = open(test_key_path, 'r')
    test_key_file_content = test_key_file.read()
    test_key_file.close()
    return str(test_key_file_content)

def get_key():
    test_key_path = "/var/www/aitanmall.com/private/stripe/secret_key.txt"
    test_key_file = open(test_key_path, 'r')
    test_key_file_content = test_key_file.read()
    test_key_file.close()
    return str(test_key_file_content)

def get_test_webhook_scret_key():
    webhook_scret_key_path = "/var/www/stage-aitanmall.tech/private/stripe/webhook_test_endpoint_secret.txt"
    webhook_scret_key_file = open(webhook_scret_key_path, 'r')
    webhook_scret_key_content = webhook_scret_key_file.read()
    webhook_scret_key_file.close()
    return str(webhook_scret_key_content)

def get_webhook_scret_key():
    webhook_scret_key_path = "/var/www/aitanmall.com/private/stripe/webhook_endpoint_secret.txt"
    webhook_scret_key_file = open(webhook_scret_key_path, 'r')
    webhook_scret_key_content = webhook_scret_key_file.read()
    webhook_scret_key_file.close()
    return str(webhook_scret_key_content)

def customer_exist(api_key, user_email) -> bool:
    stripe.api_key = api_key

    customer_list = stripe.Customer.list(email=user_email)
    if len(customer_list["data"]) > 0:
        return True
    return False

def customer_payment_method_exist(api_key, stripe_customer_id, type = None)->bool:
    stripe.api_key = api_key

    customer_payment_method_list = stripe.PaymentMethod.list(
        customer=stripe_customer_id,
        type=type,
    )
    if len(customer_payment_method_list["data"]) > 0:
        return True
    return False

def price_id_valid(api_key, option_id)->bool:
    stripe.api_key = api_key

    price_id_response = stripe.Price.retrieve(
    option_id,
    )
    if(price_id_response["object"] == "price"):
        return price_id_response["active"]
    return False

def get_country_code(country_name):
    country_code_dict = json_tools.read_json("/var/www/aitanmall.com/private/stripe/country_code.json")
    try:
        return country_code_dict[country_name]
    except Exception as e:
        return None
    
def get_customer_payment_methods(api_key, stripe_customer_id, type = None):
    """
    This method gets customer's list of payment methods
    :param customer_id: The customer id for stripe stored in databse user
    :param type: Type of payment methods looking for
    :raises Exception: If any process in between goes wrong
    :return: JSON object from Stripe
    """
    
    stripe.api_key = api_key

    customer_payment_method_list = stripe.PaymentMethod.list(
        customer=stripe_customer_id,
        type=type,
    )
    if len(customer_payment_method_list["data"]) > 0:
        return customer_payment_method_list
    return None

def get_price(api_key, option_id)->bool:
    stripe.api_key = api_key

    price_id_response = stripe.Price.retrieve(
    option_id,
    )
    if(price_id_response["object"] == "price"):
        return price_id_response
    return False

# MUTATOR FUNCTIONS!!!!!!!!!!
# MUTATOR FUNCTIONS!!!!!!!!!!
# MUTATOR FUNCTIONS!!!!!!!!!!

def create_customer(api_key, name, phone_number, email, customer_address_dict = None):
    """
    This method create stripe customer and return response in json
    :raises Exception: If any process in between goes wrong
    :return: a json response in format of {id, object, address, balance, created, currency, default_source}
    """

    try:
        stripe.api_key = api_key

        customer_created = stripe.Customer.create(
            name = name,
            phone = "+"+str(phone_number),
            email = email,
            address = customer_address_dict,
            description="My First Test Customer (created for API docs at https://www.stripe.com/docs/api)",
        )
        return customer_created
    except Exception as e:
        return e

def set_up_payments(api_key, customer_id, success_url, cancel_url) -> bool:
    """
    This method set up future payments for customer
    :param success_url: The url to redirect upon successful action. PLEASE DO NOT GIVE ANY GET PARAMETERS. ONLY THE LINK.
    :param cancel_url: The url that you want to redirect upon failed action.
    :raises Exception: If any process in between goes wrong
    :return: Session object if no exception thrown; False otherwise.
    """

    try:
        stripe.api_key = api_key

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='setup',
            customer=customer_id,
            success_url=success_url+'?session_id={CHECKOUT_SESSION_ID}&type=stripe',
            cancel_url=cancel_url+'?session_id={CHECKOUT_SESSION_ID}&type=stripe',
        )
        return session
    except Exception as e:
        return e

def create_portal_session(api_key, customer_id, return_url):
    """
    This method create a portal session for customer linked to stripe
    :param api_key: Stripe api_scret_key
    :param customer_id: User's customer ID with stripe
    :param return_url: Return url
    :raises Exception: If any process in between goes wrong
    :return: Session object if no exception thrown; False otherwise.
    """

    try:
        stripe.api_key = api_key

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session
    except Exception as e:
        return e
    
def create_subscription_checkout(api_key, customer_id, item_list, success_url, cancel_url, trial_end):
    """
    This method create a payment link for customer
    :param item_list: list of item in format: [{"price": PRICE_ID, "quantity":QUANTITY},....]
    :param success_url: The url to redirect upon successful action. PLEASE DO NOT GIVE ANY GET PARAMETERS. ONLY THE LINK.
    :param cancel_url: The url that you want to redirect upon failed action.
    :raises Exception: If any process in between goes wrong
    :return: Session object if no exception thrown; False otherwise.
    """

    try:
        stripe.api_key = api_key

        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            line_items=item_list,
            mode="subscription",
            success_url=success_url+'?session_id={CHECKOUT_SESSION_ID}&type=stripe',
            cancel_url=cancel_url ,
            subscription_data ={
                "trial_end":trial_end,
            },
        )
        return checkout_session
    except Exception as e:
        return e

def create_payment_link(api_key, customer_id, item_list, success_url, cancel_url):
    """
    This method create a payment link for customer
    :param item_list: list of item in format: [{"price": PRICE_ID, "quantity":QUANTITY},....]
    :param success_url: The url to redirect upon successful action. PLEASE DO NOT GIVE ANY GET PARAMETERS. ONLY THE LINK.
    :param cancel_url: The url that you want to redirect upon failed action.
    :raises Exception: If any process in between goes wrong
    :return: Session object if no exception thrown; False otherwise.
    """

    try:
        stripe.api_key = api_key

        payment_link = stripe.PaymentLink.create(
            line_items=item_list,
        )
        return payment_link
    except Exception as e:
        return e

def charge_customer(api_key, customer_id, payment_id, amount_in_cents:int):
    """
    This method create a charge for a customer that has a payment intent linked.
    :param customer_id: Stripe customer ID
    :param payment_id: Stripe customer's payment intent ID
    :raises Exception: If any process in between goes wrong
    :return: the payment_intent object
    """
    try:
        stripe.api_key = api_key
        payment_intent = stripe.PaymentIntent.create(
            customer= customer_id,
            payment_method= payment_id,
            amount=amount_in_cents,
            currency="myr",
            confirm=True,
        )
        return payment_intent
    except Exception as e:
        return e