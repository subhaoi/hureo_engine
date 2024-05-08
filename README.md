# Flask App for Processing and Analyzing Customer Feedback

This Flask application is designed to analyze customer feedback by processing conversation transcripts, extracting issues and good features, categorizing them, and presenting the analysis in a structured format.

## Features

- **Conversation Analysis:** Analyzes chunks of customer feedback to identify issues and good features.
- **Supercategory Mapping:** Categorizes identified issues and features into supercategories for a structured overview.
- **Batch Processing:** Processes items in batches to efficiently handle large datasets.
- **OpenAI Integration:** Utilizes OpenAI's GPT model to interpret and categorize feedback.
- **REST API:** Offers a RESTful endpoint to accept conversation transcripts and return analyzed data.

## How It Works

1. **Receiving Transcripts:** The application accepts a JSON payload containing customer conversation transcripts through the `/process-conversations` POST endpoint.
2. **Chunking Conversations:** Conversations are divided into manageable chunks for analysis.
3. **Extracting Data:** Each chunk is analyzed to extract issues and good features, utilizing the OpenAI API.
4. **Categorizing Data:** Extracted items are categorized into predefined supercategories based on their content.
5. **Aggregating Data:** Results are aggregated and mapped to their supercategories.
6. **Serializing for Output:** The aggregated data is serialized into a JSON-compatible format for output.
7. **Returning Results:** The analyzed and categorized data is returned as a JSON response.

## Requirements

To run this application, ensure you have the following installed:
- Python 3.7 or higher
- Flask
- openai
- Other dependencies listed in `requirements.txt`

## Setup

1. Clone the repository and navigate into the project directory.
2. Install dependencies using `pip install -r requirements.txt`.
3. Set your OpenAI API key in the application code.
4. Run the Flask app using `flask run` or `python -m flask run`.

## Usage

Send a POST request to `http://127.0.0.1:5000/process-conversations` with a JSON payload containing the conversation transcripts. The response will be a JSON structure with the analyzed data.

# API Documentation for Customer Feedback Analysis

## Endpoint

`POST /process-conversations`

Accepts a list of conversation transcripts and returns an analyzed and categorized summary of issues and good features identified in the conversations.

## Input

- The request body must be a JSON array of conversation transcript objects.
- Each object represents a single message within a conversation.

### Sample Input JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "description": "A list of users with their respective conversation transcripts",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "userID": {
        "type": "string",
        "description": "A unique identifier for each user"
      },
      "transcript": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {
              "type": "integer",
              "description": "Unique identifier for the transcript entry"
            },
            "startTime": {
              "type": "number",
              "description": "Start time of the transcript segment"
            },
            "endTime": {
              "type": "number",
              "description": "End time of the transcript segment"
            },
            "name": {
              "type": "string",
              "description": "Name of the entity speaking"
            },
            "message": {
              "type": "string",
              "description": "Content of the message spoken"
            }
          },
          "required": ["id", "startTime", "endTime", "name", "message"]
        }
      }
    },
    "required": ["userID", "transcript"]
  }
}

```

### Sample Input

```json
[
    {
        "userID": "user1",
        "transcript": [
            {
                "id": 2,
                "startTime": 11.77,
                "endTime": 20,
                "name": "Hureo UX Research Company",
                "message": "I'm just testing it out, if recording and trans  this is edited from UI. edited!"
            },
            {
                "id": 4,
                "startTime": 31.45,
                "endTime": 33.479,
                "name": "Hureo UX Research Company",
                "message": "updating after deployment"
            }
        ]
    },
    {
        "userID": "user2",
        "transcript": [
            {
                "id": 2,
                "startTime": 11.77,
                "endTime": 20,
                "name": "Hureo UX Research Company",
                "message": "I'm just testing it out, if recording and trans this is edited from UI. edited!"
            },
            {
                "id": 4,
                "startTime": 31.45,
                "endTime": 33.479,
                "name": "Hureo UX Research Company",
                "message": "updating after deployment"
            }
        ]
    }
]

```

## Output

- The response is a JSON array containing the analyzed data for each message chunk, categorized by issue and good features.
- Each object in the array represents a category of feedback, with the count of instances for each identified issue or good feature.

### Output JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "category": { "type": "string" },
      "type": {
        "type": "string",
        "enum": ["Issue", "Good Feature"]
      },
      "issue_feature": {
        "type": ["string", "array"],
        "items": { "type": "string" }
      },
      "user": { "type": "string" },
      "transcript_chunk": { "type": "string" },
      "no_of_instances": {
        "type": ["integer", "array"],
        "items": { "type": "integer" },
        "minimum": 1
      }
    },
    "required": ["category", "type", "issue_feature", "user", "transcript_chunk", "no_of_instances"],
    "additionalProperties": false
  }
}
```

### Sample Output

```json
[
  {
    "category_level_1": "Uncategorized",
    "category_level_2": "Issue",
    "category_level_3": "Swigen Stomach Works",
    "user": "user1",
    "transcript_chunk": "Unknown: Morning. Arunima: Yeah, I've started the recording. So you have any questions for me right now. Unknown: No, nothing. As of now. I'm just waiting to understand exactly. So basically, all are doing research on. Jismitha Poojary: Are you doing research on how Swigen stomach works Jismitha Poojary: for me? Or is it about the platform that you all want to know?",
    "no_of_instances": 1
  }
]
```

This API endpoint provides detailed insights into the conversations by analyzing and categorizing the feedback into issues and good features, facilitating a better understanding of customer experiences.
