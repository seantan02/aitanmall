from flask import Flask, render_template, request, session

def create_app():
    app = Flask(__name__)
    app.config["SESSION_COOKIE_DOMAIN"] = False
    @app.before_request
    def check_for_maintenance():
        whitelist = ['2a0d:5600:43:5001::55f3']
        secret_token = "AUSduawdbu@U12bBWWABDIbuawdbuawbdadawdio12@YASBDW717231828dha7H@H1723bdBDHABHDBHAWBDdadaj12h3u12h9db"
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
    from webApp.views.dashboard import dashboard
    from webApp.views.api.api import api
    from webApp.views.test import test
    
    app.register_blueprint(shared, url_prefix="/")
    app.register_blueprint(dashboard, url_prefix="/dashboard")
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(test, url_prefix="/test")
    
    return [app]

apps = create_app()
app = apps[0]