import os
import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="Visual Search Engine", page_icon="🔍", layout="wide")

API_URL = "https://tanishqueagrawal-flipkart-visual-search.hf.space/search"
IMAGES_DIR = "dataset_full/images"  # local product images folder

st.title("🔍 Multi-Modal Visual Search Engine")
st.write("Upload a product photo and find visually similar items in the catalog.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

top_k = st.slider("Number of results", min_value=1, max_value=10, value=5)

if uploaded_file is not None:
    st.subheader("Query Image")
    st.image(uploaded_file, width=250)

    st.subheader("Matching Products")

    with st.spinner("Searching catalog..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        params = {"top_k": top_k}

        try:
            response = requests.post(API_URL, files=files, params=params, timeout=30)

            if response.status_code == 200:
                results = response.json().get("results", [])

                if not results:
                    st.warning("No matches found.")
                else:
                    # Show results in a responsive grid, 4 cards per row
                    cols_per_row = 4
                    for i in range(0, len(results), cols_per_row):
                        row_results = results[i:i + cols_per_row]
                        cols = st.columns(cols_per_row)

                        for col, r in zip(cols, row_results):
                            product = r["product"]
                            score = r["score"]
                            product_id = product.get("product_id")

                            with col:
                                with st.container(border=True):
                                    img_path = os.path.join(IMAGES_DIR, f"{product_id}.jpg")
                                    if os.path.exists(img_path):
                                        st.image(img_path, use_column_width=True)
                                    else:
                                        st.write("📦 (image not found)")

                                    st.markdown(f"**{product.get('title', 'Unknown Product')}**")
                                    st.caption(f"Similarity: {score:.2f}")
                                    st.write(f"₹{product.get('price', 'N/A')}")
                                    st.write(f"{product.get('category', 'N/A')} • {product.get('color', '')}")

                                    if product.get("is_in_stock"):
                                        st.success("In Stock", icon="✅")
                                    else:
                                        st.error("Out of Stock", icon="❌")
            else:
                st.error(f"Search failed: {response.status_code} - {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the search API. Make sure app.py (FastAPI server) is running on port 8000.")