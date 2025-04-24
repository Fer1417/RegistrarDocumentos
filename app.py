#python -m venv venv
#venv\\Scripts\\activate 

from flask import Flask
from config import Config
from db import mysql
from routes.auth import bp as auth_bp
from routes.users import bp as users_bp

app = Flask(__name__)
app.config.from_object(Config)
mysql.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)

@app.route("/")
def index():
    return "<h1>Servidor Flask corriendo</h1>"

if __name__ == "__main__":
    app.run(debug=True)
