import streamlit as st
import json
import tempfile
import os
from src.insight_engine import generate_insights

# ─── Page Configuration ───────────────────────────────────────────────────────
# Sets the browser tab title and page layout
st.set_page_config(
    page_title="DataMind",
    page_icon="🧠",
    layout="centered"
)

# ─── Header Section ───────────────────────────────────────────────────────────
st.title("🧠 DataMind")
st.subheader("Turn raw data into business insights in seconds")

st.markdown("""
DataMind uses AI to analyze your dataset and generate 10 actionable business insights with recommendations. 
No SQL, no dashboards, no data science degree required — just upload your file and let the AI do the work.

**How to use:**
1. Prepare your CSV file with clean column headers in the first row
2. Upload it using the file uploader below
3. Wait 20-30 seconds while DataMind analyzes your data
4. Review your 10 ranked insights with recommendations and confidence scores

**Accepted files:** CSV only (PDF support coming soon)
""")

st.info("""
**Best practices:**
- Make sure your first row contains column headers
- Remove any completely empty rows or columns before uploading
- Larger datasets give richer insights — aim for at least 500 rows
""")

# ─── File Upload Section ───────────────────────────────────────────────────────
# st.file_uploader returns a file object when a file is uploaded, None otherwise
uploaded_file = st.file_uploader("Upload your dataset", type=['csv'])

if uploaded_file is not None:

    # Save uploaded file to a temporary location on disk
    # Our pipeline functions require a file path, not a file object
    # delete=False ensures the file persists after closing so pipeline can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # ─── Pipeline Execution ───────────────────────────────────────────────────
    # Show a spinner while the LLM generates insights
    # This prevents the user from thinking the app has frozen
    with st.spinner("Analyzing your data... this may take 20-30 seconds"):
        result = generate_insights(tmp_path)

    # Clean up temporary file after pipeline is done
    # Good practice to avoid filling up disk space
    os.unlink(tmp_path)

    # ─── Parse LLM Response ───────────────────────────────────────────────────
    # LLM returns a JSON string — parse it into a Python dictionary
    # so we can loop through and display each insight individually
    try:
        insights_data = json.loads(result)
        insights_list = insights_data['insights']

        # ─── Display Insights ─────────────────────────────────────────────────
        st.subheader("Your 10 Business Insights")
        st.markdown("---")

        for insight in insights_list:
            # Each insight displayed as a collapsible card
            with st.expander(f"#{insight['insight_number']} — {insight['category']}"):
                
                # Replace $ signs to prevent Streamlit interpreting them as LaTeX
                insight_text = insight['insight'].replace('$', '\\$')
                recommendation_text = insight['recommendation'].replace('$', '\\$')

                st.markdown(insight_text)
                st.info(f"**Recommendation:** {recommendation_text}")
                
                # Confidence score displayed as a metric widget
                # This is LLM confidence, not statistical confidence
                st.metric(label="LLM Confidence", value=f"{insight['confidence']}%")

    except json.JSONDecodeError:
        # Handle cases where LLM returns malformed JSON
        st.error("Something went wrong parsing the insights. Please try again.")
        st.write(result)