# 📄 Registro de Documentos

Sistema web para validación automática de documentos oficiales como CURP, RFC, INE, cédula profesional, comprobante de domicilio, etc., usando OCR con Tesseract y Flask.

---

## 🧩 ¿Qué hace este sistema?

- Permite subir distintos tipos de documentos oficiales (PDF o imagen).
- Detecta y extrae texto usando Tesseract OCR (`spa`).
- Valida automáticamente datos clave como:
  - CURP, RFC, número IMSS, INE.
  - Domicilio (4 líneas después del nombre).
  - Régimen fiscal (comparando con lista válida).
  - Nombre en INE, cédula profesional, etc.
- Coincidencia por tokens + fuzzy matching para nombres.
- Muestra y gestiona usuarios en un dashboard con Bootstrap.
- Guarda resultados en base de datos MySQL.

---

## ⚙️ Requisitos

Instala:

- Python 3.10+
- pip (instalador de paquetes Python)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) instalado en:
  `C:\Program Files\Tesseract-OCR`
- [Poppler for Windows](https://blog.alivate.com.au/poppler-windows/) (para PDFs)
- MySQL (con tabla `usuarios`, `cedulas_profesionales`, etc.)
- (Opcional) Laragon como entorno local

---

## 📦 Instalación

1. Clona el repositorio o descarga el código:

```bash
https://github.com/Fer1417/RegistroDocs.git
cd docs-validacion2
```
2. Crea y activa entorno virtual:

```bash
python -m venv venv
venv\Scripts\activate
```
3. Instala dependencias Python:

```bash
pip install -r requirements.txt
```
4. Configura las rutas en ocr.py:

```bash
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"
```
Asegúrate de tener tu base de datos MySQL configurada y la tabla usuarios creada con los campos esperados.

▶️ ¿Cómo ejecutar?
Desde terminal, con entorno activado:

```bash
python app.py
Abre en tu navegador:
http://localhost:5000
```

🖼️ Panel de usuario
Buscar usuarios por nombre o ID
Subir documentos
Visualizar CURP, RFC, INE, domicilio, cédula, etc.
Interfaz responsive con Bootstrap 5

📁 Estructura del proyecto
```bash
├── app.py
├── db.py
├── config.py
├── routes/
│   ├── auth.py
│   ├── users.py
│   └── upload.py
├── services/
│   └── ocr.py
├── templates/
│   └── login.html
├── static/
│   ├── styles_table.css
│   ├── app.js
│   └── img/cedula1.jpg ...
├── uploads/
├── venv/
