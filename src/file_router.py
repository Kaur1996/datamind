import os
from pathlib import Path

def detect_file_type(path):
    extensions_list = Path(path).suffixes

    if len(extensions_list) >= 1:

        file_extension = extensions_list[-1].lower()

        if file_extension == '.csv':
            return 'csv'
        

        elif file_extension == '.pdf':
            return 'pdf'

        else:
            raise ValueError('unknown file type, try again with csv or pdf file only')
    else:
        raise ValueError('Please input correct file path with file name .csv or .pdf extension')


