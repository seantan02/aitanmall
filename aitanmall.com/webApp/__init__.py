from flask import Flask, render_template, request, session

def create_app():
    app = Flask(__name__)
    
    app.config["DOMAIN_NAME"] = "https://aitanmall.com"
    app.config["WEBSOCKET_URI"] = "socket.aitanmall.com"
    app.config['SECRET_KEY'] = "6a900693bc86211512315111254096asd156aw1156125631256da61bc7a8"
    @app.before_request
    def check_for_maintenance():
        whitelist = ['2607:fb91:22cb:41a5:a5f7:3665:dbec:a78e']
        secret_token = "ASBDNIUwuqijnunui120buawdbuas456daw15616w156a156awdbdBDawd15185112312h9db"
        maintenaince_mode = False
        if maintenaince_mode:
            if is_webhook_request(request):
                pass
            elif request.remote_addr not in whitelist:
                return render_template('maintenance.html', ip = request.remote_addr)
            else:
                if request.args.get("token") == secret_token:
                    session["is_admin"] = True
                else:
                    if session.get("is_admin") != True:
                        return render_template('maintenance.html', ip = request.remote_addr)
            
    def is_webhook_request(request):
        # Implement your logic to identify webhook requests
        # You can check for specific paths, headers, or any other criteria
        # In this example, we assume webhook requests have a specific path prefix
        return request.path.startswith('/webhooks')

    # Import and register blueprints for main domain
    from webApp.views.shared import shared
    from webApp.views.api.api import api
    from webApp.views.api.stripe import stripe_api
    from webApp.views.user import user
    from webApp.views.guest import guest
    from webApp.views.test import test
    from webApp.views.tracking import tracking
    from webApp.views.webhooks.stripe.router import stripe_webhook
    from webApp.views.webhooks.chat.router import chat_webhook
    from webApp.views.webhooks.toyyibpay.online_banking import toyyibpay_ob
    from webApp.views.webhooks.twilio.router import twilio_webhook
    from webApp.views.webhooks.ninjavan.router import ninjavan_webhook

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(shared, url_prefix="/")
    app.register_blueprint(stripe_api, url_prefix="/api/stripe")
    app.register_blueprint(user, url_prefix="/user")
    app.register_blueprint(guest, url_prefix="/guest")
    app.register_blueprint(test, url_prefix="/test")
    app.register_blueprint(tracking, url_prefix="/tracking")
    app.register_blueprint(stripe_webhook, url_prefix="/webhooks/stripe")
    app.register_blueprint(chat_webhook, url_prefix="/webhooks/chat")
    app.register_blueprint(toyyibpay_ob, url_prefix="/webhooks/toyyibpay/online_banking")
    app.register_blueprint(twilio_webhook, url_prefix="/webhooks/twilio")
    app.register_blueprint(ninjavan_webhook, url_prefix="/webhooks/ninjavan")

    return [app]

apps = create_app()
app = apps[0]