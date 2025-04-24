
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
        SELECT id,
               CONCAT(nombre, ' ', apellido_paterno, ' ', apellido_materno) AS nombre_completo,
               curp, rfc, imss, situacion_fiscal AS fiscal,
               constancias_cursos AS cursos, cedulas_profesionales AS cedulas
        FROM usuarios
        WHERE id = %s
    """, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return jsonify(user) if user else (jsonify({'error': 'Usuario no encontrado'}), 404)
