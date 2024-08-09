# major-project-backend: The Catalyst API
This is the Flask API that facilitates sales prediction using a pre-trained model and user-uploaded data for The Catalyst app.

**Getting Started:**

To get started with this project, follow these steps:

1. Clone the repository from the GitHub link provided: [https://github.com/sshahniaz/major-project-backend](https://github.com/sshahniaz/major-project-backend)

2. Navigate to the project directory:

    ```
    cd major-project-backend
    ```

3. Set up a Python virtual environment:

    ```
    python -m venv venv
    ```

4. Activate the virtual environment:

    - For Windows:

        ```
        venv\Scripts\activate
        ```

    - For macOS/Linux:

        ```
        source venv/bin/activate
        ```

5. Install the required dependencies by running the following command in your terminal:

    ```
    pip install -r requirements.txt
    ```

6. Run the Flask API by executing the following command:

    ```
    python app.py
    ```
7. To deploy the Flask API using Gunicorn, execute the following command:

    ```
         gunicorn -w 2 src.app:app  
    ```

    This will start the API using Gunicorn as the server. You can access the API endpoints using tools like cURL or Postman.

    - Note: Make sure you have Gunicorn installed in your Python virtual environment.



7. The API will start running on `http://localhost:5000`. You can access the API endpoints using tools like cURL or Postman.

8. Use the provided routes (`/predict`, `/getTestScores`, `/downloadPredicted`) to interact with the API and perform the desired functionalities.


To get started with this project, follow these steps:

1. Clone the repository from the GitHub link provided: [https://github.com/sshahniaz/major-project-backend](https://github.com/sshahniaz/major-project-backend)

2. Install the required dependencies by running the following command in your terminal:

    ```
    pip install -r requirements.txt
    ```

3. Make sure you have Python installed on your system. This project requires Python 3.7 or higher.

4. Once the dependencies are installed, navigate to the project directory:

    ```
    cd major-project-backend
    ```

5. Run the Flask API by executing the following command:

    ```
    python app.py
    ```

6. The API will start running on `http://localhost:5000`. You can access the API endpoints using tools like cURL or Postman.

7. Use the provided routes (`/predict`, `/getTestScores`, `/downloadPredicted`) to interact with the API and perform the desired functionalities.



**Key Functionalities:**

*   **Prediction:** Upload a CSV file containing product and outlet information. The API predicts sales figures using the loaded model and returns a JSON response with:
    
    *   Top 10 product types by predicted sales
        
    *   Average sales for various categories (Location Type, Outlet Type, Outlet Size, Product Type) in a nested structure
        
    *   Additional metrics like Mean Squared Error (MSE) and R-squared
        
*   **Test Scores Retrieval:** Retrieves historical test scores stored in a CSV file and returns them as JSON.
    
*   **Predicted Data Download:** Allows users to download the predicted sales data (including original data with predicted sales) as a CSV file.
    

**Flask Routes:**

*   **/predict (POST):** Handles prediction requests.
    
*   **/getTestScores (GET):** Retrieves test scores.
    
*   **/downloadPredicted (GET):** Provides a downloadable predicted sales data CSV.
    

**Code Breakdown:**

**1\. Imports:**

*   Flask: Core web framework for building the API.
    
*   Libraries for data manipulation (pandas, numpy), model loading (pickle), file handling (os), error handling (json), and request processing (flask).
    

**2\. Model Loading:**

*   Loads the pre-trained Lasso regression model from a pickle file (BigMart\_Sales\_Model.pkl).
    

**3\. Prediction Route (/predict):**

*   Checks for uploaded file.
    
*   Validates file format (CSV).
    
*   Reads the CSV data using pandas.
    
*   Performs data cleaning and pre-processing steps:
    
    *   Handles missing columns.
        
    *   Encodes categorical variables using a dictionary (encode\_dict).
        
    *   Applies label encoding for remaining categorical features.
        
    *   Standardizes numerical features using a StandardScaler.
        
*   Uses the loaded model to predict sales for the processed data.
    
*   Calculates performance metrics (MSE, R-squared) by comparing predicted sales with actual values from a corresponding full data CSV (based on filename).
    
*   Appends the score data (filename, MSE, R-squared) to a CSV file (testScores.csv).
    
*   Decodes some features back to their original labels.
    
*   Saves the processed data with predicted sales to a CSV file (predicted.csv).
    
*   Calculates and structures sales data by product type, location type, outlet type, and outlet size.
    
*   Prepares the JSON response with the prediction results and nested sales data.
    
*   Allows Cross-Origin Resource Sharing (CORS) for broader accessibility.
    

**4\. Test Scores Route (/getTestScores):**

*   Reads the testScores.csv file containing historical test scores.
    
*   Converts the data to a dictionary using pandas.
    
*   Returns the data as JSON with CORS enabled.
    

**5\. Predicted Data Download Route (/downloadPredicted):**

*   Checks if the predicted data CSV (predicted.csv) exists.
    
*   Sends the file for download as an attachment with CORS enabled.
    
*   Attempts to delete the downloaded file to avoid storage issues.
    

**6\. Main Block:**

*   Runs the Flask development server if the script is executed directly.
    

**Additional Notes:**

*   The code utilizes pre-defined dictionaries for categorical variable encoding (encode\_dict) and label encoders (label\_encoders).
    
*   File paths for model, data, and output files are constructed dynamically using os.path.join for better maintainability.
    
*   Error handling is implemented to gracefully handle exceptions during file operations, data processing, and model prediction.
    

**GitHub Link:** [**https://github.com/sshahniaz/major-project-backend**](https://github.com/sshahniaz/major-project-backend)

**Hosted Link (this is the API link use the methods above to access):** [**https://sea-turtle-app-vktl8.ondigitalocean.app/**](https://sea-turtle-app-vktl8.ondigitalocean.app/)
