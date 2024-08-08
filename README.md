# major-project-backend: The Catalyst API
This is the Flask API that facilitates sales prediction using a pre-trained model and user-uploaded data for The Catalyst app.

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
