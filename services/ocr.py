import pytesseract
import os
from PIL import Image
from pdf2image import convert_from_path
import re
from unidecode import unidecode
from flask import request
import difflib
import platform

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"
    POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"
else:
    # En Linux, tesseract y poppler están en el PATH por defecto si los instalaste con apt
    pytesseract.pytesseract.tesseract_cmd = 'tesseract'
    os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata/'
    POPPLER_PATH = None

REGIMENES_VALIDOS = {
    "REGIMEN GENERAL DE LEY PERSONAS MORALES",
    "REGIMEN SIMPLIFICADO DE LEY PERSONAS MORALES",
    "PERSONAS MORALES CON FINES NO LUCRATIVOS",
    "REGIMEN DE PEQUEÑOS CONTRIBUYENTES",
    "REGIMEN DE SUELDOS Y SALARIOS E INGRESOS ASIMILADOS A SALARIOS",
    "REGIMEN DE ARRENDAMIENTO",
    "REGIMEN DE ENAJENACION O ADQUISICION DE BIENES",
    "REGIMEN DE LOS DEMAS INGRESOS",
    "REGIMEN DE CONSOLIDACION",
    "REGIMEN RESIDENTES EN EL EXTRANJERO SIN ESTABLECIMIENTO PERMANENTE EN MEXICO",
    "REGIMEN DE INGRESOS POR DIVIDENDOS (SOCIOS Y ACCIONISTAS)",
    "REGIMEN DE LAS PERSONAS FISICAS CON ACTIVIDADES EMPRESARIALES Y PROFESIONALES",
    "REGIMEN INTERMEDIO DE LAS PERSONAS FISICAS CON ACTIVIDADES EMPRESARIALES",
    "REGIMEN DE LOS INGRESOS POR INTERESES",
    "REGIMEN DE LOS INGRESOS POR OBTENCION DE PREMIOS",
    "SIN OBLIGACIONES FISCALES",
    "PEMEX",
    "REGIMEN SIMPLIFICADO DE LEY PERSONAS FISICAS",
    "INGRESOS POR LA OBTENCION DE PRESTAMOS",
    "SOCIEDADES COOPERATIVAS DE PRODUCCION QUE OPTAN POR DIFERIR SUS INGRESOS",
    "REGIMEN DE INCORPORACION FISCAL",
    "REGIMEN DE ACTIVIDADES AGRICOLAS, GANADERAS, SILVICOLAS Y PESQUERAS PM",
    "REGIMEN DE OPCIONAL PARA GRUPOS DE SOCIEDADES",
    "REGIMEN DE LOS COORDINADOS",
    "REGIMEN DE LAS ACTIVIDADES EMPRESARIALES CON INGRESOS A TRAVES DE PLATAFORMAS TECNOLOGICAS",
    "REGIMEN SIMPLIFICADO DE CONFIANZA"
}


def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.pdf':
        images = convert_from_path(filepath, poppler_path=POPPLER_PATH)
        text = "\n".join([
            pytesseract.image_to_string(img, lang='spa', config='--psm 6')
            for img in images
        ])
    elif ext in ['.jpg', '.jpeg', '.png']:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img, lang='spa', config='--psm 6')
    else:
        raise ValueError("Tipo de archivo no soportado para OCR")

    return text

