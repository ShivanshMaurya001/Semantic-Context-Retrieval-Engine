from google import genai
from app.utils.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_embedding(text: str):
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )

    return response.embeddings[0].values

if __name__ == "__main__":
    text = "FastAPI is a Python framework for building APIs."

    embedding = generate_embedding(text)

    print("Embedding Generated Successfully!")
    print("Vector Length:", len(embedding))
    print("First 5 Values:", embedding[:5])

