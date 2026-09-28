# Import necessary libraries
import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify

# Initialize the Flask application
app = Flask("SuperKart Sales Predictor")

# Load the trained model pipeline (preprocessing + model together)
model = joblib.load("superkart_sales_prediction_model_v1_0.joblib")

# Reference year used when the model was trained (to compute store age)
REFERENCE_YEAR = 2026


def feature_engineering(df):
    """Apply the SAME feature engineering used during training."""
    df = df.copy()
    # Fix the sugar content typo
    if "Product_Sugar_Content" in df.columns:
        df["Product_Sugar_Content"] = df["Product_Sugar_Content"].replace({"reg": "Regular"})
    # Derive product category from the first two letters of Product_Id
    if "Product_Id" in df.columns:
        id_map = {"FD": "Food", "NC": "Non-Consumable", "DR": "Drinks"}
        df["Product_Id_Type"] = df["Product_Id"].astype(str).str[:2].map(id_map)
        df = df.drop(columns=["Product_Id"])
    # Convert establishment year into store age
    if "Store_Establishment_Year" in df.columns:
        df["Store_Age"] = REFERENCE_YEAR - df["Store_Establishment_Year"]
        df = df.drop(columns=["Store_Establishment_Year"])
    return df


@app.get("/")
def home():
    """Simple welcome message so I can check the API is alive."""
    return "Welcome to the SuperKart Sales Prediction API!"


@app.post("/v1/sales")
def predict_sales():
    """Single prediction. Expects a JSON body with one product/store record."""
    data = request.get_json()
    input_df = pd.DataFrame([data])          # one row
    input_df = feature_engineering(input_df) # same FE as training
    prediction = model.predict(input_df)
    return jsonify({"predicted_sales": round(float(prediction[0]), 2)})


@app.post("/v1/salesbatch")
def predict_sales_batch():
    """Batch prediction. Expects a CSV file uploaded under the key 'file'."""
    file = request.files["file"]
    input_df = pd.read_csv(file)
    input_df = feature_engineering(input_df)
    predictions = model.predict(input_df)
    # Return a dictionary: row index -> predicted sales
    output = {i: round(float(p), 2) for i, p in enumerate(predictions)}
    return jsonify(output)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
