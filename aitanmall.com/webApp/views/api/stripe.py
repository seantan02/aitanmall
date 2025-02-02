from flask import Blueprint, jsonify, current_app
from webApp.helper import stripe

stripe_api = Blueprint("stripe_api", __name__, static_folder=None, template_folder=None)

@stripe_api.route("create_customer", methods=["POST"])
def stripe_create_customer():
    try:
        test_key = stripe.get_key()
        customer_created = stripe.create_customer(test_key)
        msg = customer_created["id"]
    except Exception as e:
        msg = str(e)
    return jsonify({"msg":msg})