import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import os

def clean_data(filepath,missing_strategy,remove_duplicates,drop_columns):

    df=pd.read_csv(filepath)


   # Missing values
    if missing_strategy == 'drop':
      df = df.dropna()
    elif missing_strategy == 'mean':
        df = df.fillna(df.mean(numeric_only=True))
    elif missing_strategy == 'median':
        df = df.fillna(df.median(numeric_only=True))
    elif missing_strategy == 'zero':
        df = df.fillna(0)
    elif missing_strategy == 'mode':
        for col in df.select_dtypes(include='object').columns:
            mode = df[col].mode()[0]
            df[col].fillna(mode, inplace=True)
    elif missing_strategy == 'unknown':
        for col in df.select_dtypes(include='object').columns:
            df[col].fillna('Unknown', inplace=True)

    # Remove duplicates
    if remove_duplicates:
        df = df.drop_duplicates()

    # Drop columns
    if drop_columns:
        df = df.drop(columns=drop_columns)

    dir_path = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    cleaned_filename = filename.replace('.csv', '_cleaned.csv')
    cleaned_path = os.path.join(dir_path, cleaned_filename)
    df.to_csv(cleaned_path, index=False)
    return cleaned_path

  

def perform_eda(filepath):
    
    
    df = pd.read_csv(filepath)

    # Summary stats
    summary = df.describe(include='all').to_html()
   
    return summary
