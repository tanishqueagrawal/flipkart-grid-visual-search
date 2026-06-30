import os
from io import BytesIO
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from PIL import Image

# 1. Load secrets
load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "flipkart_catalog"

# 2. Initialize app, model, and Qdrant client ONCE at startup
app = FastAPI(title="Visual Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading CLIP Model for search server...")
model = SentenceTransformer('clip-ViT-B-32')
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
print("Server ready.")


@app.get("/")
def root():
    return {"status": "Visual Search API is running"}


@app.post("/search")
async def search_by_image(file: UploadFile = File(...), top_k: int = 5):
    # Read uploaded image into memory
    contents = await file.read()
    image = Image.open(BytesIO(contents)).convert("RGB")

    # Vectorize the query image using the same CLIP model used at ingestion
    query_vector = model.encode(image).tolist()

    # Search Qdrant for nearest neighbors
    results = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )

    # Format response
    response = []
    for hit in results:
        response.append({
            "score": hit.score,
            "product": hit.payload
        })

    return {"results": response}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)