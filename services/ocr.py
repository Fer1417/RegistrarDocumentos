import pytesseract
import re
from PIL import Image
from pdf2image import convert_from_path
import os
from tempfile import NamedTemporaryFile

os.environ['TESSDATA_PREFIX'] = "C:\Program Files\Tesseract-OCR\tessdata"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"

def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        images = convert_from_path(filepath, poppler_path=POPPLER_PATH)
        text = "\n".join([pytesseract.image_to_string(img, lang='spa') for img in images])
    elif ext in ['.jpg', '.jpeg', '.png']:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img, lang='spa')
    else:
        raise ValueError("Tipo de archivo no soportado para OCR")
    return text

def validate_document(doc_type, text, nombre_completo):
    text_upper = text.upper()
    nombre_ok = nombre_completo.upper() in text_upper

    resultado = {
        "nombre_coincide": nombre_ok,
        "extraido": {}
    }

    if doc_type == 'curp':
        curp_match = re.search(r'[A-Z]{4}\d{6}[A-Z0-9]{8}', text_upper)
        if curp_match:
            resultado["extraido"]["curp"] = curp_match.group(0)

    elif doc_type == 'rfc':
        rfc_match = re.search(r'[A-Z]{4}\d{6}[A-Z0-9]{3}', text_upper)
        if rfc_match:
            resultado["extraido"]["rfc"] = rfc_match.group(0)

    elif doc_type == 'imss':
        imss_match = re.search(r'\b\d{11}\b', text_upper)
        if imss_match:
            resultado["extraido"]["imss"] = imss_match.group(0)

    elif doc_type == 'fiscal':
        resultado["extraido"]["constancia_fiscal"] = "OK" if nombre_ok else None

    elif doc_type == 'curso':
        resultado["extraido"]["curso"] = "Validado" if nombre_ok else None

    elif doc_type == 'cedula':
        cedula_match = re.findall(r'\b\d{7,8}\b', text_upper)
        resultado["extraido"]["cedulas"] = cedula_match if cedula_match else []

    return resultado
