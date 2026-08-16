from google import genai

from app.utils.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

def generate_answer(question, context):

    prompt = f"""
You are an assistant that answers questions about a document.

Use ONLY the information provided in the context below.

If the answer is not present in the context, say:
"The answer was not found in the document."

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text