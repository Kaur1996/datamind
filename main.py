from src.file_router import detect_file_type, file_name
from src.csv_processor import stats_processor
from src.insight_engine import generate_insights

def run_pipeline(path):
    """
    Main pipeline function that orchestrates the entire insight generation process.
    
    Takes a file path as input, detects the file type, processes the data
    and returns 10 LLM generated business insights with recommendations.
    
    Args:
        file_path (str): Path to the input file (CSV or PDF)
    
    Returns:
        str: JSON string containing 10 business insights
    
    Raises:
        ValueError: If file type is not supported
    """
    
    is_csv = detect_file_type(path)

    if is_csv == 'csv':
        insights = generate_insights(path)
        return insights
    else:
        print("support on PDF coming soon")

if __name__ == "__main__":
    path = input("Enter file path: ")
    result = run_pipeline(path)
    print(result)