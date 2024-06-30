import flask
from flask import request
import json
import csv
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

import pickle 

app = flask.Flask(__name__)

# Load your pre-trained ML model (replace with your loading logic)
with open("../models/BigMart_Sales_Model.pkl", "rb") as file:
    model = pickle.load(file) # Adjust the filename as needed

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

    categorical_col = ['ProductID', 'FatContent', 'ProductType', 'OutletID', 'OutletSize', 'LocationType', 'OutletType']
    numerical_col = ['Weight', 'ProductVisibility', 'MRP', 'EstablishmentYear', 'OutletSales']


    # Check if the CSV data has the expected columns
    expected_columns = ['ProductID', 'FatContent', 'ProductType', 'OutletID', 'OutletSize', 'LocationType', 'OutletType', 'Weight', 'ProductVisibility', 'MRP', 'EstablishmentYear']
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
      return flask.jsonify({"error": f"Missing columns in CSV file: {', '.join(missing_columns)}"}), 400
    
    #Standardasing the FatContent column
    ifc_dict = {'Low Fat':'Low Fat', 'Regular':'Regular', 'LF':'Low Fat', 'reg':'Regular', 'low fat':'Low Fat'}
    df['FatContent'] = df['FatContent'].replace(ifc_dict)

    #Encoding data
    encode_dict = {'Low Fat':0, 'Regular': 1, 'Small':0, 'Medium':1,'High':2, 'Tier 3':2, 'Tier 2': 1, 'Tier 1': 0, 'Grocery Store':0, 'Supermarket Type1':1, 'Supermarket Type2':2, 'Supermarket Type3':3}
    df = df.replace(encode_dict)

    

    categorical_columns = df.select_dtypes(include=['object']).columns

    label_encoders = {}
    for col in categorical_columns:
      le = LabelEncoder()
      df[col] = le.fit_transform(df[col].astype(str))
      label_encoders[col] = le

    features = df.drop(columns = ['Weight', 'FatContent','ProductID','OutletID'], axis = 1)  
    scaler = StandardScaler()
    features = scaler.fit_transform(features)


    # Make the prediction using your pre-trained Lasso model
    prediction = model.predict(features)

    # Prepare the JSON response with the prediction
    response = {"prediction": prediction.tolist()}  # Convert to list for JSON

    return flask.jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)
