
from flask import Blueprint, jsonify
from db import mysql

bp = Blueprint('users', __name__, url_prefix='/api')

# routes/users.py
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
        SELECT 
            u.id,
            CONCAT(u.nombre, ' ', u.apellido_paterno, ' ', u.apellido_materno) AS nombre_completo,
            u.curp, u.rfc, u.imss, u.constancia_fiscal
        FROM usuarios u
        WHERE u.id = %s
    """, (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Cursos
    cursor.execute("SELECT nombre_curso FROM constancias_cursos WHERE usuario_id = %s", (user_id,))
    cursos = [row['nombre_curso'] for row in cursor.fetchall()]

    # Cédulas
    cursor.execute("SELECT numero_cedula FROM cedulas_profesionales WHERE usuario_id = %s", (user_id,))
    cedulas = [row['numero_cedula'] for row in cursor.fetchall()]

    cursor.close()

    user["fiscal"] = user.pop("constancia_fiscal")
    user["cursos"] = cursos
    user["cedulas"] = cedulas

    return jsonify(user)

