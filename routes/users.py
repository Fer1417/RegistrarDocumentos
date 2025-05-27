from flask import Blueprint, jsonify
from db import mysql

bp = Blueprint('users', __name__, url_prefix='/api')

@bp.route('/users')
def get_users():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id,
            CONCAT(nombre, ' ', apellido_paterno, ' ', apellido_materno) AS nombre_completo,
            curp, rfc
        FROM usuarios
    """)
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users)

@bp.route('/users/<int:user_id>')
def get_user_detail(user_id):
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT id, nombre, apellido_paterno, apellido_materno,
            curp, rfc, imss, constancia_fiscal,
            domicilio, numero_ine
        FROM usuarios
        WHERE id = %s
    """, (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        return jsonify({"error": "Usuario no encontrado"}), 404

    nombre_completo = f"{user['nombre']} {user['apellido_paterno']} {user['apellido_materno']}"

    cursor.execute("SELECT nombre_curso FROM constancias_cursos WHERE usuario_id = %s", (user_id,))
    cursos = [c["nombre_curso"] for c in cursor.fetchall()]

    cursor.execute("SELECT numero_cedula, nombre FROM cedulas_profesionales WHERE usuario_id = %s", (user_id,))
    cedulas = [f"{c['nombre']} - {c['numero_cedula']}" for c in cursor.fetchall()]

    cursor.execute("SELECT nombre_regimen FROM regimenes_fiscales WHERE usuario_id = %s", (user_id,))
    regimenes = [r["nombre_regimen"] for r in cursor.fetchall()]

    cursor.close()

    return jsonify({
        "id": user["id"],
        "nombre_completo": nombre_completo,
        "curp": user["curp"],
        "rfc": user["rfc"],
        "imss": user["imss"],
        "constancia_fiscal": user["constancia_fiscal"],
        "domicilio": user["domicilio"],
        "numero_ine": user["numero_ine"],
        "cursos": cursos,
        "cedulas": cedulas,
        "regimenes": regimenes
    })

