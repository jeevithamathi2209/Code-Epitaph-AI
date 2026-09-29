import pandas as pd


def calculate_missing_percentage(df):
    """
    Calculate missing-value percentage for each column.
    """
    return (
        df.isnull()
        .mean()
        .mul(100)
        .round(2)
        .sort_values(ascending=False)
    )


def calculate_column_uniqueness(df):
    """
    Calculate uniqueness percentage for each column.
    """
    results = {}

    for column in df.columns:
        total = len(df[column])

        if total == 0:
            results[column] = 0
        else:
            unique_values = df[column].nunique(dropna=True)
            results[column] = round((unique_values / total) * 100, 2)

    return pd.Series(results).sort_values(ascending=False)


def analyze_dataset(df):
    """
    Generate a basic structural analysis of the dataset.
    """

    analysis = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": len(df.select_dtypes(include="number").columns),
        "text_columns": len(df.select_dtypes(include="object").columns),
    }

    return analysis