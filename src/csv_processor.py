import pandas as pd
import numpy as np
from pathlib import Path

path = "data/Superstore.csv"

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


   null_percentage_dict = null_percentage.to_dict()
   null_percentage_dict_x = {k: str(v) for k, v in null_percentage_dict.items()}


   output_dic.update({'null_row_count': null_counts_x, 'null_percentage': null_percentage_dict_x})

   return output_dic

result = stats_processor(path)
print(result)
   
