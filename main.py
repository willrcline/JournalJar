import config
# import flask_auth
# import flask_app
# import flask_payment
# import flask_sms_received
from flask import Flask
from flask_app import app_blueprint
from flask_auth import auth_blueprint, init_flask_oauth
from authlib.integrations.flask_client import OAuth



app = Flask(__name__)
app.secret_key = config.flask_secret_key
app.config.from_object('config')

app.register_blueprint(auth_blueprint)
app.register_blueprint(app_blueprint)

init_flask_oauth(app)




# app.add_url_rule('/', view_func=flask_auth.index)
# app.add_url_rule('/sign_up', view_func=flask_auth.sign_up)
# app.add_url_rule('/successful_sign_up', view_func=flask_auth.successful_sign_up)
# app.add_url_rule('/sign_in', view_func=flask_auth.sign_in, methods=['POST', 'GET'])
# app.add_url_rule('/auth', view_func=flask_auth.auth, methods=['POST'])
# app.add_url_rule('/portal', view_func=flask_app.portal)
# app.add_url_rule('/sign_out', view_func=flask_auth.sign_out)

# app.add_url_rule('/stripe_create_customer', view_func=flask_payment.stripe_create_customer, methods=['POST'])

# app.add_url_rule('/sms', view_func=flask_sms_received.sms_received, methods=['POST'])

if __name__ == "__main__":
    app.debug = True
    app.run()