import os
import random
import pandas as pd
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from PIL import Image

# 1. Load secrets
load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "flipkart_catalog"
DATASET_DIR = "dataset_full"
IMAGES_DIR = os.path.join(DATASET_DIR, "images")
CSV_PATH = os.path.join(DATASET_DIR, "styles.csv")

SAMPLE_SIZE = 300  # how many products to ingest (increase later once confirmed working)

# 2. Initialize CLIP model + Qdrant client
print("Loading CLIP Model (ViT-B-32)...")
model = SentenceTransformer('clip-ViT-B-32')
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def setup_collection():
    collections = qdrant_client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)

    if exists:
        print(f"Collection '{COLLECTION_NAME}' already exists. Recreating fresh...")
        qdrant_client.delete_collection(collection_name=COLLECTION_NAME)

    print(f"Creating collection: {COLLECTION_NAME}...")
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=512, distance=Distance.COSINE)
    )


def ingest_catalog():
    setup_collection()

    print("Reading product metadata...")
    df = pd.read_csv(CSV_PATH, on_bad_lines='skip')

    # Only keep rows whose image file actually exists
    df["image_path"] = df["id"].apply(lambda x: os.path.join(IMAGES_DIR, f"{x}.jpg"))
    df = df[df["image_path"].apply(os.path.exists)]

    # Random sample for fast local demo ingestion
    if len(df) > SAMPLE_SIZE:
        df = df.sample(n=SAMPLE_SIZE, random_state=42)

    print(f"Ingesting {len(df)} products...")

    batch_size = 32
    batch_points = []

    for i, row in enumerate(df.itertuples(index=False), 1):
        try:
            image = Image.open(row.image_path).convert("RGB")
            vector = model.encode(image).tolist()

            # Mock a realistic price since this dataset has no price column
            price = round(random.uniform(399, 4999), 2)

            payload = {
                "product_id": int(row.id),
                "title": str(row.productDisplayName),
                "category": str(row.articleType),
                "master_category": str(row.masterCategory),
                "gender": str(row.gender),
                "color": str(row.baseColour),
                "price": price,
                "is_in_stock": random.choice([True, True, True, False])  # mostly in stock
            }

            batch_points.append(PointStruct(id=int(row.id), vector=vector, payload=payload))

            if len(batch_points) >= batch_size:
                qdrant_client.upsert(collection_name=COLLECTION_NAME, points=batch_points)
                print(f"  Indexed {i}/{len(df)}...")
                batch_points = []

        except Exception as e:
            print(f"Failed on id {row.id}: {e}")

    if batch_points:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=batch_points)

    print(f"Done. Indexed {len(df)} products into Qdrant Vector DB.")


if __name__ == "__main__":
    ingest_catalog()