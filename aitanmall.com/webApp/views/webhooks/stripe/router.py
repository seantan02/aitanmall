from flask import Blueprint, jsonify, request
import stripe
from webApp.helper import stripe as strp
from webApp.views.webhooks.stripe.handlers import checkout as handler_checkout
from webApp.views.webhooks.stripe.handlers import payment as handler_payment
from webApp.views.webhooks.stripe.handlers import setup as handler_setup
from webApp.views.webhooks.stripe.handlers import subscription as handler_subscription

stripe_webhook= Blueprint("stripe_webhook", __name__, static_folder="static", template_folder="templates")

# webhook URL
@stripe_webhook.route("", methods=["POST"])
@stripe_webhook.route("/", methods=["POST"])
def handle_webhooks():
    try:
        event = None
        handler_status = False
        payload = request.data
        sig_header = request.headers['STRIPE_SIGNATURE']
        endpoint_secret = strp.get_webhook_scret_key()

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            raise e
        except Exception as e:
            # Invalid signature
            raise e

        # Handle the event
        event_type = event['type']

        if event_type == "checkout.session.completed":
            handler_status = handler_checkout.handle_checkout_session_complete(event)
        elif event_type == "checkout.session.async_payment_failed":
            handler_status = handler_checkout.handle_checkout_session_payment_failed(event)
        elif event_type == "checkout.session.async_payment_succeeded":
            handler_status = handler_checkout.handle_checkout_session_payment_succeeded(event)
        elif event_type == "payment_method.attached":
            handler_status =handler_payment.handle_payment_method_attached(event)
        elif event_type == "payment_method.detached":
            handler_status =handler_payment.handle_payment_method_detached(event)
        elif event_type == "setup_intent.succeeded":
            handler_status =handler_setup.handle_setup_intent_succeeded(event)
        elif event_type == "customer.subscription.created":
            handler_status = handler_subscription.handle_customer_subscription_created(event)
        elif event_type == "customer.subscription.updated":
            handler_status = handler_subscription.handle_customer_subscription_updated(event)
        elif event_type == "customer.subscription.deleted":
            handler_status = handler_subscription.handle_customer_subscription_deleted(event)

        return jsonify({"success":True, "handler_status":handler_status})
    except Exception as e:
        return jsonify({"success":False, "handler_status":str(e)})