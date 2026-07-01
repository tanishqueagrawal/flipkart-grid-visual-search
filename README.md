---
title: Flipkart Visual Search
emoji: 🔍
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 🔍 Multi-Modal AI Visual Search Engine

> Built for **Flipkart GRiD 8.0** | Track: Software Development / AI

A production-style visual search engine that lets users upload any product photo and instantly find visually similar items from a catalog — powered by CLIP embeddings and vector similarity search.

---

## 🚀 Demo

Upload a product image → Get ranked visual matches from 300+ catalog items in real-time.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Visual Embeddings | CLIP (ViT-B/32) via `sentence-transformers` |
| Vector Database | Qdrant Cloud (free tier) |
| Search Backend | FastAPI + Uvicorn |
| Frontend UI | Streamlit |
| Dataset | Fashion Product Images (Myntra, via Kaggle) |

---

## ⚙️ How It Works

1. **Ingestion** (`ingest.py`) — Product images are encoded into 512-dimensional CLIP vectors and stored in Qdrant Cloud with metadata (title, category, price, stock).
2. **Search API** (`app.py`) — FastAPI server accepts an uploaded image, encodes it with the same CLIP model, and queries Qdrant for top-K nearest neighbors by cosine similarity.
3. **Frontend** (`interface.py`) — Streamlit UI shows the query image and returns a 4-column product grid with images, prices, and stock status.

---

## 📦 Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/tanishqueagrawal/flipkart-grid-visual-search.git
cd flipkart-grid-visual-search
```

### 2. Create virtual environment
```bash
py -3.12 -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the root folder:
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
### 4. Download dataset & run ingestion
```bash
kaggle datasets download -d paramaggarwal/fashion-product-images-small
mkdir dataset_full
tar -xf fashion-product-images-small.zip -C dataset_full
python ingest.py
```

### 5. Start the backend
```bash
python app.py
```

### 6. Start the frontend (new terminal)
```bash
streamlit run interface.py
```

Open `http://localhost:8501` — upload any product image and search!

---

## 📁 Project Structure
flipkart-grid-visual-search/
├── app.py              # FastAPI search backend
├── ingest.py           # Dataset ingestion + CLIP vectorization
├── interface.py        # Streamlit frontend
├── requirements.txt    # Python dependencies
├── dataset/            # Sample test images
└── .env                # Secrets (not committed)
---

## 👤 Author

**Tanishque Agrawal** — B.Tech AI & Data Science, Arya College of Engineering, Jaipur  
[GitHub](https://github.com/tanishqueagrawal) • [LinkedIn](https://linkedin.com/in/tanishque-agrawal)