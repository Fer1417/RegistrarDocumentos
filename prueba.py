import pytesseract
import os
from PIL import Image
from pdf2image import convert_from_path
import re
from unidecode import unidecode

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata"
POPPLER_PATH = r"C:\Program Files\poppler-24.08.0\Library\bin"

def read_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"[ERROR] Al leer la imagen: {e}"

def read_text_from_pdf(pdf_path):
    try:
        pages = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        full_text = ""
        for i, page in enumerate(pages):
            text = pytesseract.image_to_string(page)
            full_text += f"\n--- Página {i + 1} ---\n{text}"
        return full_text
    except Exception as e:
        return f"[ERROR] Al leer el PDF: {e}"

def main():
    image_path = input("Ruta de la imagen: ").strip()
    pdf_path = input("Ruta del PDF: ").strip()

    print("\n[Imagen]\n")
    print(read_text_from_image(image_path))

    print("\n[PDF]\n")
    print(read_text_from_pdf(pdf_path))

if __name__ == "__main__":
    main()
