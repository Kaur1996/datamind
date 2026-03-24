import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.file_router import file_name
from src.csv_processor import stats_processor

load_dotenv()

client = genai.Client(api_key=os.getenv("google_api_key"))


def generate_insights(file_path):
    fn = file_name(file_path)
    stats = stats_processor(file_path)
    llm_stats_context = json.dumps(stats)

    # The prompt below is very important. It can be customised for the dataset we are using or else a generic one
    # for general datasets and not a specific one.
    system_prompt = f"""Assume that you are a data analyst and you want to draw insights and recommendations from {fn}.
    The user message contains the descriptive statistics of the data. It contains sample first 10 rows of data, 
    row and column count of the data, mean, median and other descriptive stats, null row counts and percentages of nulls. 
    The output should be just 10 insights from the data in json format. No extra text, no redundant markdowns or backticks.
    Each insight should be max 3-4 sentences with a numeric data pointer supporting it.
    The json format is as follows:
    {{
        "insights": [
            {{
                "insight_number": 1,
                "category": "...",
                "insight": "...",
                "recommendation": "...",
                "confidence": 85
            }}
        ]
    }}
    Number each insight from 1 to 10. Define categories based on the dataset.
    Each insight max 3-4 sentences, each recommendation max 2-3 sentences.
    The confidence score is between 0 and 100 - it is LLM confidence, not statistical confidence.

    The dataset statistics dictionary contains the following sections in order:

    row count and column count — dataset dimensions
    columns — all column names
    data_types — column names and their data types
    sample_rows — first 10 rows of actual data
    statistics — descriptive stats for numeric columns
    null_row_count and null_percentage — missing data per column
    categorical_columns, numeric_columns, id_columns — classified column lists
    colname_aggregate — for low cardinality categorical columns, full aggregation table
    colname_top10_by_metric and colname_bottom10_by_metric — for high cardinality columns, 
    top and bottom 10 rows by each metric. Use each section wisely to generate useful insights
    """

    user_message = f"""Dataset name: {fn}
    Dataset statistics: {llm_stats_context}"""

    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=10000,
        system_instruction=system_prompt,
        response_mime_type="application/json"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=config
    ) 
    return response.text

if __name__ == "__main__":
    result = generate_insights("data/Superstore.csv")
    print(result)