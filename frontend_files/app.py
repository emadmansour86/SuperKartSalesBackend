import os
import requests
import pandas as pd
import streamlit as st

# Backend (Flask) URL.
# Inside the Codespace Docker network the frontend reaches the backend by its container name.
# If the frontend runs outside that network, set BACKEND_URL to the forwarded Codespace URL for port 7860.
API_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860").rstrip("/")

st.set_page_config(page_title="SuperKart Sales Prediction", layout="centered")
st.title("SuperKart Sales Prediction")
st.write("Predict the total sales revenue of a product in a store.")

# ---------------- Online (single) prediction ----------------
st.subheader("Online Prediction")

product_id = st.text_input("Product Id (e.g., FD1234, NC1234, DR1234)", "FD1234")
product_weight = st.number_input("Product Weight", min_value=0.0, value=12.5, step=0.1)
product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
product_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
product_type = st.selectbox("Product Type", [
    "Frozen Foods", "Dairy", "Canned", "Baking Goods", "Health and Hygiene",
    "Snack Foods", "Meat", "Household", "Hard Drinks", "Fruits and Vegetables",
    "Breads", "Soft Drinks", "Breakfast", "Others", "Starchy Foods", "Seafood"])
product_mrp = st.number_input("Product MRP", min_value=0.0, value=150.0, step=1.0)
store_id = st.selectbox("Store Id", ["OUT001", "OUT002", "OUT003", "OUT004"])
store_year = st.number_input("Store Establishment Year", min_value=1950, max_value=2026, value=1999, step=1)
store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
store_type = st.selectbox("Store Type", ["Departmental Store", "Supermarket Type1", "Supermarket Type2", "Food Mart"])

if st.button("Predict Sales"):
    # Raw column names - the backend applies the same feature engineering used in training
    payload = {
        "Product_Id": product_id,
        "Product_Weight": product_weight,
        "Product_Sugar_Content": product_sugar,
        "Product_Allocated_Area": product_area,
        "Product_Type": product_type,
        "Product_MRP": product_mrp,
        "Store_Id": store_id,
        "Store_Establishment_Year": int(store_year),
        "Store_Size": store_size,
        "Store_Location_City_Type": city_type,
        "Store_Type": store_type,
    }
    try:
        response = requests.post(f"{API_URL}/v1/sales", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Predicted Sales: {result['predicted_sales']:,.2f}")
        else:
            st.error(f"Backend error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Could not reach the backend at {API_URL}: {e}")

# ---------------- Batch prediction ----------------
st.subheader("Batch Prediction")
st.write("Upload a CSV file in the SuperKart format (same columns as the original data) to get predictions for many rows at once.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    batch_df = pd.read_csv(uploaded_file)
    st.write("Preview of the uploaded data:")
    st.dataframe(batch_df.head())

    if st.button("Predict for File"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
        try:
            response = requests.post(f"{API_URL}/v1/salesbatch", files=files, timeout=120)
            if response.status_code == 200:
                preds = response.json()   # {"0": value, "1": value, ...}
                batch_df["Predicted_Sales"] = [preds.get(str(i)) for i in range(len(batch_df))]
                st.success(f"Predicted sales for {len(batch_df)} rows.")
                st.dataframe(batch_df)
                st.download_button(
                    "Download predictions as CSV",
                    batch_df.to_csv(index=False).encode("utf-8"),
                    file_name="superkart_predictions.csv",
                    mime="text/csv",
                )
            else:
                st.error(f"Backend error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend at {API_URL}: {e}")
