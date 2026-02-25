import seaborn as sns
import os
import pandas as pd

def load_dataset():
    """
    Loads seaborn titanic dataset and saves to titanic.csv if not present.
    Returns the DataFrame.
    """
    csv_path = "titanic.csv"
    if not os.path.exists(csv_path):
        df = sns.load_dataset("titanic")
        df = df.copy()
        df.to_csv(csv_path, index=False)
        print("Created titanic.csv from seaborn dataset.")
    else:
        df = pd.read_csv(csv_path)
    df.columns = [c.lower() for c in df.columns]
    return df