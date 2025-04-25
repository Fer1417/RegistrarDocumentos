import pytesseract
import re
from PIL import Image
from pdf2image import convert_from_path
import os
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

    curp = None
    if doc_type == 'curp':
        match = re.search(r'[A-Z]{4}\d{6}[A-Z0-9]{8}', text_upper)
        if match:
            curp = match.group(0)

    return {
        "nombre_coincide": nombre_ok,
        "extraido": {
            "curp": curp
        }
    }