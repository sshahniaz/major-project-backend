import flask
from flask import request
import json
import csv
import pandas as pd
import numpy as np


from sklearn.model_selection import load_model 

app = flask.Flask(__name__)

# Load your pre-trained ML model (replace with your loading logic)
model = load_model("./ml_project/models/BigMart_Sales_Model.pkl")  # Adjust the filename as needed

@app.route("/predict", methods=["POST"])
def predict():
    # Check if a file was uploaded
    if "file" not in request.files:
        return flask.jsonify({"error": "No file uploaded."}), 400

    # Get the uploaded CSV file
    uploaded_file = request.files["file"]

    # Validate the uploaded file (optional but recommended)
    if uploaded_file.filename.lower().endswith(".csv") is False:
        return flask.jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

    # Read the CSV data using pandas
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        return flask.jsonify({"error": f"Error reading CSV file: {str(e)}"}), 400

    # Extract features from the DataFrame (replace with your logic)
    features = df  # Assuming all columns are features (adjust as needed)

    # Check if required features are present (optional but recommended)
    # Assuming no specific features are required for the model

    # Make the prediction using your pre-trained Lasso model
    prediction = model.predict(features)

    # Prepare the JSON response with the prediction
    response = {"prediction": prediction.tolist()}  # Convert to list for JSON

    return flask.jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)
