import pandas as pd
import numpy as np


def clean_column_names(df):
    """
    Standardize column names.
    """
    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    return df


def remove_duplicates(df):
    """
    Remove duplicate records.
    """
    df = df.copy()
    return df.drop_duplicates().reset_index(drop=True)


def handle_missing_values(df):
    """
    Handle missing values based on column type.
    """
    df = df.copy()

    for column in df.columns:

        if df[column].isnull().sum() == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[column]):
            df[column] = df[column].fillna(df[column].median())

        else:
            mode = df[column].mode()

            if not mode.empty:
                df[column] = df[column].fillna(mode.iloc[0])
            else:
                df[column] = df[column].fillna("Unknown")

    return df


def preprocess_data(df):
    """
    Complete preprocessing pipeline.
    """
    df = clean_column_names(df)
    df = remove_duplicates(df)
    df = handle_missing_values(df)

    return df