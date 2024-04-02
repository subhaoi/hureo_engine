
Flask App for Processing and Analyzing Customer Feedback
This Flask application is designed to analyze customer feedback by processing conversation transcripts, extracting issues and good features, categorizing them, and presenting the analysis in a structured format.

Features
Conversation Analysis: Analyzes chunks of customer feedback to identify issues and good features.
Supercategory Mapping: Categorizes identified issues and features into supercategories for a structured overview.
Batch Processing: Processes items in batches to efficiently handle large datasets.
OpenAI Integration: Utilizes OpenAI's GPT-3.5 model to interpret and categorize feedback.
REST API: Offers a RESTful endpoint to accept conversation transcripts and return analyzed data.
How It Works
Receiving Transcripts: The application accepts a JSON payload containing customer conversation transcripts through the /process-conversations POST endpoint.
Chunking Conversations: Conversations are divided into manageable chunks for analysis.
Extracting Data: Each chunk is analyzed to extract issues and good features, utilizing the OpenAI API.
Categorizing Data: Extracted items are categorized into predefined supercategories based on their content.
Aggregating Data: Results are aggregated and mapped to their supercategories.
Serializing for Output: The aggregated data is serialized into a JSON-compatible format for output.
Returning Results: The analyzed and categorized data is returned as a JSON response.
Requirements
To run this application, ensure you have the following installed:

Python 3.7 or higher
Flask
openai
Other dependencies listed in requirements.txt
Setup
Clone the repository and navigate into the project directory.
Install dependencies using pip install -r requirements.txt.
Set your OpenAI API key in the application code.
Run the Flask app using flask run or python -m flask run.
Usage
Send a POST request to http://127.0.0.1:5000/process-conversations with a JSON payload containing the conversation transcripts. The response will be a JSON structure with the analyzed data.