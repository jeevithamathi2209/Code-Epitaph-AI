import pandas as pd
from pathlib import Path


def load_data(file_path):
    """
    Load a CSV dataset safely.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("The dataset is empty.")

    return df


def get_dataset_info(df):
    """
    Return basic information about the dataset.
    """
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "column_names": list(df.columns)
    }