import flask
from flask import request
import json
import csv
import uuid
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os

import pickle 

app = flask.Flask(__name__)

# Get the full path to the model file
model_path = os.path.join(os.path.dirname(__file__), "..", "models", "BigMart_Sales_Model.pkl")

# Get the full path to the test scores CSV file
test_scores_path = os.path.join(os.path.dirname(__file__), "..", "data", "testScores.csv")


predicted_csv_path = os.path.join(os.path.dirname(__file__), "..", "data","outputs", "predicted.csv")

# Load your pre-trained ML model using pickle
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
    expected_columns = [ 'ProductType', 'OutletSize', 'LocationType', 'OutletType', 'ProductVisibility', 'MRP', 'EstablishmentYear']
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
      return flask.jsonify({"error": f"Missing columns in CSV file: {', '.join(missing_columns)}"}), 400
    
    initialDf = df

    #Standardasing the FatContent column
    # ifc_dict = {'Low Fat':'Low Fat', 'Regular':'Regular', 'LF':'Low Fat', 'reg':'Regular', 'low fat':'Low Fat'}
    # df['FatContent'] = df['FatContent'].replace(ifc_dict)

    #Encoding data
    encode_dict = {'Low Fat':0, 'Regular': 1, 'Small':0, 'Medium':1,'High':2, 'Tier 3':2, 'Tier 2': 1, 'Tier 1': 0, 'Grocery Store':0, 'Supermarket Type1':1, 'Supermarket Type2':2, 'Supermarket Type3':3}
    df = df.replace(encode_dict)

    

    categorical_columns = df.select_dtypes(include=['object']).columns

    label_encoders = {}
    for col in categorical_columns:
      le = LabelEncoder()
      df[col] = le.fit_transform(df[col].astype(str))
      label_encoders[col] = le

    # features = df.drop(columns = ['Weight', 'FatContent','ProductID','OutletID'], axis = 1) 
    features = df 
    scaler = StandardScaler()
    features = scaler.fit_transform(features)


    # Make the prediction using your pre-trained Lasso model
    prediction = model.predict(features)

    initialDf['OutletSales'] = prediction

     # Load corresponding full data CSV based on filename
    full_data_filename = None
    if uploaded_file.filename.startswith("CleanedSynth1_Test_Set"):
        full_data_filename = "CleanedSynth1_Test_Set_Full.csv"
    elif uploaded_file.filename.startswith("CleanedSynth2_Test_Set"):
        full_data_filename = "CleanedSynth2_Test_Set_Full.csv"
    else:
        return flask.jsonify({"error": "Invalid file name. Expected 'CleanedSynth1_Test_Set.csv' or 'CleanedSynth2_Test_Set.csv'"}), 400

    # Load full data CSV
    try:
        full_data = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "data", full_data_filename))
    except Exception as e:
        return flask.jsonify({"error": f"Error reading full data CSV: {str(e)}"}), 400

    # Calculate MSE and R-squared
    mse = np.sqrt(mean_squared_error(full_data['OutletSales'], initialDf['OutletSales']))
    r2 = r2_score(full_data['OutletSales'], initialDf['OutletSales'])

    # Create a new DataFrame for the score
    score_data = {'filename': uploaded_file.filename, 'mse': mse, 'r2': r2}
    score_df = pd.DataFrame(score_data, index=[0])

    ## Append the score DataFrame to the CSV file
    if not os.path.exists(test_scores_path):
        score_df.to_csv(test_scores_path, index=False)
    else:
        score_df.to_csv(test_scores_path, mode='a', header=False, index=False)


    #decode the dataframe to original form
    # initialDf['FatContent'] = initialDf['FatContent'].replace({0:'Low Fat', 1:'Regular'})
    initialDf['OutletSize'] = initialDf['OutletSize'].replace({0:'Small', 1:'Medium', 2:'High'})
    initialDf['LocationType'] = initialDf['LocationType'].replace({0:'Tier 1', 1:'Tier 2', 2:'Tier 3'})
    initialDf['OutletType'] = initialDf['OutletType'].replace({0:'Grocery Store', 1:'Supermarket Type1', 2:'Supermarket Type2', 3:'Supermarket Type3'})


    #Saving initailDf to csv for download via API
    initialDf.to_csv(predicted_csv_path, index=False)    


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

@app.route("/getTestScores" , methods=["GET"])
def get_test_scores():
  """
  Reads the testScores.csv file and returns its contents as JSON.
  """
  # Get the full path to the test scores CSV file
  test_scores_path = os.path.join(os.path.dirname(__file__), "..", "data", "testScores.csv")

  # Try to read the CSV data using pandas
  try:
    df = pd.read_csv(test_scores_path)
    # Convert the DataFrame to a dictionary (optional)
    data = df.to_dict(orient="records")
    response = flask.jsonify(data)
  except Exception as e:
    # Handle errors gracefully
    return flask.jsonify({"error": f"Error reading test scores: {str(e)}"}), 500

  response.headers['Access-Control-Allow-Origin'] = '*'
  return response

#Add a route to download the initialDf.csv file
@app.route("/downloadPredicted", methods=["GET"])
def download_predicted():

    # Check if the file exists
    if not os.path.exists(predicted_csv_path):
        return flask.jsonify({"error": "Predicted CSV file not found"}), 404

    response = flask.send_file(predicted_csv_path, as_attachment=True)
    response.headers['Access-Control-Allow-Origin'] = '*'
    try:
        return response
    finally:
        # Delete the file immediately after download
        try:
            os.remove(predicted_csv_path)
            print("Predicted CSV file deleted successfully after download")
        except FileNotFoundError:
            print("Predicted CSV file not found after download")
        except Exception as e:
            print(f"Error deleting predicted file after download: {e}")


if __name__ == "__main__":
    app.run()
