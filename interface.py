import os
import streamlit as st
import requests

st.set_page_config(page_title="Visual Search Engine", page_icon="🔍", layout="wide")

API_URL = "https://tanishqueagrawal-flipkart-visual-search.hf.space/search"
PLACEHOLDER = "https://via.placeholder.com/200x250?text=Product+Image"

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
            response = requests.post(API_URL, files=files, params=params, timeout=60)

            if response.status_code == 200:
                results = response.json().get("results", [])

                if not results:
                    st.warning("No matches found.")
                else:
                    cols_per_row = 4
                    for i in range(0, len(results), cols_per_row):
                        row_results = results[i:i + cols_per_row]
                        cols = st.columns(cols_per_row)

                        for col, r in zip(cols, row_results):
                            product = r["product"]
                            score = r["score"]
                            product_id = product.get("product_id")

                            # Try Myntra CDN URL
                            img_url = f"https://assets.myntassets.com/assets/images/{product_id}/1/images/315/315/image.jpg"

                            with col:
                                with st.container(border=True):
                                    try:
                                        st.image(img_url, use_column_width=True)
                                    except:
                                        st.image(PLACEHOLDER, use_column_width=True)

                                    st.markdown(f"**{product.get('title', 'Unknown')}**")
                                    st.caption(f"Similarity: {score:.2f}")
                                    st.write(f"₹{product.get('price', 'N/A')}")
                                    st.write(f"{product.get('category', '')} • {product.get('color', '')}")

                                    if product.get("is_in_stock"):
                                        st.success("In Stock", icon="✅")
                                    else:
                                        st.error("Out of Stock", icon="❌")
            else:
                st.error(f"Search failed: {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to search API.")
        except requests.exceptions.Timeout:
            st.error("Request timed out — HuggingFace Space may be waking up (free tier). Try again in 30 seconds.")