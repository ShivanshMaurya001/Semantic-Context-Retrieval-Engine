from app.services.pdf_service import extract_text_from_pdf


pdf_path = "uploads/5273f2bf-e71a-4df9-acea-74de51fb690b.pdf"
#2f823707-1169-4ed4-8bd7-9f96563ee626.pdf

pages = extract_text_from_pdf(pdf_path)

print("Total Pages:", len(pages))

for page in pages:
    print("\n--------------------")
    print("Page:", page["page_number"])
    print(page["text"])