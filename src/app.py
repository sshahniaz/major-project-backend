import flask
from flask import request
import json
import csv
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os

import pickle 

app = flask.Flask(__name__)

# Get the full path to the model file
model_path = os.path.join(os.path.dirname(__file__), "..", "models", "BigMart_Sales_Model.pkl")

# Load your pre-trained ML model (replace with your loading logic)
with open(model_path, "rb") as file:
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
    
    initialDf = df

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

    initialDf['OutletSales'] = prediction

    #decode the dataframe to original form
    initialDf['FatContent'] = initialDf['FatContent'].replace({0:'Low Fat', 1:'Regular'})
    initialDf['OutletSize'] = initialDf['OutletSize'].replace({0:'Small', 1:'Medium', 2:'High'})
    initialDf['LocationType'] = initialDf['LocationType'].replace({0:'Tier 1', 1:'Tier 2', 2:'Tier 3'})
    initialDf['OutletType'] = initialDf['OutletType'].replace({0:'Grocery Store', 1:'Supermarket Type1', 2:'Supermarket Type2', 3:'Supermarket Type3'})

    
    # Calculate average sales for each product type
    product_sales = initialDf.groupby("ProductType")["OutletSales"].mean()
    product_sales = product_sales.sort_values(ascending=False)

    # Top 10 product types by sales
    top10_products = product_sales.head(10).reset_index()
    top10_products = top10_products.rename(columns={"ProductType": "productType", "OutletSales": "sales"})

    # Prepare location type (Tier) data
    tiers = initialDf.groupby("LocationType")["OutletSales"].mean().reset_index()
    tiers = tiers.rename(columns={"LocationType": "type", "OutletSales": "averageTierSales"})

    # Prepare Outlet Type data
    outlet_types = initialDf.groupby(["LocationType", "OutletType"])["OutletSales"].mean().reset_index()

    # Prepare Outlet Size data
    outlet_sizes = initialDf.groupby(["LocationType", "OutletType", "OutletSize"])["OutletSales"].mean().reset_index()

    # Prepare Product Type data
    product_types = initialDf.groupby(["LocationType", "OutletType", "OutletSize", "ProductType"])["OutletSales"].mean().reset_index()
    product_types = product_types.rename(columns={"ProductType": "name", "OutletSales": "averageSales"})

    # Combine data into a dictionary
    data = {
      "top10ProductTypesSales": top10_products.to_dict(orient="records"),
      "locationType": [],
    }

    # Prepare location data with nested structures

    for tier_id, tier in tiers.iterrows():
        location_data = {
            "type": tier["type"],
            "averageTierSales": tier["averageTierSales"],
            "OutletType": []
        }

        # Add Outlet Type data
        for outlet_type_id, outlet_type in outlet_types[outlet_types["LocationType"] == tier["type"]].iterrows():
            outlet_type_data = {
                "type": outlet_type["OutletType"],
                "averageTypeSales": outlet_type["OutletSales"],
                "OutletSize": []
            }

            # Add Outlet Size data
            for outlet_size_id, outlet_size in outlet_sizes[(outlet_sizes["LocationType"] == tier["type"]) & (outlet_sizes["OutletType"] == outlet_type["OutletType"])].iterrows():
                outlet_size_data = {
                    "size": outlet_size["OutletSize"],
                    "averageSalesforSize": outlet_size["OutletSales"],
                    "productTypes": []
                }

                # Add Product Type data
                for product_type_id, product_type in product_types[(product_types["LocationType"] == tier["type"]) & (product_types["OutletType"] == outlet_type["OutletType"]) & (product_types["OutletSize"] == outlet_size["OutletSize"])].iterrows():
                    product_type_data = {
                        "name": product_type["name"],
                        "averageSales": product_type["averageSales"]
                    }
                    outlet_size_data["productTypes"].append(product_type_data)

                outlet_type_data["OutletSize"].append(outlet_size_data)
            location_data["OutletType"].append(outlet_type_data)

        data["locationType"].append(location_data)

    # Prepare the JSON response with the prediction
    # response = json.dumps(data, indent=4)  # Convert to list for JSON
    response = flask.jsonify(data)
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response

if __name__ == "__main__":
    app.run()
