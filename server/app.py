from chalice import Chalice

from modules.module_1.routes import bp as module_1_bp

app = Chalice(app_name='blueprint-demo')
app.register_blueprint(module_1_bp)
