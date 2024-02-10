from chalice import Chalice

from chat_api import bp as chat_bp

app = Chalice(app_name='REsolution-API')
app.register_blueprint(chat_bp)
