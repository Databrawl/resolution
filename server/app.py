from chalice import Chalice

from chat_api import bp as chat_bp

app = Chalice(app_name='blueprint-demo')
app.register_blueprint(chat_bp)
