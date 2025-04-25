from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from db import mysql
from services.ocr import extract_text_from_file, validate_document
from tempfile import NamedTemporaryFile

bp = Blueprint('upload', __name__, url_prefix='/upload')

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route("/document", methods=["POST"])
def upload_document():
    user_id = request.form.get("user_id")
    doc_type = request.form.get("doc_type")
    file = request.files.get("file")

    if not user_id or not doc_type or not file:
        return jsonify({"error": "Faltan datos"}), 400

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT nombre, apellido_paterno, apellido_materno FROM usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        return jsonify({"error": "Usuario no encontrado"}), 404

    nombre_completo = f"{user['nombre']} {user['apellido_paterno']} {user['apellido_materno']}"
    text = extract_text_from_file(path)
    resultado = validate_document(doc_type, text, nombre_completo)

    if not resultado["nombre_coincide"]:
        return jsonify({"validado": False, "mensaje": "El nombre del documento no coincide con el usuario."})

    # Guardado automático
    if doc_type == "curp" and resultado["extraido"].get("curp"):
        cursor.execute("UPDATE usuarios SET curp = %s WHERE id = %s", (resultado["extraido"]["curp"], user_id))

    elif doc_type == "rfc" and resultado["extraido"].get("rfc"):
        cursor.execute("UPDATE usuarios SET rfc = %s WHERE id = %s", (resultado["extraido"]["rfc"], user_id))

    elif doc_type == "imss" and resultado["extraido"].get("imss"):
        cursor.execute("UPDATE usuarios SET imss = %s WHERE id = %s", (resultado["extraido"]["imss"], user_id))

    elif doc_type == "fiscal" and resultado["extraido"].get("constancia_fiscal"):
        cursor.execute("UPDATE usuarios SET constancia_fiscal = %s WHERE id = %s", ("Validado", user_id))

    elif doc_type == "curso" and resultado["extraido"].get("curso"):
        cursor.execute("INSERT INTO constancias_cursos (usuario_id, nombre_curso) VALUES (%s, %s)", (user_id, "Validado"))

    elif doc_type == "cedula" and resultado["extraido"].get("cedulas"):
        for ced in resultado["extraido"]["cedulas"]:
            cursor.execute("INSERT IGNORE INTO cedulas_profesionales (usuario_id, numero_cedula) VALUES (%s, %s)", (user_id, ced))

    mysql.connection.commit()
    cursor.close()
    return jsonify({"validado": True, "resultado": resultado})