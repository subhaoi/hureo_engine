import openai
import json
import csv
import os
import re
import sys
from collections import defaultdict, Counter
from flask import Flask, request, jsonify

app = Flask(__name__)

# Register the namespace

# Set your OpenAI API key here
openai.api_key = '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'

def query_openai_chat_model(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message['content'].strip()


def understand_issues(message):
    prompt = f'''
    Analyze the following customer feedback message and extract the issues and good features mentioned. 
    Present your findings in a dictionary format with two keys: "issues" and "good_features". Each key should map to a list of strings, where each string is an issue or good feature identified in the feedback.
    
    Message: "{message}"
    '''
    return query_openai_chat_model(prompt)


def analyze_conversation_chunk(chunk_text):
    issues = understand_issues(chunk_text)   
    return issues


def group_messages_into_chunks(transcripts, chunk_size=10):
    chunks = []
    for transcript in transcripts:
        chunk = ""
        messages = transcript['transcript']
        user = transcript['userID']
        for i, message in enumerate(messages):
            chunk += f"{message['name']}: {message['message']} "
            if (i + 1) % chunk_size == 0 or i + 1 == len(messages):
                chunks.append((user, chunk.strip()))
                chunk = ""
        if chunk:  # add remaining chunk if any
            chunks.append((user, chunk.strip()))
    return chunks


issue_pattern = re.compile(r"'issues': \[([^\]]+)\]")
good_feature_pattern = re.compile(r"'good_features': \[([^\]]+)\]")

def extract_items(pattern, text):
    """Extracts and standardizes items from text using the given pattern."""
    if not isinstance(text, str):
        return []

    match = pattern.search(text)
    if match:
        items = match.group(1)
        # Remove leading/trailing spaces, newlines, and standardize format
        standardized_items = {
            ' '.join(word.capitalize() for word in item.strip(" '\"\n").split())
            for item in items.split(',')
        }
        return standardized_items
    return []

def categorize_batch_with_gpt4(batch_items, known_supercategories):
    # Prepare a list of known supercategories to include in the prompt for reference
    supercategories_reference = "\n".join(f"- {category}" for category in set(known_supercategories))
    if supercategories_reference:
        supercategories_hint = f"Known supercategories:\n{supercategories_reference}\n\n"
    else:
        supercategories_hint = ""
    
    formatted_items = "\n".join(f"- {item}" for item in batch_items)
    prompt = (
        f"This is current super categories list use them {supercategories_hint} Below is a list of customer issues and good features. "
        "For each item, categorize it into a supercategory and return the result in the following JSON format: "
        "[{issue: 'Issue/Feature', supercategory: 'Supercategory'}]. Please provide a JSON array with a JSON object for each item.\n\n"
        f"Items:\n{formatted_items}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that categorizes customer feedback into supercategories and returns structured JSON data."},
            {"role": "user", "content": prompt}
        ],
    )
    output = response.choices[0].message['content'].strip()
    try:
        parsed_response = json.loads(output.replace('json','').replace('```', ''))
        return parsed_response
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

def process_in_batches(items, batch_size=50):
    categorized_results = []
    known_supercategories = []  # This list now resides inside the function

    # Iterate over items in batches
    for i in range(0, len(items), batch_size):
        batch_items = items[i:i + batch_size]
        # Pass both the current batch and known supercategories for contextual hints
        batch_results = categorize_batch_with_gpt4(batch_items, known_supercategories)
        categorized_results.extend(batch_results)
        
        # Update known supercategories based on this batch's results
        for result in batch_results:
            if 'supercategory' in result:
                known_supercategories.append(result['supercategory'])

    # Remove duplicates from known_supercategories if necessary
    known_supercategories = list(set(known_supercategories))
    return categorized_results

@app.route('/process-conversations', methods=['POST'])
def process_conversations():
    # Expecting JSON input containing a list of transcripts
    transcripts = request.json
    print("data received")
    chunk_size = 5  # Optional chunk size parameter

    # Group messages into chunks
    chunks = group_messages_into_chunks(transcripts, chunk_size=chunk_size)

    # Analyze each chunk
    analysis_results = []
    aggregated_data = defaultdict(int)
    distinct_issues = set()
    distinct_features = set()
    for user, chunk in chunks:
        issues = analyze_conversation_chunk(chunk)
        analysis_results.append({
            "user": user,
            "transcript_chunk": chunk,
            "issues": issues
        })
    print("analysis_results:", analysis_results)


    for transcript in analysis_results:
        user = transcript['user']
        transcript_chunk = transcript['transcript_chunk']
        issues_text = transcript['issues']

        # Convert the issues text from a JSON string to a dictionary
        try:
            issues_data = json.loads(issues_text)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            continue  # Skip this transcript if there's an error

        # Process issues
        if "issues" in issues_data:
            for issue in issues_data["issues"]:
                issue_key = (issue, user, transcript_chunk, "Issue")
                aggregated_data[issue_key] += 1
                distinct_issues.add(issue)

        # Process good features
        if "good_features" in issues_data:
            for feature in issues_data["good_features"]:
                feature_key = (feature, user, transcript_chunk, "Good Feature")
                aggregated_data[feature_key] += 1
                distinct_features.add(feature)
    # Return the analysis as JSON

    categorized_issues = process_in_batches(list(distinct_issues), 50)
    categorized_features = process_in_batches(list(distinct_features), 50)

    print("categorized_issues:", categorized_issues)

    print("categorized_features:", categorized_features)

    supercategory_mapping_issues = {item['issue']: item['supercategory'] for item in categorized_issues}
    supercategory_mapping_features = {item['issue']: item['supercategory'] for item in categorized_features}


    print("supercategory_mapping_issues:", supercategory_mapping_issues)

    print("supercategory_mapping_features:", supercategory_mapping_features)

    # New dictionary to hold data with supercategories
    enhanced_aggregated_data = defaultdict(int)

    # Process each item to include supercategories
    for row in aggregated_data.items():
        try:
            if row[0][3] == "Issue":
                supercategory = supercategory_mapping_issues.get(row[0][0], "Unknown")
            elif row[0][3] == "Good Feature":
                supercategory = supercategory_mapping_features.get(row[0][0], "Unknown")
            else:
                supercategory = "Unknown"
            # Update the enhanced structure
            enhanced_aggregated_data[(supercategory, row[0][3], row[0][0], row[0][1], row[0][2])] += row[1]
        except:
            pass
    

    # Convert tuple keys to string format
    # Convert the enhanced aggregated data into a list of dictionaries
    enhanced_aggregated_data_list = []
    for key, value in enhanced_aggregated_data.items():
        supercategory, category, issue_feature, user, transcript_chunk = key
        enhanced_aggregated_data_list.append({
            "category_level_1": supercategory,
            "category_level_2": category,
            "category_level_3": issue_feature,
            "user": user,
            "transcript_chunk": transcript_chunk,
            "no_of_instances": value
        })

    # Use the list of dictionaries with jsonify to ensure the output is in the correct format
    return jsonify(enhanced_aggregated_data_list)


if __name__ == '__main__':
    app.run(debug=True)

