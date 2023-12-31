from helpers import app
from modules.module_1.routes import hello, hello_uid

# Hello routes
app.route('/hello', methods=['GET'])(hello)
app.route('/hello/{name}', methods=['GET'])(hello_uid)
