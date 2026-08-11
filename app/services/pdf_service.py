import pdfplumber
import re

def clean_text(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text

def extract_text_from_pdf(file_path):

    pages = []

    with pdfplumber.open(file_path) as pdf:

        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text()

            if text:
             text = clean_text(text)


            if not text:
                raise ValueError("No text could be extracted from this PDF.")

            pages.append({
                "page_number": page_number,
                "text": text
            })

    return pages

