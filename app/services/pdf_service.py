import pdfplumber


def extract_text_from_pdf(file_path):

    pages = []

    with pdfplumber.open(file_path) as pdf:

        for page_number, page in enumerate(pdf.pages, start=1):

            text = page.extract_text()

            if text:
                text = text.strip()

            pages.append({
                "page_number": page_number,
                "text": text
            })

    return pages