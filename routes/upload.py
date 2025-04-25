from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from db import mysql
from services.ocr import extract_text_from_file, validate_document

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

    if doc_type == "curp" and resultado["extraido"]["curp"]:
        cursor.execute("UPDATE usuarios SET curp = %s WHERE id = %s", (resultado["extraido"]["curp"], user_id))
        mysql.connection.commit()

    cursor.close()
    return jsonify({"validado": True, "resultado": resultado})