from flask import Flask
from flask import Flask,render_template
from config import Config
from db import mysql
from routes.auth import bp as auth_bp
from routes.users import bp as users_bp
from routes.upload import bp as upload_bp
import os


app = Flask(__name__)
app.config.from_object(Config)
mysql.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(upload_bp)

@app.route("/")
def index():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
