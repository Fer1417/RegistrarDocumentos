
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from db import mysql

bp = Blueprint('auth', __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, password FROM administradores WHERE email = %s", (email,))
        admin = cursor.fetchone()
        cursor.close()
        if admin and check_password_hash(admin["password"], password):
            session["admin_id"] = admin["id"]
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Correo o contraseña incorrectos")
            return redirect(url_for("auth.login"))
    return render_template("login.html")

@bp.route("/dashboard")
def dashboard():
    if "admin_id" not in session:
        return redirect(url_for("auth.login"))
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id, CONCAT(nombre, ' ', apellido_paterno, ' ', apellido_materno) AS nombre_completo, curp, rfc
        FROM usuarios
    """)
    users = cursor.fetchall()
    cursor.close()
    return render_template("dashboard.html", users=users)
