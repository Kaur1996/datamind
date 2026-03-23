import pandas as pd
import numpy as np
from pathlib import Path
import re
import json


identifier_keywords = ['code', 'zip', 'phone', 'postal', 'number', 'no', 'num', 
                        'index', 'key', 'year', 'month', 'day', 'rank', 
                        'latitude', 'longitude', 'lat', 'lon', 'lng']

def stats_processor(path):
    output_dic = {}
    input_df = pd.read_csv(path, header=0, encoding='latin1')

    sh = input_df.shape
    output_dic.update({'row count': sh[0], 'column count': sh[1]})

    df_columns = input_df.columns.to_list()
    output_dic.update({'columns': df_columns})

    df_datatypes = input_df.dtypes.to_dict()
    df_datatypes_x = {k: str(v) for k, v in df_datatypes.items()}
    output_dic.update({'data_types': df_datatypes_x})

    df_sample_rows = input_df.head(10).to_string()
    output_dic.update({'sample_rows': df_sample_rows})

    df_stats = input_df.describe().to_string()
    output_dic.update({'statistics': df_stats})

    null_counts = input_df.isnull().sum()
    null_percentage = (null_counts / sh[0]) * 100
    null_counts_x = {k: str(v) for k, v in null_counts.to_dict().items()}
    null_percentage_dict_x = {k: str(v) for k, v in null_percentage.to_dict().items()}
    output_dic.update({'null_row_count': null_counts_x, 'null_percentage': null_percentage_dict_x})
    
    # We need actual data in some form to be passed onto the LLM
    # For this we will need some aggregations and pivot table. At first we will filter out catgeorical columns
    # and numerical columns. We also filter out ID columns such as ship_id or order_id because they are not 
    # actually used for aggregations such as mean/sum. They are just stored as INT. We also filter out cat columns 
    # such as postal zip code, phone number etc which might be classified as numeric in nature.

    # Column classification
    pattern = r"\bID\b" # this regex is to search for _ID columns such as ship_id , ship id, product_id etc
    id_columns = [col for col in df_datatypes_x.keys() if re.search(pattern, col, re.IGNORECASE)]
                # above line of code searched for the regex pattern, ignore's case in the keys of the dict
                # because keys contain the column names. If regex is found, it appends it to the list.

    # We need categorical columns idenitifed and passed onto LLM for it to 
    # know which columns will act as dimensions and which are numeric. We use for loop on key value pairs of 
    # the dict accesed with .items() function. the key is column name and value is the datatype. This is as 
    # per our structure above in df_datatypes dict. If the datatype is of type object means it is categorical
    # else a numeric one

    cat_columns = [] 
    numeric_columns = []
    for col, datatype in df_datatypes_x.items():
        if datatype == 'object':
            cat_columns.append(col)
        else:
            numeric_columns.append(col)
    # As mentioned above that we would need to filter out certain columns from categorical and numeric ones
    # We use the below logic to do exactly the same. 

    # Below is list subtraction: cat_columns - id_columns
    filtered_cat_columns = [col for col in cat_columns if col not in id_columns] 

    # We added this for three reasons:

    # Remove ID columns from numeric — columns like Row ID are integers but they're identifiers,
    #  not metrics. Averaging a Row ID means nothing business wise.
    # Remove high cardinality numeric columns — if a numeric column has more than 80% unique values 
    # it's likely an identifier disguised as a number. For example Postal Code has hundreds of 
    # unique values — averaging postal codes is meaningless.
    # Remove keyword-matched identifiers — some columns have names like postal_code or 
    # phone_number that clearly aren't metrics even if their cardinality isn't extremely high.

    # The goal was to make sure filtered_numeric_columns contains only true business metrics 
    # like Sales, Profit, Quantity, Discount — columns where aggregations like mean, sum, and std 
    # actually mean something.Without this filter, we'd be passing garbage aggregations to the LLM 
    # like "average Row ID = 4997" which would confuse it and dilute the quality of insights.

    filtered_numeric_columns = [
        col for col in numeric_columns
        if col not in id_columns
        and (input_df[col].nunique() / sh[0] < 0.8)
        and not any(keyword in col.lower() for keyword in identifier_keywords)
    ]

    output_dic.update({
        'categorical_columns': filtered_cat_columns,
        'numeric_columns': filtered_numeric_columns,
        'id_columns': id_columns
    })
    
    # This part actually created those pivot tables that we would pass to LLM along with other basic data stats
    for cat_col in filtered_cat_columns: # loop across all categorical columns
        agg_pivot = input_df.groupby(cat_col)[filtered_numeric_columns].agg(['sum', 'count', 'mean', 'min', 'max', 'std']) # create this main big group by with all ags
    
        if input_df[cat_col].nunique() < 50: # If the categorical column has low cardinality, we simply pass it fully with all values and aggregations
            output_dic.update({cat_col + "_aggregate": agg_pivot.to_string()})
        else: # If the categorical column has high cardinality, we pick on top and bottom 10 sorted by 3 aggregations - mean, sum, count
            for num_col in filtered_numeric_columns:
                for agg_func in ['mean', 'sum', 'count']:
                    top10 = agg_pivot.nlargest(10, (num_col, agg_func))
                    bottom10 = agg_pivot.nsmallest(10, (num_col, agg_func))
                    output_dic.update({
                        f"{cat_col}_top10_by_{num_col}_{agg_func}": top10.to_string(),
                        f"{cat_col}_bottom10_by_{num_col}_{agg_func}": bottom10.to_string()
                    })

    return output_dic