def validate_document(doc_type, text, nombre_completo, formato_cedula=""):
    text_upper = unidecode(text.upper())
    nombre_upper = unidecode(nombre_completo.upper())
    nombre_ok = nombre_upper in text_upper

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

    elif doc_type == 'curso':
        lines = text_upper.splitlines()
        cursos = [line.strip() for line in lines if nombre_upper in line]
        resultado["extraido"]["curso"] = cursos[0] if cursos else None

    elif doc_type == 'cedula':
        formato = request.form.get("formato_cedula", "")
        lines = [l.strip() for l in text_upper.splitlines() if l.strip()]
        nombre_detectado = None
        cedula_programa = None
        cedula_numero = None

        resultado["extraido"]["cedulas"] = []

        if formato_cedula == "formato_1":
            for i, line in enumerate(lines):
                if "NOMBRE(S) PRIMER APELLIDO SEGUNDO APELLIDO" in line:
                    if i > 0:
                        nombre_detectado = lines[i - 1].strip()
                    break

            for i, line in enumerate(lines):
                if "NUMERO DE CEDULA PROFESIONAL" in line or "NÚMERO DE CÉDULA PROFESIONAL" in line:
                    match_inline = re.search(r'\b\d{8}\b', line)
                    if match_inline:
                        cedula_numero = match_inline.group(0)
                        break
                    if i + 1 < len(lines):
                        match_next = re.search(r'\b\d{8}\b', lines[i + 1])
                        if match_next:
                            cedula_numero = match_next.group(0)
                            break
            for line in lines:
                match = re.search(r'\b(LICENCIATURA|MAESTRIA|DOCTORADO)\s+EN\s+[A-ZÁÉÍÓÚÑ ]+\s+(\d{6})\b', line)
                if match:
                    cedula_programa = match.group(0)
                    break
            if cedula_programa and cedula_numero:
                resultado["extraido"]["cedulas"].append({
                    "nombre": cedula_programa,
                    "numero": cedula_numero
                })

            resultado["extraido"]["nombre_detectado"] = nombre_detectado
            resultado["nombre_coincide"] = nombre_detectado is not None and all(
                part in unidecode(nombre_detectado) for part in nombre_upper.split()
            )

        elif formato_cedula == "formato_2":
            from difflib import get_close_matches

            def corregir_palabras(texto):
                reemplazos = {
                    "LIANCATURA": "LICENCIATURA",
                    "AIVAREZ": "ALVAREZ",
                    "MAESTIA": "MAESTRIA",
                    "DOCTORAD": "DOCTORADO"
                }
                for mal, bien in reemplazos.items():
                    texto = texto.replace(mal, bien)
                return texto

            nombre_detectado = None
            cedula_programa = None
            cedula_numero = None

            for i, line in enumerate(lines):
                if "CEDULA PROFESIONAL" in line or "CÉDULA PROFESIONAL" in line:
                    if i + 1 < len(lines):
                        num_match = re.search(r'\d{8}', lines[i + 1])
                        if num_match:
                            cedula_numero = num_match.group(0)
                    nombre_partes = []
                    if i + 2 < len(lines): nombre_partes.append(lines[i+2])
                    if i + 3 < len(lines): nombre_partes.append(lines[i+3])
                    nombre_raw = " ".join(nombre_partes)
                    nombre_corr = corregir_palabras(nombre_raw.upper())
                    nombre_limpio = unidecode(re.sub(r'[^A-Z ]+', '', nombre_corr)).strip()
                    nombre_detectado = nombre_limpio
                    for j in range(i + 4, min(i + 12, len(lines))):
                        linea_corr = corregir_palabras(lines[j])
                        if any(pal in linea_corr for pal in ["LICENCIATURA", "MAESTRIA", "DOCTORADO"]):
                            carrera_lines = [corregir_palabras(lines[k]) for k in range(j, min(j+3, len(lines)))]
                            cedula_programa = " ".join(carrera_lines).strip()
                            break
                    break

            resultado["extraido"]["cedulas"] = []
            if cedula_programa and cedula_numero:
                resultado["extraido"]["cedulas"].append({
                    "nombre": cedula_programa,
                    "numero": cedula_numero
                })

            resultado["extraido"]["nombre_detectado"] = nombre_detectado
            resultado["nombre_coincide"] = False

            if nombre_detectado:
                ocr_tokens = unidecode(nombre_detectado).split()
                user_tokens = unidecode(nombre_upper).split()
                coincidencias = 0
                for token_usr in user_tokens:
                    match = get_close_matches(token_usr, ocr_tokens, n=1, cutoff=0.75)
                    if match:
                        coincidencias += 1
                resultado["nombre_coincide"] = coincidencias >= 2

        elif formato_cedula == "formato_3":
            nombre_detectado = None
            cedula_programa = None
            cedula_numero = None

            for i, line in enumerate(lines):
                if "CEDULA" in line and not "PROFESIONAL" in line:
                    match = re.search(r'\b\d{7}\b', line)
                    if match:
                        cedula_numero = match.group(0)
                if "EN VIRTUD DE QUE" in line and i + 3 < len(lines):
                    nombre_lns = [lines[i + 1], lines[i + 2], lines[i + 3]]
                    nombre_raw = " ".join(nombre_lns)
                    nombre_limpio = unidecode(re.sub(r'[^A-Z ]+', '', nombre_raw.upper())).strip()
                    nombre_detectado = nombre_limpio
                if any(key in line for key in ["LICENCIATURA", "INGENIERO", "MAESTRIA", "DOCTORADO"]):
                    carrera_lns = [lines[k] for k in range(i, min(i+3, len(lines)))]
                    carrera_txt = " ".join(carrera_lns)
                    carrera_limpia = unidecode(re.sub(r'[^A-Z ]+', '', carrera_txt.upper())).strip()
                    cedula_programa = carrera_limpia

            resultado["extraido"]["cedulas"] = []
            if cedula_programa and cedula_numero:
                resultado["extraido"]["cedulas"].append({
                    "nombre": cedula_programa,
                    "numero": cedula_numero
                })

            resultado["extraido"]["nombre_detectado"] = nombre_detectado
            resultado["nombre_coincide"] = False

            if nombre_detectado:
                ocr_tokens = unidecode(nombre_detectado).split()
                user_tokens = unidecode(nombre_upper).split()
                coincidencias = 0
                for token_usr in user_tokens:
                    match = difflib.get_close_matches(token_usr, ocr_tokens, n=1, cutoff=0.75)
                    if match:
                        coincidencias += 1
                resultado["nombre_coincide"] = coincidencias >= 2


    elif doc_type == 'regimen':
        regimenes = re.findall(r'REG[IÍ]MEN[\s:\-A-Z]+', text_upper)
        regimenes_limpios = [unidecode(r.strip()) for r in regimenes]

        regimenes_validos = []
        for extraido in regimenes_limpios:
            for valido in REGIMENES_VALIDOS:
                if valido in extraido:
                    regimenes_validos.append(valido)

        resultado["extraido"]["regimenes"] = list(set(regimenes_validos))

    elif doc_type == 'ine':
        lines = [l.strip() for l in text_upper.splitlines() if l.strip()]
        numero_ine = None
        nombre_detectado = None

        for line in lines:
            clean_line = line.replace(" ", "")
            match = re.search(r'(?:[1I]?DMEX)(\d{9})', clean_line)
            if match:
                numero_ine = match.group(1)
                break

        for line in lines:
            if "<<" in line and re.search(r'[A-Z]{2,}<[A-Z]{2,}<<[A-Z]{2,}', line):
                nombre_detectado = line.replace('<', ' ').strip()
                break

        resultado["extraido"]["ine"] = numero_ine
        resultado["extraido"]["nombre_detectado"] = nombre_detectado or "No detectado"
        resultado["nombre_coincide"] = nombre_detectado is not None and all(
            part in nombre_detectado for part in nombre_upper.split()
        )


    elif doc_type == 'domicilio':
        lines = [l.strip() for l in text_upper.splitlines() if l.strip()]
        nombre_parts = nombre_upper.split()
        posibles_indices = []

        for i, line in enumerate(lines):
            matches = sum(1 for part in nombre_parts if part in line)
            if matches >= 0:  
                posibles_indices.append(i)

        if posibles_indices:
            idx = posibles_indices[0]
            domicilio_lines = lines[idx+1:idx+5]
            resultado["extraido"]["domicilio"] = " ".join(domicilio_lines)
        else:
            resultado["extraido"]["domicilio"] = ""
    return resultado
